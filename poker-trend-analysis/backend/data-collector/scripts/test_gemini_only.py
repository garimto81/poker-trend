#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini API 단독 테스트
"""

import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# 상위 디렉토리의 .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] .env file loaded: {env_path}")
else:
    print(f"[ERROR] .env file not found: {env_path}")

def test_gemini():
    """Gemini API 테스트"""
    print("\n" + "="*50)
    print("Gemini API Test")
    print("="*50)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY is not set.")
        return False
    
    print(f"[OK] GEMINI_API_KEY found: {gemini_key[:10]}...")
    
    try:
        # Gemini 설정
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 간단한 테스트 프롬프트
        prompt = """
        다음은 포커 관련 YouTube 영상 데이터입니다:
        - 제목: "Phil Ivey AMAZING Bluff at WSOP 2025"
        - 조회수: 150,000
        - 채널: PokerGO
        
        이 영상의 인기 요인을 한 문장으로 분석해주세요.
        """
        
        print("\n[REQUEST] Sending request to Gemini...")
        response = model.generate_content(prompt)
        
        print("[SUCCESS] Gemini response received!")
        print(f"\n[AI ANALYSIS]: {response.text[:200]}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Gemini API error: {e}")
        return False

def main():
    """메인 실행"""
    print("Starting Gemini API Test...")
    
    success = test_gemini()
    
    if success:
        print("\n[SUCCESS] Gemini API test completed!")
        print("\nNext steps:")
        print("1. Set YouTube API key and run full test")
        print("2. Set Slack Webhook URL for message test")
    else:
        print("\n[FAILED] Gemini API test failed")
        print("\nTroubleshooting:")
        print("1. Check if GEMINI_API_KEY is correct")
        print("2. Regenerate API key in Google AI Studio")
        print("3. Check if API usage is enabled")

if __name__ == "__main__":
    main()