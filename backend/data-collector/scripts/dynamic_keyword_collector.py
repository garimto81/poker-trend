#!/usr/bin/env python3
"""
동적 키워드 수집 시스템
실시간 트렌드를 반영한 키워드 자동 업데이트
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
from collections import Counter
import re
from googleapiclient.discovery import build
import requests

logger = logging.getLogger(__name__)


class DynamicKeywordCollector:
    """실시간 트렌드 기반 동적 키워드 수집기"""
    
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        self.base_keywords = [
            # 핵심 키워드 (고정)
            'poker', '포커', 'holdem', '홀덤',
            
            # 주요 브랜드/대회 (고정)
            'WSOP', 'WPT', 'EPT', 'PokerStars', 'GGPoker'
        ]
        
        # 동적 키워드 저장 경로
        self.keywords_file = 'data/dynamic_keywords.json'
        self.trending_file = 'data/trending_topics.json'
        
    def collect_trending_keywords(self) -> Dict[str, List[str]]:
        """여러 소스에서 트렌딩 키워드 수집"""
        trending_keywords = {
            'youtube_trending': self._get_youtube_trending(),
            'related_searches': self._get_related_searches(),
            'video_tags': self._get_popular_video_tags(),
            'comment_keywords': self._get_comment_keywords()
        }
        
        return trending_keywords
    
    def _get_youtube_trending(self) -> List[str]:
        """YouTube 트렌딩 비디오에서 키워드 추출"""
        try:
            # 게임 카테고리(20)에서 트렌딩 비디오 가져오기
            request = self.youtube.videos().list(
                part='snippet',
                chart='mostPopular',
                videoCategoryId='20',  # Gaming
                regionCode='US',
                maxResults=50
            )
            response = request.execute()
            
            keywords = []
            for item in response.get('items', []):
                title = item['snippet']['title'].lower()
                # 포커 관련 비디오만 필터링
                if any(base in title for base in ['poker', '포커', 'holdem', '홀덤']):
                    # 제목에서 키워드 추출
                    words = re.findall(r'\b[a-zA-Z가-힣]+\b', title)
                    keywords.extend([w for w in words if len(w) > 2])
                    
                    # 태그도 수집
                    if 'tags' in item['snippet']:
                        keywords.extend(item['snippet']['tags'][:5])
            
            return keywords
            
        except Exception as e:
            logger.error(f"YouTube trending collection error: {e}")
            return []
    
    def _get_related_searches(self) -> List[str]:
        """관련 검색어 수집"""
        related_keywords = []
        
        for base_keyword in self.base_keywords[:5]:  # 상위 5개만
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=base_keyword,
                    type='video',
                    maxResults=10
                )
                response = request.execute()
                
                # 검색 결과에서 자주 나오는 단어 추출
                for item in response.get('items', []):
                    title = item['snippet']['title']
                    words = re.findall(r'\b[a-zA-Z가-힣]+\b', title.lower())
                    related_keywords.extend([w for w in words if len(w) > 3])
                    
            except Exception as e:
                logger.error(f"Related search error for {base_keyword}: {e}")
                
        return related_keywords
    
    def _get_popular_video_tags(self) -> List[str]:
        """인기 동영상의 태그 수집"""
        tags = []
        
        try:
            # 최근 24시간 인기 포커 영상
            published_after = (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z'
            
            request = self.youtube.search().list(
                part='snippet',
                q='poker',
                type='video',
                order='viewCount',
                publishedAfter=published_after,
                maxResults=20
            )
            response = request.execute()
            
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if video_ids:
                # 비디오 상세 정보로 태그 가져오기
                videos_request = self.youtube.videos().list(
                    part='snippet',
                    id=','.join(video_ids[:10])
                )
                videos_response = videos_request.execute()
                
                for video in videos_response.get('items', []):
                    if 'tags' in video['snippet']:
                        tags.extend(video['snippet']['tags'][:10])
                        
        except Exception as e:
            logger.error(f"Popular video tags error: {e}")
            
        return tags
    
    def _get_comment_keywords(self) -> List[str]:
        """인기 댓글에서 키워드 추출"""
        comment_keywords = []
        
        try:
            # 최근 인기 포커 영상 몇 개 선택
            request = self.youtube.search().list(
                part='snippet',
                q='poker',
                type='video',
                order='relevance',
                maxResults=5
            )
            response = request.execute()
            
            for item in response.get('items', [])[:3]:  # 상위 3개만
                video_id = item['id']['videoId']
                
                # 댓글 가져오기
                comments_request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    order='relevance',
                    maxResults=20
                )
                
                try:
                    comments_response = comments_request.execute()
                    
                    for comment in comments_response.get('items', []):
                        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        # 영어와 한글 단어 추출
                        words = re.findall(r'\b[a-zA-Z가-힣]{3,}\b', text.lower())
                        comment_keywords.extend(words)
                        
                except Exception as e:
                    # 댓글이 비활성화된 경우 무시
                    pass
                    
        except Exception as e:
            logger.error(f"Comment keywords error: {e}")
            
        return comment_keywords
    
    def analyze_and_rank_keywords(self, all_keywords: Dict[str, List[str]]) -> List[tuple]:
        """수집된 키워드 분석 및 순위 매기기"""
        # 모든 키워드 통합
        combined_keywords = []
        for source, keywords in all_keywords.items():
            combined_keywords.extend(keywords)
        
        # 불용어 제거
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'was', 'are', 'were', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'some', 'any', 'many', 'much',
            '의', '를', '을', '이', '가', '은', '는', '에', '에서', '으로', '와', '과'
        }
        
        # 필터링 및 정규화
        filtered_keywords = []
        for keyword in combined_keywords:
            keyword = keyword.lower().strip()
            if (len(keyword) > 2 and 
                keyword not in stopwords and 
                keyword not in self.base_keywords and
                not keyword.isdigit()):
                filtered_keywords.append(keyword)
        
        # 빈도수 계산
        keyword_counter = Counter(filtered_keywords)
        
        # 상위 키워드 반환
        return keyword_counter.most_common(30)
    
    def update_dynamic_keywords(self) -> Dict[str, any]:
        """동적 키워드 업데이트 및 저장"""
        logger.info("Starting dynamic keyword collection...")
        
        # 트렌딩 키워드 수집
        trending_keywords = self.collect_trending_keywords()
        
        # 키워드 분석 및 순위
        ranked_keywords = self.analyze_and_rank_keywords(trending_keywords)
        
        # 결과 구성
        result = {
            'timestamp': datetime.now().isoformat(),
            'base_keywords': self.base_keywords,
            'trending_keywords': [kw[0] for kw in ranked_keywords[:20]],
            'keyword_scores': dict(ranked_keywords),
            'sources': {
                source: len(keywords) 
                for source, keywords in trending_keywords.items()
            }
        }
        
        # 파일로 저장
        os.makedirs('data', exist_ok=True)
        with open(self.keywords_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Updated {len(ranked_keywords)} trending keywords")
        
        return result
    
    def get_search_keywords(self) -> List[str]:
        """검색에 사용할 최종 키워드 목록 반환"""
        try:
            # 저장된 동적 키워드 로드
            if os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 24시간 이내 데이터인지 확인
                timestamp = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - timestamp < timedelta(hours=24):
                    # 기본 키워드 + 상위 트렌딩 키워드
                    return self.base_keywords + data['trending_keywords'][:10]
            
            # 오래된 데이터거나 없으면 업데이트
            self.update_dynamic_keywords()
            return self.get_search_keywords()
            
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            # 오류 시 기본 키워드만 반환
            return self.base_keywords
    
    def get_trending_report(self) -> Dict[str, any]:
        """트렌딩 리포트 생성"""
        if os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 새로운 트렌딩 키워드 (이전과 비교)
            new_trending = []
            rising_keywords = []
            
            # 이전 데이터와 비교 (있다면)
            if os.path.exists(self.trending_file):
                with open(self.trending_file, 'r', encoding='utf-8') as f:
                    prev_data = json.load(f)
                
                prev_keywords = set(prev_data.get('trending_keywords', []))
                curr_keywords = set(data['trending_keywords'])
                
                new_trending = list(curr_keywords - prev_keywords)[:5]
                
                # 순위 상승 키워드
                prev_scores = prev_data.get('keyword_scores', {})
                curr_scores = data['keyword_scores']
                
                for keyword in curr_keywords:
                    if keyword in prev_scores:
                        prev_rank = list(prev_scores.keys()).index(keyword) if keyword in prev_scores else 999
                        curr_rank = list(curr_scores.keys()).index(keyword) if keyword in curr_scores else 999
                        if curr_rank < prev_rank:
                            rising_keywords.append({
                                'keyword': keyword,
                                'rank_change': prev_rank - curr_rank,
                                'score': curr_scores[keyword]
                            })
                
                rising_keywords.sort(key=lambda x: x['rank_change'], reverse=True)
            
            # 현재 데이터를 trending 파일로 저장
            with open(self.trending_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                'current_trending': data['trending_keywords'][:10],
                'new_keywords': new_trending,
                'rising_keywords': rising_keywords[:5],
                'keyword_sources': data['sources'],
                'last_updated': data['timestamp']
            }
        
        return None


def main():
    """테스트 실행"""
    collector = DynamicKeywordCollector()
    
    # 키워드 업데이트
    result = collector.update_dynamic_keywords()
    
    print("=== 동적 키워드 수집 결과 ===")
    print(f"기본 키워드: {', '.join(result['base_keywords'])}")
    print(f"\n트렌딩 키워드 TOP 20:")
    for i, keyword in enumerate(result['trending_keywords'], 1):
        score = result['keyword_scores'][keyword]
        print(f"{i}. {keyword} (빈도: {score})")
    
    print(f"\n수집 소스:")
    for source, count in result['sources'].items():
        print(f"- {source}: {count}개")
    
    # 트렌딩 리포트
    report = collector.get_trending_report()
    if report and report.get('new_keywords'):
        print(f"\n새로운 트렌딩 키워드: {', '.join(report['new_keywords'])}")


if __name__ == "__main__":
    main()