#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 포커 분석 데모 - 실제 구현 예시
"""

import json
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def demonstrate_weekly_analysis():
    """주간 분석 기능 시연"""
    
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    print("="*80)
    print("📅 주간 포커 트렌드 분석 시연")
    print("="*80)
    print("\n[실제 구현 시 작동 방식]")
    print("1. YouTube API에 publishedAfter 파라미터 추가")
    print("2. 최근 7일 이내 업로드된 영상만 수집")
    print("3. 업로드 시간별로 추가 분석 제공")
    print("4. 주간 트렌드 변화 추적")
    
    # 시뮬레이션 데이터 (실제로는 API에서 수집)
    simulated_weekly_data = {
        "period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
        "total_videos": 10,
        "videos": [
            {
                "title": "INSANE Poker Bluff at WSOP 2025!",
                "channel": "PokerGO",
                "days_ago": 1,
                "view_count": 45000,
                "like_count": 2800,
                "comment_count": 156,
                "engagement_rate": 0.066,
                "viral_score": 22.5,
                "url": "https://youtube.com/watch?v=example1"
            },
            {
                "title": "GTO vs Exploitative Play Explained",
                "channel": "Upswing Poker",
                "days_ago": 2,
                "view_count": 12000,
                "like_count": 890,
                "comment_count": 78,
                "engagement_rate": 0.081,
                "viral_score": 20.1,
                "url": "https://youtube.com/watch?v=example2"
            },
            {
                "title": "$100K Pot! High Stakes Cash Game",
                "channel": "Hustler Casino Live",
                "days_ago": 3,
                "view_count": 78000,
                "like_count": 3200,
                "comment_count": 245,
                "engagement_rate": 0.044,
                "viral_score": 19.8,
                "url": "https://youtube.com/watch?v=example3"
            }
        ],
        "insights": {
            "trending_topics": ["WSOP highlights", "GTO strategy content"],
            "active_channels": ["PokerGO", "Upswing Poker", "Hustler Casino Live"],
            "avg_engagement": 0.064,
            "total_views": 135000
        }
    }
    
    # 슬랙 메시지 구성
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📅 주간 포커 트렌드 분석 ({datetime.now().strftime('%m/%d')})"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 주간 통계 요약*\n"
                            f"• 분석 기간: {simulated_weekly_data['period']}\n"
                            f"• 신규 업로드: {simulated_weekly_data['total_videos']}개\n"
                            f"• 총 조회수: {simulated_weekly_data['insights']['total_views']:,}\n"
                            f"• 평균 참여율: {simulated_weekly_data['insights']['avg_engagement']*100:.1f}%"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 이번 주 TOP 3 바이럴 비디오*"
                }
            }
        ]
    }
    
    # TOP 3 비디오 추가
    for i, video in enumerate(simulated_weekly_data['videos'][:3], 1):
        linked_title = f"<{video['url']}|{video['title']}>"
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {linked_title}*\n"
                        f"🎬 {video['channel']} • {video['days_ago']}일 전\n"
                        f"📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video['comment_count']:,}\n"
                        f"📈 참여율: {video['engagement_rate']*100:.1f}% | 🔥 바이럴: {video['viral_score']:.1f}"
            }
        })
    
    # 주간 인사이트
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💡 주간 트렌드 인사이트*\n"
                        f"• 🔥 핫 토픽: {', '.join(simulated_weekly_data['insights']['trending_topics'])}\n"
                        f"• 📺 활발한 채널: {', '.join(simulated_weekly_data['insights']['active_channels'][:3])}\n"
                        f"• 📈 신규 업로드 평균 {video['days_ago']}일 내 {simulated_weekly_data['insights']['total_views']//simulated_weekly_data['total_videos']:,}회 조회"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎬 다음 주 콘텐츠 추천*\n"
                        "• WSOP 하이라이트 리액션 - 현재 가장 핫한 토픽\n"
                        "• GTO 기초 교육 콘텐츠 - 높은 참여율 예상\n"
                        "• 라이브 캐시게임 분석 - 꾸준한 조회수 확보"
            }
        }
    ])
    
    # 푸터
    message['blocks'].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "📌 _매주 월요일 오전 9시 자동 발송 • 최근 7일 이내 업로드만 분석_"
            }
        ]
    })
    
    # 슬랙 전송
    if slack_webhook_url:
        print("\n슬랙으로 주간 리포트 전송 중...")
        try:
            response = requests.post(slack_webhook_url, json=message)
            if response.status_code == 200:
                print("✅ 주간 리포트 슬랙 전송 완료!")
            else:
                print(f"❌ 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    # 콘솔 출력
    print("\n" + "="*80)
    print("📋 주간 분석 주요 기능")
    print("="*80)
    print("\n1. **시간 필터링**")
    print("   - publishedAfter 파라미터로 7일 이내만 수집")
    print("   - 각 영상의 업로드 경과 시간 표시")
    print("\n2. **주간 특화 분석**")
    print("   - 이번 주 새로 떠오른 채널")
    print("   - 주간 평균 대비 높은 성과 비디오")
    print("   - 요일별 업로드 패턴")
    print("\n3. **트렌드 속도 측정**")
    print("   - 업로드 후 조회수 증가 속도")
    print("   - 초기 참여율 vs 현재 참여율")
    print("\n4. **실시간성 강화**")
    print("   - 24시간 이내 핫 비디오 별도 표시")
    print("   - 급상승 중인 영상 알림")
    
    print("\n💡 실제 구현 시 코드 예시:")
    print("""
# YouTube API 호출 시
search_response = youtube.search().list(
    q='poker',
    part='id,snippet',
    maxResults=10,
    order='relevance',
    type='video',
    publishedAfter=(datetime.now() - timedelta(days=7)).isoformat() + 'Z'
).execute()
""")

if __name__ == "__main__":
    demonstrate_weekly_analysis()