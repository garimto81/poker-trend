#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
멀티 스케줄 분석 데모 - 슬랙 전송
일간/주간/월간 리포트 예시
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

def send_demo_reports():
    """데모 리포트 슬랙 전송"""
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL not found")
        return
    
    print("="*80)
    print("멀티 스케줄 분석 데모")
    print("="*80)
    
    # 1. 일간 리포트 예시
    daily_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"☀️ 일간 포커 트렌드 - {datetime.now().strftime('%m/%d %H시')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 최근 24시간 통계*\n"
                            "• 신규 업로드: 8개\n"
                            "• 총 조회수: 125,430\n"
                            "• 평균 참여율: 5.2%\n"
                            "• 가장 활발한 시간: 15-18시"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 오늘의 HOT 비디오*\n"
                            "<https://youtube.com/example|INSANE Bluff at High Stakes!>\n"
                            "🎬 PokerGO • 3시간 전 • 조회 45,000 • 참여율 6.8%"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_매일 오전 10시 자동 발송_"
                    }
                ]
            }
        ]
    }
    
    # 2. 주간 리포트 예시
    weekly_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📅 주간 포커 트렌드 - {datetime.now().strftime('%m/%d')} 주"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 주간 통계 (최근 7일)*\n"
                            "• 총 업로드: 45개\n"
                            "• 총 조회수: 2.3M\n"
                            "• 평균 참여율: 4.8%\n"
                            "• 활동 채널: 23개"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 주간 TOP 3*\n"
                            "1. WSOP Main Event Final Table\n"
                            "2. GTO vs Exploitative Strategy\n"
                            "3. $1M Pot Cash Game"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📺 주간 활발한 채널*\n"
                            "• PokerGO: 8개\n"
                            "• Doug Polk: 5개\n"
                            "• Hustler Casino: 4개"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_매주 월요일 오전 10시 자동 발송_"
                    }
                ]
            }
        ]
    }
    
    # 3. 월간 리포트 예시
    monthly_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📆 {(datetime.now() - timedelta(days=30)).strftime('%Y년 %m월')} 포커 트렌드 월간 리포트"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 월간 종합 통계*\n"
                            "• 총 업로드: 198개\n"
                            "• 총 조회수: 15.7M\n"
                            "• 총 좋아요: 285K\n"
                            "• 평균 참여율: 4.2%"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 월간 최고 기록*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔥 최고 바이럴*\nDaniel Negreanu WSOP Victory\n바이럴 점수: 28.5\n\n"
                            "*👀 최다 조회*\n$5M Pot - Biggest in History\n조회수: 3.2M\n\n"
                            "*💎 최고 참여율*\nGTO Solver Exposed\n참여율: 12.3%"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 월간 트렌드 키워드*\n"
                            "#WSOP #GTO #HighStakes #Bluff #SolverStrategy"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_매월 첫 번째 월요일 오전 10시 자동 발송_"
                    }
                ]
            }
        ]
    }
    
    # 슬랙으로 전송
    print("\n어떤 리포트를 전송하시겠습니까?")
    print("1. 일간 리포트 (매일 10시)")
    print("2. 주간 리포트 (매주 월요일)")
    print("3. 월간 리포트 (매월 첫 월요일)")
    print("4. 모든 리포트 예시")
    
    choice = input("\n선택 (1-4): ").strip()
    
    messages_to_send = []
    if choice == '1':
        messages_to_send = [("일간", daily_message)]
    elif choice == '2':
        messages_to_send = [("주간", weekly_message)]
    elif choice == '3':
        messages_to_send = [("월간", monthly_message)]
    elif choice == '4':
        messages_to_send = [
            ("일간", daily_message),
            ("주간", weekly_message),
            ("월간", monthly_message)
        ]
    else:
        print("잘못된 선택입니다.")
        return
    
    for report_type, message in messages_to_send:
        print(f"\n{report_type} 리포트 전송 중...")
        try:
            response = requests.post(slack_webhook_url, json=message)
            if response.status_code == 200:
                print(f"✅ {report_type} 리포트 전송 성공!")
            else:
                print(f"❌ {report_type} 리포트 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        
        # 연속 전송 시 잠시 대기
        if len(messages_to_send) > 1:
            import time
            time.sleep(1)
    
    print("\n" + "="*80)
    print("실제 운영 시나리오:")
    print("="*80)
    print("\n1. 스케줄러 실행:")
    print("   python multi_schedule_analyzer.py")
    print("\n2. 자동 실행 시간:")
    print("   - 일간: 매일 오전 10시 (최근 24시간 분석)")
    print("   - 주간: 매주 월요일 오전 10시 (최근 7일 분석)")
    print("   - 월간: 매월 첫 월요일 오전 10시 (전월 분석)")
    print("\n3. 테스트 실행:")
    print("   python multi_schedule_analyzer.py test-daily")
    print("   python multi_schedule_analyzer.py test-weekly")
    print("   python multi_schedule_analyzer.py test-monthly")

if __name__ == "__main__":
    send_demo_reports()