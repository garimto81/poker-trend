#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전한 포커 트렌드 분석기 - 설명 데이터 포함 및 Slack 문제 해결
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

class CompleteTrendAnalyzer:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def collect_complete_video_data(self, max_results=5):
        """완전한 YouTube 영상 데이터 수집 (설명 포함)"""
        logger.info("Starting complete video data collection...")
        all_videos = []
        
        for keyword in self.keywords:
            try:
                # 1단계: 검색
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
                    
                    # 기본 정보
                    video_data = {
                        'video_id': video_id,
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'channel_title': snippet.get('channelTitle', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'upload_date': snippet.get('publishedAt', '')[:10],  # YYYY-MM-DD 형식
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
                    }
                    
                    # 2단계: 상세 정보 가져오기 (조회수, 좋아요, 댓글 등)
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
                            'category_id': snippet.get('categoryId', '')
                        })
                    
                    all_videos.append(video_data)
                
                logger.info(f"Collected {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        logger.info(f"Total videos collected: {len(all_videos)}")
        return all_videos
    
    def create_poker_trend_analysis_prompt(self, top_videos):
        """포커 팬 관심사 분석 및 쇼츠 아이디어 생성 프롬프트"""
        
        # TOP 5 영상의 상세 정보 정리
        video_analysis = []
        for i, video in enumerate(top_videos[:5], 1):
            title = video.get('title', '')
            description = video.get('description', '')[:200] + "..." if len(video.get('description', '')) > 200 else video.get('description', '')
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            channel = video.get('channel_title', '')
            upload_date = video.get('upload_date', '')
            
            video_analysis.append(f"""
VIDEO {i}:
Title: {title}
Description: {description}
Channel: {channel}
Upload Date: {upload_date}
Performance: {views:,} views, {likes:,} likes, {comments:,} comments
URL: {video.get('url', '')}
""")
        
        videos_text = "\n".join(video_analysis)
        
        prompt = f"""
당신은 포커 트렌드 분석 전문가입니다. 다음 TOP 5 포커 관련 YouTube 영상을 종합 분석하여 현재 포커 팬들의 관심사를 파악하고, 실제 제작 가능한 쇼츠 아이디어를 제안해주세요.

=== TOP 5 포커 영상 분석 데이터 ===
{videos_text}

=== 분석 요청 사항 ===

1. **포커 팬들의 현재 관심사 분석**
   - 제목과 설명에서 발견되는 공통 패턴
   - 높은 조회수를 기록한 콘텐츠의 특징
   - 좋아요/댓글 비율이 높은 영상의 요소
   - 업로드 시기와 성과의 상관관계

2. **트렌드 키워드 및 주제 추출**
   - 자주 등장하는 포커 용어 및 상황
   - 감정적 반응을 이끄는 요소들
   - 시청자들이 선호하는 콘텐츠 스타일

3. **구체적인 쇼츠 제작 아이디어 5개**
   각 아이디어마다 다음 형식으로 제시:
   
   **아이디어 {번호}: [제목]**
   - 컨셉: [30초 이내 스토리라인]
   - 타겟 관심사: [분석된 팬들의 관심사 연결]
   - 핵심 요소: [시각적/감정적 포인트]
   - 예상 성과: [조회수 예측 및 근거]
   - 촬영 팁: [구체적 제작 가이드]
   - 해시태그: [최적화된 태그 5개]

4. **콘텐츠 전략 제안**
   - 최적 업로드 시간
   - 썸네일 전략
   - 제목 작성 가이드
   - 시리즈화 가능한 주제

5. **차별화 포인트**
   - 현재 시장에서 부족한 콘텐츠
   - 새로운 접근 방식 제안
   - 독특한 관점이나 각도

분석은 실제 데이터에 기반하여 구체적이고 실행 가능한 내용으로 작성해주세요. 특히 현재 포커 팬들이 가장 관심 있어하는 요소를 정확히 파악하여 쇼츠 아이디어에 반영해주세요.
"""
        return prompt
    
    def generate_complete_insights(self, videos):
        """완전한 AI 인사이트 생성"""
        logger.info("Generating complete poker trend insights...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
            prompt = self.create_poker_trend_analysis_prompt(top_videos)
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def create_detailed_slack_report(self, videos, ai_insights):
        """상세한 Slack 리포트 생성 (AI 인사이트 포함)"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # AI 인사이트를 짧게 요약
        insights_preview = ai_insights[:300] + "..." if len(ai_insights) > 300 else ai_insights
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Complete Poker Trend Analysis"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Total Videos: {len(videos)}\n👀 Total Views: {total_views:,}\n📈 Data: Title, Description, Views, Likes, Comments, Upload Date, Channel"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 VIDEOS ANALYSIS*"
                }
            }
        ]
        
        # TOP 5 영상 상세 정보
        for i, video in enumerate(top_videos, 1):
            title = video.get('title', '')[:50] + "..." if len(video.get('title', '')) > 50 else video.get('title', '')
            channel = video.get('channel_title', '')
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            upload_date = video.get('upload_date', '')
            url = video.get('url', '')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. <{url}|{title}>*\n📺 {channel}\n📊 {views:,} views • 👍 {likes:,} • 💬 {comments:,}\n📅 {upload_date}"
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
                    "text": "*🤖 AI INSIGHTS PREVIEW*"
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
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📋 *Complete analysis with shorts ideas saved to report file*"
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
                logger.error(f"Slack notification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
            return False
    
    def run_complete_analysis(self):
        """완전한 분석 실행"""
        logger.info("=" * 70)
        logger.info("COMPLETE POKER TREND ANALYSIS WITH DESCRIPTIONS")
        logger.info("=" * 70)
        
        # 1. 완전한 데이터 수집
        videos = self.collect_complete_video_data()
        
        # 2. AI 인사이트 생성
        ai_insights = self.generate_complete_insights(videos)
        
        # 3. TOP 5 데이터 추출
        top_5 = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 완전한 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "complete_with_descriptions",
            "total_videos": len(videos),
            "data_fields": [
                "title", "description", "view_count", "upload_date", 
                "like_count", "comment_count", "channel_title"
            ],
            "ai_insights": ai_insights,
            "top_5_videos": top_5,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / 'reports' / f'complete_analysis_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Complete report saved: {report_path}")
        
        # 6. AI 인사이트 별도 저장 (텍스트 파일)
        insights_path = Path(__file__).parent / 'reports' / f'ai_insights_{timestamp}.txt'
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("COMPLETE POKER TREND ANALYSIS & SHORTS IDEAS\n")
            f.write("=" * 60 + "\n\n")
            f.write(ai_insights)
        
        logger.info(f"AI insights saved: {insights_path}")
        
        # 7. Slack 알림 (수정된 버전)
        slack_message = self.create_detailed_slack_report(videos, ai_insights)
        slack_success = self.send_slack_notification(slack_message)
        
        # 8. 결과 요약
        logger.info("=" * 70)
        logger.info("COMPLETE ANALYSIS RESULTS")
        logger.info("=" * 70)
        logger.info(f"✅ Videos analyzed: {len(videos)}")
        logger.info(f"✅ TOP 5 extracted with full data")
        logger.info(f"✅ AI insights generated: {'Success' if ai_insights else 'Failed'}")
        logger.info(f"✅ Report saved: {report_path}")
        logger.info(f"✅ Insights saved: {insights_path}")
        logger.info(f"✅ Slack notification: {'Success' if slack_success else 'Failed'}")
        
        # TOP 5 요약 출력
        logger.info("\n📊 TOP 5 VIDEOS SUMMARY:")
        for i, video in enumerate(top_5, 1):
            logger.info(f"{i}. {video.get('title', '')[:60]}...")
            logger.info(f"   👀 {video.get('view_count', 0):,} views | 👍 {video.get('like_count', 0):,} | 💬 {video.get('comment_count', 0):,}")
            logger.info(f"   📺 {video.get('channel_title', '')} | 📅 {video.get('upload_date', '')}")
        
        return report_data

if __name__ == "__main__":
    analyzer = CompleteTrendAnalyzer()
    analyzer.run_complete_analysis()