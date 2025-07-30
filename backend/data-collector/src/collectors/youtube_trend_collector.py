"""
YouTube 포커 트렌드 데이터 수집기
매일 포커 관련 YouTube 영상을 수집하고 분석합니다.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import logging
from dataclasses import dataclass
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoData:
    """YouTube 비디오 데이터 구조"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_name: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    thumbnail_url: str
    tags: List[str]
    

class YouTubeTrendCollector:
    """YouTube 포커 트렌드 수집기"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.search_terms = [
            'poker', '포커', 'holdem', '홀덤', 
            'WSOP', 'WPT', 'EPT', 'PokerStars', 'GGPoker',
            '포커 전략', '포커 토너먼트', '온라인 포커'
        ]
        
    def collect_trending_videos(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """지정된 시간 내의 포커 관련 트렌딩 비디오 수집"""
        all_videos = []
        published_after = (datetime.now() - timedelta(hours=hours_back)).isoformat() + 'Z'
        
        for term in self.search_terms:
            try:
                videos = self._search_videos(term, published_after)
                all_videos.extend(videos)
                logger.info(f"Collected {len(videos)} videos for term: {term}")
            except HttpError as e:
                logger.error(f"Error searching for {term}: {e}")
                continue
                
        # 중복 제거
        unique_videos = {v['id']['videoId']: v for v in all_videos}.values()
        
        # 상세 정보 추가
        enriched_videos = self._enrich_video_data(list(unique_videos))
        
        return enriched_videos
    
    def _search_videos(self, query: str, published_after: str) -> List[Dict]:
        """YouTube API를 사용하여 비디오 검색"""
        try:
            request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=50,
                order='viewCount',
                publishedAfter=published_after,
                relevanceLanguage='ko',
                regionCode='KR'
            )
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            logger.error(f"Search API error: {e}")
            return []
    
    def _enrich_video_data(self, videos: List[Dict]) -> List[Dict[str, Any]]:
        """비디오 상세 정보 (통계, 길이 등) 추가"""
        if not videos:
            return []
            
        video_ids = [v['id']['videoId'] for v in videos]
        enriched = []
        
        # API 호출 제한으로 인해 50개씩 배치 처리
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            
            try:
                stats_request = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                stats_response = stats_request.execute()
                
                # 데이터 병합
                stats_map = {item['id']: item for item in stats_response.get('items', [])}
                
                for video in videos[i:i + batch_size]:
                    video_id = video['id']['videoId']
                    if video_id in stats_map:
                        enriched_video = self._merge_video_data(video, stats_map[video_id])
                        enriched.append(enriched_video)
                        
            except Exception as e:
                logger.error(f"Error enriching video data: {e}")
                continue
                
        return enriched
    
    def _merge_video_data(self, search_data: Dict, stats_data: Dict) -> Dict[str, Any]:
        """검색 결과와 상세 정보를 병합"""
        snippet = search_data['snippet']
        statistics = stats_data.get('statistics', {})
        content_details = stats_data.get('contentDetails', {})
        
        return {
            'video_id': search_data['id']['videoId'],
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'channel_id': snippet['channelId'],
            'channel_name': snippet['channelTitle'],
            'published_at': snippet['publishedAt'],
            'thumbnail_url': snippet['thumbnails']['high']['url'],
            'tags': snippet.get('tags', []),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration': self._parse_duration(content_details.get('duration', 'PT0S')),
            'video_url': f"https://www.youtube.com/watch?v={search_data['id']['videoId']}"
        }
    
    def _parse_duration(self, duration: str) -> int:
        """ISO 8601 duration을 초 단위로 변환"""
        # PT15M33S -> 933 seconds
        import re
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
            
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_channel_info(self, channel_ids: List[str]) -> Dict[str, Dict]:
        """채널 정보 조회"""
        if not channel_ids:
            return {}
            
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=','.join(channel_ids[:50])  # 최대 50개
            )
            response = request.execute()
            
            return {
                item['id']: {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                    'video_count': int(item['statistics'].get('videoCount', 0))
                }
                for item in response.get('items', [])
            }
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return {}


if __name__ == "__main__":
    # 테스트 실행
    collector = YouTubeTrendCollector()
    videos = collector.collect_trending_videos(hours_back=24)
    
    print(f"Collected {len(videos)} videos")
    if videos:
        print(f"Top video: {videos[0]['title']} - {videos[0]['view_count']} views")