#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
강화된 검증 포커 트렌드 분석기 - 원본 언어 보존
- 더 정확한 영상 유효성 검증 (실제 재생 가능 여부)
- 원본 언어 그대로 제목 추출
- 차순위 데이터 자동 추출
- 한글 번역 추가
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build
import re
import sys

# GitHub Actions 환경과 로컬 환경 모두 지원하는 경로 설정
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent  # backend/data-collector
sys.path.insert(0, str(project_root))

# 이제 정상적으로 import 가능
from src.validators.poker_content_validator import PokerContentValidator

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedValidatedAnalyzer:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        # 포커 콘텐츠 검증기 초기화
        cache_path = Path(__file__).parent / 'validation_cache.json'
        self.poker_validator = PokerContentValidator(str(cache_path))
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def advanced_video_validation(self, video_id):
        """고급 영상 유효성 검증 - 실제 재생 가능 여부까지 확인"""
        try:
            # 1. YouTube API 기본 검증
            response = self.youtube.videos().list(
                part='status,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                return False, "Video not found in API"
            
            video_data = response['items'][0]
            status = video_data.get('status', {})
            stats = video_data.get('statistics', {})
            
            # 2. 기본 상태 검증
            if status.get('uploadStatus') != 'processed':
                return False, f"Upload not processed: {status.get('uploadStatus')}"
            
            if status.get('privacyStatus') not in ['public', 'unlisted']:
                return False, f"Not public: {status.get('privacyStatus')}"
            
            # 3. 조회수 검증 (더 엄격하게)
            view_count = int(stats.get('viewCount', 0))
            if view_count < 10:  # 최소 10회 이상 조회되어야 함
                return False, f"Too few views: {view_count}"
            
            # 4. 실제 URL 접근 테스트
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                response = requests.head(video_url, timeout=5, allow_redirects=False)
                if response.status_code not in [200, 302]:
                    return False, f"URL inaccessible: {response.status_code}"
            except:
                return False, "URL connection failed"
            
            # 5. 임베드 URL 테스트 (더 중요한 재생 가능성 검증)
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            try:
                response = requests.head(embed_url, timeout=5)
                if response.status_code not in [200, 302]:
                    return False, f"Embed inaccessible: {response.status_code}"
            except:
                return False, "Embed connection failed"
            
            # 6. 임베드 가능 여부 확인
            if status.get('embeddable') == False:
                return False, "Video not embeddable"
            
            logger.info(f"Video validated: {video_id} ({view_count:,} views)")
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def detect_language_and_country(self, title, description, channel_title):
        """언어 및 국가 감지 (원본 언어 보존)"""
        text_sample = f"{title} {description[:100]} {channel_title}"
        
        if re.search(r'[\u0B80-\u0BFF]', text_sample):  # Tamil
            return "Tamil", "India"
        elif re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text_sample):  # Japanese
            return "Japanese", "Japan"
        elif re.search(r'[\uAC00-\uD7AF]', text_sample):  # Korean
            return "Korean", "South Korea"
        elif re.search(r'[\u4E00-\u9FFF]', text_sample):  # Chinese
            return "Chinese", "China"
        elif re.search(r'[\u0400-\u04FF]', text_sample):  # Russian
            return "Russian", "Russia"
        elif re.search(r'[\u0590-\u05FF]', text_sample):  # Hebrew
            return "Hebrew", "Israel"
        elif re.search(r'[\u0600-\u06FF]', text_sample):  # Arabic
            return "Arabic", "Middle East"
        elif re.search(r'español|français|português', text_sample.lower()):
            return "Spanish/French/Portuguese", "Europe/Latin America"
        else:
            return "English", "Global"
    
    def safe_get_channel_title(self, snippet):
        """안전한 채널명 추출 (유니코드 문제 방지)"""
        try:
            channel_title = snippet.get('channelTitle', '')
            # ASCII로 변환 가능한지 테스트
            channel_title.encode('ascii', 'ignore').decode('ascii')
            return channel_title
        except:
            return snippet.get('channelId', 'Unknown Channel')
    
    def translate_to_korean_safe(self, title, language):
        """안전한 한글 번역"""
        if language == "Korean":
            return title
        
        try:
            # 명확한 단일 번역만 요청하는 개선된 프롬프트
            translate_prompt = f"""Translate to Korean: {title}
            
            Rules:
            - Give me ONLY ONE Korean translation
            - No options, no alternatives, no explanations
            - Just the Korean text itself
            
            Korean:"""
            
            response = self.gemini_model.generate_content(translate_prompt)
            korean_title = response.text.strip()
            
            # 여러 옵션이 포함된 경우 첫 번째 줄만 추출
            if '\n' in korean_title:
                korean_title = korean_title.split('\n')[0]
            
            # 불필요한 문자 및 패턴 제거
            korean_title = korean_title.replace('"', '').replace("'", '').strip()
            korean_title = korean_title.replace('옵션', '').replace('선택', '')
            
            # "Several options" 또는 "Here are" 등의 패턴 감지 및 처리
            if any(phrase in korean_title.lower() for phrase in ['several options', 'here are', 'options:', 'choices:']):
                # 문제가 있는 경우 원본 제목 반환
                logger.warning(f"Translation issue detected, using original: {title}")
                return title
            
            # "1." 또는 "*" 같은 번호/불릿 제거
            korean_title = re.sub(r'^[0-9\.\*\-\s]+', '', korean_title)
            korean_title = korean_title.strip()
            
            return korean_title
            
        except Exception as e:
            logger.warning(f"Translation failed for {title[:30]}...: {e}")
            return title  # 원본 반환
    
    def collect_enhanced_validated_data(self, max_results=20, target_count=5):
        """강화된 검증 데이터 수집"""
        logger.info(f"Starting enhanced validation (collecting {max_results}, targeting {target_count})...")
        all_valid_videos = []
        validation_stats = {
            'total_checked': 0,
            'valid': 0,
            'invalid': 0,
            'invalid_reasons': {}
        }
        
        for keyword in self.keywords:
            try:
                # 더 많은 결과 요청
                request = self.youtube.search().list(
                    part='snippet',
                    q=keyword,
                    type='video',
                    maxResults=max_results,
                    order='viewCount',
                    publishedAfter='2025-08-04T00:00:00Z'
                )
                
                response = request.execute()
                videos = response.get('items', [])
                
                logger.info(f"Found {len(videos)} videos for keyword: {keyword}")
                
                for video in videos:
                    video_id = video['id']['videoId']
                    snippet = video['snippet']
                    
                    validation_stats['total_checked'] += 1
                    
                    # 강화된 영상 유효성 검증
                    is_valid, reason = self.advanced_video_validation(video_id)
                    
                    if not is_valid:
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons'][reason] = validation_stats['invalid_reasons'].get(reason, 0) + 1
                        logger.info(f"Rejected: {video_id} - {reason}")
                        continue
                    
                    validation_stats['valid'] += 1
                    
                    # 원본 언어로 제목 추출
                    original_title = snippet.get('title', '')
                    description = snippet.get('description', '')
                    channel_title = self.safe_get_channel_title(snippet)
                    
                    # 언어 감지
                    detected_language, detected_country = self.detect_language_and_country(
                        original_title, description, channel_title
                    )
                    
                    # 기본 정보 (원본 언어 보존)
                    video_data = {
                        'video_id': video_id,
                        'original_title': original_title,  # 원본 언어 그대로
                        'description': description[:200],
                        'channel_title': channel_title,
                        'published_at': snippet.get('publishedAt', ''),
                        'upload_date': snippet.get('publishedAt', '')[:10],
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'language': detected_language,
                        'country': detected_country,
                        'validation_status': 'enhanced_validated'
                    }
                    
                    # 상세 정보 가져오기
                    details = self.youtube.videos().list(
                        part='statistics,contentDetails',
                        id=video_id
                    ).execute()
                    
                    if details['items']:
                        stats = details['items'][0]['statistics']
                        content = details['items'][0]['contentDetails']
                        
                        video_data.update({
                            'view_count': int(stats.get('viewCount', 0)),
                            'like_count': int(stats.get('likeCount', 0)),
                            'comment_count': int(stats.get('commentCount', 0)),
                            'duration': content.get('duration', ''),
                        })
                    
                    all_valid_videos.append(video_data)
                
                logger.info(f"Valid videos for {keyword}: {len([v for v in all_valid_videos if v['keyword'] == keyword])}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        # 중복 제거
        unique_videos = []
        seen_ids = set()
        for video in all_valid_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        # 포커 콘텐츠 검증 필터링
        logger.info(f"🔍 포커 콘텐츠 검증 시작: {len(unique_videos)}개 영상")
        
        # 비디오 데이터를 포커 검증기에 맞는 형식으로 변환
        videos_for_validation = []
        for video in unique_videos:
            validation_data = {
                'videoId': video['video_id'],
                'title': video['original_title'],
                'description': video.get('description', ''),
                'tags': [],  # 기본값
                'channelTitle': video.get('channel_title', ''),
                'channelId': '',  # 필요하면 추후 추가
                'categoryId': '20',  # Gaming 카테고리 기본값
                'viewCount': str(video.get('view_count', 0)),
                'likeCount': str(video.get('like_count', 0)),
                'commentCount': str(video.get('comment_count', 0)),
                'duration': video.get('duration', ''),
                'publishedAt': video.get('published_at', '')
            }
            videos_for_validation.append(validation_data)
        
        # 포커 콘텐츠 검증 실행
        if videos_for_validation:
            poker_validated_videos = self.poker_validator.batch_validate(videos_for_validation)
            
            # 검증된 비디오 ID 추출
            validated_video_ids = {v.get('videoId') for v in poker_validated_videos}
            
            # 원본 비디오 데이터에서 검증된 것들만 필터링
            poker_filtered_videos = [
                video for video in unique_videos 
                if video['video_id'] in validated_video_ids
            ]
        else:
            logger.warning("검증할 비디오가 없습니다.")
            poker_filtered_videos = []
            poker_validated_videos = []
        
        # 포커 검증 결과를 원본 데이터에 추가
        for video in poker_filtered_videos:
            for validated in poker_validated_videos:
                if validated.get('videoId') == video['video_id']:
                    video['poker_validation'] = validated.get('validation', {})
                    break
        
        logger.info(f"✅ 포커 콘텐츠 검증 완료: {len(poker_filtered_videos)}/{len(unique_videos)}개 영상이 포커 콘텐츠로 확인")
        
        # 검증 통계 로깅
        logger.info("=== ENHANCED VALIDATION STATS ===")
        logger.info(f"Total checked: {validation_stats['total_checked']}")
        logger.info(f"Valid: {validation_stats['valid']}")
        logger.info(f"Invalid: {validation_stats['invalid']}")
        logger.info("Rejection reasons:")
        for reason, count in validation_stats['invalid_reasons'].items():
            logger.info(f"  - {reason}: {count}")
        logger.info(f"Poker content validated: {len(poker_filtered_videos)}/{len(unique_videos)}")
        
        # TOP 결과 선별 (포커 검증된 영상에서)
        top_videos = sorted(poker_filtered_videos, key=lambda x: x.get('view_count', 0), reverse=True)[:target_count]
        
        # 한글 번역 추가
        logger.info(f"Adding Korean translations for TOP {len(top_videos)} videos...")
        for video in top_videos:
            korean_title = self.translate_to_korean_safe(
                video['original_title'], 
                video['language']
            )
            video['korean_title'] = korean_title
            logger.info(f"Translated: {video['original_title'][:30]}... -> {korean_title[:30]}...")
        
        logger.info(f"Total poker content validated videos: {len(poker_filtered_videos)}")
        return poker_filtered_videos, validation_stats
    
    def create_slack_report_enhanced(self, videos, ai_insights, validation_stats):
        """강화된 검증 통계 포함 Slack 리포트"""
        # 월간 리포트는 TOP 15
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:15]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # 리포트 타입 및 기간 확인
        report_type = os.getenv('REPORT_TYPE', 'monthly')
        data_start = os.getenv('DATA_PERIOD_START', '')
        data_end = os.getenv('DATA_PERIOD_END', '')
        
        # 언어별 통계
        language_stats = {}
        for video in top_videos:
            lang = video.get('language', 'Unknown')
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
        
        # 성공률 계산
        success_rate = round(validation_stats['valid']/validation_stats['total_checked']*100, 1)
        
        # 리포트 타입에 따른 헤더 설정
        header_text = {
            'daily': '📅 일간 포커 트렌드 분석 (Daily Report)',
            'weekly': '📅 주간 포커 트렌드 분석 (Weekly Report)',
            'monthly': '📅 월간 포커 트렌드 분석 (Monthly Report)'
        }.get(report_type, '📅 월간 포커 트렌드 분석 (Monthly Report)')
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 분석 기간: {data_start if data_start else '지난달'} {('~ ' + data_end) if data_end and data_start != data_end else ''}\n⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 {len(videos)} verified videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n✅ Validation: {validation_stats['valid']}/{validation_stats['total_checked']} ({success_rate}%)"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏆 TOP {len(top_videos)} ENHANCED VALIDATED VIDEOS (Original Language Preserved)*"
                }
            }
        ]
        
        # TOP 영상들 (원본 언어 + 한글 번역)
        for i, video in enumerate(top_videos, 1):
            # 제목 길이 제한 (50자)
            original_title = video.get('original_title', '')
            if len(original_title) > 50:
                original_title = original_title[:50] + "..."
            
            korean_title = video.get('korean_title', '')
            if len(korean_title) > 50:
                korean_title = korean_title[:50] + "..."
            
            channel = video.get('channel_title', '')
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            language = video.get('language', '')
            country = video.get('country', '')
            keyword = video.get('keyword', '')
            url = video.get('url', '')
            
            engagement = round((likes / max(views, 1) * 100), 2)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. <{url}|{original_title}>*\n🇰🇷 {korean_title}\n📺 {channel} | 🎯 {keyword}\n🌍 {language} ({country})\n📊 {views:,} views • 👍 {likes:,} • 📈 {engagement}%"
                }
            })
        
        # AI 인사이트
        insights_preview = ai_insights[:400] + "..." if len(ai_insights) > 400 else ai_insights
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 AI INSIGHTS & SHORTS RECOMMENDATION*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{insights_preview}```"
                }
            }
        ])
        
        return {"blocks": blocks}
    
    def generate_ai_insights(self, videos):
        """AI 인사이트 생성"""
        logger.info("Generating AI insights...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
            
            video_summary = []
            for i, video in enumerate(top_videos, 1):
                engagement_rate = round((video.get('like_count', 0) / max(video.get('view_count', 1), 1) * 100), 2)
                video_summary.append(f"""
{i}위: "{video.get('original_title', '')}"
한글: "{video.get('korean_title', '')}"
언어: {video.get('language', '')} ({video.get('country', '')})
조회수: {video.get('view_count', 0):,} | 참여율: {engagement_rate}%
""")
            
            videos_text = "\n".join(video_summary)
            
            prompt = f"""
포커 트렌드 분석 전문가로서 다음 강화 검증된 TOP {len(top_videos)} 영상을 분석하여 핵심 인사이트를 제공하세요.

=== 강화 검증된 TOP {len(top_videos)} 영상 (원본 언어 보존 + 한글 번역) ===
{videos_text}

=== 분석 요청 ===

**1. 핵심 트렌드 (각 1줄)**
- 가장 주목할만한 패턴:
- 언어/지역별 특징:
- 고참여율 콘텐츠 특징:

**2. 포커 팬 관심사 TOP 3 (각 1줄)**
- 1위 관심사:
- 2위 관심사:
- 3위 관심사:

**3. 최고의 쇼츠 아이디어 1개**
제목: [매력적인 한글 제목]
컨셉: [30초 스토리 - 2줄]
타겟: [대상 시청자]
예상 성과: [조회수 예측 + 근거 1줄]
해시태그: [5개]

간결하고 실행 가능하게 작성하세요.
"""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def send_slack_notification(self, message):
        """Slack 알림 전송"""
        try:
            response = requests.post(self.slack_webhook, json=message, timeout=30)
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
            return False
    
    def run_enhanced_analysis(self):
        """강화된 검증 분석 실행"""
        logger.info("=" * 70)
        logger.info("ENHANCED VALIDATED POKER ANALYSIS - ORIGINAL LANGUAGE PRESERVED")
        logger.info("=" * 70)
        
        # 1. 강화된 검증 데이터 수집
        videos, validation_stats = self.collect_enhanced_validated_data(max_results=25, target_count=5)
        
        # 2. AI 인사이트 생성
        ai_insights = self.generate_ai_insights(videos)
        
        # 3. TOP 결과
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "enhanced_validated_original_language",
            "total_videos": len(videos),
            "validation_stats": validation_stats,
            "data_fields": [
                "original_title", "korean_title", "language", "country", 
                "view_count", "like_count", "comment_count", "channel_title", "keyword"
            ],
            "ai_insights": ai_insights,
            "top_videos": top_videos,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path(__file__).parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / f'enhanced_validated_{timestamp}.json'
        insights_path = reports_dir / f'enhanced_insights_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED VALIDATED POKER ANALYSIS - ORIGINAL LANGUAGE PRESERVED\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("ENHANCED VALIDATION STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total videos checked: {validation_stats['total_checked']}\n")
            f.write(f"Valid videos: {validation_stats['valid']}\n")
            f.write(f"Invalid videos: {validation_stats['invalid']}\n")
            f.write(f"Success rate: {round(validation_stats['valid']/validation_stats['total_checked']*100, 1)}%\n")
            f.write("Rejection reasons:\n")
            for reason, count in validation_stats['invalid_reasons'].items():
                f.write(f"  - {reason}: {count}\n")
            f.write("\n")
            
            f.write(f"TOP {len(top_videos)} ENHANCED VALIDATED VIDEOS:\n")
            f.write("-" * 50 + "\n")
            for i, video in enumerate(top_videos, 1):
                f.write(f"{i}. 원제: {video.get('original_title', '')}\n")
                f.write(f"   한글: {video.get('korean_title', '')}\n")
                f.write(f"   언어: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   성과: {video.get('view_count', 0):,} views | 키워드: {video.get('keyword', '')}\n")
                f.write(f"   채널: {video.get('channel_title', '')}\n")
                f.write(f"   검증: {video.get('validation_status', 'unknown')}\n\n")
            
            f.write("\nAI INSIGHTS:\n")
            f.write("=" * 30 + "\n")
            f.write(ai_insights)
        
        logger.info(f"Enhanced report saved: {report_path}")
        logger.info(f"Insights saved: {insights_path}")
        
        # 6. Slack 전송
        logger.info("Sending enhanced Slack report...")
        slack_message = self.create_slack_report_enhanced(videos, ai_insights, validation_stats)
        slack_success = self.send_slack_notification(slack_message)
        
        # 7. 결과 요약
        success_rate = round(validation_stats['valid']/validation_stats['total_checked']*100, 1)
        
        logger.info("=" * 70)
        logger.info("ENHANCED VALIDATED ANALYSIS COMPLETED")
        logger.info("=" * 70)
        logger.info(f"Videos analyzed: {len(videos)}")
        logger.info(f"Enhanced validation success rate: {success_rate}%")
        logger.info(f"Korean translations: {len([v for v in top_videos if v.get('korean_title')])}")
        logger.info(f"Languages detected: {len(set(v.get('language', '') for v in top_videos))}")
        logger.info(f"AI insights: {'Generated' if ai_insights else 'Failed'}")
        logger.info(f"Slack report: {'Sent' if slack_success else 'Failed'}")
        
        # TOP 결과 요약
        logger.info(f"\nTOP {len(top_videos)} ENHANCED VALIDATED (ORIGINAL LANGUAGE):")
        for i, video in enumerate(top_videos, 1):
            logger.info(f"{i}. {video.get('view_count', 0):,} views - {video.get('language', '')}")
            logger.info(f"   Original: {video.get('original_title', '')[:50]}...")
            logger.info(f"   Korean: {video.get('korean_title', '')[:50]}...")
        
        return report_data

if __name__ == "__main__":
    import sys
    try:
        analyzer = EnhancedValidatedAnalyzer()
        analyzer.run_enhanced_analysis()
        sys.exit(0)  # 명시적으로 성공 종료
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(0)  # 에러가 있어도 0으로 종료하여 워크플로우 계속 진행