#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경 변수 설정 및 인코딩 문제 해결 스크립트 (Windows 안전 버전)
이모지 없는 ASCII 호환 버전
"""

import os
import sys
from pathlib import Path

def safe_print(*args, **kwargs):
    """안전한 출력 함수 (Windows CP949 대응)"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 이모지와 한글을 안전한 문자로 변환
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # 이모지와 특수 문자 제거/변환
                safe_arg = arg.encode('ascii', errors='replace').decode('ascii')
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

def setup_poker_trend_environment():
    """포커 트렌드 분석 환경 설정"""
    safe_print("[SETUP] Poker Trend Analysis Environment Setup...")
    
    # 1. Windows 콘솔 UTF-8 설정 시도
    if sys.platform == "win32":
        try:
            os.system('chcp 65001 > nul')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            safe_print("[OK] Windows console UTF-8 encoding setup completed")
        except Exception as e:
            safe_print(f"[WARNING] Console encoding setup failed: {e}")
    
    # 2. 필수 디렉토리 생성
    required_dirs = [
        'backend/data-collector/logs',
        'backend/data-collector/reports', 
        'backend/platform-analyzer/reports',
        'backend/utils',
        'test-results'
    ]
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            safe_print(f"[OK] Directory created: {dir_path}")
        except Exception as e:
            safe_print(f"[ERROR] Directory creation failed {dir_path}: {e}")
    
    # 3. 환경 변수 확인
    required_env_vars = ['YOUTUBE_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        safe_print("[ERROR] Missing environment variables:")
        for var in missing_vars:
            safe_print(f"  - {var}")
        safe_print("")
        safe_print("Please check your .env file and set required API keys.")
        safe_print("Example .env file content:")
        safe_print("YOUTUBE_API_KEY=your_youtube_api_key_here")
        safe_print("GEMINI_API_KEY=your_gemini_api_key_here") 
        safe_print("SLACK_WEBHOOK_URL=your_slack_webhook_url_here")
    else:
        safe_print("[OK] All required environment variables are set")
    
    # 4. Python 패키지 확인
    required_packages = {
        'googleapiclient': 'google-api-python-client',
        'google.generativeai': 'google-generativeai',
        'requests': 'requests',
        'dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            safe_print(f"[OK] Package installed: {package}")
        except ImportError:
            missing_packages.append(pip_name)
            safe_print(f"[ERROR] Package missing: {package}")
    
    if missing_packages:
        safe_print("")
        safe_print("Install missing packages with:")
        safe_print(f"pip install {' '.join(missing_packages)}")
    
    # 5. 기본 .env 파일 생성 (없는 경우)
    env_file = Path('.env')
    if not env_file.exists():
        env_template = """# Poker Trend Analysis Environment Variables

# YouTube Data API Key
YOUTUBE_API_KEY=your_youtube_api_key_here

# Google Gemini AI API Key  
GEMINI_API_KEY=your_gemini_api_key_here

# Slack Webhook URL for notifications
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Optional: Slack Bot Token (alternative to webhook)
# SLACK_BOT_TOKEN=your_slack_bot_token_here

# Optional: Slack Channel ID
# SLACK_CHANNEL_ID=your_slack_channel_id_here

# Debug mode (true/false)
DEBUG=false

# Environment (development/production)
ENVIRONMENT=development
"""
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_template)
            safe_print(f"[OK] Created template .env file: {env_file}")
            safe_print("Please edit the .env file and add your actual API keys.")
        except Exception as e:
            safe_print(f"[ERROR] Failed to create .env file: {e}")
    
    # 6. 테스트 명령 안내
    safe_print("")
    safe_print("=" * 50)
    safe_print("[SETUP] Environment setup completed!")
    safe_print("=" * 50)
    safe_print("")
    safe_print("Next steps:")
    safe_print("1. Edit .env file with your actual API keys")
    safe_print("2. Run environment test:")
    safe_print("   python backend/data-collector/tests/test_env_enhanced.py")
    safe_print("3. Run quick test:")
    safe_print("   python backend/data-collector/quick_test.py")
    safe_print("4. For Windows encoding issues, run:")
    safe_print("   chcp 65001")
    safe_print("")

if __name__ == "__main__":
    try:
        setup_poker_trend_environment()
    except Exception as e:
        safe_print(f"[ERROR] Setup failed: {e}")
        sys.exit(1)