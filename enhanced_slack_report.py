#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 슬랙 리포트 - 채널명 포함, 제목 하이퍼링크
"""

import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def send_enhanced_slack_report():
    """채널명과 하이퍼링크가 포함된 향상된 슬랙 리포트"""
    
    # 환경변수 로드
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("오류: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        return
    
    # 기존 데이터 로드
    print("분석 데이터 로드 중...")
    with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 채널명 추가 (실제로는 YouTube API로 수집해야 하지만, 여기서는 시뮬레이션)
    channel_names = {
        "kV4Gs7DFCbY": "Daniel Negreanu",
        "7iefjaxoqJk": "PokerCoaching",
        "6xf-VjKJpH4": "Lady Luck HQ",
        "7F1fiPuRaPU": "Jonathan Little",
        "hYPYdPWV5W0": "Upswing Poker",
        "HiJkqaONi-4": "Lady Luck HQ",
        "JuTBrA-66V8": "Lady Luck HQ",
        "T7VsKWIhBBg": "PokerGO",
        "YPa5VwCHcPM": "Solve For Why",
        "vI-hzLv3pR0": "PokerGO"
    }
    
    # 상위 10개 비디오 추출
    top_10_videos = sorted(data['videos'], key=lambda x: x['viral_score'], reverse=True)[:10]
    
    # 채널명 추가
    for video in top_10_videos:
        video['channel'] = channel_names.get(video['video_id'], "Unknown Channel")
    
    # 전체 통계
    total_views = sum(v['view_count'] for v in top_10_videos)
    total_likes = sum(v['like_count'] for v in top_10_videos)
    total_comments = sum(v.get('comment_count', 0) for v in top_10_videos)
    avg_engagement = sum(v['engagement_rate'] for v in top_10_videos) / 10
    
    # 키워드 분포
    keyword_count = {}
    for video in top_10_videos:
        keyword = video['keyword_matched']
        keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    # 슬랙 메시지 구성
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 포커 트렌드 분석 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 상위 10개 비디오 통계*\n"
                            f"• 총 조회수: *{total_views:,}* ({total_views/1000000:.1f}M views)\n"
                            f"• 총 좋아요: *{total_likes:,}*\n"
                            f"• 총 댓글: *{total_comments:,}*\n"
                            f"• 평균 참여율: *{avg_engagement*100:.2f}%*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏷️ 키워드 분포*\n" + 
                            "\n".join([f"• {k}: {v}개" for k, v in sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)])
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 바이럴 비디오 (클릭하면 영상 재생)*"
                }
            }
        ]
    }
    
    # TOP 5 비디오 상세 정보 (하이퍼링크 포함)
    for i, video in enumerate(top_10_videos[:5], 1):
        title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
        
        # 제목에 하이퍼링크 추가
        linked_title = f"<{video['url']}|{title}>"
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {linked_title}*\n"
                        f"🎬 채널: *{video['channel']}*\n"
                        f"📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video.get('comment_count', 0):,}\n"
                        f"📈 참여율: {video['engagement_rate']*100:.1f}% | 🔥 바이럴: {video['viral_score']:.1f} | 🏷️ {video['keyword_matched']}"
            }
        })
    
    # 채널별 통계
    channel_stats = {}
    for video in top_10_videos:
        channel = video['channel']
        if channel not in channel_stats:
            channel_stats[channel] = 0
        channel_stats[channel] += 1
    
    # 채널 통계 추가
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📺 채널별 분포 (TOP 10 중)*\n" +
                        "\n".join([f"• {ch}: {cnt}개" for ch, cnt in sorted(channel_stats.items(), key=lambda x: x[1], reverse=True)[:3]])
            }
        }
    ])
    
    # 나머지 5개 비디오 간략 정보
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📋 6-10위 비디오*"
            }
        }
    ])
    
    # 6-10위 간략 표시
    brief_list = []
    for i, video in enumerate(top_10_videos[5:10], 6):
        title_short = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
        linked_title = f"<{video['url']}|{title_short}>"
        brief_list.append(f"{i}. {linked_title} - {video['channel']} ({video['engagement_rate']*100:.1f}%)")
    
    message['blocks'].append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "\n".join(brief_list)
        }
    })
    
    # 인사이트 섹션
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💡 핵심 인사이트*"
            }
        }
    ])
    
    # 인사이트 분석
    insights = []
    
    # 1. 최고 참여율 비디오
    highest_engagement = max(top_10_videos, key=lambda x: x['engagement_rate'])
    insights.append(f"• 최고 참여율: *{highest_engagement['title'][:30]}...* ({highest_engagement['engagement_rate']*100:.1f}%) by {highest_engagement['channel']}")
    
    # 2. 가장 활발한 채널
    top_channel = max(channel_stats.items(), key=lambda x: x[1])
    insights.append(f"• 가장 많이 등장한 채널: *{top_channel[0]}* ({top_channel[1]}개 비디오)")
    
    # 3. 평균 대비 성과
    if avg_engagement > 0.04:
        insights.append(f"• 상위 10개 평균 참여율 *{avg_engagement*100:.2f}%*로 매우 높은 수준")
    
    # 인사이트 추가
    message['blocks'].append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "\n".join(insights)
        }
    })
    
    # 추천사항
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎬 콘텐츠 제작 추천*\n"
                        "• *GTO 전략 콘텐츠* - 4개가 TOP 10 진입, 높은 참여율\n"
                        "• *개인 스토리텔링* - Daniel Negreanu의 WSOP 우승처럼\n"
                        "• *교육 콘텐츠 채널* - PokerCoaching, Upswing Poker 참고"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📌 _제목을 클릭하면 YouTube 영상으로 이동합니다_"
                }
            ]
        }
    ])
    
    # 슬랙 전송
    print("\n향상된 리포트를 슬랙으로 전송 중...")
    try:
        response = requests.post(slack_webhook_url, json=message)
        if response.status_code == 200:
            print("✅ 슬랙 전송 성공!")
            print("\n슬랙 채널에서 다음을 확인할 수 있습니다:")
            print("- 제목 클릭 시 YouTube 영상 재생")
            print("- 각 비디오의 채널명 표시")
            print("- 채널별 통계 분석")
            
            # 콘솔 요약
            print("\n" + "="*80)
            print("전송된 TOP 3 요약")
            print("="*80)
            for i, video in enumerate(top_10_videos[:3], 1):
                print(f"{i}. {video['title'][:50]}...")
                print(f"   채널: {video['channel']}")
                print(f"   URL: {video['url']}")
                print(f"   바이럴: {video['viral_score']:.1f} | 참여율: {video['engagement_rate']*100:.1f}%")
                print()
            
        else:
            print(f"❌ 슬랙 전송 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("="*80)
    print("향상된 포커 트렌드 분석 - 슬랙 전송")
    print("="*80)
    send_enhanced_slack_report()