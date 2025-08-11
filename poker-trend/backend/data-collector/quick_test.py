#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 트렌드 분석 시스템 빠른 테스트
API 키 설정 후 이 스크립트를 실행하세요.
"""

import os
import sys
from dotenv import load_dotenv

def main():
    # .env 파일 로드
    load_dotenv()
    
    print("=" * 60)
    print("포커 트렌드 분석 시스템 빠른 테스트")
    print("=" * 60)
    
    # 환경 변수 확인
    env_vars = {
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'), 
        'SLACK_WEBHOOK_URL': os.getenv('SLACK_WEBHOOK_URL')
    }
    
    missing_vars = [k for k, v in env_vars.items() if not v]
    
    if missing_vars:
        print("\n[ERROR] 다음 환경 변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"   - {var}")
        
        print("\n[INFO] 설정 방법:")
        print("1. .env.example 파일을 .env로 복사")
        print("2. .env 파일에 실제 API 키 입력")
        print("3. 이 스크립트를 다시 실행")
        
        print("\n또는 다음 명령으로 테스트:")
        print("   python scripts/test_with_mock.py  # 모의 데이터 테스트")
        return
    
    print("\n[SUCCESS] 모든 환경 변수가 설정되었습니다!")
    print("\n다음 명령으로 전체 테스트를 실행하세요:")
    print("   python scripts/test_integrated_analyzer.py")
    
    print("\n또는 실제 분석을 실행하세요:")
    print("   python scripts/integrated_trend_analyzer.py --report-type daily")

if __name__ == "__main__":
    main()