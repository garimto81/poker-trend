#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일간 키워드 분석 데모 - 슬랙 전송
실제 작동 예시
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def send_daily_demo():
    """일간 분석 데모 슬랙 전송"""
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL not found")
        return
    
    # 시뮬레이션 데이터 (실제로는 YouTube API에서 수집)
    search_keyword = "poker tournament"
    
    # 데모 메시지 구성
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
                    "text": f"*🔍 검색 키워드: `{search_keyword}`*\n"
                            f"*📅 분석 기간: 최근 24시간*"
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
                            f"• 총 조회수: *859,759*\n"
                            f"• 총 좋아요: *25,177*\n"
                            f"• 총 댓글: *1,842*\n"
                            f"• 평균 참여율: *3.87%*\n"
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
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*1. <https://youtube.com/watch?v=example1|Final Table WSOP Main Event - Incredible Bluff!>*\n"
                            f"🎬 PokerGO • 3시간 전\n"
                            f"📊 조회: *206,584* | 👍 4,961 | 💬 287 | 📈 2.4%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*2. <https://youtube.com/watch?v=example2|$1M Pot - Biggest Tournament Hand Ever!>*\n"
                            f"🎬 Hustler Casino Live • 8시간 전\n"
                            f"📊 조회: *126,719* | 👍 3,439 | 💬 156 | 📈 2.8%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*3. <https://youtube.com/watch?v=example3|How I Won The Sunday Million>*\n"
                            f"🎬 Doug Polk • 12시간 전\n"
                            f"📊 조회: *117,684* | 👍 2,967 | 💬 89 | 📈 2.6%"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💎 최고 참여율 비디오*\n"
                            f"<https://youtube.com/watch?v=example4|Bad Beat for $500K!>\n"
                            f"참여율: *8.3%* | 조회: 45,231"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⏰ 업로드 시간 분포*\n"
                            f"0-6시간 전: 4개 / 6-12시간 전: 3개 / 12-18시간 전: 2개 / 18-24시간 전: 1개"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 AI 분석*\n"
                            f"1. 현재 WSOP 관련 토너먼트 콘텐츠가 가장 주목받고 있으며, 특히 파이널 테이블과 큰 팟 하이라이트가 인기입니다.\n\n"
                            f"2. 높은 조회수를 얻는 비디오들은 금액을 제목에 명시하고, 감정적 요소(bluff, bad beat)를 강조하는 특징이 있습니다.\n\n"
                            f"3. 오늘의 추천: WSOP 메인 이벤트 분석 영상 - 한국 플레이어 관점에서의 전략 해설"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_검색어: {search_keyword} | 조회수 상위 10개 분석 | 최근 24시간_"
                    }
                ]
            }
        ]
    }
    
    # 슬랙 전송
    print(f"\n일간 분석 데모 전송 중...")
    print(f"검색 키워드: {search_keyword}")
    print(f"분석 기간: 최근 24시간")
    
    try:
        response = requests.post(slack_webhook_url, json=message)
        if response.status_code == 200:
            print("✅ 슬랙 전송 성공!")
            
            print("\n" + "="*80)
            print("📋 개선된 일간 분석 특징")
            print("="*80)
            print("\n1. **검색 키워드 명시**")
            print(f"   - 상단에 검색 키워드 표시: `{search_keyword}`")
            print("   - 다양한 키워드로 검색 가능")
            print("\n2. **조회수 상위 10개 추출**")
            print("   - 50개 수집 → 조회수 기준 TOP 10 선택")
            print("   - 최신성과 인기도의 균형")
            print("\n3. **시간대별 분포**")
            print("   - 24시간을 6시간 단위로 구분")
            print("   - 언제 업로드된 콘텐츠가 많은지 파악")
            print("\n4. **AI 분석 개선**")
            print("   - 검색 키워드 기반 맞춤 분석")
            print("   - 실행 가능한 콘텐츠 아이디어 제공")
            
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("="*80)
    print("일간 키워드 분석 데모")
    print("="*80)
    send_daily_demo()