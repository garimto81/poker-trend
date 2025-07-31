#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 트렌드 멀티 스케줄 분석기
- 일간: 매일 오전 10시 (최근 24시간)
- 주간: 매주 월요일 오전 10시 (최근 7일)
- 월간: 매월 첫 월요일 오전 10시 (전월)
"""

import os
import json
import requests
import schedule
import time
from datetime import datetime, timedelta
from calendar import monthrange
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv
import math
import sys
import logging

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_schedule_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiSchedulePokerAnalyzer:
    def __init__(self):
        load_dotenv()
        
        # API 키 로드
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not all([self.youtube_api_key, self.gemini_api_key, self.slack_webhook_url]):
            raise ValueError("Required API keys not found in .env file")
        
        # YouTube API 초기화
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        
        # Gemini AI 초기화
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Multi-schedule analyzer initialized")
    
    def collect_videos(self, time_filter, max_results=20):
        """비디오 수집 (시간 필터 적용)"""
        try:
            search_params = {
                'q': 'poker',
                'part': 'id,snippet',
                'maxResults': max_results,
                'order': 'relevance',
                'type': 'video',
                'regionCode': 'US',
                'relevanceLanguage': 'en'
            }
            
            if time_filter:
                search_params['publishedAfter'] = time_filter
            
            search_response = self.youtube.search().list(**search_params).execute()
            
            if not search_response.get('items'):
                return []
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # 비디오 상세 정보
            videos_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for video in videos_response['items']:
                view_count = int(video['statistics'].get('viewCount', 0))
                like_count = int(video['statistics'].get('likeCount', 0))
                comment_count = int(video['statistics'].get('commentCount', 0))
                
                engagement_rate = ((like_count + comment_count) / view_count) if view_count > 0 else 0
                viral_score = self._calculate_viral_score(view_count, like_count, comment_count, engagement_rate)
                
                published_at = video['snippet']['publishedAt']
                published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                
                video_data = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'published_at': published_at,
                    'published_date': published_date,
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': engagement_rate,
                    'viral_score': viral_score,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                
                videos.append(video_data)
            
            return sorted(videos, key=lambda x: x['viral_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error collecting videos: {str(e)}")
            return []
    
    def _calculate_viral_score(self, views, likes, comments, engagement_rate):
        """바이럴 점수 계산"""
        if views == 0:
            return 0
        
        view_score = math.log10(views + 1) * 0.4
        engagement_score = engagement_rate * 1000 * 0.3
        like_score = math.log10(likes + 1) * 0.2
        comment_score = math.log10(comments + 1) * 0.1
        
        return view_score + engagement_score + like_score + comment_score
    
    def analyze_daily(self):
        """일간 분석 (최근 24시간)"""
        logger.info("Starting daily analysis...")
        
        # 24시간 전
        time_filter = (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z'
        videos = self.collect_videos(time_filter, max_results=10)
        
        if not videos:
            logger.warning("No videos found for daily analysis")
            return
        
        # 통계 계산
        total_views = sum(v['view_count'] for v in videos)
        total_likes = sum(v['like_count'] for v in videos)
        avg_engagement = sum(v['engagement_rate'] for v in videos) / len(videos)
        
        # 슬랙 메시지 구성
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"☀️ 일간 포커 트렌드 - {datetime.now().strftime('%m/%d %H시')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 최근 24시간 통계*\n"
                                f"• 신규 업로드: {len(videos)}개\n"
                                f"• 총 조회수: {total_views:,}\n"
                                f"• 평균 참여율: {avg_engagement*100:.2f}%"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🔥 오늘의 TOP 3*"
                    }
                }
            ]
        }
        
        # TOP 3 비디오
        for i, video in enumerate(videos[:3], 1):
            hours_ago = int((datetime.utcnow() - video['published_date'].replace(tzinfo=None)).total_seconds() / 3600)
            title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
            
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{i}. *<{video['url']}|{title}>*\n"
                            f"   🎬 {video['channel']} • {hours_ago}시간 전\n"
                            f"   📊 조회: {video['view_count']:,} | 참여율: {video['engagement_rate']*100:.1f}%"
                }
            })
        
        # 하루 중 가장 활발한 시간대
        hour_distribution = {}
        for video in videos:
            hour = video['published_date'].hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        if hour_distribution:
            peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0]
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⏰ 인사이트*\n• 가장 활발한 업로드 시간: {peak_hour}시"
                }
            })
        
        self._send_to_slack(message)
        logger.info("Daily analysis completed")
    
    def analyze_weekly(self):
        """주간 분석 (최근 7일)"""
        logger.info("Starting weekly analysis...")
        
        # 7일 전
        time_filter = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
        videos = self.collect_videos(time_filter, max_results=20)
        
        if not videos:
            logger.warning("No videos found for weekly analysis")
            return
        
        # 통계 계산
        total_views = sum(v['view_count'] for v in videos)
        total_likes = sum(v['like_count'] for v in videos)
        avg_engagement = sum(v['engagement_rate'] for v in videos) / len(videos)
        
        # 채널별 통계
        channel_stats = {}
        for video in videos:
            channel = video['channel']
            if channel not in channel_stats:
                channel_stats[channel] = 0
            channel_stats[channel] += 1
        
        # 슬랙 메시지 구성
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📅 주간 포커 트렌드 - {datetime.now().strftime('%m/%d')} 주"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 주간 통계 (최근 7일)*\n"
                                f"• 총 업로드: {len(videos)}개\n"
                                f"• 총 조회수: {total_views:,} ({total_views/1000000:.1f}M)\n"
                                f"• 평균 참여율: {avg_engagement*100:.2f}%\n"
                                f"• 활동 채널: {len(channel_stats)}개"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🏆 주간 TOP 5*"
                    }
                }
            ]
        }
        
        # TOP 5 비디오
        for i, video in enumerate(videos[:5], 1):
            days_ago = (datetime.utcnow() - video['published_date'].replace(tzinfo=None)).days
            title = video['title'][:45] + "..." if len(video['title']) > 45 else video['title']
            
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{i}. *<{video['url']}|{title}>*\n"
                            f"   🎬 {video['channel']} • {days_ago}일 전\n"
                            f"   📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,}"
                }
            })
        
        # 주간 활발한 채널
        top_channels = sorted(channel_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        channel_text = "\n".join([f"• {ch[0]}: {ch[1]}개" for ch in top_channels])
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📺 주간 활발한 채널*\n{channel_text}"
            }
        })
        
        self._send_to_slack(message)
        logger.info("Weekly analysis completed")
    
    def analyze_monthly(self):
        """월간 분석 (전월)"""
        logger.info("Starting monthly analysis...")
        
        # 전월 첫날과 마지막날 계산
        today = datetime.now()
        first_day_this_month = today.replace(day=1)
        last_day_prev_month = first_day_this_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        
        # 시간 필터 설정 (전월 전체)
        time_filter_start = first_day_prev_month.isoformat() + 'Z'
        time_filter_end = last_day_prev_month.isoformat() + 'Z'
        
        # 월간은 더 많은 비디오 수집
        videos = self.collect_videos(time_filter_start, max_results=50)
        
        # 해당 월의 비디오만 필터링
        monthly_videos = [
            v for v in videos 
            if first_day_prev_month <= v['published_date'].replace(tzinfo=None) <= last_day_prev_month
        ]
        
        if not monthly_videos:
            logger.warning("No videos found for monthly analysis")
            return
        
        # 통계 계산
        total_views = sum(v['view_count'] for v in monthly_videos)
        total_likes = sum(v['like_count'] for v in monthly_videos)
        avg_engagement = sum(v['engagement_rate'] for v in monthly_videos) / len(monthly_videos)
        
        # 월간 최고 성과 비디오
        top_viral = max(monthly_videos, key=lambda x: x['viral_score'])
        top_views = max(monthly_videos, key=lambda x: x['view_count'])
        top_engagement = max(monthly_videos, key=lambda x: x['engagement_rate'])
        
        # 슬랙 메시지 구성
        month_name = last_day_prev_month.strftime('%Y년 %m월')
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📆 {month_name} 포커 트렌드 월간 리포트"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 월간 종합 통계*\n"
                                f"• 총 업로드: {len(monthly_videos)}개\n"
                                f"• 총 조회수: {total_views:,} ({total_views/1000000:.1f}M)\n"
                                f"• 총 좋아요: {total_likes:,}\n"
                                f"• 평균 참여율: {avg_engagement*100:.2f}%"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🏆 월간 최고 기록*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔥 최고 바이럴*\n<{top_viral['url']}|{top_viral['title'][:50]}...>\n"
                                f"바이럴 점수: {top_viral['viral_score']:.1f} | {top_viral['channel']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*👀 최다 조회*\n<{top_views['url']}|{top_views['title'][:50]}...>\n"
                                f"조회수: {top_views['view_count']:,} | {top_views['channel']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💎 최고 참여율*\n<{top_engagement['url']}|{top_engagement['title'][:50]}...>\n"
                                f"참여율: {top_engagement['engagement_rate']*100:.1f}% | {top_engagement['channel']}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📈 월간 TOP 10*"
                    }
                }
            ]
        }
        
        # TOP 10 리스트
        top_10_text = []
        for i, video in enumerate(monthly_videos[:10], 1):
            title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
            top_10_text.append(f"{i}. <{video['url']}|{title}> ({video['view_count']:,} views)")
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(top_10_text[:5])
            }
        })
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(top_10_text[5:10])
            }
        })
        
        self._send_to_slack(message)
        logger.info("Monthly analysis completed")
    
    def _send_to_slack(self, message):
        """슬랙으로 메시지 전송"""
        try:
            response = requests.post(self.slack_webhook_url, json=message)
            if response.status_code == 200:
                logger.info("Successfully sent to Slack")
            else:
                logger.error(f"Failed to send to Slack: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending to Slack: {str(e)}")
    
    def is_first_monday_of_month(self):
        """오늘이 이번 달 첫 번째 월요일인지 확인"""
        today = datetime.now()
        
        # 오늘이 월요일인지 확인 (0 = Monday)
        if today.weekday() != 0:
            return False
        
        # 이번 달 1일부터 오늘까지의 모든 날짜 확인
        for day in range(1, today.day):
            date = today.replace(day=day)
            if date.weekday() == 0:  # 이전에 월요일이 있었다면
                return False
        
        return True
    
    def setup_schedules(self):
        """스케줄 설정"""
        # 일간: 매일 오전 10시
        schedule.every().day.at("10:00").do(self.analyze_daily)
        
        # 주간: 매주 월요일 오전 10시
        schedule.every().monday.at("10:00").do(self.analyze_weekly)
        
        # 월간: 매월 첫 번째 월요일 오전 10시
        # schedule 라이브러리는 복잡한 조건을 직접 지원하지 않으므로 수동 체크
        def check_and_run_monthly():
            if self.is_first_monday_of_month():
                self.analyze_monthly()
        
        schedule.every().monday.at("10:00").do(check_and_run_monthly)
        
        logger.info("Schedules set up:")
        logger.info("- Daily: Every day at 10:00 AM")
        logger.info("- Weekly: Every Monday at 10:00 AM")
        logger.info("- Monthly: First Monday of month at 10:00 AM")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        logger.info("Multi-schedule analyzer started")
        logger.info(f"Current time: {datetime.now()}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

def main():
    analyzer = MultiSchedulePokerAnalyzer()
    
    # 테스트 모드 확인
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test-daily':
            print("Running daily analysis test...")
            analyzer.analyze_daily()
        elif sys.argv[1] == 'test-weekly':
            print("Running weekly analysis test...")
            analyzer.analyze_weekly()
        elif sys.argv[1] == 'test-monthly':
            print("Running monthly analysis test...")
            analyzer.analyze_monthly()
        else:
            print("Unknown test mode. Use: test-daily, test-weekly, or test-monthly")
    else:
        # 실제 스케줄러 실행
        analyzer.setup_schedules()
        print("="*80)
        print("포커 트렌드 멀티 스케줄 분석기")
        print("="*80)
        print("스케줄:")
        print("- 일간: 매일 오전 10시 (최근 24시간)")
        print("- 주간: 매주 월요일 오전 10시 (최근 7일)")
        print("- 월간: 매월 첫 번째 월요일 오전 10시 (전월)")
        print("\n실행 중... (Ctrl+C로 중단)")
        
        try:
            analyzer.run_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

if __name__ == "__main__":
    main()