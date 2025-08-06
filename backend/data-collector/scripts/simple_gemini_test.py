#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 Gemini API 테스트
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 상위 디렉토리의 .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] .env file loaded")
else:
    print(f"[ERROR] .env file not found")

def test_gemini_simple():
    """간단한 Gemini 테스트"""
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY not found")
        return False
    
    print(f"[OK] API Key found: {gemini_key[:20]}...")
    
    try:
        import google.generativeai as genai
        
        # API 키 설정
        genai.configure(api_key=gemini_key)
        
        # 사용 가능한 모델 확인
        print("\n[INFO] Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # 간단한 모델로 테스트
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 간단한 요청
        response = model.generate_content("Hello, world!")
        
        print(f"\n[SUCCESS] Response: {response.text[:100]}")
        return True
        
    except ImportError:
        print("[ERROR] google-generativeai not installed")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("Simple Gemini API Test")
    print("=" * 30)
    test_gemini_simple()