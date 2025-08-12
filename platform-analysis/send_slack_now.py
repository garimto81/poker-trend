#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
슬랙 보고서 즉시 전송
"""

import json
import requests
from datetime import datetime

# 실제 슬랙 웹훅 URL
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')

def send_to_slack(message):
    """슬랙으로 메시지 전송"""
    try:
        print("[전송] 슬랙으로 메시지 전송 중...")
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("[성공] 슬랙 메시지 전송 완료!")
            return True
        else:
            print(f"[실패] 응답 코드: {response.status_code}")
            print(f"[실패] 응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] 전송 실패: {e}")
        return False

def create_platform_report():
    """플랫폼 분석 종합 보고서"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 플랫폼 분석 보고서"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{current_time}* | 일간/주간/월간 종합 분석"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📅 일간 현황 (2025-08-10)*"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*총 온라인*\n171,706명"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*총 캐시*\n16,921명"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*리더*\nGGNetwork (89.1%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*HHI 지수*\n7966 (매우 집중)"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 플랫폼*\n"
                           "1. GGNetwork: 153,008명 (89.1%)\n"
                           "2. IDNPoker: 5,528명 (3.2%)\n"
                           "3. WPT Global: 5,237명 (3.1%)\n"
                           "4. Pokio: 3,039명 (1.8%)\n"
                           "5. Pokerdom: 2,693명 (1.6%)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 주간 변화 (8/4-8/10)*"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*전체 시장*\n-9.5%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*최대 하락*\nIDNPoker (-43.8%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*GGNetwork*\n-7.4% (점유율 증가)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*WPT Global*\n-30.4%"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 월간 분석 (7/30-8/10)*"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*전체 시장*\n-43.9%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*최대 성장*\niPoker.it (+71.2%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*GGNetwork*\n-44.5% (점유율 65%→89%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*시장 집중도*\n급격히 상승"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 핵심 인사이트*\n"
                           "• GGNetwork의 절대적 지배력 강화 (89.1% 점유)\n"
                           "• 전체 시장 큰 폭 위축 (-43.9%) 속 양극화 심화\n"
                           "• 중소 플랫폼 급격한 하락 (IDNPoker -43.8%, WPT -30.4%)\n"
                           "• 미국 시장 캐시 게임 성장 (WSOP MI +244.7%)\n"
                           "• PokerStars.it 8/4 이후 데이터 수집 이슈"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📌 데이터 소스*\n"
                           "• Firebase REST API (실시간 수집)\n"
                           "• PokerStars US/Ontario 제외 (데이터 오염)\n"
                           "• 기준일: 2025-08-10"
                }
            }
        ]
    }
    return message

def main():
    """메인 실행"""
    print("="*60)
    print("슬랙 플랫폼 분석 보고서 전송")
    print("="*60)
    print(f"[정보] Webhook URL: {SLACK_WEBHOOK_URL[:50]}...")
    
    # 보고서 생성 및 전송
    message = create_platform_report()
    
    if send_to_slack(message):
        print("\n[완료] 플랫폼 분석 보고서가 슬랙으로 전송되었습니다!")
    else:
        print("\n[실패] 슬랙 전송에 실패했습니다.")
        print("Webhook URL을 확인해주세요.")
    
    print("="*60)

if __name__ == "__main__":
    main()