# -*- coding: utf-8 -*-
"""
API 연결 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv

def test_youtube_api():
    """YouTube API 연결 테스트"""
    print("YouTube API 연결 테스트...")
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not api_key or api_key == 'your_youtube_api_key_here':
            print("YouTube API 키가 설정되지 않았습니다.")
            print("테스트용 더미 키로 연결 시도...")
            api_key = "dummy_key_for_test"
        
        # YouTube API 서비스 생성 시도
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 간단한 검색 시도 (실패해도 OK)
        try:
            search_response = youtube.search().list(
                q='poker',
                part='id,snippet',
                maxResults=1,
                type='video'
            ).execute()
            print("YouTube API 연결 성공!")
            return True
        except HttpError as e:
            if "API key not valid" in str(e) or "quota" in str(e).lower():
                print("YouTube API 서비스 연결은 되지만 유효한 API 키가 필요합니다.")
                print("오류:", str(e))
                return False
            else:
                print(f"YouTube API 연결 오류: {e}")
                return False
                
    except ImportError as e:
        print(f"YouTube API 라이브러리 가져오기 실패: {e}")
        return False
    except Exception as e:
        print(f"YouTube API 테스트 중 예상치 못한 오류: {e}")
        return False

def test_gemini_api():
    """Gemini AI API 연결 테스트"""
    print("Gemini AI API 연결 테스트...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("Gemini API 키가 설정되지 않았습니다.")
            print("테스트용 더미 키로 연결 시도...")
            api_key = "dummy_key_for_test"
        
        # Gemini API 설정
        genai.configure(api_key=api_key)
        
        # 모델 생성 시도
        model = genai.GenerativeModel('gemini-pro')
        
        # 간단한 생성 시도 (실패해도 OK)
        try:
            response = model.generate_content("Hello")
            print("Gemini AI API 연결 성공!")
            return True
        except Exception as e:
            if "API key" in str(e) or "authentication" in str(e).lower():
                print("Gemini AI 서비스 연결은 되지만 유효한 API 키가 필요합니다.")
                print("오류:", str(e))
                return False
            else:
                print(f"Gemini AI 연결 오류: {e}")
                return False
                
    except ImportError as e:
        print(f"Gemini AI 라이브러리 가져오기 실패: {e}")
        return False
    except Exception as e:
        print(f"Gemini AI 테스트 중 예상치 못한 오류: {e}")
        return False

def test_basic_functionality():
    """기본 기능 테스트"""
    print("기본 기능 테스트...")
    
    try:
        # 필수 라이브러리 import 테스트
        import json
        import asyncio
        from datetime import datetime, timedelta
        from dataclasses import dataclass
        import pandas as pd
        
        print("모든 필수 라이브러리 import 성공!")
        
        # 간단한 데이터 구조 테스트
        @dataclass
        class TestVideoData:
            video_id: str
            title: str
            view_count: int
        
        test_video = TestVideoData("test123", "Test Video", 1000)
        print(f"테스트 비디오 데이터: {test_video}")
        
        # 비동기 함수 테스트
        async def test_async():
            await asyncio.sleep(0.1)
            return "비동기 테스트 성공"
        
        result = asyncio.run(test_async())
        print(result)
        
        return True
        
    except Exception as e:
        print(f"기본 기능 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("포커 트렌드 분석기 연결 테스트")
    print("=" * 50)
    
    # 환경 변수 로드
    load_dotenv()
    
    results = []
    
    # 1. 기본 기능 테스트
    basic_ok = test_basic_functionality()
    results.append(("기본 기능", basic_ok))
    print()
    
    # 2. YouTube API 테스트
    youtube_ok = test_youtube_api()
    results.append(("YouTube API", youtube_ok))
    print()
    
    # 3. Gemini AI API 테스트
    gemini_ok = test_gemini_api()
    results.append(("Gemini AI", gemini_ok))
    print()
    
    # 결과 요약
    print("=" * 50)
    print("테스트 결과 요약:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "성공" if result else "실패"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n모든 테스트 통과! 시스템이 준비되었습니다.")
    else:
        print("\n일부 테스트 실패. API 키를 확인하고 다시 시도하세요.")
        print("API 키 설정 방법:")
        print("1. .env 파일을 편집하세요")
        print("2. YOUTUBE_API_KEY와 GEMINI_API_KEY에 실제 키를 입력하세요")

if __name__ == "__main__":
    main()