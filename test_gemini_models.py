# -*- coding: utf-8 -*-
"""
Gemini AI 사용 가능한 모델 확인
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_available_models():
    """사용 가능한 Gemini 모델 목록 확인"""
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("Gemini API 키가 설정되지 않았습니다.")
        return
    
    try:
        genai.configure(api_key=api_key)
        
        print("사용 가능한 Gemini 모델:")
        print("=" * 50)
        
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"모델명: {model.name}")
                print(f"설명: {model.description}")
                print(f"지원 방법: {model.supported_generation_methods}")
                print("-" * 30)
        
    except Exception as e:
        print(f"모델 목록 조회 오류: {e}")

def test_gemini_model(model_name='gemini-1.5-flash'):
    """특정 Gemini 모델 테스트"""
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("API 키가 없습니다.")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        print(f"{model_name} 모델 테스트 중...")
        
        response = model.generate_content("Hello, please respond with 'Model working!'")
        print(f"응답: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"{model_name} 모델 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("Gemini AI 모델 확인 도구")
    print("=" * 50)
    
    # 1. 사용 가능한 모델 목록
    list_available_models()
    print()
    
    # 2. 최신 모델들 테스트
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-pro'
    ]
    
    for model_name in models_to_test:
        print(f"\n{model_name} 테스트:")
        success = test_gemini_model(model_name)
        if success:
            print(f"✓ {model_name} 작동 확인")
            break
        else:
            print(f"✗ {model_name} 작동 실패")