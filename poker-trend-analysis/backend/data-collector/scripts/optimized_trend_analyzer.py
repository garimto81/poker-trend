#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최적화된 포커 트렌드 분석기
- 언어/국가 감지 및 제목 한글 번역
- 간소화된 쇼츠 아이디어 1개
- 일괄 Slack 업로드
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

class OptimizedTrendAnalyzer:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def detect_language_and_country(self, title, description, channel_title):
        """언어 및 국가 감지"""
        text_sample = f"{title} {description[:100]} {channel_title}"
        
        # 언어 패턴 감지
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
        elif re.search(r'[àáâãäåæçèéêëìíîïñòóôõöøùúûüý]', text_sample.lower()):  # European
            if 'español' in text_sample.lower() or 'en français' in text_sample.lower():
                return "Spanish/French", "Europe"
            return "European", "Europe"
        else:
            return "English", "Global"
    
    def translate_title_to_korean(self, title, detected_language):
        """제목을 한글로 번역"""
        if detected_language == "Korean":
            return title
        
        try:
            if detected_language != "English":
                # 먼저 영어로 번역 후 한글로
                translate_prompt = f"Translate this {detected_language} text to Korean briefly: {title}"
            else:
                translate_prompt = f"Translate this English text to Korean briefly: {title}"
            
            response = self.gemini_model.generate_content(translate_prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.warning(f"Translation failed for {title}: {e}")
            return title  # 원본 반환
    
    def collect_enhanced_video_data(self, max_results=5):
        """향상된 YouTube 영상 데이터 수집"""
        logger.info("Starting enhanced video data collection...")
        all_videos = []
        
        for keyword in self.keywords:
            try:
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
                
                for video in videos:
                    video_id = video['id']['videoId']
                    snippet = video['snippet']
                    
                    # 언어 및 국가 감지
                    original_title = snippet.get('title', '')
                    description = snippet.get('description', '')
                    channel_title = snippet.get('channelTitle', '')
                    
                    detected_language, detected_country = self.detect_language_and_country(
                        original_title, description, channel_title
                    )
                    
                    # 기본 정보
                    video_data = {
                        'video_id': video_id,
                        'original_title': original_title,
                        'description': description[:300],  # 300자로 제한
                        'channel_title': channel_title,
                        'channel_id': snippet.get('channelId', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'upload_date': snippet.get('publishedAt', '')[:10],
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'language': detected_language,
                        'country': detected_country
                    }
                    
                    # 한글 번역 추가
                    korean_title = self.translate_title_to_korean(original_title, detected_language)
                    video_data['korean_title'] = korean_title
                    
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
                            'definition': content.get('definition', ''),
                        })
                    
                    all_videos.append(video_data)
                
                logger.info(f"Collected {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        logger.info(f"Total videos collected: {len(all_videos)}")
        return all_videos
    
    def create_concise_analysis_prompt(self, top_videos):
        """간소화된 분석 프롬프트 생성"""
        
        video_summary = []
        for i, video in enumerate(top_videos[:5], 1):
            video_summary.append(f"""
{i}위: {video.get('korean_title', '')} ({video.get('language', '')})
- 조회수: {video.get('view_count', 0):,}
- 참여율: {round((video.get('like_count', 0) / video.get('view_count', 1) * 100), 2)}%
- 국가: {video.get('country', '')}
- 채널: {video.get('channel_title', '')}
""")
        
        videos_text = "\n".join(video_summary)
        
        prompt = f"""
포커 트렌드 전문가로서 다음 TOP 5 영상을 분석하여 간결하고 정확한 인사이트를 제공하세요.

=== TOP 5 영상 데이터 ===
{videos_text}

=== 요청사항 ===

1. **핵심 트렌드 (3줄 이내)**
   - 가장 주목할 만한 패턴 1가지
   - 언어/지역별 특징 1가지  
   - 참여율이 높은 콘텐츠 특징 1가지

2. **포커 팬 관심사 (3줄 이내)**
   - 1위 관심사와 근거
   - 2위 관심사와 근거
   - 3위 관심사와 근거

3. **최고의 쇼츠 아이디어 1개**
   **제목**: [클릭을 유도하는 제목]
   **컨셉**: [30초 스토리라인 - 2줄 이내]
   **타겟**: [누구를 대상으로 하는지]
   **예상 성과**: [조회수 예측과 간단한 근거]
   **해시태그**: [최적화된 5개]

모든 답변은 간결하고 실행 가능하게 작성하세요.
"""
        return prompt
    
    def generate_concise_insights(self, videos):
        """간소화된 AI 인사이트 생성"""
        logger.info("Generating concise AI insights...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
            prompt = self.create_concise_analysis_prompt(top_videos)
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def create_comprehensive_slack_report(self, videos, ai_insights):
        """포괄적인 Slack 리포트 (일괄 전송용)"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # 언어별 통계
        language_stats = {}
        for video in top_videos:
            lang = video.get('language', 'Unknown')
            if lang not in language_stats:
                language_stats[lang] = 0
            language_stats[lang] += 1
        
        lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Optimized Poker Trend Analysis"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Videos: {len(videos)} | Views: {total_views:,}\n🌍 Languages: {lang_summary}\n📈 Enhanced Data: Language, Translation, Country"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 VIDEOS WITH KOREAN TRANSLATION*"
                }
            }
        ]
        
        # TOP 5 영상 (번역된 제목 포함)
        for i, video in enumerate(top_videos, 1):
            original_title = video.get('original_title', '')[:40] + "..."
            korean_title = video.get('korean_title', '')[:40] + "..."
            channel = video.get('channel_title', '')
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            language = video.get('language', '')
            country = video.get('country', '')
            url = video.get('url', '')
            
            engagement = round((likes / views * 100), 2) if views > 0 else 0
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. <{url}|{korean_title}>*\n📺 {channel} | 🌍 {language} ({country})\n📊 {views:,} views • 👍 {likes:,} • 📈 {engagement}%\n🔤 Original: {original_title}"
                }
            })
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 CONCISE AI INSIGHTS*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{ai_insights}```"
                }
            }
        ])
        
        return {"blocks": blocks}
    
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
    
    def run_optimized_analysis(self):
        """최적화된 분석 실행"""
        logger.info("=" * 70)
        logger.info("OPTIMIZED POKER TREND ANALYSIS")
        logger.info("=" * 70)
        
        # 1. 향상된 데이터 수집 (언어/국가 감지, 번역 포함)
        logger.info("Step 1: Enhanced data collection with translation...")
        videos = self.collect_enhanced_video_data()
        
        # 2. 간소화된 AI 인사이트 생성
        logger.info("Step 2: Generating concise AI insights...")
        ai_insights = self.generate_concise_insights(videos)
        
        # 3. TOP 5 추출
        logger.info("Step 3: Extracting TOP 5 with translations...")
        top_5 = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 완전한 리포트 생성
        logger.info("Step 4: Creating comprehensive report...")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "optimized_with_translation",
            "total_videos": len(videos),
            "data_fields": [
                "original_title", "korean_title", "language", "country", 
                "view_count", "like_count", "comment_count", "channel_title"
            ],
            "ai_insights": ai_insights,
            "top_5_videos": top_5,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / 'reports' / f'optimized_analysis_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # 6. AI 인사이트 별도 저장
        insights_path = Path(__file__).parent / 'reports' / f'concise_insights_{timestamp}.txt'
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("OPTIMIZED POKER TREND ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            f.write("TOP 5 VIDEOS (WITH TRANSLATION):\n")
            f.write("-" * 30 + "\n")
            for i, video in enumerate(top_5, 1):
                f.write(f"{i}. {video.get('korean_title', '')}\n")
                f.write(f"   Original: {video.get('original_title', '')}\n")
                f.write(f"   Language: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   Performance: {video.get('view_count', 0):,} views\n\n")
            
            f.write("\nCONCISE AI INSIGHTS:\n")
            f.write("=" * 30 + "\n")
            f.write(ai_insights)
        
        logger.info(f"Report saved: {report_path}")
        logger.info(f"Insights saved: {insights_path}")
        
        # 7. 모든 데이터 준비 완료 후 일괄 Slack 전송
        logger.info("Step 5: Sending comprehensive Slack report...")
        slack_message = self.create_comprehensive_slack_report(videos, ai_insights)
        slack_success = self.send_slack_notification(slack_message)
        
        # 8. 결과 요약
        logger.info("=" * 70)
        logger.info("OPTIMIZED ANALYSIS COMPLETED")
        logger.info("=" * 70)
        logger.info(f"✅ Videos analyzed: {len(videos)}")
        logger.info(f"✅ Languages detected: {len(set(v.get('language', '') for v in top_5))}")
        logger.info(f"✅ Translations completed: {len(top_5)}")
        logger.info(f"✅ Concise insights generated: {'Yes' if ai_insights else 'No'}")
        logger.info(f"✅ Slack report sent: {'Yes' if slack_success else 'No'}")
        
        return report_data

if __name__ == "__main__":
    analyzer = OptimizedTrendAnalyzer()
    analyzer.run_optimized_analysis()