#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 포커 트렌드 분석 - Webhook 버전
GEMINI_API_KEY, YOUTUBE_API_KEY, SLACK_WEBHOOK_URL만 사용
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 확인
REQUIRED_ENV_VARS = [
    'YOUTUBE_API_KEY',
    'SLACK_WEBHOOK_URL'
]

missing_vars = []
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        missing_vars.append(var)
        logger.error(f"Missing required environment variable: {var}")

if missing_vars:
    logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# YouTube API 클라이언트 초기화
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')


class YouTubeTrendAnalyzer:
    """YouTube 포커 트렌드 분석기"""
    
    def __init__(self):
        self.search_terms = ['poker', '포커', 'holdem', '홀덤', 'WSOP', 'WPT']
        self.categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', '토너먼트'],
            'online': ['포커스타즈', 'PokerStars', 'GGPoker'],
            'education': ['전략', 'strategy', '강의', 'tutorial'],
            'entertainment': ['하이라이트', 'highlights', '재미있는']
        }
    
    def collect_videos(self) -> List[Dict]:
        """YouTube에서 포커 관련 영상 수집"""
        all_videos = []
        published_after = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        
        for term in self.search_terms:
            try:
                request = youtube.search().list(
                    q=term,
                    part='snippet',
                    type='video',
                    maxResults=20,  # API 할당량 절약
                    order='viewCount',
                    publishedAfter=published_after
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    if not any(v.get('video_id') == video_id for v in all_videos):
                        all_videos.append({
                            'video_id': video_id,
                            'title': item['snippet']['title'],
                            'channel_title': item['snippet']['channelTitle'],
                            'published_at': item['snippet']['publishedAt'],
                            'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                        })
                        
            except HttpError as e:
                logger.error(f"YouTube API error for term '{term}': {e}")
                continue
        
        return self.enrich_video_data(all_videos[:50])  # 상위 50개만
    
    def enrich_video_data(self, videos: List[Dict]) -> List[Dict]:
        """비디오 상세 정보 추가"""
        if not videos:
            return []
        
        video_ids = [v['video_id'] for v in videos]
        
        try:
            stats_request = youtube.videos().list(
                part='statistics',
                id=','.join(video_ids)
            )
            stats_response = stats_request.execute()
            
            stats_map = {
                item['id']: item['statistics']
                for item in stats_response.get('items', [])
            }
            
            for video in videos:
                if video['video_id'] in stats_map:
                    stats = stats_map[video['video_id']]
                    video['view_count'] = int(stats.get('viewCount', 0))
                    video['like_count'] = int(stats.get('likeCount', 0))
                    video['comment_count'] = int(stats.get('commentCount', 0))
                    
        except HttpError as e:
            logger.error(f"Error fetching video statistics: {e}")
        
        return videos
    
    def analyze_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """트렌드 분석"""
        if not videos:
            return {'total_videos': 0, 'trending_videos': []}
        
        # 트렌드 스코어 계산
        for video in videos:
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            comments = video.get('comment_count', 0)
            
            # 간단한 트렌드 스코어
            engagement_rate = (likes + comments) / views if views > 0 else 0
            video['trend_score'] = views * engagement_rate
            video['category'] = self.categorize_video(video)
        
        # 트렌드 스코어로 정렬
        videos.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        return {
            'total_videos': len(videos),
            'trending_videos': videos[:10],  # TOP 10
            'avg_views': sum(v.get('view_count', 0) for v in videos) / len(videos) if videos else 0
        }
    
    def categorize_video(self, video: Dict) -> str:
        """비디오 카테고리 분류"""
        title_lower = video['title'].lower()
        
        for category, keywords in self.categories.items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return category
        
        return 'general'


def send_slack_webhook(data: Dict[str, Any]):
    """Slack Webhook으로 메시지 전송"""
    
    # 메시지 포맷팅
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎰 오늘의 포커 YouTube 트렌드 ({datetime.now().strftime('%Y.%m.%d')})"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 전체 요약*\n" +
                       f"• 총 분석 영상: {data['total_videos']}개\n" +
                       f"• 평균 조회수: {format_number(data['avg_views'])}회"
            }
        },
        {"type": "divider"}
    ]
    
    # TOP 5 트렌딩 영상
    if data['trending_videos']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔥 TOP 5 급상승 영상*"
            }
        })
        
        for i, video in enumerate(data['trending_videos'][:5], 1):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {video['title'][:80]}*\n" +
                           f"채널: {video['channel_title']}\n" +
                           f"조회수: {format_number(video.get('view_count', 0))}회\n" +
                           f"<https://youtube.com/watch?v={video['video_id']}|▶️ 바로가기>"
                }
            })
    
    # Webhook 전송
    payload = {
        "blocks": blocks,
        "text": "🎰 오늘의 포커 YouTube 트렌드"  # 알림용 텍스트
    }
    
    try:
        response = requests.post(
            slack_webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Slack webhook sent successfully")
        else:
            logger.error(f"Slack webhook error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Slack webhook: {e}")


def format_number(num: float) -> str:
    """숫자 포맷팅"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))


def main():
    """메인 실행 함수"""
    logger.info("Starting YouTube poker trend analysis...")
    
    try:
        # YouTube 트렌드 분석
        analyzer = YouTubeTrendAnalyzer()
        logger.info("Collecting YouTube videos...")
        videos = analyzer.collect_videos()
        
        logger.info(f"Collected {len(videos)} videos")
        
        # 트렌드 분석
        logger.info("Analyzing trends...")
        analysis_result = analyzer.analyze_trends(videos)
        
        # Slack Webhook 전송
        logger.info("Sending Slack webhook...")
        send_slack_webhook(analysis_result)
        
        logger.info("YouTube trend analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        
        # 에러 알림 전송
        error_payload = {
            "text": f"⚠️ YouTube 트렌드 분석 오류: {str(e)}"
        }
        requests.post(slack_webhook_url, json=error_payload)
        
        sys.exit(1)


if __name__ == "__main__":
    main()