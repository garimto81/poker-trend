#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 검증 포커 트렌드 분석기 - 원본 언어 보존
- 기본적인 영상 유효성 검증
- 원본 언어 그대로 제목 추출
- 한글 번역 추가
- 빠른 실행을 위한 최적화
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build
import requests
import re

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickValidatedAnalyzer:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def quick_video_validation(self, video_id, view_count):
        """빠른 영상 유효성 검증"""
        try:
            # 1. 기본 조회수 검증
            if view_count < 50:  # 최소 50회 이상
                return False, f"Too few views: {view_count}"
            
            # 2. 간단한 URL 접근 테스트 (HEAD 요청)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                response = requests.head(video_url, timeout=3)
                if response.status_code not in [200, 302]:
                    return False, f"URL inaccessible: {response.status_code}"
            except:
                return False, "URL connection failed"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def detect_language_and_country(self, title, description, channel_title):
        """언어 및 국가 감지"""
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
        else:
            return "English", "Global"
    
    def safe_get_channel_title(self, snippet):
        """안전한 채널명 추출"""
        try:
            channel_title = snippet.get('channelTitle', '')
            # 특수 문자 제거하여 안전하게 처리
            safe_title = ''.join(char for char in channel_title if ord(char) < 128)
            return safe_title if safe_title else snippet.get('channelId', 'Unknown Channel')
        except:
            return snippet.get('channelId', 'Unknown Channel')
    
    def translate_to_korean_batch(self, titles_and_languages):
        """배치로 한글 번역"""
        translations = {}
        
        for title, language in titles_and_languages:
            if language == "Korean":
                translations[title] = title
                continue
            
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
                korean_title = korean_title.replace('"', '').replace("'", '')
                korean_title = korean_title.replace('옵션', '').replace('선택', '')
                
                # "Several options" 또는 "Here are" 등의 패턴 감지 및 처리
                if any(phrase in korean_title.lower() for phrase in ['several options', 'here are', 'options:', 'choices:']):
                    # 문제가 있는 경우 원본 제목 반환
                    logger.warning(f"Translation issue detected, using original: {title}")
                    translations[title] = title
                    continue
                
                # "1." 또는 "*" 같은 번호/불릿 제거
                korean_title = re.sub(r'^[0-9\.\*\-\s]+', '', korean_title)
                korean_title = korean_title.strip()
                
                translations[title] = korean_title
                logger.info(f"Translated: {title[:30]}... -> {korean_title[:30]}...")
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
                translations[title] = title
        
        return translations
    
    def collect_quick_validated_data(self, max_results=10, target_count=5):
        """빠른 검증 데이터 수집"""
        logger.info(f"Starting quick validation (max {max_results} per keyword, target {target_count})...")
        all_valid_videos = []
        validation_stats = {
            'total_checked': 0,
            'valid': 0,
            'invalid': 0,
            'invalid_reasons': {}
        }
        
        for keyword in self.keywords:
            try:
                # 검색 요청
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
                
                # 상세 정보를 한 번에 가져오기 (최적화)
                video_ids = [video['id']['videoId'] for video in videos]
                details_response = self.youtube.videos().list(
                    part='statistics,status,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                details_dict = {item['id']: item for item in details_response.get('items', [])}
                
                for video in videos:
                    video_id = video['id']['videoId']
                    snippet = video['snippet']
                    
                    validation_stats['total_checked'] += 1
                    
                    # 상세 정보 가져오기
                    details = details_dict.get(video_id, {})
                    stats = details.get('statistics', {})
                    status = details.get('status', {})
                    content = details.get('contentDetails', {})
                    
                    view_count = int(stats.get('viewCount', 0))
                    
                    # API 레벨 검증
                    if status.get('uploadStatus') != 'processed':
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons']['Not processed'] = validation_stats['invalid_reasons'].get('Not processed', 0) + 1
                        continue
                    
                    if status.get('privacyStatus') not in ['public', 'unlisted']:
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons']['Not public'] = validation_stats['invalid_reasons'].get('Not public', 0) + 1
                        continue
                    
                    if status.get('embeddable') == False:
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons']['Not embeddable'] = validation_stats['invalid_reasons'].get('Not embeddable', 0) + 1
                        continue
                    
                    # 빠른 검증
                    is_valid, reason = self.quick_video_validation(video_id, view_count)
                    
                    if not is_valid:
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons'][reason] = validation_stats['invalid_reasons'].get(reason, 0) + 1
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
                    
                    # 비디오 데이터 (원본 언어 보존)
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
                        'view_count': view_count,
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration': content.get('duration', ''),
                        'validation_status': 'quick_validated'
                    }
                    
                    all_valid_videos.append(video_data)
                
                logger.info(f"Valid videos for {keyword}: {len([v for v in all_valid_videos if v['keyword'] == keyword])}")
                
            except Exception as e:
                logger.error(f"Error collecting {keyword}: {e}")
        
        # 중복 제거
        unique_videos = []
        seen_ids = set()
        for video in all_valid_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        # 검증 통계
        success_rate = round(validation_stats['valid']/max(validation_stats['total_checked'], 1)*100, 1)
        logger.info(f"Quick validation: {validation_stats['valid']}/{validation_stats['total_checked']} ({success_rate}%)")
        
        # TOP 선별 후 번역
        top_videos = sorted(unique_videos, key=lambda x: x.get('view_count', 0), reverse=True)[:target_count]
        
        # 한글 번역
        logger.info(f"Translating TOP {len(top_videos)} videos...")
        titles_for_translation = [(video['original_title'], video['language']) for video in top_videos]
        translations = self.translate_to_korean_batch(titles_for_translation)
        
        for video in top_videos:
            video['korean_title'] = translations.get(video['original_title'], video['original_title'])
        
        logger.info(f"Total unique validated videos: {len(unique_videos)}")
        return unique_videos, validation_stats
    
    def create_slack_report_quick(self, videos, ai_insights, validation_stats):
        """빠른 검증 Slack 리포트"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # 언어별 통계
        language_stats = {}
        for video in top_videos:
            lang = video.get('language', 'Unknown')
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
        success_rate = round(validation_stats['valid']/max(validation_stats['total_checked'], 1)*100, 1)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Quick Validated Poker Analysis (Original Language)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 {len(videos)} validated videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n⚡ Quick validation: {success_rate}% success rate"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏆 TOP {len(top_videos)} QUICK VALIDATED VIDEOS (Original Language Preserved)*"
                }
            }
        ]
        
        # TOP 영상들
        for i, video in enumerate(top_videos, 1):
            original_title = video.get('original_title', '')[:50] + ("..." if len(video.get('original_title', '')) > 50 else "")
            korean_title = video.get('korean_title', '')[:50] + ("..." if len(video.get('korean_title', '')) > 50 else "")
            
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
                    "text": "*🤖 AI INSIGHTS & BEST SHORTS IDEA*"
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
포커 트렌드 분석 전문가로서 다음 검증된 TOP {len(top_videos)} 영상을 분석하여 핵심 인사이트를 제공하세요.

=== 검증된 TOP {len(top_videos)} 영상 (원본 언어 + 한글 번역) ===
{videos_text}

**1. 핵심 트렌드 (각 1줄)**
- 가장 주목할만한 패턴:
- 언어/지역별 특징:
- 고참여율 콘텐츠 특징:

**2. 포커 팬 관심사 TOP 3 (각 1줄)**
- 1위 관심사:
- 2위 관심사:
- 3위 관심사:

**3. 최고의 쇼츠 아이디어 1개**
제목: [한글 제목]
컨셉: [30초 스토리 - 2줄]
타겟: [대상 시청자]
예상 성과: [조회수 예측 + 근거]
해시태그: [5개]

간결하게 작성하세요.
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
            return response.status_code == 200
        except:
            return False
    
    def run_quick_analysis(self):
        """빠른 검증 분석 실행"""
        logger.info("=" * 70)
        logger.info("QUICK VALIDATED POKER ANALYSIS - ORIGINAL LANGUAGE PRESERVED")
        logger.info("=" * 70)
        
        # 1. 빠른 검증 데이터 수집
        videos, validation_stats = self.collect_quick_validated_data(max_results=10, target_count=5)
        
        # 2. AI 인사이트 생성
        ai_insights = self.generate_ai_insights(videos)
        
        # 3. TOP 결과
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path(__file__).parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        insights_path = reports_dir / f'quick_validated_{timestamp}.txt'
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("QUICK VALIDATED POKER ANALYSIS - ORIGINAL LANGUAGE PRESERVED\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("QUICK VALIDATION STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total checked: {validation_stats['total_checked']}\n")
            f.write(f"Valid: {validation_stats['valid']}\n")
            f.write(f"Invalid: {validation_stats['invalid']}\n")
            f.write(f"Success rate: {round(validation_stats['valid']/max(validation_stats['total_checked'], 1)*100, 1)}%\n")
            f.write("Rejection reasons:\n")
            for reason, count in validation_stats['invalid_reasons'].items():
                f.write(f"  - {reason}: {count}\n")
            f.write("\n")
            
            f.write(f"TOP {len(top_videos)} QUICK VALIDATED VIDEOS:\n")
            f.write("-" * 50 + "\n")
            for i, video in enumerate(top_videos, 1):
                f.write(f"{i}. 원제: {video.get('original_title', '')}\n")
                f.write(f"   한글: {video.get('korean_title', '')}\n")
                f.write(f"   언어: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   성과: {video.get('view_count', 0):,} views | 키워드: {video.get('keyword', '')}\n")
                f.write(f"   채널: {video.get('channel_title', '')}\n\n")
            
            f.write("\nAI INSIGHTS:\n")
            f.write("=" * 30 + "\n")
            f.write(ai_insights)
        
        # 5. Slack 전송
        slack_message = self.create_slack_report_quick(videos, ai_insights, validation_stats)
        slack_success = self.send_slack_notification(slack_message)
        
        # 6. 결과 요약
        success_rate = round(validation_stats['valid']/max(validation_stats['total_checked'], 1)*100, 1)
        
        logger.info("=" * 70)
        logger.info("QUICK VALIDATED ANALYSIS COMPLETED")
        logger.info("=" * 70)
        logger.info(f"Videos analyzed: {len(videos)}")
        logger.info(f"Quick validation success rate: {success_rate}%")
        logger.info(f"Korean translations: {len([v for v in top_videos if v.get('korean_title')])}")
        logger.info(f"Slack report: {'Sent' if slack_success else 'Failed'}")
        
        # TOP 결과
        logger.info(f"\nTOP {len(top_videos)} QUICK VALIDATED (ORIGINAL LANGUAGE):")
        for i, video in enumerate(top_videos, 1):
            logger.info(f"{i}. {video.get('view_count', 0):,} views - {video.get('language', '')}")
            logger.info(f"   Original: {video.get('original_title', '')[:50]}...")
            logger.info(f"   Korean: {video.get('korean_title', '')[:50]}...")

if __name__ == "__main__":
    analyzer = QuickValidatedAnalyzer()
    analyzer.run_quick_analysis()