#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poker 키워드 10개 비디오 분석 및 슬랙 공유
API 할당량 절약을 위한 최소 버전
"""

import os
import json
import requests
from datetime import datetime
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

class PokerMiniAnalyzer:
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
    
    def collect_poker_videos(self):
        """poker 키워드로 10개 비디오 수집"""
        print("[1/4] YouTube에서 'poker' 비디오 수집 중...")
        
        try:
            # YouTube 검색
            search_response = self.youtube.search().list(
                q='poker',
                part='id,snippet',
                maxResults=10,
                order='relevance',
                type='video',
                regionCode='US',
                relevanceLanguage='en'
            ).execute()
            
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
                
                # 참여율 계산
                engagement_rate = ((like_count + comment_count) / view_count) if view_count > 0 else 0
                
                # 바이럴 점수 계산
                viral_score = self._calculate_viral_score(view_count, like_count, comment_count, engagement_rate)
                
                video_data = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'][:300],
                    'channel': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': engagement_rate,
                    'viral_score': viral_score,
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                
                self.videos.append(video_data)
            
            print(f"✓ {len(self.videos)}개 비디오 수집 완료")
            
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
    
    def analyze_trends(self):
        """수집된 데이터 분석"""
        print("\n[2/4] 정량적 데이터 분석 중...")
        
        # 전체 통계
        total_views = sum(v['view_count'] for v in self.videos)
        total_likes = sum(v['like_count'] for v in self.videos)
        total_comments = sum(v['comment_count'] for v in self.videos)
        avg_engagement = sum(v['engagement_rate'] for v in self.videos) / len(self.videos)
        
        # 정렬
        videos_by_viral = sorted(self.videos, key=lambda x: x['viral_score'], reverse=True)
        videos_by_engagement = sorted(self.videos, key=lambda x: x['engagement_rate'], reverse=True)
        
        self.analysis = {
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_engagement': avg_engagement,
            'top_viral': videos_by_viral[:3],
            'top_engagement': videos_by_engagement[:3],
            'all_videos': self.videos
        }
        
        print("✓ 분석 완료")
        return self.analysis
    
    def generate_ai_insights(self):
        """Gemini AI로 트렌드 인사이트 생성"""
        print("\n[3/4] AI 트렌드 분석 중...")
        
        # 프롬프트 준비
        video_summaries = []
        for i, video in enumerate(self.videos, 1):
            summary = f"{i}. {video['title']} - 조회수: {video['view_count']:,}, 참여율: {video['engagement_rate']*100:.2f}%"
            video_summaries.append(summary)
        
        prompt = f"""
다음은 YouTube에서 'poker' 키워드로 검색한 최신 10개 비디오입니다:

{chr(10).join(video_summaries)}

이 데이터를 바탕으로:
1. 현재 가장 뜨거운 포커 트렌드 2가지
2. 시청자들이 가장 관심있어하는 콘텐츠 유형
3. 앞으로 만들면 좋을 콘텐츠 아이디어 2가지

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
    
    def send_to_slack(self):
        """슬랙으로 분석 결과 전송"""
        print("\n[4/4] 슬랙으로 전송 중...")
        
        # 메시지 구성
        top_viral = self.analysis['top_viral'][0]
        top_engagement = self.analysis['top_engagement'][0]
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 포커 트렌드 미니 분석 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 전체 통계 (10개 비디오)*\n"
                                f"• 총 조회수: {self.analysis['total_views']:,}\n"
                                f"• 총 좋아요: {self.analysis['total_likes']:,}\n"
                                f"• 평균 참여율: {self.analysis['avg_engagement']*100:.2f}%"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🏆 최고 바이럴 비디오*\n"
                                f"`{top_viral['title'][:60]}...`\n"
                                f"• 조회수: {top_viral['view_count']:,}\n"
                                f"• 좋아요: {top_viral['like_count']:,}\n"
                                f"• 댓글: {top_viral['comment_count']:,}\n"
                                f"• 참여율: {top_viral['engagement_rate']*100:.1f}%\n"
                                f"• 바이럴 점수: {top_viral['viral_score']:.1f}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💎 최고 참여율 비디오*\n"
                                f"`{top_engagement['title'][:60]}...`\n"
                                f"• 조회수: {top_engagement['view_count']:,}\n"
                                f"• 참여율: {top_engagement['engagement_rate']*100:.1f}%"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📈 TOP 5 비디오 (바이럴 점수 순)*"
                    }
                }
            ]
        }
        
        # TOP 5 비디오 추가
        for i, video in enumerate(self.analysis['top_viral'][:5], 1):
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{i}. *{video['title'][:50]}...*\n"
                            f"   📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,} | 📈 {video['engagement_rate']*100:.1f}%"
                }
            })
        
        # AI 인사이트 추가
        if hasattr(self, 'ai_insights'):
            message['blocks'].append({
                "type": "divider"
            })
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 AI 트렌드 분석*\n{self.ai_insights[:500]}"
                }
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
        """콘솔에 요약 표시"""
        print("\n" + "="*80)
        print("📊 분석 요약")
        print("="*80)
        
        print(f"\n【전체 통계】")
        print(f"총 조회수: {self.analysis['total_views']:,}")
        print(f"총 좋아요: {self.analysis['total_likes']:,}")
        print(f"평균 참여율: {self.analysis['avg_engagement']*100:.2f}%")
        
        print(f"\n【TOP 3 바이럴 비디오】")
        for i, video in enumerate(self.analysis['top_viral'][:3], 1):
            print(f"\n{i}. {video['title'][:60]}...")
            print(f"   조회수: {video['view_count']:,} | 좋아요: {video['like_count']:,} | 댓글: {video['comment_count']:,}")
            print(f"   참여율: {video['engagement_rate']*100:.1f}% | 바이럴: {video['viral_score']:.1f}")

def main():
    print("="*80)
    print("포커 미니 트렌드 분석 (10개 비디오)")
    print("="*80)
    
    analyzer = PokerMiniAnalyzer()
    
    try:
        # 1. 비디오 수집
        analyzer.collect_poker_videos()
        
        # 2. 데이터 분석
        analyzer.analyze_trends()
        
        # 3. AI 인사이트 생성
        analyzer.generate_ai_insights()
        
        # 4. 콘솔 요약
        analyzer.display_console_summary()
        
        # 5. 슬랙 전송
        analyzer.send_to_slack()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()