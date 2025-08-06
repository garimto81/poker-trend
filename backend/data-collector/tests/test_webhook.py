#!/usr/bin/env python3
"""Webhook 테스트 스크립트"""

import os
import requests

def test_webhook():
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("ERROR: SLACK_WEBHOOK_URL not set")
        return
    
    payload = {
        "text": "✅ Webhook 테스트 성공! YouTube 포커 트렌드 분석이 정상적으로 설정되었습니다."
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print(f"❌ Webhook error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook()