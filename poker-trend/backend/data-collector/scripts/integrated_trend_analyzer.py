#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 YouTube 포커 트렌드 분석기
일간, 주간, 월간 리포트를 생성하는 통합 시스템
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 확인
REQUIRED_ENV_VARS = ['YOUTUBE_API_KEY', 'SLACK_WEBHOOK_URL', 'GEMINI_API_KEY']
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
        sys.exit(1)

# API 클라이언트 초기화
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')


class IntegratedTrendAnalyzer:
    """통합 포커 트렌드 분석기"""
    
    def __init__(self, report_type: str, date_range: int):
        self.report_type = report_type  # daily, weekly, monthly
        self.date_range = date_range    # 1, 7, 30
        
        # 검색 키워드 (영어 전용, Global 검색)
        self.search_terms = [
            'poker',
            'holdem',
            'wsop',
            'wpt',
            'ept',
            'pokerstars',
            'ggpoker',
            'triton poker'
        ]
        
        # 카테고리 분류
        self.categories = {
            'tournament': ['WSOP', 'WPT', 'EPT', 'tournament', 'final table', 'Triton'],
            'cash_game': ['cash game', 'high stakes', 'cash', 'NLH', 'PLO'],
            'online': ['PokerStars', 'GGPoker', 'online poker', 'online'],
            'education': ['strategy', 'tutorial', 'how to', 'tips', 'learn', 'guide'],
            'entertainment': ['highlights', 'funny', 'best', 'epic', 'amazing', 'crazy']
        }
        
        self.all_videos = []
        self.keyword_videos = defaultdict(list)
        self.channel_stats = defaultdict(lambda: {'count': 0, 'views': 0})
        
    def collect_videos(self) -> Dict[str, List[Dict]]:
        """각 키워드별로 상위 5개 영상 수집"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self.date_range)
        
        published_after = start_date.isoformat() + 'Z'
        published_before = end_date.isoformat() + 'Z'
        
        logger.info(f"수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        for keyword in self.search_terms:
            try:
                # 각 키워드별로 조회수 상위 5개 영상 검색
                request = youtube.search().list(
                    q=keyword,
                    part='snippet',
                    type='video',
                    maxResults=5,
                    order='viewCount',
                    publishedAfter=published_after,
                    publishedBefore=published_before,
                    relevanceLanguage='en',  # 영어 콘텐츠 우선
                    videoDuration='short' if self.report_type == 'daily' else 'any'
                )
                response = request.execute()
                
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                if video_ids:
                    # 영상 상세 정보 가져오기
                    details_request = youtube.videos().list(
                        part='statistics,contentDetails,snippet',
                        id=','.join(video_ids)
                    )
                    details_response = details_request.execute()
                    
                    for item in details_response.get('items', []):
                        video_data = {
                            'video_id': item['id'],
                            'title': item['snippet']['title'],
                            'channel_title': item['snippet']['channelTitle'],
                            'channel_id': item['snippet']['channelId'],
                            'published_at': item['snippet']['publishedAt'],
                            'view_count': int(item['statistics'].get('viewCount', 0)),
                            'like_count': int(item['statistics'].get('likeCount', 0)),
                            'comment_count': int(item['statistics'].get('commentCount', 0)),
                            'duration': item['contentDetails']['duration'],
                            'url': f"https://youtube.com/watch?v={item['id']}",
                            'keyword': keyword,
                            'category': self._categorize_video(item['snippet']['title'], item['snippet'].get('description', ''))
                        }
                        
                        # 중복 제거
                        if not any(v['video_id'] == video_data['video_id'] for v in self.all_videos):
                            self.all_videos.append(video_data)
                            self.keyword_videos[keyword].append(video_data)
                            
                            # 채널 통계 업데이트
                            channel = video_data['channel_title']
                            self.channel_stats[channel]['count'] += 1
                            self.channel_stats[channel]['views'] += video_data['view_count']
                
                logger.info(f"키워드 '{keyword}': {len(self.keyword_videos[keyword])}개 영상 수집")
                
            except HttpError as e:
                logger.error(f"YouTube API 오류 (키워드: {keyword}): {e}")
                continue
            except Exception as e:
                logger.error(f"예상치 못한 오류 (키워드: {keyword}): {e}")
                continue
        
        # 전체 영상을 조회수 기준으로 정렬
        self.all_videos.sort(key=lambda x: x['view_count'], reverse=True)
        
        logger.info(f"총 {len(self.all_videos)}개 영상 수집 완료")
        return self.keyword_videos
    
    def _categorize_video(self, title: str, description: str) -> str:
        """영상 카테고리 분류"""
        text = (title + ' ' + description).lower()
        
        for category, keywords in self.categories.items():
            if any(keyword.lower() in text for keyword in keywords):
                return category
        
        return 'general'
    
    def analyze_trends(self) -> Dict[str, Any]:
        """트렌드 분석"""
        if not self.all_videos:
            return {}
        
        # 기본 통계
        total_views = sum(v['view_count'] for v in self.all_videos)
        avg_views = total_views // len(self.all_videos)
        
        # 카테고리별 분석
        category_stats = defaultdict(lambda: {'count': 0, 'views': 0})
        for video in self.all_videos:
            cat = video['category']
            category_stats[cat]['count'] += 1
            category_stats[cat]['views'] += video['view_count']
        
        # 시간대별 분석 (일간 리포트용)
        hourly_uploads = defaultdict(int)
        if self.report_type == 'daily':
            for video in self.all_videos:
                hour = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).hour
                hourly_uploads[hour] += 1
        
        # 성장률 계산 (주간/월간용)
        growth_videos = []
        if self.report_type in ['weekly', 'monthly']:
            for video in self.all_videos[:20]:  # 상위 20개만
                # 간단한 성장률 계산 (일평균 조회수)
                days_since_upload = (datetime.utcnow() - datetime.fromisoformat(
                    video['published_at'].replace('Z', '+00:00')
                )).days or 1
                daily_views = video['view_count'] / days_since_upload
                
                growth_videos.append({
                    'title': video['title'],
                    'channel': video['channel_title'],
                    'views': video['view_count'],
                    'daily_growth': int(daily_views),
                    'url': video['url']
                })
        
        return {
            'total_videos': len(self.all_videos),
            'total_views': total_views,
            'avg_views': avg_views,
            'category_stats': dict(category_stats),
            'channel_stats': dict(self.channel_stats),
            'hourly_uploads': dict(hourly_uploads),
            'growth_videos': sorted(growth_videos, key=lambda x: x['daily_growth'], reverse=True)[:10]
        }
    
    def generate_ai_insights(self, analysis_data: Dict[str, Any]) -> str:
        """Gemini AI를 사용한 인사이트 생성"""
        
        # 리포트 타입별 프롬프트
        prompts = {
            'daily': f"""
다음은 최근 24시간 YouTube 포커 트렌드 데이터입니다.
총 {analysis_data['total_videos']}개 영상, 총 조회수 {analysis_data['total_views']:,}회

카테고리별 분포: {json.dumps(analysis_data['category_stats'], ensure_ascii=False)}
상위 채널: {', '.join([f"{ch} ({stats['count']}개)" for ch, stats in list(analysis_data['channel_stats'].items())[:5]])}

다음을 분석해주세요:
1. 오늘의 핫 토픽 2-3개
2. 가장 주목받는 채널/선수
3. 내일 예상되는 트렌드
한국어로 3-4문장으로 간결하게 요약해주세요.
""",
            'weekly': f"""
다음은 지난 7일간 YouTube 포커 트렌드 데이터입니다.
총 {analysis_data['total_videos']}개 영상, 총 조회수 {analysis_data['total_views']:,}회

카테고리별 분포: {json.dumps(analysis_data['category_stats'], ensure_ascii=False)}
급성장 영상: {len(analysis_data.get('growth_videos', []))}개

다음을 분석해주세요:
1. 이번 주 가장 큰 트렌드 변화
2. 새롭게 떠오르는 키워드나 토픽
3. 다음 주 콘텐츠 전략 제안
한국어로 5-6문장으로 분석해주세요.
""",
            'monthly': f"""
다음은 지난 30일간 YouTube 포커 트렌드 데이터입니다.
총 {analysis_data['total_videos']}개 영상, 총 조회수 {analysis_data['total_views']:,}회

카테고리별 분포: {json.dumps(analysis_data['category_stats'], ensure_ascii=False)}
주요 채널: {', '.join([f"{ch} ({stats['views']:,}회)" for ch, stats in list(analysis_data['channel_stats'].items())[:5]])}

다음을 분석해주세요:
1. 이번 달의 주요 트렌드 3개
2. 가장 성공적인 콘텐츠 유형
3. 장기적인 트렌드 방향 예측
한국어로 7-8문장으로 종합 분석해주세요.
"""
        }
        
        try:
            prompt = prompts.get(self.report_type, prompts['daily'])
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI 인사이트 생성 실패: {e}")
            return "AI 분석을 생성할 수 없습니다."
    
    def format_slack_message(self, analysis_data: Dict[str, Any], ai_insights: str) -> Dict[str, Any]:
        """Slack 메시지 포맷팅"""
        
        # 리포트 타입별 제목
        titles = {
            'daily': '🎰 포커 트렌드 일일 분석',
            'weekly': '📊 포커 트렌드 주간 분석',
            'monthly': '📊 포커 트렌드 월간 종합 리포트'
        }
        
        # 기간 텍스트
        date_ranges = {
            'daily': '최근 24시간',
            'weekly': '지난 7일',
            'monthly': '지난 30일'
        }
        
        # 기본 정보
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": titles[self.report_type]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y년 %m월 %d일')} ({['월','화','수','목','금','토','일'][datetime.now().weekday()]})\n"
                           f"⏰ 분석 기간: {date_ranges[self.report_type]}\n"
                           f"📊 분석 영상: {analysis_data['total_videos']}개"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # AI 인사이트
        if ai_insights:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 AI 트렌드 분석*\n{ai_insights}"
                }
            })
            blocks.append({"type": "divider"})
        
        # 키워드별 TOP 영상
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📺 키워드별 TOP 영상*"
            }
        })
        
        # 각 키워드별로 상위 1-2개만 표시
        for keyword in self.search_terms:
            if keyword in self.keyword_videos and self.keyword_videos[keyword]:
                top_videos = self.keyword_videos[keyword][:2]
                video_text = f"\n*【{keyword}】*\n"
                
                for i, video in enumerate(top_videos, 1):
                    video_text += f"{i}. <{video['url']}|{video['title'][:50]}...>\n"
                    video_text += f"   조회수: {video['view_count']:,} | {video['channel_title']}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": video_text
                    }
                })
        
        blocks.append({"type": "divider"})
        
        # 채널 통계
        top_channels = sorted(
            self.channel_stats.items(),
            key=lambda x: x[1]['views'],
            reverse=True
        )[:5]
        
        channel_text = "*🎬 TOP 5 채널*\n"
        for i, (channel, stats) in enumerate(top_channels, 1):
            channel_text += f"{i}. {channel}: {stats['count']}개 영상, {stats['views']:,}회\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": channel_text
            }
        })
        
        # 통계 요약
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 통계 요약*\n"
                       f"• 총 조회수: {analysis_data['total_views']:,}회\n"
                       f"• 평균 조회수: {analysis_data['avg_views']:,}회\n"
                       f"• 가장 활발한 카테고리: {max(analysis_data['category_stats'].items(), key=lambda x: x[1]['views'])[0]}"
            }
        })
        
        return {
            "blocks": blocks,
            "text": f"{titles[self.report_type]} - {datetime.now().strftime('%Y-%m-%d')}"
        }
    
    def send_to_slack(self, message: Dict[str, Any]) -> bool:
        """Slack으로 메시지 전송"""
        try:
            response = requests.post(
                slack_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"Slack 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 전송 중 오류 발생: {e}")
            return False
    
    def save_report(self, analysis_data: Dict[str, Any], ai_insights: str):
        """리포트 데이터 저장"""
        os.makedirs('reports', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/{self.report_type}_report_{timestamp}.json"
        
        report_data = {
            'report_type': self.report_type,
            'date_range': self.date_range,
            'generated_at': datetime.now().isoformat(),
            'total_videos': len(self.all_videos),
            'analysis': analysis_data,
            'ai_insights': ai_insights,
            'videos': self.all_videos[:50]  # 상위 50개만 저장
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"리포트 저장 완료: {filename}")
    
    def run(self):
        """전체 프로세스 실행"""
        logger.info(f"{'='*50}")
        logger.info(f"{self.report_type.upper()} 리포트 생성 시작")
        logger.info(f"{'='*50}")
        
        # 1. 데이터 수집
        logger.info("1. YouTube 데이터 수집 중...")
        self.collect_videos()
        
        if not self.all_videos:
            logger.error("수집된 영상이 없습니다.")
            return
        
        # 2. 트렌드 분석
        logger.info("2. 트렌드 분석 중...")
        analysis_data = self.analyze_trends()
        
        # 3. AI 인사이트 생성
        logger.info("3. AI 인사이트 생성 중...")
        ai_insights = self.generate_ai_insights(analysis_data)
        
        # 4. 리포트 저장
        logger.info("4. 리포트 저장 중...")
        self.save_report(analysis_data, ai_insights)
        
        # 5. Slack 전송
        logger.info("5. Slack 메시지 생성 및 전송 중...")
        slack_message = self.format_slack_message(analysis_data, ai_insights)
        self.send_to_slack(slack_message)
        
        logger.info(f"{'='*50}")
        logger.info("리포트 생성 완료!")
        logger.info(f"{'='*50}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='YouTube 포커 트렌드 분석기')
    parser.add_argument('--report-type', choices=['daily', 'weekly', 'monthly'],
                      default='daily', help='리포트 타입')
    parser.add_argument('--date-range', type=int, default=1,
                      help='분석 기간 (일 단위)')
    
    args = parser.parse_args()
    
    # 환경 변수에서 값 가져오기 (GitHub Actions에서 설정)
    report_type = os.getenv('REPORT_TYPE', args.report_type)
    date_range = int(os.getenv('DATE_RANGE', args.date_range))
    
    # 분석기 실행
    analyzer = IntegratedTrendAnalyzer(report_type, date_range)
    analyzer.run()


if __name__ == "__main__":
    main()