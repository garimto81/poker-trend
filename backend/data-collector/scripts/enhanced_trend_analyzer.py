#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 포커 트렌드 분석기 - 쇼츠 제작용 AI 인사이트 포함
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

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedTrendAnalyzer:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def collect_video_data(self, max_results=5):
        """YouTube 영상 데이터 수집"""
        logger.info("Starting video data collection...")
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
                    video_data = {
                        'video_id': video['id']['videoId'],
                        'title': video['snippet']['title'],
                        'channel_title': video['snippet']['channelTitle'],
                        'published_at': video['snippet']['publishedAt'],
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video['id']['videoId']}"
                    }
                    
                    # 상세 정보 가져오기
                    details = self.youtube.videos().list(
                        part='statistics,contentDetails',
                        id=video['id']['videoId']
                    ).execute()
                    
                    if details['items']:
                        stats = details['items'][0]['statistics']
                        content = details['items'][0]['contentDetails']
                        
                        video_data.update({
                            'view_count': int(stats.get('viewCount', 0)),
                            'like_count': int(stats.get('likeCount', 0)),
                            'comment_count': int(stats.get('commentCount', 0)),
                            'duration': content.get('duration', '')
                        })
                    
                    all_videos.append(video_data)
                
                logger.info(f"Collected {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        logger.info(f"Total videos collected: {len(all_videos)}")
        return all_videos
    
    def create_enhanced_ai_prompt(self, top_videos):
        """쇼츠 제작용 개선된 AI 프롬프트 생성"""
        
        titles_summary = "\n".join([
            f"{i+1}. {video.get('title', '')} - {video.get('view_count', 0):,} views"
            for i, video in enumerate(top_videos[:5])
        ])
        
        prompt = f"""
You are a YouTube Shorts strategy expert specializing in poker content. Analyze these TOP performing videos and provide actionable insights for viral shorts creation.

TOP 5 PERFORMING VIDEOS:
{titles_summary}

PROVIDE DETAILED ANALYSIS:

1. VIRAL SUCCESS PATTERNS
- What specific elements make these titles click-worthy?
- Identify the psychological triggers being used
- Essential keywords that drive discoverability

2. OPTIMAL CONTENT STRATEGY
- Recommended video length for maximum engagement
- Best practices for hook creation (first 3 seconds)
- Pacing and editing recommendations

3. IMMEDIATE ACTION ITEMS (3 Specific Shorts Ideas)
Format each as:
TITLE: [Compelling title with emojis]
CONCEPT: [15-second storyline breakdown]
HOOK: [First 3 seconds strategy]
VISUAL ELEMENTS: [Camera angles, editing style]
HASHTAGS: [5 optimized tags]
SUCCESS PROBABILITY: [High/Medium/Low with reasoning]

4. THUMBNAIL OPTIMIZATION
- Most effective facial expressions and poses
- Color psychology for poker content
- Text overlay best practices

5. MARKET OPPORTUNITIES
- Underserved niches in current poker content
- Trending topics to capitalize on
- Differentiation strategies from competitors

6. CONTENT CALENDAR SUGGESTIONS
- Best posting times based on current trends
- Weekly content themes
- Seasonal opportunities

Make all recommendations immediately actionable. Focus on strategies a creator can implement TODAY to increase their viral potential.
"""
        return prompt
    
    def generate_enhanced_insights(self, videos):
        """개선된 AI 인사이트 생성"""
        logger.info("Generating enhanced AI insights...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
            prompt = self.create_enhanced_ai_prompt(top_videos)
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def create_slack_report(self, videos, ai_insights):
        """Slack 리포트 생성"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Enhanced Poker Trend Analysis"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d')}\n📊 Videos: {len(videos)}\n👀 Total Views: {total_views:,}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 VIDEOS*"
                }
            }
        ]
        
        for i, video in enumerate(top_videos, 1):
            title = video.get('title', '')[:60]
            views = video.get('view_count', 0)
            channel = video.get('channel_title', '')
            url = video.get('url', '')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{i}. <{url}|{title}>\n   {views:,} views • {channel}"
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
                    "text": "*🤖 AI INSIGHTS FOR SHORTS CREATION*\n_See detailed analysis in report file_"
                }
            }
        ])
        
        return {"blocks": blocks}
    
    def send_slack_notification(self, message):
        """Slack 알림 전송"""
        try:
            response = requests.post(self.slack_webhook, json=message)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    def run_analysis(self):
        """전체 분석 실행"""
        logger.info("=" * 60)
        logger.info("ENHANCED POKER TREND ANALYSIS STARTED")
        logger.info("=" * 60)
        
        # 1. 데이터 수집
        videos = self.collect_video_data()
        
        # 2. AI 인사이트 생성
        ai_insights = self.generate_enhanced_insights(videos)
        
        # 3. 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_videos": len(videos),
            "enhanced_ai_insights": ai_insights,
            "top_videos": sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:10],
            "all_videos": videos
        }
        
        # 4. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / 'reports' / f'enhanced_analysis_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report saved: {report_path}")
        
        # 5. Slack 알림
        slack_message = self.create_slack_report(videos, ai_insights)
        if self.send_slack_notification(slack_message):
            logger.info("Slack notification sent successfully")
        else:
            logger.error("Failed to send Slack notification")
        
        # 6. 결과 요약
        logger.info("=" * 60)
        logger.info("ANALYSIS COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Videos analyzed: {len(videos)}")
        logger.info(f"AI insights generated: {'✓' if ai_insights else '✗'}")
        logger.info(f"Report saved: ✓")
        logger.info(f"Slack sent: {'✓' if self.send_slack_notification else '✗'}")
        
        return report_data

if __name__ == "__main__":
    analyzer = EnhancedTrendAnalyzer()
    analyzer.run_analysis()