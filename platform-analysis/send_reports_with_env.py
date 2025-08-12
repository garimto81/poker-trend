#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
슬랙 보고서 전송 - .env 파일 사용
"""

import json
import requests
import os
from datetime import datetime
from pathlib import Path

# .env 파일 로드
def load_env():
    """환경 변수 로드"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if value and value != 'your_slack_webhook_url_here':
                        os.environ[key] = value

def send_to_slack(webhook_url, message):
    """슬랙으로 메시지 전송"""
    if not webhook_url or webhook_url == 'your_slack_webhook_url_here':
        print("[경고] 유효한 SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        print("메시지 미리보기 모드로 실행됩니다.")
        
        # JSON 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'slack_preview_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        print(f"[저장] 메시지가 {filename}에 저장되었습니다.")
        return True
        
    try:
        print(f"[전송] 슬랙으로 메시지 전송 중...")
        response = requests.post(
            webhook_url,
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

def create_summary_report():
    """종합 요약 보고서 생성"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 플랫폼 분석 종합 보고서"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{current_time}* | 일간/주간/월간 종합"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📅 일간 하이라이트 (8/10)*\n"
                           "• GGNetwork 독주 체제: *89.1%* 점유율\n"
                           "• 총 온라인 플레이어: *171,706명*\n"
                           "• 시장 집중도: HHI *7966* (매우 집중)"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 주간 트렌드 (8/4-8/10)*\n"
                           "• 전체 시장 *-9.5%* 하락\n"
                           "• IDNPoker 급락: *-43.8%*\n"
                           "• GGNetwork 점유율 증가: 82.6% → *89.1%*"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 월간 분석 (7/30-8/10)*\n"
                           "• 전체 시장 큰 폭 하락: *-43.9%*\n"
                           "• 최대 성장: iPoker.it (*+71.2%*)\n"
                           "• 시장 양극화 심화 중"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 핵심 인사이트*\n"
                           "1️⃣ GGNetwork의 시장 지배력 강화\n"
                           "2️⃣ 중소 플랫폼들의 급격한 위축\n"
                           "3️⃣ 미국 시장 캐시 게임 성장세\n"
                           "4️⃣ PokerStars.it 데이터 이슈 지속"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "상세 보고서"
                    },
                    "value": "view_details",
                    "action_id": "button-action"
                }
            }
        ]
    }
    return message

def main():
    """메인 실행"""
    # 환경 변수 로드
    load_env()
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    print("="*60)
    print("플랫폼 분석 슬랙 보고서 전송")
    print("="*60)
    
    if webhook_url and webhook_url != 'your_slack_webhook_url_here':
        print(f"[확인] SLACK_WEBHOOK_URL 설정됨")
        print(f"[정보] URL: {webhook_url[:30]}...")
    else:
        print("[경고] SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        print("미리보기 모드로 실행됩니다.")
    
    # 종합 보고서 전송
    print("\n[전송] 종합 보고서 생성 중...")
    summary_message = create_summary_report()
    
    if send_to_slack(webhook_url, summary_message):
        print("[완료] 종합 보고서 처리 완료")
    else:
        print("[실패] 종합 보고서 처리 실패")
    
    print("\n" + "="*60)
    print("작업 완료")
    print("="*60)
    
    # 설정 안내
    if not webhook_url or webhook_url == 'your_slack_webhook_url_here':
        print("\n[안내] 실제 슬랙 전송을 위해서는:")
        print("1. .env 파일의 SLACK_WEBHOOK_URL을 실제 URL로 변경")
        print("2. 또는 환경 변수로 설정:")
        print("   set SLACK_WEBHOOK_URL=your-webhook-url-here...")

if __name__ == "__main__":
    main()