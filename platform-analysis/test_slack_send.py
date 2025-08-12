#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
슬랙 전송 테스트
"""

import os
import json
import requests
from datetime import datetime

def test_slack_webhook():
    """슬랙 웹훅 테스트"""
    
    # 환경 변수에서 SLACK_WEBHOOK_URL 가져오기
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("="*60)
        print("[경고] SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        print("="*60)
        print("\n설정 방법:")
        print("1. Windows:")
        print("   set SLACK_WEBHOOK_URL=your-webhook-url-here_WEBHOOK_URL")
        print("\n2. PowerShell:")
        print("   $env:SLACK_WEBHOOK_URL = 'your-webhook-url-here_WEBHOOK_URL'")
        print("\n3. Linux/Mac:")
        print("   export SLACK_WEBHOOK_URL='your-webhook-url-here_WEBHOOK_URL'")
        print("="*60)
        return False
    
    print(f"[확인] SLACK_WEBHOOK_URL이 설정되어 있습니다.")
    print(f"[정보] URL 시작: {webhook_url[:30]}...")
    
    # 테스트 메시지
    test_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔔 슬랙 연결 테스트"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*테스트 시간*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                           f"*상태*: ✅ 정상 연결됨\n"
                           f"*준비된 보고서*:\n"
                           f"• 📊 일간 플랫폼 분석 보고서\n"
                           f"• 📈 주간 플랫폼 분석 보고서\n"
                           f"• 📉 월간 플랫폼 분석 보고서"
                }
            }
        ]
    }
    
    try:
        print("[전송] 슬랙으로 테스트 메시지 전송 중...")
        response = requests.post(
            webhook_url,
            json=test_message,
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

def main():
    """메인 실행"""
    print("="*60)
    print("슬랙 웹훅 연결 테스트")
    print("="*60)
    
    if test_slack_webhook():
        print("\n[SUCCESS] 슬랙 연결 테스트 성공!")
        print("이제 send_slack_reports.py를 실행하여 실제 보고서를 전송할 수 있습니다.")
    else:
        print("\n[FAIL] 슬랙 연결 테스트 실패")
        print("SLACK_WEBHOOK_URL 환경 변수를 확인해주세요.")

if __name__ == "__main__":
    main()