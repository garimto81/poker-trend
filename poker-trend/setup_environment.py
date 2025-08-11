#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경 변수 설정 및 인코딩 문제 해결 스크립트
자동 생성됨
"""

import os
import sys
from pathlib import Path

def setup_poker_trend_environment():
    """포커 트렌드 분석 환경 설정"""
    print("🚀 포커 트렌드 분석 환경 설정 중...")
    
    # 1. Windows 콘솔 UTF-8 설정
    if sys.platform == "win32":
        try:
            os.system('chcp 65001 > nul')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            print("✅ Windows 콘솔 UTF-8 인코딩 설정 완료")
        except Exception as e:
            print(f"⚠️  콘솔 인코딩 설정 실패: {e}")
    
    # 2. 필수 디렉토리 생성
    required_dirs = [
        'backend/data-collector/logs',
        'backend/data-collector/reports',
        'backend/platform-analyzer/reports',
        'test-results'
    ]
    
    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ 디렉토리 생성: {dir_path}")
        except Exception as e:
            print(f"❌ 디렉토리 생성 실패 {dir_path}: {e}")
    
    # 3. 환경 변수 확인
    required_env_vars = ['YOUTUBE_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 누락된 환경 변수:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n.env 파일을 확인하고 필요한 API 키를 설정하세요.")
    else:
        print("✅ 모든 필수 환경 변수가 설정됨")
    
    print("\n🎯 설정 완료! 이제 테스트를 실행할 수 있습니다:")
    print("  python backend/data-collector/tests/test_env_enhanced.py")

if __name__ == "__main__":
    setup_poker_trend_environment()
