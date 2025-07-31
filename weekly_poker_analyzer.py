#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 포커 트렌드 분석기 - 1주일 이내 영상만 수집
"""

import os
import json
import requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv
import math
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class WeeklyPokerAnalyzer:
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
        
        self.videos = []
        
        # 1주일 전 날짜 계산
        self.one_week_ago = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
    
    def collect_weekly_poker_videos(self):
        """1주일 이내의 poker 비디오 10개 수집"""
        print(f"[1/4] 최근 1주일 이내 'poker' 비디오 수집 중...")
        print(f"검색 기간: {self.one_week_ago[:10]} ~ {datetime.now().strftime('%Y-%m-%d')}")
        
        try:
            # YouTube 검색 - publishedAfter 파라미터 추가
            search_response = self.youtube.search().list(
                q='poker',
                part='id,snippet',
                maxResults=10,
                order='relevance',
                type='video',
                regionCode='US',
                relevanceLanguage='en',
                publishedAfter=self.one_week_ago  # 1주일 이내만
            ).execute()
            
            if not search_response.get('items'):
                print("⚠️ 최근 1주일 이내 비디오가 없습니다.")
                return False
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # 비디오 상세 정보
            videos_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # 데이터 추출 및 정량 지표 계산
            for video in videos_response['items']:
                view_count = int(video['statistics'].get('viewCount', 0))
                like_count = int(video['statistics'].get('likeCount', 0))
                comment_count = int(video['statistics'].get('commentCount', 0))
                
                # 게시 시간 계산
                published_at = video['snippet']['publishedAt']
                published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(published_date.tzinfo) - published_date).days
                
                # 참여율 계산
                engagement_rate = ((like_count + comment_count) / view_count) if view_count > 0 else 0
                
                # 바이럴 점수 계산
                viral_score = self._calculate_viral_score(view_count, like_count, comment_count, engagement_rate)
                
                video_data = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'][:300],
                    'channel': video['snippet']['channelTitle'],
                    'channel_id': video['snippet']['channelId'],
                    'published_at': published_at,
                    'days_ago': days_ago,
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': engagement_rate,
                    'viral_score': viral_score,
                    'url': f"https://www.youtube.com/watch?v={video['id']}",
                    'thumbnail': video['snippet']['thumbnails']['medium']['url']
                }
                
                self.videos.append(video_data)
            
            print(f"✓ {len(self.videos)}개 비디오 수집 완료")
            return True
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            raise
    
    def _calculate_viral_score(self, views, likes, comments, engagement_rate):
        """바이럴 점수 계산"""
        if views == 0:
            return 0
        
        view_score = math.log10(views + 1) * 0.4
        engagement_score = engagement_rate * 1000 * 0.3
        like_score = math.log10(likes + 1) * 0.2
        comment_score = math.log10(comments + 1) * 0.1
        
        return view_score + engagement_score + like_score + comment_score
    
    def analyze_weekly_trends(self):
        """주간 트렌드 분석"""
        print("\n[2/4] 주간 데이터 분석 중...")
        
        # 전체 통계
        total_views = sum(v['view_count'] for v in self.videos)
        total_likes = sum(v['like_count'] for v in self.videos)
        total_comments = sum(v['comment_count'] for v in self.videos)
        avg_engagement = sum(v['engagement_rate'] for v in self.videos) / len(self.videos) if self.videos else 0
        
        # 정렬
        videos_by_viral = sorted(self.videos, key=lambda x: x['viral_score'], reverse=True)
        videos_by_engagement = sorted(self.videos, key=lambda x: x['engagement_rate'], reverse=True)
        videos_by_recent = sorted(self.videos, key=lambda x: x['days_ago'])
        
        # 채널별 통계
        channel_stats = {}
        for video in self.videos:
            channel = video['channel']
            if channel not in channel_stats:
                channel_stats[channel] = []
            channel_stats[channel].append(video)
        
        self.analysis = {
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_engagement': avg_engagement,
            'top_viral': videos_by_viral[:3],
            'top_engagement': videos_by_engagement[:3],
            'most_recent': videos_by_recent[:3],
            'channel_stats': channel_stats,
            'all_videos': self.videos
        }
        
        print("✓ 분석 완료")
        return self.analysis
    
    def generate_weekly_insights(self):
        """주간 AI 인사이트 생성"""
        print("\n[3/4] AI 주간 트렌드 분석 중...")
        
        # 프롬프트 준비
        video_summaries = []
        for i, video in enumerate(self.videos, 1):
            summary = f"{i}. {video['title']} ({video['channel']}) - {video['days_ago']}일 전, 조회수: {video['view_count']:,}, 참여율: {video['engagement_rate']*100:.2f}%"
            video_summaries.append(summary)
        
        prompt = f"""
다음은 최근 1주일간 YouTube에 업로드된 포커 관련 비디오 10개입니다:

{chr(10).join(video_summaries)}

이 주간 데이터를 바탕으로:
1. 이번 주 가장 뜨거운 포커 트렌드 2가지
2. 채널별 콘텐츠 전략의 차이점
3. 다음 주에 만들면 좋을 콘텐츠 아이디어 2가지

간결하게 분석해주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            self.ai_insights = response.text
            print("✓ AI 분석 완료")
            return self.ai_insights
        except Exception as e:
            print(f"AI 분석 오류: {str(e)}")
            self.ai_insights = "AI 분석을 생성할 수 없습니다."
            return self.ai_insights
    
    def send_weekly_report_to_slack(self):
        """주간 리포트 슬랙 전송"""
        print("\n[4/4] 주간 리포트 슬랙 전송 중...")
        
        if not self.videos:
            print("전송할 데이터가 없습니다.")
            return False
        
        # 메시지 구성
        top_viral = self.analysis['top_viral'][0] if self.analysis['top_viral'] else None
        most_recent = self.analysis['most_recent'][0] if self.analysis['most_recent'] else None
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📅 주간 포커 트렌드 분석 ({datetime.now().strftime('%m/%d')} 기준)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 최근 1주일 통계 ({len(self.videos)}개 비디오)*\n"
                                f"• 총 조회수: *{self.analysis['total_views']:,}*\n"
                                f"• 총 좋아요: *{self.analysis['total_likes']:,}*\n"
                                f"• 평균 참여율: *{self.analysis['avg_engagement']*100:.2f}%*\n"
                                f"• 분석 기간: {self.one_week_ago[:10]} ~ {datetime.now().strftime('%Y-%m-%d')}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        
        # 최신 업로드 섹션
        if most_recent:
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🆕 가장 최근 업로드*\n"
                            f"<{most_recent['url']}|{most_recent['title'][:50]}...>\n"
                            f"🎬 {most_recent['channel']} • {most_recent['days_ago']}일 전\n"
                            f"👀 {most_recent['view_count']:,} views"
                }
            })
        
        # TOP 3 바이럴 비디오
        message['blocks'].extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 주간 TOP 3 바이럴 비디오*"
                }
            }
        ])
        
        for i, video in enumerate(self.analysis['top_viral'][:3], 1):
            title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
            linked_title = f"<{video['url']}|{title}>"
            
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {linked_title}*\n"
                            f"🎬 {video['channel']} • {video['days_ago']}일 전\n"
                            f"📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,}\n"
                            f"📈 참여율: {video['engagement_rate']*100:.1f}% | 🔥 바이럴: {video['viral_score']:.1f}"
                },
                "accessory": {
                    "type": "image",
                    "image_url": video['thumbnail'],
                    "alt_text": video['title']
                }
            })
        
        # 채널별 활동
        channel_count = len(self.analysis['channel_stats'])
        message['blocks'].extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📺 주간 활발한 채널*\n"
                            f"이번 주 {channel_count}개 채널이 포커 콘텐츠 업로드\n\n" +
                            "\n".join([f"• *{ch}*: {len(vids)}개" 
                                     for ch, vids in sorted(self.analysis['channel_stats'].items(), 
                                                          key=lambda x: len(x[1]), reverse=True)[:3]])
                }
            }
        ])
        
        # AI 인사이트
        if hasattr(self, 'ai_insights'):
            message['blocks'].extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🤖 AI 주간 트렌드 분석*\n{self.ai_insights[:600]}"
                    }
                }
            ])
        
        # 푸터
        message['blocks'].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📌 _최근 1주일 이내 업로드된 영상만 분석 • 제목 클릭 시 YouTube 재생_"
                }
            ]
        })
        
        # 슬랙 전송
        try:
            response = requests.post(self.slack_webhook_url, json=message)
            if response.status_code == 200:
                print("✓ 슬랙 전송 완료!")
                return True
            else:
                print(f"슬랙 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"슬랙 전송 오류: {str(e)}")
            return False
    
    def display_console_summary(self):
        """콘솔 요약 표시"""
        print("\n" + "="*80)
        print("📊 주간 분석 요약")
        print("="*80)
        
        print(f"\n【주간 통계】")
        print(f"분석 기간: {self.one_week_ago[:10]} ~ {datetime.now().strftime('%Y-%m-%d')}")
        print(f"수집 비디오: {len(self.videos)}개")
        print(f"총 조회수: {self.analysis['total_views']:,}")
        print(f"평균 참여율: {self.analysis['avg_engagement']*100:.2f}%")
        
        print(f"\n【TOP 3 바이럴】")
        for i, video in enumerate(self.analysis['top_viral'][:3], 1):
            print(f"\n{i}. {video['title'][:60]}...")
            print(f"   채널: {video['channel']}")
            print(f"   {video['days_ago']}일 전 업로드")
            print(f"   조회수: {video['view_count']:,} | 참여율: {video['engagement_rate']*100:.1f}%")

def main():
    print("="*80)
    print("주간 포커 트렌드 분석 (최근 1주일)")
    print("="*80)
    
    analyzer = WeeklyPokerAnalyzer()
    
    try:
        # 1. 주간 비디오 수집
        if analyzer.collect_weekly_poker_videos():
            # 2. 데이터 분석
            analyzer.analyze_weekly_trends()
            
            # 3. AI 인사이트 생성
            analyzer.generate_weekly_insights()
            
            # 4. 콘솔 요약
            analyzer.display_console_summary()
            
            # 5. 슬랙 전송
            analyzer.send_weekly_report_to_slack()
            
            print("\n✅ 주간 분석 완료!")
        else:
            print("\n⚠️ 수집할 데이터가 없습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()