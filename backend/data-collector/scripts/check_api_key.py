#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 키 형식 검증
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

# 상위 디렉토리의 .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] .env file loaded from: {env_path}")
else:
    print(f"[ERROR] .env file not found at: {env_path}")

def check_api_key():
    """API 키 형식 검증"""
    print("\n" + "="*50)
    print("API Key Format Check")
    print("="*50)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY not found in environment")
        return False
    
    print(f"[INFO] Raw key: '{gemini_key}'")
    print(f"[INFO] Key length: {len(gemini_key)}")
    print(f"[INFO] Key starts with: '{gemini_key[:10]}'")
    print(f"[INFO] Key ends with: '{gemini_key[-10:]}'")
    
    # 키 형식 검증
    if "여기에_실제_키_입력" in gemini_key:
        print("[ERROR] API key still contains example text")
        print("[ACTION] Please replace the example text with your actual API key")
        return False
    
    # Google API 키 형식 검증 (AIzaSy로 시작하고 39자)
    if not gemini_key.startswith('AIzaSy'):
        print("[WARNING] API key doesn't start with 'AIzaSy' (expected for Google APIs)")
    
    if len(gemini_key) != 39:
        print(f"[WARNING] API key length is {len(gemini_key)}, expected 39 characters")
    
    # 특수문자 확인
    if re.search(r'[^\w-]', gemini_key):
        print("[WARNING] API key contains special characters (only alphanumeric and hyphens allowed)")
    
    print("[INFO] API key format appears valid")
    return True

def show_fix_instructions():
    """수정 방법 안내"""
    print("\n" + "="*50)
    print("How to Fix")
    print("="*50)
    print("1. Open the .env file:")
    print(f"   {Path(__file__).parent.parent / '.env'}")
    print()
    print("2. Find this line:")
    print("   GEMINI_API_KEY=AIzaSy...여기에_실제_키_입력...")
    print()
    print("3. Replace with your actual API key:")
    print("   GEMINI_API_KEY=AIzaSyABC123def456ghi789...")
    print()
    print("4. Save the file and run this test again")

if __name__ == "__main__":
    print("Gemini API Key Validator")
    print("=" * 30)
    
    if check_api_key():
        print("\n[SUCCESS] API key format looks good!")
        print("You can now run: python simple_gemini_test.py")
    else:
        show_fix_instructions()