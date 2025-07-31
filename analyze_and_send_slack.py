#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 데이터에서 포커 트렌드 분석 후 슬랙 전송
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

def analyze_and_send_to_slack():
    """기존 데이터 분석 후 슬랙 전송"""
    
    # 환경변수 로드
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("오류: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        return
    
    # 기존 데이터 로드
    print("기존 분석 데이터 로드 중...")
    with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 상위 10개 비디오 추출 (바이럴 점수 기준)
    top_10_videos = sorted(data['videos'], key=lambda x: x['viral_score'], reverse=True)[:10]
    
    # 전체 통계 (상위 10개 기준)
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
                            f"• 총 조회수: {total_views:,} ({total_views/1000:.1f}K)\n"
                            f"• 총 좋아요: {total_likes:,}\n"
                            f"• 총 댓글: {total_comments:,}\n"
                            f"• 평균 참여율: {avg_engagement*100:.2f}%"
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
                    "text": "*🏆 TOP 5 바이럴 비디오*"
                }
            }
        ]
    }
    
    # TOP 5 비디오 상세 정보
    for i, video in enumerate(top_10_videos[:5], 1):
        title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {title}*\n"
                        f"📊 조회: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video.get('comment_count', 0):,}\n"
                        f"📈 참여율: {video['engagement_rate']*100:.1f}% | 🔥 바이럴: {video['viral_score']:.1f} | 🏷️ {video['keyword_matched']}"
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
    insights.append(f"• 최고 참여율: *{highest_engagement['title'][:40]}...* ({highest_engagement['engagement_rate']*100:.1f}%)")
    
    # 2. 평균 대비 성과
    if avg_engagement > 0.04:
        insights.append(f"• 상위 10개 평균 참여율 {avg_engagement*100:.2f}%로 매우 높은 수준")
    
    # 3. 주요 키워드
    top_keyword = max(keyword_count.items(), key=lambda x: x[1])[0]
    insights.append(f"• 가장 많이 등장한 키워드: *{top_keyword}* ({keyword_count[top_keyword]}개)")
    
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
                        "• GTO 전략 콘텐츠 - 높은 참여율 기대\n"
                        "• 개인 성취 스토리 - WSOP 우승 사례처럼 감정적 연결\n"
                        "• 중간 규모 타겟팅 - 1-5만 조회수에서 최적 참여율"
            }
        }
    ])
    
    # 슬랙 전송
    print("\n슬랙으로 전송 중...")
    try:
        response = requests.post(slack_webhook_url, json=message)
        if response.status_code == 200:
            print("✅ 슬랙 전송 성공!")
            print("\n슬랙 채널을 확인해보세요.")
            
            # 콘솔에도 요약 표시
            print("\n" + "="*80)
            print("전송된 내용 요약")
            print("="*80)
            print(f"총 조회수: {total_views:,}")
            print(f"평균 참여율: {avg_engagement*100:.2f}%")
            print(f"TOP 1: {top_10_videos[0]['title'][:60]}...")
            print(f"       바이럴 점수: {top_10_videos[0]['viral_score']:.1f}")
            
        else:
            print(f"❌ 슬랙 전송 실패: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("="*80)
    print("포커 트렌드 분석 - 슬랙 전송")
    print("="*80)
    analyze_and_send_to_slack()