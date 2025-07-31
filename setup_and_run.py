"""
포커 트렌드 분석기 설정 및 실행 도우미
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    print(f"Python 버전 확인: {sys.version}")
    return True

def install_requirements():
    """필수 라이브러리 설치"""
    print("📦 필수 라이브러리 설치 중...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 라이브러리 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 라이브러리 설치 실패: {e}")
        return False

def setup_env_file():
    """환경 변수 파일 설정"""
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if not env_file.exists():
        if example_file.exists():
            # .env.example을 .env로 복사
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("📝 .env 파일이 생성되었습니다.")
            print("⚠️  .env 파일을 열어서 실제 API 키를 입력해주세요:")
            print("   - YOUTUBE_API_KEY=your_actual_key")
            print("   - GEMINI_API_KEY=your_actual_key")
            print()
            print("🔗 API 키 생성 방법:")
            print("   YouTube API: https://console.developers.google.com/")
            print("   Gemini AI: https://makersuite.google.com/app/apikey")
            return False
        else:
            print("❌ .env.example 파일을 찾을 수 없습니다.")
            return False
    else:
        print("✅ .env 파일 존재 확인")
        return True

def check_api_keys():
    """API 키 설정 확인"""
    from dotenv import load_dotenv
    load_dotenv()
    
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not youtube_key or youtube_key == 'your_youtube_api_key_here':
        print("❌ YouTube API 키가 설정되지 않았습니다.")
        return False
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        return False
    
    print("✅ API 키 설정 확인 완료")
    return True

def run_analyzer():
    """분석기 실행"""
    print("🚀 포커 트렌드 분석기 실행 중...")
    try:
        subprocess.check_call([
            sys.executable, "specific_keyword_trend_analyzer.py"
        ])
        print("✅ 분석 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 분석기 실행 실패: {e}")
        return False

def main():
    """메인 설정 및 실행 함수"""
    print("포커 트렌드 분석기 설정 및 실행")
    print("=" * 50)
    
    # 1. Python 버전 확인
    if not check_python_version():
        return
    
    # 2. 필수 라이브러리 설치
    if not install_requirements():
        return
    
    # 3. 환경 설정 파일 생성
    if not setup_env_file():
        print("\n⏸️  API 키를 설정한 후 다시 실행해주세요.")
        print("python setup_and_run.py")
        return
    
    # 4. API 키 확인
    if not check_api_keys():
        print("\n⏸️  .env 파일에서 API 키를 올바르게 설정한 후 다시 실행해주세요.")
        return
    
    # 5. 분석기 실행
    print("\n" + "="*50)
    print("🎯 모든 설정이 완료되었습니다. 분석을 시작합니다...")
    print("="*50)
    
    run_analyzer()
    
    print("\n📊 분석이 완료되었습니다!")
    print("📁 결과 파일들을 현재 디렉토리에서 확인하세요.")

if __name__ == "__main__":
    main()