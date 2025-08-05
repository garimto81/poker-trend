#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간소화된 포커 트렌드 분석기
- 언어/국가 감지 (번역 제외로 속도 향상)
- 간결한 쇼츠 아이디어 1개
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

class StreamlinedAnalyzer:
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
        """언어 및 국가 감지 (번역 없음)"""
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
        elif re.search(r'español|français|português', text_sample.lower()):
            return "Spanish/French/Portuguese", "Europe/Latin America"
        else:
            return "English", "Global"
    
    def collect_streamlined_data(self, max_results=5):
        """간소화된 데이터 수집"""
        logger.info("Starting streamlined video data collection...")
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
                    
                    # 언어 및 국가 감지 (번역 없음)
                    title = snippet.get('title', '')
                    description = snippet.get('description', '')
                    channel_title = snippet.get('channelTitle', '')
                    
                    detected_language, detected_country = self.detect_language_and_country(
                        title, description, channel_title
                    )
                    
                    # 기본 정보
                    video_data = {
                        'video_id': video_id,
                        'title': title,
                        'description': description[:200],  # 200자로 제한
                        'channel_title': channel_title,
                        'published_at': snippet.get('publishedAt', ''),
                        'upload_date': snippet.get('publishedAt', '')[:10],
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'language': detected_language,
                        'country': detected_country
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
                    
                    all_videos.append(video_data)
                
                logger.info(f"Collected {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        # 중복 제거
        unique_videos = []
        seen_ids = set()
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        logger.info(f"Total unique videos collected: {len(unique_videos)}")
        return unique_videos
    
    def create_focused_analysis_prompt(self, top_videos):
        """집중된 분석 프롬프트 생성"""
        
        video_summary = []
        for i, video in enumerate(top_videos[:5], 1):
            engagement_rate = round((video.get('like_count', 0) / max(video.get('view_count', 1), 1) * 100), 2)
            video_summary.append(f"""
{i}위: "{video.get('title', '')}" ({video.get('language', '')})
조회수: {video.get('view_count', 0):,} | 참여율: {engagement_rate}% | 국가: {video.get('country', '')}
채널: {video.get('channel_title', '')} | 키워드: {video.get('keyword', '')}
""")
        
        videos_text = "\n".join(video_summary)
        
        prompt = f"""
포커 트렌드 분석 전문가로서 다음 TOP 5 영상을 분석하여 핵심 인사이트와 최고의 쇼츠 아이디어 1개를 제안하세요.

=== TOP 5 영상 데이터 ===
{videos_text}

=== 간결한 분석 요청 ===

**1. 핵심 트렌드 (각 1줄)**
- 가장 주목할만한 패턴:
- 언어/지역별 특징:
- 고참여율 콘텐츠 특징:

**2. 포커 팬 관심사 TOP 3 (각 1줄)**
- 1위 관심사:
- 2위 관심사:
- 3위 관심사:

**3. 최고의 쇼츠 아이디어 1개**
제목: [매력적인 제목]
컨셉: [30초 스토리 - 2줄]
타겟: [대상 시청자]
예상 성과: [조회수 예측 + 근거 1줄]
해시태그: [5개]

모든 답변은 간결하고 구체적으로 작성하세요.
"""
        return prompt
    
    def generate_focused_insights(self, videos):
        """집중된 AI 인사이트 생성"""
        logger.info("Generating focused AI insights...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
            prompt = self.create_focused_analysis_prompt(top_videos)
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def create_final_slack_report(self, videos, ai_insights):
        """최종 Slack 리포트 (모든 데이터 완료 후 일괄 전송)"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # 언어별 통계
        language_stats = {}
        for video in top_videos:
            lang = video.get('language', 'Unknown')
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Streamlined Poker Trend Report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Total: {len(videos)} videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n⚡ Enhanced: Language detection, Country identification"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 VIDEOS WITH LANGUAGE ANALYSIS*"
                }
            }
        ]
        
        # TOP 5 영상 상세 정보
        for i, video in enumerate(top_videos, 1):
            title = video.get('title', '')[:50] + "..." if len(video.get('title', '')) > 50 else video.get('title', '')
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
                    "text": f"*{i}. <{url}|{title}>*\n📺 {channel} | 🎯 {keyword}\n🌍 {language} ({country})\n📊 {views:,} views • 👍 {likes:,} • 📈 {engagement}%"
                }
            })
        
        # AI 인사이트 미리보기 (400자 제한)
        insights_preview = ai_insights[:400] + "..." if len(ai_insights) > 400 else ai_insights
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 FOCUSED AI INSIGHTS & BEST SHORTS IDEA*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{insights_preview}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📋 Complete analysis with detailed insights saved to report files"
                    }
                ]
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
    
    def run_streamlined_analysis(self):
        """간소화된 분석 실행"""
        logger.info("=" * 60)
        logger.info("STREAMLINED POKER TREND ANALYSIS")
        logger.info("=" * 60)
        
        # 1. 데이터 수집 (언어/국가 감지)
        videos = self.collect_streamlined_data()
        
        # 2. AI 인사이트 생성
        ai_insights = self.generate_focused_insights(videos)
        
        # 3. TOP 5 추출
        top_5 = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "streamlined_with_language_detection",
            "total_videos": len(videos),
            "data_fields": [
                "title", "language", "country", "view_count", 
                "like_count", "comment_count", "channel_title", "keyword"
            ],
            "ai_insights": ai_insights,
            "top_5_videos": top_5,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / 'reports' / f'streamlined_analysis_{timestamp}.json'
        insights_path = Path(__file__).parent / 'reports' / f'focused_insights_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("STREAMLINED POKER TREND ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            f.write("TOP 5 VIDEOS WITH LANGUAGE ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            for i, video in enumerate(top_5, 1):
                f.write(f"{i}. {video.get('title', '')}\n")
                f.write(f"   Language: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   Views: {video.get('view_count', 0):,} | Keyword: {video.get('keyword', '')}\n\n")
            
            f.write("\nFOCUSED AI INSIGHTS:\n")
            f.write("=" * 30 + "\n")
            f.write(ai_insights)
        
        logger.info(f"Report saved: {report_path}")
        logger.info(f"Insights saved: {insights_path}")
        
        # 6. **모든 데이터 완료 후** 일괄 Slack 전송
        logger.info("Sending comprehensive Slack report (after all data processed)...")
        slack_message = self.create_final_slack_report(videos, ai_insights)
        slack_success = self.send_slack_notification(slack_message)
        
        # 7. 결과 요약
        logger.info("=" * 60)
        logger.info("STREAMLINED ANALYSIS COMPLETED")
        logger.info("=" * 60)
        logger.info(f"✅ Videos analyzed: {len(videos)}")
        logger.info(f"✅ Languages detected: {len(set(v.get('language', '') for v in top_5))}")
        logger.info(f"✅ Focused insights: {'Generated' if ai_insights else 'Failed'}")
        logger.info(f"✅ Slack report: {'Sent' if slack_success else 'Failed'}")
        
        # TOP 5 간단 요약
        logger.info("\n🏆 TOP 5 SUMMARY:")
        for i, video in enumerate(top_5, 1):
            logger.info(f"{i}. {video.get('view_count', 0):,} views - {video.get('language', '')} - {video.get('title', '')[:40]}...")
        
        return report_data

if __name__ == "__main__":
    analyzer = StreamlinedAnalyzer()
    analyzer.run_streamlined_analysis()