#!/usr/bin/env python3
"""환경 변수 및 의존성 테스트 스크립트"""

import os
import sys

print("=== Environment Variables Test ===")

# 필수 환경 변수 확인
required_vars = [
    'YOUTUBE_API_KEY',
    'SLACK_BOT_TOKEN', 
    'SLACK_CHANNEL_ID'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var}: Set (length: {len(value)})")
    else:
        print(f"✗ {var}: Not set")

print("\n=== Python Dependencies Test ===")

try:
    import googleapiclient
    print("✓ google-api-python-client: Installed")
except ImportError:
    print("✗ google-api-python-client: Not installed")

try:
    import slack_sdk
    print("✓ slack-sdk: Installed")
except ImportError:
    print("✗ slack-sdk: Not installed")

try:
    import requests
    print("✓ requests: Installed")
except ImportError:
    print("✗ requests: Not installed")

print("\n=== Directory Test ===")
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")
print(f"Logs directory: {os.path.join(script_dir, 'logs')}")
print(f"Reports directory: {os.path.join(script_dir, 'reports')}")

# 디렉토리 생성 테스트
try:
    os.makedirs(os.path.join(script_dir, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'reports'), exist_ok=True)
    print("✓ Directory creation: Success")
except Exception as e:
    print(f"✗ Directory creation: Failed - {e}")

print("\n=== Python Version ===")
print(f"Python {sys.version}")