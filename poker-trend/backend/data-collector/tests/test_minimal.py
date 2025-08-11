#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""최소 테스트 스크립트"""

import os
import sys

print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("Script directory:", os.path.dirname(os.path.abspath(__file__)))

# 환경 변수 확인
env_vars = ['YOUTUBE_API_KEY', 'SLACK_BOT_TOKEN', 'SLACK_CHANNEL_ID']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}: Set (length: {len(value)})")
    else:
        print(f"{var}: Not set")

# 최소 Slack 메시지 전송 테스트
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    
    token = os.getenv('SLACK_BOT_TOKEN')
    channel = os.getenv('SLACK_CHANNEL_ID')
    
    if token and channel:
        client = WebClient(token=token)
        response = client.chat_postMessage(
            channel=channel,
            text="🧪 GitHub Actions 테스트 메시지"
        )
        print("✓ Slack message sent successfully")
    else:
        print("✗ Missing Slack credentials")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\nTest completed!")