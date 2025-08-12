#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
슬랙 보고서 전송 - 기존 데이터 사용
"""

import json
import requests
import os
from datetime import datetime

def send_to_slack(webhook_url, message):
    """슬랙으로 메시지 전송"""
    if not webhook_url:
        print("[슬랙 미리보기]")
        print("메시지가 생성되었습니다. SLACK_WEBHOOK_URL 설정 시 전송됩니다.")
        # JSON 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'slack_message_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        print(f"메시지 저장됨: {filename}")
        return True
        
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[오류] 슬랙 전송 실패: {e}")
        return False

def create_daily_report():
    """일간 보고서 생성"""
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 일간 플랫폼 분석 보고서"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*2025년 8월 10일* | 총 37개 플랫폼 분석"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🌍 전체 시장 현황*\n"
                           "• 총 온라인: *171,706명*\n"
                           "• 총 캐시: *16,921명*\n"
                           "• HHI 지수: *7966* (매우 집중)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 플랫폼*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🥇 *1. GGNetwork*\n"
                           "• 온라인: *153,008명* (89.1%)\n"
                           "• 캐시: *10,404명*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🥈 *2. IDNPoker*\n"
                           "• 온라인: *5,528명* (3.2%)\n"
                           "• 캐시: *1,400명*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🥉 *3. WPT Global*\n"
                           "• 온라인: *5,237명* (3.1%)\n"
                           "• 캐시: *3,019명*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📊 *4. Pokio*\n"
                           "• 온라인: *3,039명* (1.8%)\n"
                           "• 캐시: *0명*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📊 *5. Pokerdom*\n"
                           "• 온라인: *2,693명* (1.6%)\n"
                           "• 캐시: *555명*"
                }
            }
        ]
    }
    return message

def create_weekly_report():
    """주간 보고서 생성"""
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 주간 플랫폼 분석 보고서"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*2025년 8월 4일 - 8월 10일* | 주요 변화 분석"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 온라인 플레이어 주요 변화*\n"
                           "📉 *GGNetwork*: -7.4% (165,234 → 153,008)\n"
                           "📉 *IDNPoker*: -43.8% (9,837 → 5,528)\n"
                           "📉 *WPT Global*: -30.4% (7,521 → 5,237)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💰 캐시 플레이어 주요 변화*\n"
                           "📉 *GGNetwork*: -7.4% (11,234 → 10,404)\n"
                           "📉 *WPT Global*: -14.2% (3,521 → 3,019)\n"
                           "📉 *IDNPoker*: -35.1% (2,156 → 1,400)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 주간 시장 동향*\n"
                           "• 전체 시장: -9.5% 감소\n"
                           "• 최대 하락: IDNPoker (-43.8%)\n"
                           "• GGNetwork 점유율: 82.6% → 89.1%"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 핵심 인사이트*\n"
                           "• 전반적인 시장 위축 중 GGNetwork 점유율은 오히려 증가\n"
                           "• PokerStars.it 8월 4일 이후 데이터 없음\n"
                           "• IDNPoker, WPT Global 급격한 하락세"
                }
            }
        ]
    }
    return message

def create_monthly_report():
    """월간 보고서 생성"""
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 월간 플랫폼 분석 보고서"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*2025년 7월 30일 - 8월 10일* | 월간 종합 분석"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🚀 월간 TOP 성장 플랫폼*\n"
                           "📈 *iPoker.it*: +71.2% (2,582명)\n"
                           "📈 *iPoker EU*: +52.5% (2,660명)\n"
                           "📈 *Ray.fi*: +74.4% (캐시 546명)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*⚠️ 월간 TOP 하락 플랫폼*\n"
                           "📉 *GGNetwork*: -44.5% (275,661 → 153,008)\n"
                           "📉 *Chico Poker*: -47.0% (1,797 → 953)\n"
                           "📉 *PokerMatch*: -44.4% (554 → 308)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 월간 시장 요약*\n"
                           "• 전체 시장 변화: -43.9%\n"
                           "• 시장 집중도: HHI 7966 (매우 집중)\n"
                           "• 활성 플랫폼 수: 37개"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 핵심 인사이트*\n"
                           "• 전체 시장 큰 폭 하락 (-43.9%)\n"
                           "• GGNetwork 절대 수치 감소에도 점유율 증가 (65% → 89%)\n"
                           "• 소규모 플랫폼들의 급격한 위축\n"
                           "• 시장 양극화 심화 (HHI 지수 상승)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 캐시 게임 시장 특이사항*\n"
                           "• WSOP MI: +244.7% (393명)\n"
                           "• BetMGM MI: +140.7% (402명)\n"
                           "• 미국 시장 캐시 게임 성장세"
                }
            }
        ]
    }
    return message

def main():
    """메인 실행"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    print("="*60)
    print("플랫폼 분석 슬랙 보고서 전송")
    print("="*60)
    
    # 일간 보고서
    print("\n[1/3] 일간 보고서 전송 중...")
    daily_message = create_daily_report()
    if send_to_slack(webhook_url, daily_message):
        print("[OK] 일간 보고서 전송 완료")
    else:
        print("[ERROR] 일간 보고서 전송 실패")
    
    # 주간 보고서
    print("\n[2/3] 주간 보고서 전송 중...")
    weekly_message = create_weekly_report()
    if send_to_slack(webhook_url, weekly_message):
        print("[OK] 주간 보고서 전송 완료")
    else:
        print("[ERROR] 주간 보고서 전송 실패")
    
    # 월간 보고서
    print("\n[3/3] 월간 보고서 전송 중...")
    monthly_message = create_monthly_report()
    if send_to_slack(webhook_url, monthly_message):
        print("[OK] 월간 보고서 전송 완료")
    else:
        print("[ERROR] 월간 보고서 전송 실패")
    
    print("\n" + "="*60)
    print("모든 보고서 처리 완료")
    print("="*60)

if __name__ == "__main__":
    main()