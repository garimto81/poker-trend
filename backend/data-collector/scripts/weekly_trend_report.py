#!/usr/bin/env python3
"""
주간 포커 트렌드 분석 리포트
매주 월요일 오전 10시 실행 (첫째주 제외)
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


class WeeklyTrendAnalyzer:
    """주간 포커 트렌드 분석기"""
    
    def __init__(self):
        self.week_data = {
            'total_videos': 0,
            'total_views': 0,
            'daily_trends': [],
            'top_keywords': Counter(),
            'category_performance': defaultdict(lambda: {'videos': 0, 'views': 0}),
            'best_times': defaultdict(int),
            'emerging_trends': [],
            'weekly_insights': []
        }
    
    def analyze_weekly_trends(self) -> Dict[str, Any]:
        """일주일간의 트렌드 분석"""
        logger.info("Starting weekly trend analysis...")
        
        # 지난 7일간 데이터 수집
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 일별 데이터 수집
        all_videos = []
        for day in range(7):
            day_date = start_date + timedelta(days=day)
            day_videos = self._collect_daily_data(day_date)
            
            self.week_data['daily_trends'].append({
                'date': day_date.strftime('%Y-%m-%d'),
                'day_name': day_date.strftime('%A'),
                'video_count': len(day_videos),
                'total_views': sum(v.get('view_count', 0) for v in day_videos),
                'avg_views': sum(v.get('view_count', 0) for v in day_videos) / len(day_videos) if day_videos else 0
            })
            
            all_videos.extend(day_videos)
        
        # 주간 통계 계산
        self.week_data['total_videos'] = len(all_videos)
        self.week_data['total_views'] = sum(v.get('view_count', 0) for v in all_videos)
        
        # 상세 분석
        self._analyze_keywords(all_videos)
        self._analyze_categories(all_videos)
        self._analyze_upload_times(all_videos)
        self._identify_emerging_trends(all_videos)
        
        # AI 인사이트 생성
        self.week_data['weekly_insights'] = self._generate_ai_insights()
        
        return self.week_data
    
    def _collect_daily_data(self, date: datetime) -> List[Dict]:
        """특정 날짜의 데이터 수집"""
        videos = []
        search_terms = self._get_dynamic_keywords()
        
        start_time = date.isoformat() + 'Z'
        end_time = (date + timedelta(days=1)).isoformat() + 'Z'
        
        for term in search_terms[:10]:  # 상위 10개 키워드만 사용
            try:
                request = youtube.search().list(
                    q=term,
                    part='snippet',
                    type='video',
                    maxResults=20,
                    order='viewCount',
                    publishedAfter=start_time,
                    publishedBefore=end_time
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    videos.append({
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'description': item['snippet']['description'][:200]
                    })
            except Exception as e:
                logger.error(f"Error collecting data for {term}: {e}")
        
        # 중복 제거 및 상세 정보 추가
        unique_videos = list({v['video_id']: v for v in videos}.values())
        return self._enrich_videos(unique_videos[:50])
    
    def _get_dynamic_keywords(self) -> List[str]:
        """동적 키워드 로드"""
        try:
            keywords_file = 'data/dynamic_keywords.json'
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data['base_keywords'] + data.get('trending_keywords', [])
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
        
        # 기본 키워드
        return ['poker', '포커', 'holdem', '홀덤', 'WSOP', 'WPT']
    
    def _enrich_videos(self, videos: List[Dict]) -> List[Dict]:
        """비디오 상세 정보 추가"""
        if not videos:
            return []
        
        video_ids = [v['video_id'] for v in videos]
        
        try:
            request = youtube.videos().list(
                part='statistics',
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
                    
                    # 참여율 계산
                    views = video['view_count']
                    if views > 0:
                        video['engagement_rate'] = ((video['like_count'] + video['comment_count']) / views) * 100
                    else:
                        video['engagement_rate'] = 0
                        
                    # 업로드 시간 분석
                    published_time = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                    video['upload_hour'] = published_time.hour
                    
        except Exception as e:
            logger.error(f"Error enriching videos: {e}")
        
        return videos
    
    def _analyze_keywords(self, videos: List[Dict]):
        """키워드 분석"""
        import re
        
        for video in videos:
            # 제목과 설명에서 키워드 추출
            text = f"{video['title']} {video.get('description', '')}"
            words = re.findall(r'\b[a-zA-Z가-힣]{3,}\b', text.lower())
            
            # 불용어 제거
            stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'have', 'from'}
            keywords = [w for w in words if w not in stopwords and len(w) > 3]
            
            # 조회수로 가중치
            weight = min(video.get('view_count', 0) / 1000, 10)
            for keyword in keywords:
                self.week_data['top_keywords'][keyword] += weight
    
    def _analyze_categories(self, videos: List[Dict]):
        """카테고리별 분석"""
        categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', '토너먼트', 'final table'],
            'cash_game': ['cash', '캐시', 'high stakes'],
            'online': ['online', '온라인', 'PokerStars', 'GGPoker'],
            'education': ['strategy', '전략', 'tutorial', '강의', 'tips'],
            'entertainment': ['funny', '재미', 'fail', 'compilation', 'highlights']
        }
        
        for video in videos:
            title_lower = video['title'].lower()
            desc_lower = video.get('description', '').lower()
            
            for cat, keywords in categories.items():
                if any(kw.lower() in title_lower or kw.lower() in desc_lower for kw in keywords):
                    self.week_data['category_performance'][cat]['videos'] += 1
                    self.week_data['category_performance'][cat]['views'] += video.get('view_count', 0)
                    break
    
    def _analyze_upload_times(self, videos: List[Dict]):
        """업로드 시간대 분석"""
        for video in videos:
            hour = video.get('upload_hour', 0)
            engagement = video.get('engagement_rate', 0)
            self.week_data['best_times'][hour] += engagement
    
    def _identify_emerging_trends(self, videos: List[Dict]):
        """새롭게 떠오르는 트렌드 감지"""
        # 이번 주 키워드와 지난 주 키워드 비교
        current_keywords = set([k for k, _ in self.week_data['top_keywords'].most_common(20)])
        
        # 이전 주 데이터 로드 (있다면)
        try:
            prev_report = f'reports/weekly_report_{(datetime.now() - timedelta(weeks=1)).strftime("%Y%W")}.json'
            if os.path.exists(prev_report):
                with open(prev_report, 'r', encoding='utf-8') as f:
                    prev_data = json.load(f)
                prev_keywords = set([k for k, _ in prev_data.get('top_keywords', {}).items()][:20])
                
                # 새로운 키워드
                self.week_data['emerging_trends'] = list(current_keywords - prev_keywords)[:10]
        except Exception as e:
            logger.error(f"Error loading previous report: {e}")
    
    def _generate_ai_insights(self) -> List[str]:
        """AI 주간 인사이트 생성"""
        try:
            # 주간 데이터 요약
            summary = f"""
            주간 포커 트렌드 데이터:
            - 총 영상: {self.week_data['total_videos']}개
            - 총 조회수: {self.week_data['total_views']:,}회
            - TOP 키워드: {', '.join([k for k, _ in self.week_data['top_keywords'].most_common(10)])}
            - 카테고리 성과: {dict(self.week_data['category_performance'])}
            - 새로운 트렌드: {', '.join(self.week_data['emerging_trends'][:5])}
            """
            
            prompt = f"""
            다음 주간 포커 트렌드 데이터를 분석하여 실용적인 인사이트 3개를 제공해주세요:
            
            {summary}
            
            다음 관점에서 분석해주세요:
            1. 이번 주 가장 주목할 트렌드
            2. 카테고리별 성과 분석
            3. 다음 주 콘텐츠 제작 추천
            
            각 인사이트는 구체적이고 실행 가능해야 합니다.
            """
            
            response = gemini_model.generate_content(prompt)
            return response.text.split('\n\n')[:3]
            
        except Exception as e:
            logger.error(f"AI insights error: {e}")
            return ["AI 인사이트 생성 중 오류가 발생했습니다."]


def send_weekly_report(data: Dict[str, Any]):
    """주간 리포트 Slack 전송"""
    
    kst_time = datetime.now() + timedelta(hours=9)
    week_start = (kst_time - timedelta(days=7)).strftime('%m/%d')
    week_end = kst_time.strftime('%m/%d')
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 포커 트렌드 주간 리포트 ({week_start} - {week_end})"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📈 주간 요약*\n" +
                       f"• 총 분석 영상: {data['total_videos']:,}개\n" +
                       f"• 총 조회수: {data['total_views']:,}회\n" +
                       f"• 일평균 영상: {data['total_videos'] // 7}개"
            }
        },
        {"type": "divider"}
    ]
    
    # 일별 트렌드
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📅 일별 트렌드*"
        }
    })
    
    daily_text = []
    for day in data['daily_trends']:
        daily_text.append(f"• {day['date']} ({day['day_name'][:3]}): {day['video_count']}개, 평균 {int(day['avg_views']):,}회")
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '\n'.join(daily_text)
        }
    })
    
    blocks.append({"type": "divider"})
    
    # TOP 키워드
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🔥 주간 TOP 10 키워드*\n" +
                   ', '.join([f"`{k}`" for k, _ in data['top_keywords'].most_common(10)])
        }
    })
    
    # 새로운 트렌드
    if data['emerging_trends']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🌟 새롭게 떠오르는 키워드*\n{', '.join([f'`{k}`' for k in data['emerging_trends'][:5]])}"
            }
        })
    
    blocks.append({"type": "divider"})
    
    # 카테고리별 성과
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📊 카테고리별 성과*"
        }
    })
    
    cat_fields = []
    for cat, stats in sorted(data['category_performance'].items(), key=lambda x: x[1]['views'], reverse=True):
        if stats['videos'] > 0:
            avg_views = stats['views'] // stats['videos']
            emoji = {
                'tournament': '🏆',
                'cash_game': '💰', 
                'online': '💻',
                'education': '📚',
                'entertainment': '🎭'
            }.get(cat, '📌')
            cat_fields.append({
                "type": "mrkdwn",
                "text": f"{emoji} *{cat}*\n{stats['videos']}개 (평균 {avg_views:,}회)"
            })
    
    blocks.append({
        "type": "section",
        "fields": cat_fields[:4]  # 최대 4개만 표시
    })
    
    blocks.append({"type": "divider"})
    
    # 최적 업로드 시간
    best_hours = sorted(data['best_times'].items(), key=lambda x: x[1], reverse=True)[:3]
    if best_hours:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*⏰ 최적 업로드 시간 (KST)*\n" +
                       '\n'.join([f"{i+1}. {(h[0]+9)%24}:00 (참여율 {h[1]:.1f})" for i, h in enumerate(best_hours)])
            }
        })
    
    blocks.append({"type": "divider"})
    
    # AI 인사이트
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🤖 AI 주간 인사이트*"
        }
    })
    
    for insight in data['weekly_insights']:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": insight[:500]
            }
        })
    
    blocks.append({"type": "divider"})
    
    # 다음 주 추천
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*💡 다음 주 콘텐츠 추천*\n" +
                   f"1. 키워드 활용: {', '.join([k for k, _ in data['top_keywords'].most_common(3)])}\n" +
                   f"2. 주력 카테고리: {max(data['category_performance'].items(), key=lambda x: x[1]['views'])[0] if data['category_performance'] else 'N/A'}\n" +
                   f"3. 업로드 시간: {(best_hours[0][0]+9)%24 if best_hours else 20}:00 KST\n" +
                   f"4. 신규 트렌드: {', '.join(data['emerging_trends'][:3]) if data['emerging_trends'] else '지속 관찰 필요'}"
        }
    })
    
    # Slack 전송
    payload = {
        "blocks": blocks,
        "text": f"📊 포커 트렌드 주간 리포트 ({week_start} - {week_end})"
    }
    
    try:
        response = requests.post(
            slack_webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("Weekly report sent successfully")
        else:
            logger.error(f"Slack webhook error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending weekly report: {e}")


def main():
    """메인 실행 함수"""
    logger.info("Starting weekly poker trend analysis...")
    
    try:
        analyzer = WeeklyTrendAnalyzer()
        weekly_data = analyzer.analyze_weekly_trends()
        
        # 리포트 저장
        os.makedirs('reports', exist_ok=True)
        report_file = f'reports/weekly_report_{datetime.now().strftime("%Y%W")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, ensure_ascii=False, indent=2, default=str)
        
        # Slack 전송
        send_weekly_report(weekly_data)
        
        logger.info("Weekly trend analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in weekly analysis: {e}", exc_info=True)
        
        # 에러 알림
        error_payload = {
            "text": f"⚠️ 주간 트렌드 분석 오류: {str(e)}"
        }
        requests.post(slack_webhook_url, json=error_payload)
        
        raise


if __name__ == "__main__":
    main()