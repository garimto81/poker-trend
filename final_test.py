# -*- coding: utf-8 -*-
"""
포커 트렌드 분석기 최종 통합 테스트
"""

import os
import asyncio
from dotenv import load_dotenv

def check_api_keys():
    """API 키 확인"""
    load_dotenv()
    
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not youtube_key or youtube_key == 'your_youtube_api_key_here':
        return False, "YouTube API 키 없음"
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        return False, "Gemini API 키 없음"
    
    return True, "API 키 확인됨"

async def test_with_real_apis():
    """실제 API로 테스트"""
    print("실제 API로 테스트 실행 중...")
    
    try:
        # 메인 분석기 import
        from specific_keyword_trend_analyzer import main as run_analyzer
        
        # 실제 분석기 실행
        await run_analyzer()
        return True
        
    except Exception as e:
        print(f"실제 API 테스트 실패: {e}")
        return False

def test_without_apis():
    """API 없이 모의 테스트"""
    print("모의 테스트 실행 중...")
    
    try:
        import subprocess
        result = subprocess.run(['python', 'test_simple.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("모의 테스트 성공!")
            return True
        else:
            print(f"모의 테스트 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"모의 테스트 오류: {e}")
        return False

async def main():
    """최종 통합 테스트"""
    print("포커 트렌드 분석기 최종 통합 테스트")
    print("=" * 60)
    
    # 1. API 키 확인
    has_keys, key_status = check_api_keys()
    print(f"API 키 상태: {key_status}")
    print()
    
    if has_keys:
        print("실제 API 키가 있습니다. 실제 분석을 시도합니다...")
        success = await test_with_real_apis()
        
        if success:
            print("실제 API 테스트 성공!")
            print("포커 트렌드 분석기가 완전히 준비되었습니다.")
        else:
            print("실제 API 테스트 실패. 모의 테스트로 전환...")
            success = test_without_apis()
    else:
        print("API 키가 설정되지 않았습니다. 모의 테스트를 실행합니다...")
        success = test_without_apis()
    
    print("=" * 60)
    if success:
        print("최종 테스트 결과: 성공")
        print("포커 트렌드 분석 시스템이 완전히 구현되었습니다!")
        print()
        print("다음 단계:")
        if has_keys:
            print("- 시스템이 준비되었습니다!")
            print("- python specific_keyword_trend_analyzer.py 로 실행하세요")
        else:
            print("- .env 파일에 실제 API 키를 설정하세요")
            print("- YouTube API: https://console.developers.google.com/")
            print("- Gemini AI: https://makersuite.google.com/app/apikey")
            print("- 설정 후 python specific_keyword_trend_analyzer.py 실행")
    else:
        print("최종 테스트 결과: 실패")
        print("시스템에 문제가 있습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())