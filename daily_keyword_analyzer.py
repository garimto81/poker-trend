#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일간 키워드 기반 포커 트렌드 분석기
- 검색 키워드 명시
- 조회수 상위 10개 추출
- 최근 24시간 필터
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

class DailyKeywordAnalyzer:
    def __init__(self, search_keyword='poker'):
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
        
        self.search_keyword = search_keyword
        self.videos = []
    
    def collect_daily_videos(self):
        """24시간 이내 비디오 수집 후 조회수 상위 10개 추출"""
        print(f"\n[1/4] '{self.search_keyword}' 키워드로 최근 24시간 비디오 검색 중...")
        
        # 24시간 전 시간
        time_filter = (datetime.utcnow() - timedelta(hours=24)).isoformat() + 'Z'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        print(f"검색 기간: 최근 24시간 ({current_time} 기준)")
        print(f"검색 키워드: {self.search_keyword}")
        
        try:
            # YouTube 검색 - 더 많이 가져온 후 상위 10개 선택
            search_response = self.youtube.search().list(
                q=self.search_keyword,
                part='id,snippet',
                maxResults=50,  # 50개 가져온 후 필터링
                order='relevance',
                type='video',
                regionCode='US',
                relevanceLanguage='en',
                publishedAfter=time_filter
            ).execute()
            
            if not search_response.get('items'):
                print(f"⚠️ '{self.search_keyword}' 키워드로 최근 24시간 내 비디오가 없습니다.")
                return False
            
            print(f"✓ {len(search_response['items'])}개 비디오 발견")
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # 비디오 상세 정보 가져오기
            videos_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # 모든 비디오 데이터 수집
            all_videos = []
            for video in videos_response['items']:
                view_count = int(video['statistics'].get('viewCount', 0))
                like_count = int(video['statistics'].get('likeCount', 0))
                comment_count = int(video['statistics'].get('commentCount', 0))
                
                # 게시 시간 계산
                published_at = video['snippet']['publishedAt']
                published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_ago = int((datetime.now(published_date.tzinfo) - published_date).total_seconds() / 3600)
                
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
                    'hours_ago': hours_ago,
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': engagement_rate,
                    'viral_score': viral_score,
                    'url': f"https://www.youtube.com/watch?v={video['id']}",
                    'thumbnail': video['snippet']['thumbnails']['medium']['url']
                }
                
                all_videos.append(video_data)
            
            # 조회수 기준 상위 10개 선택
            self.videos = sorted(all_videos, key=lambda x: x['view_count'], reverse=True)[:10]
            
            print(f"✓ 조회수 상위 10개 비디오 선택 완료")
            print(f"  - 최고 조회수: {self.videos[0]['view_count']:,}")
            print(f"  - 10위 조회수: {self.videos[9]['view_count']:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
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
    
    def analyze_daily_trends(self):
        """일간 트렌드 분석"""
        print("\n[2/4] 수집된 데이터 분석 중...")
        
        # 전체 통계
        total_views = sum(v['view_count'] for v in self.videos)
        total_likes = sum(v['like_count'] for v in self.videos)
        total_comments = sum(v['comment_count'] for v in self.videos)
        avg_engagement = sum(v['engagement_rate'] for v in self.videos) / len(self.videos)
        
        # 시간대별 분포
        hour_distribution = {}
        for video in self.videos:
            hour = video['hours_ago'] // 6  # 6시간 단위로 그룹화
            hour_group = f"{hour*6}-{(hour+1)*6}시간 전"
            hour_distribution[hour_group] = hour_distribution.get(hour_group, 0) + 1
        
        # 채널별 통계
        channel_stats = {}
        for video in self.videos:
            channel = video['channel']
            if channel not in channel_stats:
                channel_stats[channel] = []
            channel_stats[channel].append(video)
        
        self.analysis = {
            'search_keyword': self.search_keyword,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_engagement': avg_engagement,
            'hour_distribution': hour_distribution,
            'channel_stats': channel_stats,
            'top_by_views': self.videos[:3],
            'top_by_engagement': sorted(self.videos, key=lambda x: x['engagement_rate'], reverse=True)[:3],
            'top_by_viral': sorted(self.videos, key=lambda x: x['viral_score'], reverse=True)[:3]
        }
        
        print("✓ 분석 완료")
        return self.analysis
    
    def generate_ai_insights(self):
        """AI 인사이트 생성"""
        print("\n[3/4] AI 트렌드 분석 중...")
        
        # 프롬프트 준비
        video_summaries = []
        for i, video in enumerate(self.videos, 1):
            summary = f"{i}. {video['title']} - {video['channel']} ({video['hours_ago']}시간 전)"
            summary += f"\n   조회수: {video['view_count']:,}, 좋아요: {video['like_count']:,}, 참여율: {video['engagement_rate']*100:.2f}%"
            video_summaries.append(summary)
        
        prompt = f"""
다음은 '{self.search_keyword}' 키워드로 검색한 최근 24시간 내 YouTube 비디오 중 조회수 상위 10개입니다:

{chr(10).join(video_summaries)}

이 데이터를 바탕으로 간결하게 분석해주세요:
1. 현재 가장 주목받는 콘텐츠 유형 (1-2문장)
2. 높은 조회수를 얻는 비디오의 특징 (1-2문장)
3. 오늘 만들면 좋을 콘텐츠 아이디어 1개
"""
        
        try:
            response = self.model.generate_content(prompt)
            self.ai_insights = response.text
            print("✓ AI 분석 완료")
            return self.ai_insights
        except Exception as e:
            print(f"⚠️ AI 분석 실패: {str(e)}")
            self.ai_insights = "AI 분석을 생성할 수 없습니다."
            return self.ai_insights
    
    def send_to_slack(self):
        """슬랙으로 일간 리포트 전송"""
        print("\n[4/4] 슬랙으로 전송 중...")
        
        # 상위 3개 비디오
        top_3_views = self.analysis['top_by_views']
        
        # 메시지 구성
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 일간 포커 트렌드 분석 - {datetime.now().strftime('%m/%d %H시')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔍 검색 키워드: `{self.search_keyword}`*\n"
                                f"*📅 검색 기간: 최근 24시간 ({datetime.now().strftime('%m/%d %H:%M')} 기준)*\n"
                                f"*📌 분석 방법: 조회수 상위 10개 비디오*"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 전체 통계 (조회수 TOP 10)*\n"
                                f"• 총 조회수: *{self.analysis['total_views']:,}*\n"
                                f"• 총 좋아요: *{self.analysis['total_likes']:,}*\n"
                                f"• 총 댓글: *{self.analysis['total_comments']:,}*\n"
                                f"• 평균 참여율: *{self.analysis['avg_engagement']*100:.2f}%*\n"
                                f"  _→ 참여율 = (좋아요 + 댓글) ÷ 조회수 × 100_"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*👀 조회수 TOP 3*"
                    }
                }
            ]
        }
        
        # TOP 3 비디오 (조회수 기준)
        for i, video in enumerate(top_3_views, 1):
            title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
            linked_title = f"<{video['url']}|{title}>"
            
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {linked_title}*\n"
                            f"🎬 {video['channel']} • {video['hours_ago']}시간 전\n"
                            f"📊 조회: *{video['view_count']:,}* | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,} | 📈 {video['engagement_rate']*100:.1f}%"
                }
            })
        
        # 참여율 TOP 1
        top_engagement = self.analysis['top_by_engagement'][0]
        if top_engagement not in top_3_views:  # 중복 방지
            message['blocks'].extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💎 최고 참여율 비디오*\n"
                                f"<{top_engagement['url']}|{top_engagement['title'][:50]}...>\n"
                                f"참여율: *{top_engagement['engagement_rate']*100:.1f}%* | 조회: {top_engagement['view_count']:,}"
                    }
                }
            ])
        
        # 시간대별 분포
        if self.analysis['hour_distribution']:
            time_text = " / ".join([f"{k}: {v}개" for k, v in sorted(self.analysis['hour_distribution'].items())])
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⏰ 업로드 시간 분포*\n{time_text}"
                }
            })
        
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
                        "text": f"*🤖 AI 분석*\n{self.ai_insights}"
                    }
                }
            ])
        
        # 푸터
        message['blocks'].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_검색어: {self.search_keyword} | 조회수 상위 10개 분석 | 최근 24시간_"
                }
            ]
        })
        
        # 슬랙 전송
        try:
            response = requests.post(self.slack_webhook_url, json=message)
            if response.status_code == 200:
                print("✅ 슬랙 전송 완료!")
                return True
            else:
                print(f"❌ 슬랙 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 슬랙 전송 오류: {str(e)}")
            return False
    
    def display_console_summary(self):
        """콘솔에 요약 표시"""
        print("\n" + "="*80)
        print(f"📊 일간 분석 요약 - '{self.search_keyword}'")
        print("="*80)
        
        print(f"\n【검색 정보】")
        print(f"키워드: {self.search_keyword}")
        print(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"분석 기간: 최근 24시간")
        
        print(f"\n【전체 통계】")
        print(f"분석 비디오: 조회수 상위 10개")
        print(f"총 조회수: {self.analysis['total_views']:,}")
        print(f"총 좋아요: {self.analysis['total_likes']:,}")
        print(f"평균 참여율: {self.analysis['avg_engagement']*100:.2f}%")
        
        print(f"\n【조회수 TOP 3】")
        for i, video in enumerate(self.analysis['top_by_views'], 1):
            print(f"\n{i}. {video['title'][:60]}...")
            print(f"   채널: {video['channel']}")
            print(f"   {video['hours_ago']}시간 전 업로드")
            print(f"   조회수: {video['view_count']:,} | 좋아요: {video['like_count']:,} | 참여율: {video['engagement_rate']*100:.1f}%")

def main():
    print("="*80)
    print("일간 키워드 기반 포커 트렌드 분석")
    print("="*80)
    
    # 검색 키워드 입력 (기본값: poker)
    keyword = input("\n검색 키워드를 입력하세요 (기본값: poker): ").strip()
    if not keyword:
        keyword = 'poker'
    
    analyzer = DailyKeywordAnalyzer(search_keyword=keyword)
    
    try:
        # 1. 비디오 수집 (24시간 이내, 조회수 상위 10개)
        if analyzer.collect_daily_videos():
            # 2. 데이터 분석
            analyzer.analyze_daily_trends()
            
            # 3. AI 인사이트 생성
            analyzer.generate_ai_insights()
            
            # 4. 콘솔 요약
            analyzer.display_console_summary()
            
            # 5. 슬랙 전송
            analyzer.send_to_slack()
            
            print("\n✅ 일간 분석 완료!")
        else:
            print("\n⚠️ 분석할 데이터가 없습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()