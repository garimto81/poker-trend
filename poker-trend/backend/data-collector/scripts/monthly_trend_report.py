#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
월간 포커 트렌드 종합 분석 리포트
매월 첫째주 월요일 오전 10시 실행
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from collections import Counter, defaultdict
from googleapiclient.discovery import build
import google.generativeai as genai

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# API 초기화
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-pro')


class MonthlyTrendAnalyzer:
    """월간 포커 트렌드 분석기"""
    
    def __init__(self):
        self.month_data = {
            'total_videos': 0,
            'total_views': 0,
            'category_performance': defaultdict(lambda: {'videos': 0, 'views': 0}),
            'top_keywords': Counter(),
            'top_channels': Counter(),
            'viral_videos': [],
            'trend_evolution': [],
            'monthly_insights': []
        }
    
    def analyze_monthly_trends(self) -> Dict[str, Any]:
        """한 달간의 트렌드 종합 분석"""
        logger.info("Starting monthly trend analysis...")
        
        # 지난 30일간 데이터 수집
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 주차별 데이터 수집
        weekly_data = []
        for week in range(4):
            week_start = start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=7)
            week_videos = self._collect_week_data(week_start, week_end)
            weekly_data.append({
                'week': week + 1,
                'videos': week_videos,
                'total': len(week_videos),
                'avg_views': sum(v.get('view_count', 0) for v in week_videos) / len(week_videos) if week_videos else 0
            })
        
        # 월간 통계 계산
        all_videos = []
        for week in weekly_data:
            all_videos.extend(week['videos'])
        
        self.month_data['total_videos'] = len(all_videos)
        self.month_data['total_views'] = sum(v.get('view_count', 0) for v in all_videos)
        
        # 카테고리별 성과 분석
        self._analyze_categories(all_videos)
        
        # 키워드 트렌드 분석
        self._analyze_keywords(all_videos)
        
        # 채널 순위 분석
        self._analyze_channels(all_videos)
        
        # 바이럴 영상 선정 (상위 1%)
        viral_threshold = sorted([v.get('view_count', 0) for v in all_videos], reverse=True)[int(len(all_videos) * 0.01)] if all_videos else 0
        self.month_data['viral_videos'] = [v for v in all_videos if v.get('view_count', 0) >= viral_threshold][:10]
        
        # 주차별 트렌드 변화
        self.month_data['trend_evolution'] = self._analyze_trend_evolution(weekly_data)
        
        # AI 인사이트 생성
        self.month_data['monthly_insights'] = self._generate_ai_insights()
        
        return self.month_data
    
    def _collect_week_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """특정 주의 데이터 수집"""
        videos = []
        # 검색 키워드 (영어 전용, Global 검색)
        # 설정 문서: docs/SEARCH_KEYWORDS.md
        search_terms = [
            'poker', 'holdem', 'wsop', 'wpt', 
            'ept', 'pokerstars', 'ggpoker', 'triton poker'
        ]
        
        for term in search_terms:
            try:
                request = youtube.search().list(
                    q=term,
                    part='snippet',
                    type='video',
                    maxResults=50,
                    order='viewCount',
                    publishedAfter=start_date.isoformat() + 'Z',
                    publishedBefore=end_date.isoformat() + 'Z'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    videos.append({
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt']
                    })
            except Exception as e:
                logger.error(f"Error collecting data: {e}")
        
        # 중복 제거 및 상세 정보 추가
        unique_videos = list({v['video_id']: v for v in videos}.values())
        return self._enrich_videos(unique_videos[:100])
    
    def _enrich_videos(self, videos: List[Dict]) -> List[Dict]:
        """비디오 상세 정보 추가"""
        if not videos:
            return []
        
        video_ids = [v['video_id'] for v in videos]
        
        try:
            request = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids[:50])
            )
            response = request.execute()
            
            stats_map = {
                item['id']: item['statistics']
                for item in response.get('items', [])
            }
            
            for video in videos:
                if video['video_id'] in stats_map:
                    stats = stats_map[video['video_id']]
                    video['view_count'] = int(stats.get('viewCount', 0))
                    video['like_count'] = int(stats.get('likeCount', 0))
                    video['comment_count'] = int(stats.get('commentCount', 0))
        except Exception as e:
            logger.error(f"Error enriching videos: {e}")
        
        return videos
    
    def _analyze_categories(self, videos: List[Dict]):
        """카테고리별 성과 분석"""
        categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', '토너먼트'],
            'cash_game': ['cash', '캐시', 'high stakes'],
            'online': ['online', '온라인', 'PokerStars', 'GGPoker'],
            'education': ['strategy', '전략', 'tutorial', '강의']
        }
        
        for video in videos:
            title_lower = video['title'].lower()
            categorized = False
            
            for cat, keywords in categories.items():
                if any(kw.lower() in title_lower for kw in keywords):
                    self.month_data['category_performance'][cat]['videos'] += 1
                    self.month_data['category_performance'][cat]['views'] += video.get('view_count', 0)
                    categorized = True
                    break
            
            if not categorized:
                self.month_data['category_performance']['other']['videos'] += 1
                self.month_data['category_performance']['other']['views'] += video.get('view_count', 0)
    
    def _analyze_keywords(self, videos: List[Dict]):
        """키워드 빈도 분석"""
        import re
        
        for video in videos:
            # 제목에서 키워드 추출
            words = re.findall(r'\b[a-zA-Z가-힣]{3,}\b', video['title'].lower())
            
            # 불용어 제거
            stopwords = {'the', 'and', 'for', 'with', 'poker', '포커'}
            keywords = [w for w in words if w not in stopwords]
            
            # 조회수로 가중치 부여
            weight = min(video.get('view_count', 0) / 10000, 10)  # 최대 가중치 10
            for keyword in keywords:
                self.month_data['top_keywords'][keyword] += weight
    
    def _analyze_channels(self, videos: List[Dict]):
        """채널별 성과 분석"""
        for video in videos:
            channel = video['channel_title']
            views = video.get('view_count', 0)
            self.month_data['top_channels'][channel] += views
    
    def _analyze_trend_evolution(self, weekly_data: List[Dict]) -> List[Dict]:
        """주차별 트렌드 변화 분석"""
        evolution = []
        
        for week in weekly_data:
            # 해당 주의 TOP 키워드
            week_keywords = Counter()
            for video in week['videos']:
                words = video['title'].lower().split()
                week_keywords.update(words)
            
            evolution.append({
                'week': week['week'],
                'total_videos': week['total'],
                'avg_views': week['avg_views'],
                'top_keywords': week_keywords.most_common(5)
            })
        
        return evolution
    
    def _generate_ai_insights(self) -> List[str]:
        """AI를 활용한 월간 인사이트 생성"""
        try:
            # 월간 데이터 요약
            summary = f"""
            월간 포커 트렌드 데이터:
            - 총 분석 영상: {self.month_data['total_videos']}개
            - 총 조회수: {self.month_data['total_views']:,}회
            - TOP 키워드: {', '.join([k for k, _ in self.month_data['top_keywords'].most_common(10)])}
            - 카테고리별 성과: {dict(self.month_data['category_performance'])}
            """
            
            prompt = f"""
            다음 월간 포커 트렌드 데이터를 분석하여 3가지 핵심 인사이트를 도출해주세요:
            
            {summary}
            
            각 인사이트는 다음 형식으로 작성:
            1. 트렌드 패턴 (무엇이 주목받았는가)
            2. 원인 분석 (왜 이런 트렌드가 발생했는가)
            3. 향후 전망 (다음 달 예상 트렌드)
            
            실용적이고 구체적인 인사이트를 제공해주세요.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text.split('\n\n')[:3]  # 3개 인사이트만
            
        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            return ["AI 인사이트 생성 중 오류가 발생했습니다."]


def send_monthly_report(data: Dict[str, Any]):
    """월간 리포트 Slack 전송"""
    
    # 현재 시간 (한국 시간)
    kst_time = datetime.now() + timedelta(hours=9)
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📅 포커 트렌드 월간 종합 리포트 ({kst_time.strftime('%Y년 %m월')})"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 월간 종합 통계*\n" +
                       f"• 총 분석 영상: {data['total_videos']:,}개\n" +
                       f"• 총 조회수: {data['total_views']:,}회\n" +
                       f"• 평균 조회수: {data['total_views'] // data['total_videos'] if data['total_videos'] > 0 else 0:,}회"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🏆 월간 TOP 10 키워드*"
            }
        }
    ]
    
    # TOP 키워드
    keyword_text = []
    for i, (keyword, score) in enumerate(data['top_keywords'].most_common(10), 1):
        keyword_text.append(f"{i}. `{keyword}` (점수: {score:.1f})")
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '\n'.join(keyword_text[:5]) + '\n' + '\n'.join(keyword_text[5:])
        }
    })
    
    blocks.append({"type": "divider"})
    
    # 카테고리별 성과
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📈 카테고리별 성과*"
        }
    })
    
    cat_text = []
    for cat, stats in sorted(data['category_performance'].items(), key=lambda x: x[1]['views'], reverse=True):
        avg_views = stats['views'] // stats['videos'] if stats['videos'] > 0 else 0
        emoji = {
            'tournament': '🏆',
            'cash_game': '💰',
            'online': '💻',
            'education': '📚',
            'other': '🎮'
        }.get(cat, '📌')
        cat_text.append(f"{emoji} *{cat}*: {stats['videos']}개 (평균 {avg_views:,}회)")
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '\n'.join(cat_text)
        }
    })
    
    blocks.append({"type": "divider"})
    
    # TOP 채널
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🎬 TOP 5 채널 (조회수 기준)*\n" +
                   '\n'.join([f"{i+1}. {ch} ({views:,}회)" 
                            for i, (ch, views) in enumerate(data['top_channels'].most_common(5))])
        }
    })
    
    blocks.append({"type": "divider"})
    
    # 주차별 트렌드 변화
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📊 주차별 트렌드 변화*"
        }
    })
    
    for week in data['trend_evolution']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{week['week']}주차*: {week['total_videos']}개 영상, 평균 {int(week['avg_views']):,}회\n" +
                       f"주요 키워드: {', '.join([f'`{k[0]}`' for k in week['top_keywords'][:3]])}"
            }
        })
    
    blocks.append({"type": "divider"})
    
    # AI 인사이트
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🤖 AI 월간 인사이트*"
        }
    })
    
    for insight in data['monthly_insights']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": insight[:600]  # 길이 제한
            }
        })
    
    blocks.append({"type": "divider"})
    
    # 다음 달 추천 전략
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*💡 다음 달 콘텐츠 전략 추천*\n" +
                   f"1. TOP 키워드 활용: {', '.join([k for k, _ in data['top_keywords'].most_common(3)])}\n" +
                   f"2. 주력 카테고리: {max(data['category_performance'].items(), key=lambda x: x[1]['views'])[0]}\n" +
                   "3. 바이럴 영상 벤치마킹: 상위 1% 영상 분석\n" +
                   "4. 신규 트렌드 실험: AI 포커, NFT 토너먼트 등"
        }
    })
    
    # Slack 전송
    payload = {
        "blocks": blocks,
        "text": f"📅 포커 트렌드 월간 종합 리포트 ({kst_time.strftime('%Y년 %m월')})"
    }
    
    try:
        response = requests.post(
            slack_webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Monthly report sent successfully")
        else:
            logger.error(f"Slack webhook error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending monthly report: {e}")


def main():
    """메인 실행 함수"""
    logger.info("Starting monthly poker trend analysis...")
    
    try:
        analyzer = MonthlyTrendAnalyzer()
        monthly_data = analyzer.analyze_monthly_trends()
        
        # 리포트 저장
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/monthly_report_{datetime.now(, encoding='utf-8').strftime("%Y%m")}.json', 'w', encoding='utf-8') as f:
            json.dump(monthly_data, f, ensure_ascii=False, indent=2, default=str)
        
        # Slack 전송
        send_monthly_report(monthly_data)
        
        logger.info("Monthly trend analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in monthly analysis: {e}", exc_info=True)
        
        # 에러 알림
        error_payload = {
            "text": f"⚠️ 월간 트렌드 분석 오류: {str(e)}"
        }
        requests.post(slack_webhook_url, json=error_payload)
        
        raise


if __name__ == "__main__":
    main()