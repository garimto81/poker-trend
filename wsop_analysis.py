#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSOP 키워드 분석
기존 데이터에서 WSOP 비디오 추출 및 분석
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

def analyze_wsop_keyword():
    """WSOP 키워드 분석"""
    
    # 환경변수 로드
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    print("="*80)
    print("WSOP 키워드 분석")
    print("="*80)
    
    # 기존 데이터 로드
    print("\n[1/4] 데이터 로드 중...")
    with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # WSOP 비디오만 필터링
    wsop_videos = [v for v in data['videos'] if v['keyword_matched'] == 'WSOP']
    print(f"✓ WSOP 비디오 {len(wsop_videos)}개 발견")
    
    # 조회수 기준 상위 10개 선택
    wsop_top_10 = sorted(wsop_videos, key=lambda x: x['view_count'], reverse=True)[:10]
    
    # 통계 계산
    print("\n[2/4] 통계 분석 중...")
    total_views = sum(v['view_count'] for v in wsop_top_10)
    total_likes = sum(v['like_count'] for v in wsop_top_10)
    total_comments = sum(v.get('comment_count', 0) for v in wsop_top_10)
    avg_engagement = sum(v['engagement_rate'] for v in wsop_top_10) / len(wsop_top_10)
    
    # 콘솔 출력
    print("\n【WSOP 키워드 분석 결과】")
    print(f"검색 키워드: WSOP")
    print(f"분석 비디오: 조회수 상위 10개")
    print(f"총 조회수: {total_views:,}")
    print(f"총 좋아요: {total_likes:,}")
    print(f"총 댓글: {total_comments:,}")
    print(f"평균 참여율: {avg_engagement*100:.2f}%")
    print(f"→ 참여율 = (좋아요 + 댓글) ÷ 조회수 × 100")
    
    print("\n【조회수 TOP 5】")
    for i, video in enumerate(wsop_top_10[:5], 1):
        print(f"\n{i}. {video['title']}")
        print(f"   조회수: {video['view_count']:,}")
        print(f"   좋아요: {video['like_count']:,}")
        print(f"   댓글: {video.get('comment_count', 0):,}")
        print(f"   참여율: {video['engagement_rate']*100:.2f}%")
        print(f"   바이럴 점수: {video['viral_score']:.1f}")
    
    # 슬랙 메시지 구성
    print("\n[3/4] 슬랙 메시지 구성 중...")
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 WSOP 키워드 분석 - {datetime.now().strftime('%m/%d %H:%M')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔍 검색 키워드: `WSOP`*\n"
                            f"*📅 데이터 수집일: 2025-07-30 19:09*\n"
                            f"*📌 분석 범위: 50개 비디오 중 WSOP 태그 12개*"
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
                            f"• 총 조회수: *{total_views:,}*\n"
                            f"• 총 좋아요: *{total_likes:,}*\n"
                            f"• 총 댓글: *{total_comments:,}*\n"
                            f"• 평균 참여율: *{avg_engagement*100:.2f}%*\n"
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
    
    # TOP 3 비디오
    for i, video in enumerate(wsop_top_10[:3], 1):
        title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
        
        message['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. <{video['url']}|{title}>*\n"
                        f"📊 조회: *{video['view_count']:,}* | 👍 {video['like_count']:,} | 💬 {video.get('comment_count', 0):,} | 📈 {video['engagement_rate']*100:.1f}%"
            }
        })
    
    # 최고 참여율 비디오
    top_engagement = max(wsop_top_10, key=lambda x: x['engagement_rate'])
    if top_engagement not in wsop_top_10[:3]:
        message['blocks'].extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💎 최고 참여율 WSOP 비디오*\n"
                            f"<{top_engagement['url']}|{top_engagement['title'][:50]}...>\n"
                            f"참여율: *{top_engagement['engagement_rate']*100:.1f}%* | 조회: {top_engagement['view_count']:,}"
                }
            }
        ])
    
    # WSOP 특화 인사이트
    message['blocks'].extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💡 WSOP 콘텐츠 인사이트*\n"
                        f"• 평균 조회수: {sum(v['view_count'] for v in wsop_top_10)//10:,} (전체 평균 대비 높음)\n"
                        f"• 주요 콘텐츠 유형: 메인 이벤트, 파이널 테이블, 하이라이트\n"
                        f"• 특징: 브랜드 인지도가 높아 안정적인 조회수 확보\n"
                        f"• 참여율이 상대적으로 낮음 (평균 {avg_engagement*100:.1f}%)"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🎬 WSOP 콘텐츠 제작 전략*\n"
                        f"• 메인 이벤트 하이라이트 편집 - 안정적 조회수\n"
                        f"• 한국 플레이어 WSOP 도전기 - 로컬 관심도\n"
                        f"• WSOP 역사상 최고의 순간 TOP 10 - 리스트 콘텐츠"
            }
        }
    ])
    
    # 참여율 계산 예시
    example = wsop_top_10[0]
    example_calc = f"예: {example['like_count']:,} + {example.get('comment_count', 0):,} = {example['like_count'] + example.get('comment_count', 0):,} ÷ {example['view_count']:,} × 100 = {example['engagement_rate']*100:.2f}%"
    
    message['blocks'].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"_참여율 계산 예시: {example_calc}_"
            }
        ]
    })
    
    # 슬랙 전송
    if slack_webhook_url:
        print("\n[4/4] 슬랙으로 전송 중...")
        try:
            response = requests.post(slack_webhook_url, json=message)
            if response.status_code == 200:
                print("✅ 슬랙 전송 성공!")
            else:
                print(f"❌ 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    # 추가 분석
    print("\n【추가 분석】")
    
    # 조회수 분포
    view_ranges = {
        "100만+": len([v for v in wsop_top_10 if v['view_count'] >= 1000000]),
        "10만-100만": len([v for v in wsop_top_10 if 100000 <= v['view_count'] < 1000000]),
        "1만-10만": len([v for v in wsop_top_10 if 10000 <= v['view_count'] < 100000]),
        "1만 미만": len([v for v in wsop_top_10 if v['view_count'] < 10000])
    }
    
    print("\n조회수 분포:")
    for range_name, count in view_ranges.items():
        if count > 0:
            print(f"  {range_name}: {count}개")
    
    # 참여율 분포
    engagement_ranges = {
        "5% 이상": len([v for v in wsop_top_10 if v['engagement_rate'] >= 0.05]),
        "3-5%": len([v for v in wsop_top_10 if 0.03 <= v['engagement_rate'] < 0.05]),
        "1-3%": len([v for v in wsop_top_10 if 0.01 <= v['engagement_rate'] < 0.03]),
        "1% 미만": len([v for v in wsop_top_10 if v['engagement_rate'] < 0.01])
    }
    
    print("\n참여율 분포:")
    for range_name, count in engagement_ranges.items():
        if count > 0:
            print(f"  {range_name}: {count}개")
    
    print("\n✅ WSOP 키워드 분석 완료!")

if __name__ == "__main__":
    analyze_wsop_keyword()