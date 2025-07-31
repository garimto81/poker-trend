#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다중 키워드 포커 트렌드 분석기
- 8개 키워드 검색
- 중복 제거
- Gemini AI로 포커 관련 콘텐츠 필터링
- TOP 5 표시
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

class MultiKeywordPokerAnalyzer:
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
        
        # 검색 키워드
        self.search_keywords = [
            "Texas Holdem",
            "Holdem", 
            "Poker",
            "WSOP",
            "Triton Poker",
            "Pokerstars",
            "WPT",
            "Poker tournament"
        ]
        
        self.all_videos = []
        self.unique_videos = {}
        self.poker_related_videos = []
        
    def collect_videos_by_keyword(self):
        """각 키워드별로 YouTube 비디오 수집"""
        print(f"\n[1/5] 다중 키워드로 YouTube 비디오 수집 중...")
        print(f"📌 검색 필터: 오늘 (최근 24시간)")
        print(f"🔍 검색 키워드:")
        for i, keyword in enumerate(self.search_keywords, 1):
            print(f"   {i}. {keyword}")
        
        # 24시간 전 시간 설정
        time_filter = (datetime.now() - timedelta(hours=24)).isoformat() + 'Z'
        print(f"\n⏰ 검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준 24시간 이내")
        
        total_api_calls = 0
        
        for keyword in self.search_keywords:
            print(f"\n'{keyword}' 검색 중...")
            
            try:
                # YouTube 검색 - 조회수 순, 24시간 이내
                search_response = self.youtube.search().list(
                    q=keyword,
                    part='snippet',
                    maxResults=10,
                    order='viewCount',
                    type='video',
                    publishedAfter=time_filter
                ).execute()
                
                total_api_calls += 1
                
                if not search_response.get('items'):
                    print(f"  └─ 결과 없음")
                    continue
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                # 비디오 상세 정보 가져오기
                videos_response = self.youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids)
                ).execute()
                
                total_api_calls += 1
                
                # 키워드별 비디오 처리
                keyword_videos = 0
                for video in videos_response['items']:
                    video_id = video['id']
                    
                    # 중복 체크
                    if video_id not in self.unique_videos:
                        view_count = int(video['statistics'].get('viewCount', 0))
                        like_count = int(video['statistics'].get('likeCount', 0))
                        comment_count = int(video['statistics'].get('commentCount', 0))
                        
                        # 참여율 계산
                        engagement_rate = ((like_count + comment_count) / view_count) if view_count > 0 else 0
                        
                        # 바이럴 점수 계산
                        viral_score = self._calculate_viral_score(view_count, like_count, comment_count, engagement_rate)
                        
                        video_data = {
                            'video_id': video_id,
                            'title': video['snippet']['title'],
                            'description': video['snippet']['description'][:500],
                            'channel': video['snippet']['channelTitle'],
                            'published_at': video['snippet']['publishedAt'],
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'engagement_rate': engagement_rate,
                            'viral_score': viral_score,
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                            'search_keyword': keyword,
                            'keywords_found': [keyword]
                        }
                        
                        self.unique_videos[video_id] = video_data
                        keyword_videos += 1
                    else:
                        # 이미 있는 비디오에 키워드 추가
                        self.unique_videos[video_id]['keywords_found'].append(keyword)
                
                print(f"  └─ {keyword_videos}개 고유 비디오 수집")
                
            except Exception as e:
                print(f"  └─ 오류 발생: {str(e)}")
        
        print(f"\n총 API 호출 횟수: {total_api_calls}")
        print(f"총 고유 비디오 수: {len(self.unique_videos)}")
        
        # 딕셔너리를 리스트로 변환
        self.all_videos = list(self.unique_videos.values())
        
        return len(self.all_videos) > 0
    
    def _calculate_viral_score(self, views, likes, comments, engagement_rate):
        """바이럴 점수 계산"""
        if views == 0:
            return 0
        
        view_score = math.log10(views + 1) * 0.4
        engagement_score = engagement_rate * 1000 * 0.3
        like_score = math.log10(likes + 1) * 0.2
        comment_score = math.log10(comments + 1) * 0.1
        
        return view_score + engagement_score + like_score + comment_score
    
    def filter_poker_content(self):
        """Gemini AI로 포커 관련 콘텐츠 필터링"""
        print(f"\n[2/5] AI로 포커 관련 콘텐츠 필터링 중...")
        
        # 배치 처리를 위해 비디오 정보 준비
        batch_size = 10
        filtered_videos = []
        
        for i in range(0, len(self.all_videos), batch_size):
            batch = self.all_videos[i:i + batch_size]
            
            # 프롬프트 준비
            video_list = []
            for idx, video in enumerate(batch, start=i+1):
                video_list.append(
                    f"{idx}. 제목: {video['title']}\n"
                    f"   채널: {video['channel']}\n"
                    f"   설명: {video['description'][:200]}..."
                )
            
            prompt = f"""
다음은 YouTube 비디오 목록입니다. 각 비디오가 실제 포커 게임, 전략, 토너먼트, 플레이어와 관련된 콘텐츠인지 판단해주세요.

{chr(10).join(video_list)}

각 비디오 번호에 대해 다음 형식으로 답변해주세요:
- 포커 관련 콘텐츠인 경우: "번호: YES - 간단한 이유"
- 포커와 무관한 경우: "번호: NO"

판단 기준:
- 실제 포커 게임플레이, 전략, 토너먼트, 선수 관련 콘텐츠는 YES
- 단순히 제목에 poker가 있지만 다른 주제(음악, 영화 등)인 경우 NO
"""
            
            try:
                response = self.model.generate_content(prompt)
                result_text = response.text
                
                # 결과 파싱
                for idx, video in enumerate(batch, start=i+1):
                    # 번호에 해당하는 라인 찾기
                    found = False
                    for line in result_text.split('\n'):
                        if line.strip().startswith(f"{idx}:"):
                            if "YES" in line.upper():
                                video['ai_filter_reason'] = line.split('-', 1)[1].strip() if '-' in line else "포커 관련"
                                filtered_videos.append(video)
                                found = True
                                break
                    # 디버그: AI가 어떤 판단을 했는지 확인
                    if not found and i == 0 and idx <= i + 3:  # 첫 배치의 처음 3개만 출력
                        print(f"     디버그: {video['title'][:50]}... → AI 필터링됨")
                
                print(f"  └─ {i+1}-{min(i+batch_size, len(self.all_videos))} 처리 완료")
                
            except Exception as e:
                print(f"  └─ AI 필터링 오류: {str(e)}")
                print(f"  └─ 오류 발생한 배치를 모두 포함합니다.")
                # 오류 시 배치 전체 포함
                for video in batch:
                    video['ai_filter_reason'] = "AI 필터링 오류로 포함"
                filtered_videos.extend(batch)
        
        self.poker_related_videos = filtered_videos
        print(f"\n필터링 결과: {len(self.all_videos)}개 → {len(self.poker_related_videos)}개 (모든 포커 콘텐츠 유지)")
        
        return len(self.poker_related_videos) > 0
    
    def analyze_trends(self):
        """필터링된 데이터로 트렌드 분석"""
        print(f"\n[3/5] 트렌드 분석 중...")
        
        # 조회수 기준 TOP 5 선정
        self.top_videos = sorted(self.poker_related_videos, key=lambda x: x['view_count'], reverse=True)[:5]
        
        # 전체 통계
        total_views = sum(v['view_count'] for v in self.poker_related_videos)
        total_likes = sum(v['like_count'] for v in self.poker_related_videos)
        total_comments = sum(v['comment_count'] for v in self.poker_related_videos)
        avg_engagement = sum(v['engagement_rate'] for v in self.poker_related_videos) / len(self.poker_related_videos) if self.poker_related_videos else 0
        
        # 키워드별 통계
        keyword_stats = {}
        for video in self.poker_related_videos:
            for kw in video['keywords_found']:
                if kw not in keyword_stats:
                    keyword_stats[kw] = {'count': 0, 'total_views': 0, 'avg_engagement': 0, 'videos': []}
                keyword_stats[kw]['count'] += 1
                keyword_stats[kw]['total_views'] += video['view_count']
                keyword_stats[kw]['videos'].append(video['title'][:50])
        
        # 키워드별 평균 참여율 계산
        for kw in keyword_stats:
            kw_videos = [v for v in self.poker_related_videos if kw in v['keywords_found']]
            keyword_stats[kw]['avg_engagement'] = sum(v['engagement_rate'] for v in kw_videos) / len(kw_videos) if kw_videos else 0
        
        # 채널별 통계
        channel_stats = {}
        for video in self.poker_related_videos:
            channel = video['channel']
            if channel not in channel_stats:
                channel_stats[channel] = {'count': 0, 'total_views': 0, 'avg_engagement': 0}
            channel_stats[channel]['count'] += 1
            channel_stats[channel]['total_views'] += video['view_count']
        
        # 채널별 평균 참여율 계산
        for channel in channel_stats:
            ch_videos = [v for v in self.poker_related_videos if v['channel'] == channel]
            channel_stats[channel]['avg_engagement'] = sum(v['engagement_rate'] for v in ch_videos) / len(ch_videos) if ch_videos else 0
        
        self.analysis = {
            'total_videos': len(self.poker_related_videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_engagement': avg_engagement,
            'keyword_stats': keyword_stats,
            'channel_stats': channel_stats,
            'top_videos': self.top_videos
        }
        
        print(f"✓ 전체 {len(self.poker_related_videos)}개 포커 콘텐츠 분석 완료")
        return self.analysis
    
    def generate_ai_insights(self):
        """AI 최종 트렌드 인사이트 생성"""
        print(f"\n[4/5] AI 최종 트렌드 분석 중...")
        
        if not self.top_videos:
            self.ai_insights = "분석할 비디오가 없습니다."
            return self.ai_insights
        
        # TOP 5 비디오 정보 준비
        top_5_summary = []
        for i, video in enumerate(self.top_videos, 1):
            summary = (
                f"{i}. {video['title']} - {video['channel']}\n"
                f"   조회수: {video['view_count']:,} | 좋아요: {video['like_count']:,} | "
                f"참여율: {video['engagement_rate']*100:.2f}%\n"
                f"   검색 키워드: {', '.join(video['keywords_found'])}"
            )
            top_5_summary.append(summary)
        
        # 키워드 통계 요약
        keyword_summary = []
        for kw, stats in sorted(self.analysis['keyword_stats'].items(), key=lambda x: x[1]['total_views'], reverse=True)[:5]:
            keyword_summary.append(f"- {kw}: {stats['count']}개 비디오, 총 {stats['total_views']:,}회 조회")
        
        prompt = f"""
다음은 포커 관련 YouTube 콘텐츠 분석 결과입니다.

【TOP 5 비디오】
{chr(10).join(top_5_summary)}

【키워드별 성과】
{chr(10).join(keyword_summary)}

【전체 통계】
- 총 포커 비디오: {self.analysis['total_videos']}개
- 총 조회수: {self.analysis['total_views']:,}
- 평균 참여율: {self.analysis['avg_engagement']*100:.2f}%

위 데이터를 바탕으로 다음을 분석해주세요:
1. 현재 포커 콘텐츠의 주요 트렌드 (2-3문장)
2. 가장 인기 있는 콘텐츠 유형과 특징 (2-3문장)
3. 성공적인 포커 콘텐츠 제작을 위한 전략 제안 (2-3개)
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
        """슬랙으로 분석 결과 전송"""
        print(f"\n[5/5] 슬랙으로 전송 중...")
        
        # 메시지 구성
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 포커 트렌드 종합 분석 - {datetime.now().strftime('%m/%d %H:%M')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📌 검색 필터*: 오늘 (최근 24시간)\n"
                                f"*📊 분석 결과*: {len(self.unique_videos)}개 수집 → {len(self.poker_related_videos)}개 포커 콘텐츠 (AI 필터링)\n"
                                f"*🏆 표시*: 조회수 기준 TOP 5"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*🔍 검색 키워드 ({len(self.search_keywords)}개)*\n```{chr(10).join(['• ' + kw for kw in self.search_keywords])}```"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📈 전체 통계*\n"
                                f"• 총 조회수: *{self.analysis['total_views']:,}*\n"
                                f"• 총 좋아요: *{self.analysis['total_likes']:,}*\n"
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
                        "text": "*🏆 조회수 TOP 5*"
                    }
                }
            ]
        }
        
        # TOP 5 비디오
        for i, video in enumerate(self.top_videos, 1):
            title = video['title'][:80] + "..." if len(video['title']) > 80 else video['title']
            linked_title = f"<{video['url']}|{title}>"
            
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {linked_title}*\n"
                            f"🎬 {video['channel']}\n"
                            f"📊 조회: *{video['view_count']:,}* | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,} | 📈 {video['engagement_rate']*100:.1f}%\n"
                            f"🔍 키워드: {', '.join(video['keywords_found'])}"
                }
            })
        
        # 키워드별 성과
        keyword_text = []
        for kw, stats in sorted(self.analysis['keyword_stats'].items(), key=lambda x: x[1]['total_views'], reverse=True)[:5]:
            keyword_text.append(f"• *{kw}*: {stats['count']}개 비디오")
        
        if keyword_text:
            message['blocks'].extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📌 키워드별 포커 콘텐츠 수*\n" + "\n".join(keyword_text)
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
                        "text": f"*🤖 AI 트렌드 분석*\n{self.ai_insights}"
                    }
                }
            ])
        
        # 푸터
        message['blocks'].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_최근 24시간 | 다중 키워드 검색 | 중복 제거 | AI 필터링 | {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준_"
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
        print(f"📊 포커 트렌드 종합 분석 요약")
        print("="*80)
        
        print(f"\n【검색 정보】")
        print(f"📌 검색 필터: 오늘 (최근 24시간)")
        print(f"🔍 검색 키워드 ({len(self.search_keywords)}개):")
        for kw in self.search_keywords:
            print(f"   • {kw}")
        print(f"\n📊 분석 결과:")
        print(f"   수집 비디오: {len(self.unique_videos)}개")
        print(f"   포커 콘텐츠: {len(self.poker_related_videos)}개 (AI 필터링)")
        
        print(f"\n【전체 통계】")
        print(f"총 조회수: {self.analysis['total_views']:,}")
        print(f"총 좋아요: {self.analysis['total_likes']:,}")
        print(f"평균 참여율: {self.analysis['avg_engagement']*100:.2f}%")
        
        print(f"\n【키워드별 성과】")
        for kw, stats in sorted(self.analysis['keyword_stats'].items(), key=lambda x: x[1]['total_views'], reverse=True)[:5]:
            print(f"{kw}: {stats['count']}개 비디오, {stats['total_views']:,}회 조회, 평균 참여율 {stats['avg_engagement']*100:.2f}%")
        
        print(f"\n【채널별 성과】")
        for ch, stats in sorted(self.analysis['channel_stats'].items(), key=lambda x: x[1]['total_views'], reverse=True)[:5]:
            print(f"{ch}: {stats['count']}개 비디오, {stats['total_views']:,}회 조회")
        
        print(f"\n【조회수 TOP 5 상세 정보】")
        for i, video in enumerate(self.top_videos, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   채널: {video['channel']}")
            print(f"   조회수: {video['view_count']:,}")
            print(f"   좋아요: {video['like_count']:,}")
            print(f"   댓글: {video['comment_count']:,}")
            print(f"   참여율: {video['engagement_rate']*100:.2f}%")
            print(f"   바이럴 점수: {video['viral_score']:.2f}")
            print(f"   키워드: {', '.join(video['keywords_found'])}")
            print(f"   업로드: {video['published_at'][:10]}")

def main():
    print("="*80)
    print("다중 키워드 포커 트렌드 분석")
    print("="*80)
    
    analyzer = MultiKeywordPokerAnalyzer()
    
    try:
        # 1. 다중 키워드로 비디오 수집
        if analyzer.collect_videos_by_keyword():
            # 2. AI로 포커 관련 콘텐츠 필터링
            if analyzer.filter_poker_content():
                # 3. 트렌드 분석
                analyzer.analyze_trends()
                
                # 4. AI 최종 인사이트 생성
                analyzer.generate_ai_insights()
                
                # 5. 콘솔 요약
                analyzer.display_console_summary()
                
                # 6. 슬랙 전송
                analyzer.send_to_slack()
                
                print("\n✅ 분석 완료!")
            else:
                print("\n⚠️ 포커 관련 콘텐츠를 찾을 수 없습니다.")
        else:
            print("\n⚠️ 비디오를 수집할 수 없습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()