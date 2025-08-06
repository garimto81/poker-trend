#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 콘텐츠 검증 시스템
YouTube 영상이 진짜 포커 관련 콘텐츠인지 검증하는 모듈

기능:
- 메타데이터 기반 검증 (제목, 설명, 태그)
- 카테고리 및 채널 신뢰도 검증
- 통계 패턴 분석 (길이, 조회수, 참여율)
- 캐싱 시스템
- 학습 기반 정확도 개선
"""

import os
import re
import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class PokerContentValidator:
    """포커 콘텐츠 검증기"""
    
    def __init__(self, cache_file_path: Optional[str] = None):
        """
        초기화
        
        Args:
            cache_file_path: 캐시 파일 경로 (선택사항)
        """
        # 포커 관련 키워드 정의
        self.poker_keywords = {
            # 필수 키워드 (높은 가중치)
            'essential': [
                'poker', 'holdem', 'hold\'em', 'texas holdem', 'omaha', 'stud',
                'wsop', 'world series of poker', 'wpt', 'world poker tour',
                'ept', 'european poker tour', 'triton poker', 'triton'
            ],
            
            # 강력한 지표 키워드
            'strong_indicators': [
                'pokerstars', 'ggpoker', 'partypoker', '888poker',
                'hustler casino', 'aria', 'bellagio', 'bicycle casino',
                'commerce casino', 'borgata'
            ],
            
            # 게임 용어
            'game_terms': [
                'flop', 'turn', 'river', 'preflop', 'postflop',
                'blind', 'small blind', 'big blind', 'ante', 
                'all in', 'all-in', 'fold', 'raise', 'call', 'check',
                'bet', 'pot', 'stack', 'chips'
            ],
            
            # 핸드 및 전략 용어
            'hand_terms': [
                'flush', 'straight', 'full house', 'four of a kind', 'quads',
                'royal flush', 'straight flush', 'pair', 'two pair', 'trips',
                'set', 'nuts', 'outs', 'odds', 'bluff', 'semi-bluff',
                'value bet', 'continuation bet', 'c-bet'
            ],
            
            # 유명 플레이어
            'famous_players': [
                'phil ivey', 'daniel negreanu', 'phil hellmuth', 'doyle brunson',
                'johnny chan', 'stu ungar', 'antonio esfandiari', 'erik seidel',
                'tom dwan', 'durrrr', 'isildur1', 'patrik antonius',
                'doug polk', 'vanessa selbst', 'kathy liebert', 'jennifer harman'
            ]
        }
        
        # 제외 키워드 (스팸 또는 무관한 콘텐츠)
        self.exclude_keywords = {
            # 명백한 스팸
            'spam': [
                'free money', 'free chips', 'hack', 'cheat', 'bot', 'script',
                'unlimited chips', 'generator', 'mod apk', 'cracked'
            ],
            
            # 포커와 무관한 콘텐츠
            'unrelated': [
                'minecraft', 'fortnite', 'roblox', 'among us',
                'cooking', 'recipe', 'makeup', 'tutorial',
                'workout', 'fitness', 'yoga', 'dance'
            ],
            
            # 오해의 소지가 있는 키워드
            'misleading': [
                'poker face song', 'lady gaga', 'poker face makeup',
                'poker face dance', 'poker face cover', 'poker face karaoke',
                'strip poker', 'video poker machine'
            ],
            
            # 저품질 콘텐츠 지표
            'low_quality': [
                'click here', 'subscribe now', 'like and subscribe',
                'easy money', 'get rich quick', '100% win rate'
            ]
        }
        
        # 신뢰할 수 있는 포커 채널
        self.trusted_channels = {
            # 공식 채널 (100% 신뢰)
            'PokerGO': 100,
            'PokerStars': 100,
            'World Poker Tour': 100,
            'WSOP': 100,
            'partypoker': 100,
            '888poker': 100,
            
            # 유명 카지노 (95% 신뢰)
            'Hustler Casino Live': 95,
            'Live at the Bike': 95,
            'Texas Card House': 95,
            
            # 유명 플레이어/크리에이터 (90% 신뢰)
            'Brad Owen': 90,
            'Rampage Poker': 90,
            'Alec Torelli': 90,
            'Andrew Neeme': 90,
            'Poker Vlogs': 90,
            
            # 포커 전문 채널 (85% 신뢰)
            'Doug Polk Poker': 85,
            'Daniel Negreanu': 85,
            'Phil Hellmuth': 85,
            'Jonathan Little': 85,
            'SplitSuit Poker': 85,
            'Red Chip Poker': 85,
            'Upswing Poker': 85,
            
            # 교육 채널 (80% 신뢰)
            'PokerCoaching': 80,
            'Run It Once': 80,
            'Card Player': 80,
            'PokerNews': 80
        }
        
        # YouTube 카테고리 ID
        self.valid_categories = {
            "20": "Gaming",
            "24": "Entertainment", 
            "17": "Sports",
            "22": "People & Blogs",
            "19": "Travel & Events"
        }
        
        # 캐시 시스템
        self.cache_file = cache_file_path or Path(__file__).parent / "validation_cache.json"
        self.cache = self._load_cache()
        
        # 검증 통계
        self.stats = defaultdict(int)
        
        # 임계값 설정
        self.thresholds = {
            'high_confidence': 80,    # 80점 이상: 확실한 포커 콘텐츠
            'medium_confidence': 60,  # 60-79점: 가능성 높은 포커 콘텐츠
            'low_confidence': 40,     # 40-59점: 불확실
            'reject': 40              # 40점 미만: 포커 콘텐츠 아님
        }
    
    def _load_cache(self) -> Dict:
        """캐시 파일 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"캐시 파일 로드 실패: {e}")
        
        return {
            'trusted_videos': set(),
            'rejected_videos': set(),
            'validation_history': {},
            'last_updated': None
        }
    
    def _save_cache(self):
        """캐시 파일 저장"""
        try:
            # Set을 list로 변환하여 JSON 직렬화 가능하게 만듦
            cache_to_save = {
                'trusted_videos': list(self.cache.get('trusted_videos', set())),
                'rejected_videos': list(self.cache.get('rejected_videos', set())),
                'validation_history': self.cache.get('validation_history', {}),
                'last_updated': str(datetime.now())
            }
            
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_to_save, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"캐시 파일 저장 실패: {e}")
    
    def check_cache(self, video_id: str) -> Tuple[Optional[bool], float]:
        """
        캐시에서 비디오 검증 결과 확인
        
        Returns:
            (is_poker_content, confidence) 또는 (None, 0) if not cached
        """
        if video_id in self.cache.get('trusted_videos', set()):
            return True, 1.0
        elif video_id in self.cache.get('rejected_videos', set()):
            return False, 1.0
        else:
            return None, 0.0
    
    def validate_metadata(self, video_data: Dict) -> Tuple[int, List[str]]:
        """
        메타데이터 기반 검증 (제목, 설명, 태그)
        
        Args:
            video_data: 비디오 메타데이터
            
        Returns:
            (점수, 플래그 리스트)
        """
        title = video_data.get('title', '').lower()
        description = video_data.get('description', '').lower()
        tags = [tag.lower() for tag in video_data.get('tags', [])]
        
        score = 0
        flags = []
        
        # 1. 제목에서 필수 키워드 검색
        essential_matches = sum(1 for kw in self.poker_keywords['essential'] 
                               if kw in title)
        if essential_matches > 0:
            score += essential_matches * 25  # 필수 키워드당 25점
            flags.append(f'essential_keywords_{essential_matches}')
        
        # 2. 강력한 지표 키워드
        strong_matches = sum(1 for kw in self.poker_keywords['strong_indicators'] 
                            if kw in title)
        if strong_matches > 0:
            score += strong_matches * 20
            flags.append(f'strong_indicators_{strong_matches}')
        
        # 3. 설명에서 게임 용어 찾기
        game_term_count = sum(1 for term in self.poker_keywords['game_terms'] 
                             if term in description)
        score += min(game_term_count * 3, 15)  # 최대 15점
        if game_term_count > 0:
            flags.append(f'game_terms_{game_term_count}')
        
        # 4. 핸드 및 전략 용어
        hand_term_count = sum(1 for term in self.poker_keywords['hand_terms'] 
                             if term in description)
        score += min(hand_term_count * 2, 10)  # 최대 10점
        if hand_term_count > 0:
            flags.append(f'hand_terms_{hand_term_count}')
        
        # 5. 유명 플레이어 언급
        player_mentions = sum(1 for player in self.poker_keywords['famous_players'] 
                             if player in title or player in description)
        score += min(player_mentions * 10, 20)  # 최대 20점
        if player_mentions > 0:
            flags.append(f'famous_players_{player_mentions}')
        
        # 6. 제외 키워드 확인 (패널티)
        for category, keywords in self.exclude_keywords.items():
            penalty_count = sum(1 for kw in keywords 
                               if kw in title or kw in description)
            if penalty_count > 0:
                penalty = penalty_count * 20
                score -= penalty
                flags.append(f'penalty_{category}_{penalty_count}')
        
        # 7. 태그 검증
        poker_tag_count = sum(1 for tag in tags 
                             if any(kw in tag for kw in self.poker_keywords['essential']))
        score += min(poker_tag_count * 5, 10)  # 최대 10점
        if poker_tag_count > 0:
            flags.append(f'poker_tags_{poker_tag_count}')
        
        return max(0, score), flags  # 음수 점수 방지
    
    def validate_channel_category(self, video_data: Dict) -> int:
        """
        채널 신뢰도 및 카테고리 검증
        
        Args:
            video_data: 비디오 메타데이터
            
        Returns:
            점수 (0-100)
        """
        score = 0
        
        # 1. 채널 신뢰도 확인
        channel_title = video_data.get('channelTitle', '')
        channel_id = video_data.get('channelId', '')
        
        # 채널명 기반 신뢰도
        max_trust_score = 0
        for trusted_channel, trust_score in self.trusted_channels.items():
            if trusted_channel.lower() in channel_title.lower():
                max_trust_score = max(max_trust_score, trust_score)
        
        score += max_trust_score
        
        # 2. 카테고리 확인
        category_id = video_data.get('categoryId', '')
        if category_id in self.valid_categories:
            score += 15
        
        return min(score, 100)  # 최대 100점 제한
    
    def parse_duration(self, duration_str: str) -> int:
        """
        YouTube duration을 분 단위로 변환
        
        Args:
            duration_str: PT4M13S 형식의 문자열
            
        Returns:
            분 단위 duration
        """
        try:
            # PT4M13S -> 4분 13초
            duration_pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(duration_pattern, duration_str)
            
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                
                return hours * 60 + minutes + (1 if seconds > 0 else 0)
                
        except Exception as e:
            logger.warning(f"Duration 파싱 실패: {duration_str}, {e}")
        
        return 0
    
    def validate_statistics(self, video_data: Dict) -> Tuple[int, Dict]:
        """
        통계 패턴 기반 검증
        
        Args:
            video_data: 비디오 통계 데이터
            
        Returns:
            (점수, 통계 정보)
        """
        duration = video_data.get('duration', 'PT0M0S')
        view_count = int(video_data.get('viewCount', 0))
        like_count = int(video_data.get('likeCount', 0))
        comment_count = int(video_data.get('commentCount', 0))
        
        score = 0
        stats_info = {}
        
        # 1. 영상 길이 패턴 분석
        duration_minutes = self.parse_duration(duration)
        stats_info['duration_minutes'] = duration_minutes
        
        if 1 <= duration_minutes <= 5:
            # 짧은 하이라이트 (포커 클립)
            score += 10
        elif 10 <= duration_minutes <= 30:
            # 일반적인 포커 핸드 분석
            score += 20
        elif 30 <= duration_minutes <= 120:
            # 캐시게임 세션 또는 토너먼트
            score += 25
        elif duration_minutes > 120:
            # 라이브 스트림 (매우 높은 신뢰도)
            score += 30
        
        # 2. 조회수 패턴
        stats_info['view_count'] = view_count
        if view_count >= 100000:
            score += 15  # 인기 영상
        elif view_count >= 10000:
            score += 10  # 적당한 인기
        elif view_count >= 1000:
            score += 5   # 기본 인기
        elif view_count < 100:
            score -= 10  # 매우 낮은 조회수는 의심스러움
        
        # 3. 참여율 계산
        if view_count > 0:
            engagement_rate = (like_count + comment_count) / view_count
            stats_info['engagement_rate'] = engagement_rate
            
            if engagement_rate > 0.1:      # 10% 이상 (매우 높음)
                score += 20
            elif engagement_rate > 0.05:  # 5-10% (높음)
                score += 15
            elif engagement_rate > 0.02:  # 2-5% (보통)
                score += 10
            elif engagement_rate < 0.005: # 0.5% 미만 (의심스러움)
                score -= 5
        
        # 4. 좋아요/싫어요 비율 (가능한 경우)
        dislike_count = int(video_data.get('dislikeCount', 0))
        if like_count > 0 and dislike_count > 0:
            like_ratio = like_count / (like_count + dislike_count)
            stats_info['like_ratio'] = like_ratio
            
            if like_ratio > 0.9:       # 90% 이상 좋아요
                score += 15
            elif like_ratio > 0.8:     # 80-90% 좋아요
                score += 10
            elif like_ratio < 0.6:     # 60% 미만 좋아요 (문제 있을 수 있음)
                score -= 5
        
        return max(0, score), stats_info
    
    def comprehensive_validate(self, video_data: Dict) -> Dict:
        """
        종합적인 포커 콘텐츠 검증
        
        Args:
            video_data: YouTube 비디오 데이터
            
        Returns:
            검증 결과 딕셔너리
        """
        video_id = video_data.get('videoId') or video_data.get('id', {}).get('videoId', '')
        
        # 1. 캐시 확인
        cached_result, cached_confidence = self.check_cache(video_id)
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            return {
                'is_poker_content': cached_result,
                'confidence': cached_confidence,
                'total_score': cached_confidence * 100,
                'source': 'cache',
                'details': {}
            }
        
        # 2. 각 검증 단계 실행
        total_score = 0
        details = {}
        
        # 2-1. 메타데이터 검증 (가중치 40%)
        meta_score, meta_flags = self.validate_metadata(video_data)
        weighted_meta_score = meta_score * 0.4
        total_score += weighted_meta_score
        details['metadata'] = {
            'raw_score': meta_score,
            'weighted_score': weighted_meta_score,
            'flags': meta_flags
        }
        
        # 2-2. 채널/카테고리 검증 (가중치 30%)
        channel_score = self.validate_channel_category(video_data)
        weighted_channel_score = channel_score * 0.3
        total_score += weighted_channel_score
        details['channel_category'] = {
            'raw_score': channel_score,
            'weighted_score': weighted_channel_score
        }
        
        # 2-3. 통계 패턴 검증 (가중치 20%)
        stats_score, stats_info = self.validate_statistics(video_data)
        weighted_stats_score = stats_score * 0.2
        total_score += weighted_stats_score
        details['statistics'] = {
            'raw_score': stats_score,
            'weighted_score': weighted_stats_score,
            'info': stats_info
        }
        
        # 2-4. 추가 검증 (가중치 10%)
        additional_score = self._additional_validation(video_data)
        weighted_additional_score = additional_score * 0.1
        total_score += weighted_additional_score
        details['additional'] = {
            'raw_score': additional_score,
            'weighted_score': weighted_additional_score
        }
        
        # 3. 최종 판단
        confidence_level = self._calculate_confidence(total_score)
        is_poker = total_score >= self.thresholds['reject']
        confidence = min(total_score / 100, 1.0)
        
        # 4. 통계 업데이트
        self.stats['total_validations'] += 1
        self.stats[f'confidence_{confidence_level}'] += 1
        if is_poker:
            self.stats['poker_content_detected'] += 1
        else:
            self.stats['non_poker_content_detected'] += 1
        
        result = {
            'video_id': video_id,
            'is_poker_content': is_poker,
            'confidence': confidence,
            'confidence_level': confidence_level,
            'total_score': total_score,
            'details': details,
            'source': 'validation',
            'timestamp': str(datetime.now())
        }
        
        # 5. 캐시에 저장 (높은 신뢰도인 경우만)
        if confidence > 0.8:
            if is_poker:
                if isinstance(self.cache.get('trusted_videos'), list):
                    self.cache['trusted_videos'] = set(self.cache['trusted_videos'])
                self.cache.setdefault('trusted_videos', set()).add(video_id)
            else:
                if isinstance(self.cache.get('rejected_videos'), list):
                    self.cache['rejected_videos'] = set(self.cache['rejected_videos'])
                self.cache.setdefault('rejected_videos', set()).add(video_id)
            
            # 검증 히스토리에도 저장
            self.cache.setdefault('validation_history', {})[video_id] = {
                'score': total_score,
                'is_poker': is_poker,
                'timestamp': result['timestamp']
            }
            
            self._save_cache()
        
        return result
    
    def _additional_validation(self, video_data: Dict) -> int:
        """추가 검증 로직"""
        score = 0
        
        # 플레이리스트 컨텍스트 확인
        playlist_title = video_data.get('playlist', {}).get('title', '').lower()
        if playlist_title:
            poker_in_playlist = any(kw in playlist_title 
                                   for kw in self.poker_keywords['essential'])
            if poker_in_playlist:
                score += 20
        
        # 업로드 날짜 패턴 (최근 업로드일수록 신뢰도 높음)
        published_at = video_data.get('publishedAt', '')
        if published_at:
            try:
                from datetime import datetime
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(pub_date.tzinfo) - pub_date).days
                
                if days_ago <= 7:      # 1주일 이내
                    score += 10
                elif days_ago <= 30:   # 1개월 이내
                    score += 5
                elif days_ago > 365:   # 1년 이상 (약간 감점)
                    score -= 2
            except:
                pass
        
        return score
    
    def _calculate_confidence(self, total_score: float) -> str:
        """점수를 기반으로 신뢰도 레벨 계산"""
        if total_score >= self.thresholds['high_confidence']:
            return 'high'
        elif total_score >= self.thresholds['medium_confidence']:
            return 'medium'
        elif total_score >= self.thresholds['low_confidence']:
            return 'low'
        else:
            return 'very_low'
    
    def batch_validate(self, videos: List[Dict]) -> List[Dict]:
        """
        여러 비디오를 일괄 검증
        
        Args:
            videos: 비디오 데이터 리스트
            
        Returns:
            검증된 포커 콘텐츠만 포함한 리스트
        """
        validated_videos = []
        validation_results = []
        
        logger.info(f"🔍 {len(videos)}개 영상 포커 콘텐츠 검증 시작")
        
        for i, video in enumerate(videos):
            try:
                result = self.comprehensive_validate(video)
                validation_results.append(result)
                
                if result['is_poker_content']:
                    # 검증 결과를 비디오 데이터에 추가
                    video['validation'] = result
                    validated_videos.append(video)
                    
                    confidence_emoji = "🟢" if result['confidence'] > 0.8 else "🟡"
                    logger.info(f"{confidence_emoji} [{i+1}/{len(videos)}] 포커 콘텐츠 확인: {video.get('title', 'Unknown')[:50]}... "
                               f"(신뢰도: {result['confidence']:.1%}, 점수: {result['total_score']:.1f})")
                else:
                    logger.warning(f"❌ [{i+1}/{len(videos)}] 포커 콘텐츠 아님: {video.get('title', 'Unknown')[:50]}... "
                                  f"(점수: {result['total_score']:.1f})")
                    
            except Exception as e:
                logger.error(f"❌ 검증 중 오류 발생: {video.get('title', 'Unknown')}: {e}")
                continue
        
        # 검증 통계 로그
        self._log_validation_stats(validation_results)
        
        if len(videos) > 0:
            filter_rate = (1 - len(validated_videos)/len(videos))
            logger.info(f"✅ 검증 완료: {len(validated_videos)}/{len(videos)}개 영상이 포커 콘텐츠로 확인됨 "
                       f"(필터링율: {filter_rate:.1%})")
        else:
            logger.info("⚠️ 검증할 영상이 없습니다.")
        
        return validated_videos
    
    def _log_validation_stats(self, results: List[Dict]):
        """검증 통계 로그 출력"""
        if not results:
            return
            
        total = len(results)
        poker_count = sum(1 for r in results if r['is_poker_content'])
        
        confidence_stats = defaultdict(int)
        for result in results:
            confidence_stats[result['confidence_level']] += 1
        
        logger.info("📊 검증 통계:")
        logger.info(f"   총 검증: {total}개")
        logger.info(f"   포커 콘텐츠: {poker_count}개 ({poker_count/total:.1%})")
        logger.info(f"   필터링됨: {total-poker_count}개 ({(total-poker_count)/total:.1%})")
        logger.info(f"   신뢰도 분포: {dict(confidence_stats)}")
    
    def get_validation_stats(self) -> Dict:
        """현재까지의 검증 통계 반환"""
        return dict(self.stats)
    
    def update_manual_validation(self, video_id: str, is_poker: bool, reason: str = ""):
        """
        수동 검증 결과로 캐시 업데이트
        
        Args:
            video_id: 비디오 ID
            is_poker: 포커 콘텐츠 여부
            reason: 수동 판단 이유
        """
        logger.info(f"📝 수동 검증 업데이트: {video_id} -> {'포커 콘텐츠' if is_poker else '포커 아님'}")
        
        if is_poker:
            if isinstance(self.cache.get('rejected_videos'), list):
                self.cache['rejected_videos'] = set(self.cache['rejected_videos'])
            if isinstance(self.cache.get('trusted_videos'), list):
                self.cache['trusted_videos'] = set(self.cache['trusted_videos'])
                
            self.cache.setdefault('trusted_videos', set()).add(video_id)
            self.cache.setdefault('rejected_videos', set()).discard(video_id)
        else:
            if isinstance(self.cache.get('rejected_videos'), list):
                self.cache['rejected_videos'] = set(self.cache['rejected_videos'])
            if isinstance(self.cache.get('trusted_videos'), list):
                self.cache['trusted_videos'] = set(self.cache['trusted_videos'])
                
            self.cache.setdefault('rejected_videos', set()).add(video_id)
            self.cache.setdefault('trusted_videos', set()).discard(video_id)
        
        # 히스토리에도 기록
        self.cache.setdefault('validation_history', {})[video_id] = {
            'is_poker': is_poker,
            'source': 'manual',
            'reason': reason,
            'timestamp': str(datetime.now())
        }
        
        self._save_cache()
        self.stats['manual_updates'] += 1


# 편의를 위한 함수들
def validate_single_video(video_data: Dict, cache_file: Optional[str] = None) -> Dict:
    """단일 비디오 검증"""
    validator = PokerContentValidator(cache_file)
    return validator.comprehensive_validate(video_data)

def filter_poker_videos(videos: List[Dict], cache_file: Optional[str] = None) -> List[Dict]:
    """포커 비디오만 필터링"""
    validator = PokerContentValidator(cache_file)
    return validator.batch_validate(videos)

# 미션 임포트를 위한 datetime import 추가
from datetime import datetime