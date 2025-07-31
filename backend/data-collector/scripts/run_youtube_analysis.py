#!/usr/bin/env python3
"""
GitHub Actions에서 실행되는 YouTube 트렌드 분석 스크립트
매일 자동으로 포커 관련 YouTube 트렌드를 분석하고 Slack으로 리포트를 전송합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 로깅 디렉토리 생성
os.makedirs('scripts/logs', exist_ok=True)
os.makedirs('scripts/reports', exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if os.getenv('DEBUG_MODE') != 'true' else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/logs/youtube_analysis.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# 환경 변수 확인
REQUIRED_ENV_VARS = [
    'YOUTUBE_API_KEY',
    'SLACK_BOT_TOKEN',
    'SLACK_CHANNEL_ID'
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
        sys.exit(1)

# API 클라이언트 초기화
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))


class YouTubeTrendAnalyzer:
    """YouTube 포커 트렌드 분석기"""
    
    def __init__(self):
        self.search_terms = ['poker', '포커', 'holdem', '홀덤', 'WSOP', 'WPT', 'EPT']
        self.categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', '토너먼트', 'tournament'],
            'online': ['포커스타즈', 'PokerStars', 'GGPoker', '온라인'],
            'education': ['전략', 'strategy', '강의', 'tutorial', '팁'],
            'entertainment': ['하이라이트', 'highlights', '재미있는', 'funny', 'best']
        }
    
    def collect_videos(self) -> List[Dict]:
        """YouTube에서 포커 관련 영상 수집"""
        all_videos = []
        
        # 24시간 전 시간 계산
        published_after = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        
        for term in self.search_terms:
            try:
                request = youtube.search().list(
                    q=term,
                    part='snippet',
                    type='video',
                    maxResults=50,
                    order='viewCount',
                    publishedAfter=published_after,
                    relevanceLanguage='ko',
                    regionCode='KR'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    # 중복 제거
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
        
        # 상세 통계 정보 추가
        return self.enrich_video_data(all_videos)
    
    def enrich_video_data(self, videos: List[Dict]) -> List[Dict]:
        """비디오 상세 정보 추가"""
        if not videos:
            return []
        
        video_ids = [v['video_id'] for v in videos]
        
        # 50개씩 나누어 요청 (API 제한)
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                stats_request = youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                stats_response = stats_request.execute()
                
                # 통계 정보 매핑
                stats_map = {
                    item['id']: item 
                    for item in stats_response.get('items', [])
                }
                
                # 원본 데이터에 통계 추가
                for video in videos:
                    if video['video_id'] in stats_map:
                        stats = stats_map[video['video_id']]
                        video['view_count'] = int(stats['statistics'].get('viewCount', 0))
                        video['like_count'] = int(stats['statistics'].get('likeCount', 0))
                        video['comment_count'] = int(stats['statistics'].get('commentCount', 0))
                        video['duration'] = stats['contentDetails']['duration']
                        
            except HttpError as e:
                logger.error(f"Error fetching video statistics: {e}")
                continue
        
        return videos
    
    def analyze_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """트렌드 분석 및 인사이트 도출"""
        if not videos:
            return {
                'total_videos': 0,
                'trending_videos': [],
                'category_stats': {},
                'top_channels': []
            }
        
        # 트렌드 스코어 계산
        for video in videos:
            video['trend_score'] = self.calculate_trend_score(video)
            video['category'] = self.categorize_video(video)
        
        # 트렌드 스코어로 정렬
        videos.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        # 급상승 영상 (상위 10개)
        trending_videos = videos[:10]
        
        # 카테고리별 통계
        category_stats = self.calculate_category_stats(videos)
        
        # 인기 채널 TOP 5
        top_channels = self.get_top_channels(videos)
        
        return {
            'total_videos': len(videos),
            'avg_views': sum(v.get('view_count', 0) for v in videos) / len(videos) if videos else 0,
            'trending_videos': trending_videos,
            'category_stats': category_stats,
            'top_channels': top_channels
        }
    
    def calculate_trend_score(self, video: Dict) -> float:
        """트렌드 스코어 계산"""
        views = video.get('view_count', 0)
        likes = video.get('like_count', 0)
        comments = video.get('comment_count', 0)
        
        # 업로드 시간 계산
        published_at = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
        hours_since_upload = (datetime.utcnow().replace(tzinfo=published_at.tzinfo) - published_at).total_seconds() / 3600
        
        if hours_since_upload <= 0:
            hours_since_upload = 1
        
        # 시간당 조회수
        views_per_hour = views / hours_since_upload
        
        # 참여율
        engagement_rate = (likes + comments) / views if views > 0 else 0
        
        # 트렌드 스코어 계산
        score = (views_per_hour * 0.35 + 
                engagement_rate * 10000 * 0.25 + 
                views / 1000000 * 0.25 + 
                (24 - min(hours_since_upload, 24)) / 24 * 0.15)
        
        return score
    
    def categorize_video(self, video: Dict) -> str:
        """비디오 카테고리 분류"""
        title_lower = video['title'].lower()
        
        for category, keywords in self.categories.items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def calculate_category_stats(self, videos: List[Dict]) -> Dict[str, Dict]:
        """카테고리별 통계 계산"""
        stats = {}
        
        for video in videos:
            category = video.get('category', 'general')
            if category not in stats:
                stats[category] = {
                    'count': 0,
                    'total_views': 0,
                    'avg_views': 0,
                    'top_video': None
                }
            
            stats[category]['count'] += 1
            stats[category]['total_views'] += video.get('view_count', 0)
            
            if not stats[category]['top_video'] or video.get('view_count', 0) > stats[category]['top_video'].get('view_count', 0):
                stats[category]['top_video'] = video
        
        # 평균 조회수 계산
        for category in stats:
            if stats[category]['count'] > 0:
                stats[category]['avg_views'] = stats[category]['total_views'] / stats[category]['count']
        
        return stats
    
    def get_top_channels(self, videos: List[Dict]) -> List[Dict]:
        """인기 채널 TOP 5"""
        channel_stats = {}
        
        for video in videos:
            channel = video['channel_title']
            if channel not in channel_stats:
                channel_stats[channel] = {
                    'name': channel,
                    'video_count': 0,
                    'total_views': 0
                }
            
            channel_stats[channel]['video_count'] += 1
            channel_stats[channel]['total_views'] += video.get('view_count', 0)
        
        # 총 조회수 기준 정렬
        sorted_channels = sorted(channel_stats.values(), key=lambda x: x['total_views'], reverse=True)
        
        return sorted_channels[:5]


class SlackReporter:
    """Slack 리포트 전송"""
    
    def __init__(self, client: WebClient, channel_id: str):
        self.client = client
        self.channel_id = channel_id
    
    def send_daily_report(self, analysis_data: Dict[str, Any]):
        """일일 리포트 전송"""
        blocks = self.format_daily_report(analysis_data)
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text="🎰 오늘의 포커 YouTube 트렌드 리포트"
            )
            logger.info(f"Slack message sent successfully: {response['ts']}")
        except SlackApiError as e:
            logger.error(f"Error posting message: {e}")
            # Webhook 사용하여 재시도
            self.send_via_webhook(blocks)
    
    def send_via_webhook(self, blocks: List[Dict]):
        """Webhook을 통한 메시지 전송 (백업)"""
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if webhook_url:
            try:
                response = requests.post(
                    webhook_url,
                    json={'blocks': blocks},
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    logger.info("Message sent via webhook successfully")
                else:
                    logger.error(f"Webhook error: {response.status_code}")
            except Exception as e:
                logger.error(f"Webhook exception: {e}")
    
    def format_daily_report(self, data: Dict[str, Any]) -> List[Dict]:
        """일일 리포트 포맷팅"""
        blocks = []
        
        # 헤더
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎰 오늘의 포커 YouTube 트렌드 ({datetime.now().strftime('%Y.%m.%d')})"
            }
        })
        
        # 전체 요약
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 전체 요약*\n" +
                       f"• 총 분석 영상: {data['total_videos']}개\n" +
                       f"• 평균 조회수: {self.format_number(data['avg_views'])}회\n" +
                       f"• 급상승 영상: {len(data['trending_videos'])}개"
            }
        })
        
        blocks.append({"type": "divider"})
        
        # TOP 5 급상승 영상
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
                        "text": f"*{i}. {self.escape_markdown(video['title'][:80])}*\n" +
                               f"채널: {video['channel_title']}\n" +
                               f"조회수: {self.format_number(video.get('view_count', 0))}회\n" +
                               f"<https://youtube.com/watch?v={video['video_id']}|▶️ 바로가기>"
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": video['thumbnail_url'],
                        "alt_text": video['title']
                    }
                })
        
        # 카테고리별 트렌드
        if data['category_stats']:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 카테고리별 트렌드*"
                }
            })
            
            category_names = {
                'tournament': '🏆 토너먼트',
                'online': '💻 온라인 포커',
                'education': '📚 교육/전략',
                'entertainment': '🎬 엔터테인먼트',
                'general': '🎯 일반'
            }
            
            for category, stats in data['category_stats'].items():
                if stats['count'] > 0:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{category_names.get(category, category)}*\n" +
                                   f"영상 수: {stats['count']}개 | " +
                                   f"평균 조회수: {self.format_number(stats['avg_views'])}회"
                        }
                    })
        
        # 인기 채널
        if data['top_channels']:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🌟 인기 채널 TOP 3*\n" + 
                           "\n".join([
                               f"{i}. {channel['name']} ({channel['video_count']}개 영상, 총 {self.format_number(channel['total_views'])}회)"
                               for i, channel in enumerate(data['top_channels'][:3], 1)
                           ])
                }
            })
        
        return blocks
    
    def format_number(self, num: float) -> str:
        """숫자 포맷팅"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(int(num))
    
    def escape_markdown(self, text: str) -> str:
        """Markdown 특수문자 이스케이프"""
        chars_to_escape = ['*', '_', '~', '`', '>']
        for char in chars_to_escape:
            text = text.replace(char, f'\\{char}')
        return text


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
        
        # 결과 저장
        report_file = f"scripts/reports/trend_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        logger.info(f"Report saved to {report_file}")
        
        # Slack 리포트 전송
        reporter = SlackReporter(slack_client, os.getenv('SLACK_CHANNEL_ID'))
        logger.info("Sending Slack report...")
        reporter.send_daily_report(analysis_result)
        
        logger.info("YouTube trend analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()