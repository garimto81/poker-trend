#!/usr/bin/env python3
"""
Enhanced YouTube 포커 트렌드 분석 - 정밀 분석 버전
GEMINI_API_KEY, YOUTUBE_API_KEY, SLACK_WEBHOOK_URL 사용
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import requests
from collections import Counter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 확인
REQUIRED_ENV_VARS = [
    'YOUTUBE_API_KEY',
    'SLACK_WEBHOOK_URL',
    'GEMINI_API_KEY'
]

missing_vars = []
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        missing_vars.append(var)
        logger.error(f"Missing required environment variable: {var}")

if missing_vars:
    logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# API 클라이언트 초기화
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-pro')


class EnhancedYouTubeTrendAnalyzer:
    """향상된 YouTube 포커 트렌드 분석기"""
    
    def __init__(self):
        # 고정된 검색 키워드 (직접 설정)
        self.search_terms = [
            'poker', '포커', 'holdem', '홀덤', 
            'WSOP', 'WPT', 'EPT', 
            'PokerStars', 'GGPoker', 
            'tournament', '토너먼트',
            'cash game', '캐시게임',
            'poker strategy', '포커 전략'
        ]
        self.categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', '토너먼트', 'tournament', 'final table'],
            'online': ['포커스타즈', 'PokerStars', 'GGPoker', '온라인 포커', 'online poker'],
            'education': ['전략', 'strategy', '강의', 'tutorial', 'how to', 'tips'],
            'entertainment': ['하이라이트', 'highlights', '재미있는', 'funny', 'best', 'epic'],
            'pro_player': ['Phil Ivey', 'Daniel Negreanu', 'Phil Hellmuth', 'Doyle Brunson'],
            'cash_game': ['cash game', '캐시게임', 'high stakes', '하이스테이크스']
        }
        self.trend_keywords = []
    
    def collect_videos(self, lookback_hours: int = 48) -> List[Dict]:
        """YouTube에서 포커 관련 영상 수집 (더 많은 데이터)"""
        all_videos = []
        published_after = (datetime.utcnow() - timedelta(hours=lookback_hours)).isoformat() + 'Z'
        
        for term in self.search_terms:
            try:
                # 여러 정렬 기준으로 검색
                for order in ['viewCount', 'relevance', 'date']:
                    request = youtube.search().list(
                        q=term,
                        part='snippet',
                        type='video',
                        maxResults=25,
                        order=order,
                        publishedAfter=published_after,
                        videoDuration='short'  # 쇼츠에 적합한 짧은 영상
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
                                'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                                'description': item['snippet']['description'][:200]
                            })
                        
            except HttpError as e:
                logger.error(f"YouTube API error for term '{term}': {e}")
                continue
        
        # 중복 제거 후 상위 100개만
        unique_videos = list({v['video_id']: v for v in all_videos}.values())
        return self.enrich_video_data(unique_videos[:100])
    
    def enrich_video_data(self, videos: List[Dict]) -> List[Dict]:
        """비디오 상세 정보 추가 (더 많은 메트릭스)"""
        if not videos:
            return []
        
        video_ids = [v['video_id'] for v in videos]
        
        # 통계 정보 가져오기 (배치 처리)
        enriched_videos = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                stats_request = youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                stats_response = stats_request.execute()
                
                stats_map = {
                    item['id']: {
                        'statistics': item['statistics'],
                        'duration': item['contentDetails']['duration']
                    }
                    for item in stats_response.get('items', [])
                }
                
                for video in videos[i:i+50]:
                    if video['video_id'] in stats_map:
                        stats = stats_map[video['video_id']]['statistics']
                        video['view_count'] = int(stats.get('viewCount', 0))
                        video['like_count'] = int(stats.get('likeCount', 0))
                        video['comment_count'] = int(stats.get('commentCount', 0))
                        video['duration'] = stats_map[video['video_id']]['duration']
                        
                        # 추가 메트릭스 계산
                        views = video['view_count']
                        if views > 0:
                            video['engagement_rate'] = ((video['like_count'] + video['comment_count']) / views) * 100
                            video['like_ratio'] = (video['like_count'] / views) * 100
                        else:
                            video['engagement_rate'] = 0
                            video['like_ratio'] = 0
                        
                        # 시간당 조회수 계산
                        published_time = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                        hours_since_publish = (datetime.now(published_time.tzinfo) - published_time).total_seconds() / 3600
                        video['views_per_hour'] = views / hours_since_publish if hours_since_publish > 0 else 0
                        
                        enriched_videos.append(video)
                        
            except HttpError as e:
                logger.error(f"Error fetching video statistics: {e}")
        
        return enriched_videos
    
    def analyze_trends(self, videos: List[Dict]) -> Dict[str, Any]:
        """고급 트렌드 분석"""
        if not videos:
            return {'total_videos': 0, 'trending_videos': [], 'categories': {}}
        
        # 키워드 추출
        all_titles = ' '.join([v['title'] for v in videos])
        words = all_titles.lower().split()
        
        # 불용어 제외하고 빈도 계산
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were'}
        word_freq = Counter([word for word in words if word not in stopwords and len(word) > 3])
        self.trend_keywords = word_freq.most_common(15)
        
        # 동적 키워드 업데이트 트리거 (새로운 트렌드 발견시)
        trending_words = [kw[0] for kw in self.trend_keywords[:10]]
        logger.info(f"Current trending keywords: {trending_words}")
        
        # 채널별 통계
        channel_counts = Counter([v['channel_title'] for v in videos])
        top_channels = channel_counts.most_common(5)
        
        # 카테고리별 분류
        category_stats = {cat: [] for cat in self.categories}
        
        for video in videos:
            # 트렌드 스코어 계산 (개선된 알고리즘)
            views = video.get('view_count', 0)
            engagement = video.get('engagement_rate', 0)
            views_per_hour = video.get('views_per_hour', 0)
            
            # 복합 트렌드 스코어
            video['trend_score'] = (
                (views * 0.3) +  # 총 조회수
                (views_per_hour * 100 * 0.4) +  # 시간당 조회수 (가중치 높음)
                (engagement * 1000 * 0.3)  # 참여율
            )
            
            # 카테고리 분류
            video['category'] = self.categorize_video(video)
            category_stats[video['category']].append(video)
        
        # 트렌드 스코어로 정렬
        videos.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        # 카테고리별 통계
        category_summary = {}
        for cat, vids in category_stats.items():
            if vids:
                category_summary[cat] = {
                    'count': len(vids),
                    'avg_views': sum(v.get('view_count', 0) for v in vids) / len(vids),
                    'avg_engagement': sum(v.get('engagement_rate', 0) for v in vids) / len(vids)
                }
        
        return {
            'total_videos': len(videos),
            'trending_videos': videos[:10],  # TOP 10
            'avg_views': sum(v.get('view_count', 0) for v in videos) / len(videos),
            'avg_engagement': sum(v.get('engagement_rate', 0) for v in videos) / len(videos),
            'trending_keywords': self.trend_keywords,
            'category_breakdown': category_summary,
            'hourly_avg_views': sum(v.get('views_per_hour', 0) for v in videos) / len(videos),
            'search_keywords': self.search_terms,  # 검색에 사용된 키워드
            'top_channels': top_channels  # 가장 많은 영상을 생성한 채널
        }
    
    def categorize_video(self, video: Dict) -> str:
        """비디오 카테고리 분류 (개선된 버전)"""
        title_lower = video['title'].lower()
        desc_lower = video.get('description', '').lower()
        
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(
                2 if keyword.lower() in title_lower else 1 if keyword.lower() in desc_lower else 0
                for keyword in keywords
            )
            category_scores[category] = score
        
        # 가장 높은 점수의 카테고리 반환
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0] if best_category[1] > 0 else 'general'
    
    def generate_ai_suggestions(self, analysis_data: Dict) -> str:
        """Gemini AI를 사용한 쇼츠 제작 제안"""
        try:
            # 트렌드 데이터 요약
            trend_summary = f"""
            현재 포커 YouTube 트렌드 분석 결과:
            - 총 분석 영상: {analysis_data['total_videos']}개
            - 평균 조회수: {format_number(analysis_data['avg_views'])}
            - 평균 참여율: {analysis_data['avg_engagement']:.2f}%
            - 시간당 평균 조회수: {format_number(analysis_data['hourly_avg_views'])}
            
            인기 키워드: {', '.join([kw[0] for kw in analysis_data['trending_keywords'][:10]])}
            
            카테고리별 분포:
            {self._format_category_stats(analysis_data['category_breakdown'])}
            
            TOP 5 트렌딩 영상:
            {self._format_top_videos(analysis_data['trending_videos'][:5])}
            """
            
            prompt = f"""
            당신은 포커 콘텐츠 전문가입니다. 다음 YouTube 트렌드 분석을 바탕으로 
            바이럴 가능성이 높은 포커 쇼츠 아이디어를 5개 제안해주세요.
            
            {trend_summary}
            
            각 아이디어는 다음 형식으로 작성해주세요:
            1. 제목 (흥미로운 후킹 포함)
            2. 핵심 콘텐츠 (30초 분량)
            3. 예상 타겟층
            4. 차별화 포인트
            
            트렌드를 반영하되 독창적이고 시청자의 호기심을 자극하는 콘텐츠를 제안해주세요.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini AI error: {e}")
            return "AI 제안 생성 중 오류가 발생했습니다."
    
    def generate_trend_analysis(self, analysis_data: Dict) -> str:
        """Gemini AI를 사용한 트렌드 분석 한줄 요약"""
        try:
            trend_summary = f"""
            포커 YouTube 트렌드 데이터:
            - 총 영상: {analysis_data['total_videos']}개
            - 평균 조회수: {format_number(analysis_data['avg_views'])}
            - 시간당 조회수: {format_number(analysis_data['hourly_avg_views'])}
            - TOP 키워드: {', '.join([kw[0] for kw in analysis_data['trending_keywords'][:5]])}
            - 주요 카테고리: {max(analysis_data['category_breakdown'].items(), key=lambda x: x[1]['count'])[0] if analysis_data['category_breakdown'] else 'N/A'}
            """
            
            prompt = f"""
            다음 포커 트렌드 데이터를 분석하여 현재 트렌드를 한 문장으로 요약해주세요.
            
            {trend_summary}
            
            요약은 다음 요소를 포함해야 합니다:
            - 가장 주목할 만한 트렌드
            - 시청자들의 관심사
            - 향후 전망
            
            50자 이내로 간결하고 통찰력 있게 작성해주세요.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return "현재 포커 콘텐츠는 토너먼트와 전략 콘텐츠가 주도하고 있습니다."
    
    def _format_category_stats(self, category_stats: Dict) -> str:
        """카테고리 통계 포맷팅"""
        lines = []
        for cat, stats in category_stats.items():
            lines.append(f"- {cat}: {stats['count']}개 (평균 조회수: {format_number(stats['avg_views'])}, 참여율: {stats['avg_engagement']:.2f}%)")
        return '\n'.join(lines)
    
    def _format_top_videos(self, videos: List[Dict]) -> str:
        """TOP 영상 정보 포맷팅"""
        lines = []
        for i, video in enumerate(videos, 1):
            lines.append(f"{i}. {video['title'][:50]}... - 조회수: {format_number(video['view_count'])}, 참여율: {video['engagement_rate']:.2f}%")
        return '\n'.join(lines)


def send_enhanced_slack_webhook(data: Dict[str, Any], ai_suggestions: str, trend_analysis: str):
    """향상된 Slack Webhook 메시지 전송"""
    
    # 현재 시간 (한국 시간)
    kst_time = datetime.now() + timedelta(hours=9)
    
    # 메시지 블록 구성
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎰 포커 YouTube 트렌드 정밀 분석 ({kst_time.strftime('%Y.%m.%d %H:%M')} KST)"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📊 전체 트렌드 요약*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*총 분석 영상:*\n{data['total_videos']}개"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*평균 조회수:*\n{format_number(data['avg_views'])}회"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*평균 참여율:*\n{data['avg_engagement']:.2f}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*시간당 조회수:*\n{format_number(data['hourly_avg_views'])}회/h"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔍 검색 키워드:* {', '.join([f'`{kw}`' for kw in data.get('search_keywords', [])[:10]])}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🎬 TOP 채널:* {', '.join([f'{ch[0]} ({ch[1]}개)' for ch in data.get('top_channels', [])[:3]])}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📈 트렌드 분석:* {trend_analysis}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔥 핫 키워드:* {', '.join([f'`{kw[0]}`' for kw in data['trending_keywords'][:8]])}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📈 카테고리별 분석*"
            }
        }
    ]
    
    # 카테고리 통계 추가
    category_text = []
    for cat, stats in data['category_breakdown'].items():
        emoji = {
            'tournament': '🏆',
            'online': '💻',
            'education': '📚',
            'entertainment': '🎭',
            'pro_player': '👤',
            'cash_game': '💰'
        }.get(cat, '📌')
        category_text.append(f"{emoji} *{cat}*: {stats['count']}개 (평균 {format_number(stats['avg_views'])}회)")
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '\n'.join(category_text)
        }
    })
    
    blocks.append({"type": "divider"})
    
    # TOP 5 트렌딩 영상
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🚀 TOP 5 급상승 영상*"
        }
    })
    
    for i, video in enumerate(data['trending_videos'][:5], 1):
        # 제목에 하이퍼링크 추가
        video_url = f"https://youtube.com/watch?v={video['video_id']}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. <{video_url}|{video['title'][:60]}...>*"
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"📺 *{video['channel_title']}*"
                },
                {
                    "type": "mrkdwn", 
                    "text": f"👁️ *{format_number(video['view_count'])}* 조회"
                },
                {
                    "type": "mrkdwn",
                    "text": f"💕 *{format_number(video['like_count'])}* 좋아요"
                },
                {
                    "type": "mrkdwn",
                    "text": f"⚡ *{format_number(video['views_per_hour'])}*/시간"
                }
            ],
            "accessory": {
                "type": "image",
                "image_url": video['thumbnail_url'],
                "alt_text": video['title']
            }
        })
    
    blocks.append({"type": "divider"})
    
    # AI 제안 추가
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🤖 AI 쇼츠 제작 제안*"
        }
    })
    
    # AI 제안을 블록으로 나누기
    ai_text = ai_suggestions[:2000] if ai_suggestions else "AI 제안을 생성할 수 없습니다."
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ai_text
        }
    })
    
    # Webhook 전송
    payload = {
        "blocks": blocks,
        "text": "🎰 포커 YouTube 트렌드 정밀 분석"
    }
    
    try:
        response = requests.post(
            slack_webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Enhanced Slack webhook sent successfully")
        else:
            logger.error(f"Slack webhook error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Slack webhook: {e}")


def format_number(num: float) -> str:
    """숫자 포맷팅 (개선된 버전)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 10000:
        return f"{num/1000:.0f}K"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))


def main():
    """메인 실행 함수"""
    logger.info("Starting enhanced YouTube poker trend analysis...")
    
    try:
        # YouTube 트렌드 분석
        analyzer = EnhancedYouTubeTrendAnalyzer()
        logger.info("Collecting YouTube videos with enhanced parameters...")
        videos = analyzer.collect_videos(lookback_hours=48)  # 48시간 데이터
        
        logger.info(f"Collected {len(videos)} videos for analysis")
        
        # 고급 트렌드 분석
        logger.info("Performing advanced trend analysis...")
        analysis_result = analyzer.analyze_trends(videos)
        
        # AI 제안 생성
        logger.info("Generating AI suggestions...")
        ai_suggestions = analyzer.generate_ai_suggestions(analysis_result)
        
        # 트렌드 분석 생성
        logger.info("Generating trend analysis...")
        trend_analysis = analyzer.generate_trend_analysis(analysis_result)
        
        # 향상된 Slack Webhook 전송
        logger.info("Sending enhanced Slack webhook...")
        send_enhanced_slack_webhook(analysis_result, ai_suggestions, trend_analysis)
        
        logger.info("Enhanced YouTube trend analysis completed successfully!")
        
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