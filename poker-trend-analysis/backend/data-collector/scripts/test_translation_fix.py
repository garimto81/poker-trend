#!/usr/bin/env python3
"""
개선된 번역 기능 테스트
"""

import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import re

# .env 파일 로드
load_dotenv()

# Gemini API 설정
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def translate_to_korean_improved(title, language="English"):
    """개선된 한글 번역 함수"""
    if language == "Korean":
        return title
    
    try:
        # 명확한 단일 번역만 요청하는 개선된 프롬프트
        translate_prompt = f"""Translate the following {language} text to Korean.
        IMPORTANT: Provide ONLY the Korean translation, nothing else.
        Do not provide multiple options or explanations.
        Text: {title}
        Korean translation:"""
        
        response = gemini_model.generate_content(translate_prompt)
        korean_title = response.text.strip()
        
        print(f"원본 응답: {korean_title}")
        
        # 여러 옵션이 포함된 경우 첫 번째 줄만 추출
        if '\n' in korean_title:
            korean_title = korean_title.split('\n')[0]
            print(f"첫 줄 추출 후: {korean_title}")
        
        # 불필요한 문자 및 패턴 제거
        korean_title = korean_title.replace('"', '').replace("'", '').strip()
        korean_title = korean_title.replace('옵션', '').replace('선택', '')
        
        # "1." 또는 "*" 같은 번호/불릿 제거
        korean_title = re.sub(r'^[0-9\.\*\-\s]+', '', korean_title)
        korean_title = korean_title.strip()
        
        print(f"정리 후: {korean_title}")
        
        return korean_title
        
    except Exception as e:
        print(f"번역 실패: {e}")
        return title

def main():
    """테스트 실행"""
    print("=" * 60)
    print("개선된 번역 기능 테스트")
    print("=" * 60)
    
    # 테스트 케이스
    test_titles = [
        "WSOP 2025 Main Event Final Table Highlights",
        "Phil Ivey's Incredible Bluff at Triton Poker",
        "How to Play Texas Hold'em - Beginner's Guide",
        "Epic Poker Moments Compilation 2025",
        "$1,000,000 Pot - Biggest Cash Game Ever"
    ]
    
    print("\n번역 테스트 시작:\n")
    
    for i, title in enumerate(test_titles, 1):
        print(f"\n테스트 {i}:")
        print(f"원본: {title}")
        korean_title = translate_to_korean_improved(title, "English")
        print(f"번역: {korean_title}")
        print("-" * 40)
    
    print("\n✅ 테스트 완료!")
    print("\n번역 결과에 '옵션', '선택', 'Several options' 등이 포함되어 있지 않은지 확인하세요.")

if __name__ == "__main__":
    main()