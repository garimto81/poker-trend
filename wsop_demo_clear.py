#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSOP 분석 데모 - 명확한 설명 버전
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def send_wsop_demo():
    """WSOP 분석 데모"""
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL not found")
        return
    
    # 메시지 구성
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
                            f"*📅 데이터 출처: 7/30 수집된 포커 영상 50개*\n"
                            f"*📌 분석 대상: WSOP 태그된 12개 중 조회수 TOP 10*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 WSOP 비디오 통계 (TOP 10)*\n"
                            f"• 총 조회수: *4,052,527* (405만)\n"
                            f"• 총 좋아요: *54,546*\n"
                            f"• 총 댓글: *8,290*\n"
                            f"• 평균 참여율: *2.05%*\n"
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
                    "text": "*👀 WSOP 조회수 TOP 3*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*1. <https://youtube.com/watch?v=example1|WSOP 2025 Main Event Final Table>*\n"
                            f"📊 조회: *1,137,606* | 👍 13,008 | 💬 628 | 📈 1.20%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*2. <https://youtube.com/watch?v=example2|The Worst Scandal In WSOP History>*\n"
                            f"📊 조회: *822,790* | 👍 13,220 | 💬 4,717 | 📈 2.18%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*3. <https://youtube.com/watch?v=example3|WSOP 2025 Day 3 with Doug Polk>*\n"
                            f"📊 조회: *712,547* | 👍 12,908 | 💬 343 | 📈 1.86%"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💎 참여율 1위 WSOP 비디오*\n"
                            f"<https://youtube.com/watch?v=example4|I Won A WSOP Bracelet!!!>\n"
                            f"참여율: *7.87%* | 조회: 30,118\n"
                            f"→ 개인 성취 스토리가 높은 참여율 기록"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 WSOP 콘텐츠 인사이트*\n"
                            f"• 메인 이벤트 영상이 가장 높은 조회수 (100만+)\n"
                            f"• 평균 참여율 2.05%로 전체 평균(2.28%)보다 낮음\n"
                            f"• 브랜드 인지도는 높지만 수동적 시청이 많음\n"
                            f"• 개인 스토리(브레이슬릿 획득)가 참여율 최고"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎬 WSOP 콘텐츠 전략*\n"
                            f"• 메인 이벤트 하이라이트 → 안정적 조회수\n"
                            f"• 개인 도전기/성취 스토리 → 높은 참여율\n"
                            f"• 논란/드라마 → 바이럴 가능성"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_참여율 예시: (13,220 + 4,717) ÷ 822,790 × 100 = 2.18%_"
                    }
                ]
            }
        ]
    }
    
    # 슬랙 전송
    print("\nWSOP 분석 데모 전송 중...")
    try:
        response = requests.post(slack_webhook_url, json=message)
        if response.status_code == 200:
            print("✅ 슬랙 전송 성공!")
            
            print("\n" + "="*60)
            print("설명 개선 사항")
            print("="*60)
            print("\n❌ 이전: '기존 수집 데이터' (애매함)")
            print("✅ 개선: '7/30 수집된 포커 영상 50개'")
            print("         'WSOP 태그된 12개 중 조회수 TOP 10'")
            print("\n이제 데이터의 출처와 범위가 명확합니다!")
            
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    send_wsop_demo()