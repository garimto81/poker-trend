#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경 변수 및 의존성 테스트 스크립트 (개선 버전)
인코딩 문제 및 Windows 호환성 개선
"""

import os
import sys
from pathlib import Path

# 인코딩 유틸리티 로드
sys.path.append(str(Path(__file__).parent.parent.parent / 'utils'))
try:
    from encoding_utils import safe_print, safe_getenv, validate_environment
    from file_utils import ensure_dir
except ImportError:
    def safe_print(*args, **kwargs):
        try:
            print(*args, **kwargs)
        except UnicodeEncodeError:
            safe_args = [str(arg).encode('ascii', errors='replace').decode('ascii') for arg in args]
            print(*safe_args, **kwargs)
    
    def safe_getenv(key, default=None, required=False):
        return os.getenv(key, default)
    
    def validate_environment():
        return {'issues': [], 'recommendations': []}
    
    def ensure_dir(path):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

def test_environment_comprehensive():
    """종합적인 환경 검증"""
    safe_print("=" * 60)
    safe_print("🔍 포커 트렌드 분석 시스템 환경 검증")
    safe_print("=" * 60)
    
    # 시스템 정보
    safe_print(f"\n📋 시스템 정보:")
    safe_print(f"  - 플랫폼: {sys.platform}")
    safe_print(f"  - Python 버전: {sys.version.split()[0]}")
    safe_print(f"  - 인코딩: {sys.getdefaultencoding()}")
    
    # 환경 변수 검증 (개선된 버전)
    validation_result = validate_environment()
    
    safe_print("\n🔑 환경 변수 검증:")
    env_vars = validation_result.get('environment_variables', {})
    
    for var_name, var_info in env_vars.items():
        status = "✅" if var_info['set'] else "❌"
        required_text = "(필수)" if var_info['required'] else "(선택)"
        length_text = f"길이: {var_info['length']}" if var_info['set'] else "미설정"
        
        safe_print(f"  {status} {var_name} {required_text}: {length_text}")
    
    # 이슈 및 권장사항 출력
    if validation_result['issues']:
        safe_print("\n⚠️  발견된 문제점:")
        for issue in validation_result['issues']:
            safe_print(f"  - {issue}")
    
    if validation_result['recommendations']:
        safe_print("\n💡 권장사항:")
        for rec in validation_result['recommendations']:
            safe_print(f"  - {rec}")

# 추가 API 키 형식 검증
def validate_api_keys():
    """API 키 형식 검증"""
    safe_print("\n🔐 API 키 형식 검증:")
    
    # YouTube API 키 검증
    youtube_key = safe_getenv('YOUTUBE_API_KEY')
    if youtube_key:
        if len(youtube_key) == 39 and youtube_key.startswith('AIzaSy'):
            safe_print("  ✅ YOUTUBE_API_KEY: 형식 올바름")
        else:
            safe_print("  ⚠️  YOUTUBE_API_KEY: 형식이 일반적이지 않음")
    else:
        safe_print("  ❌ YOUTUBE_API_KEY: 미설정")
    
    # Gemini API 키 검증
    gemini_key = safe_getenv('GEMINI_API_KEY')
    if gemini_key:
        if len(gemini_key) == 39 and gemini_key.startswith('AIzaSy'):
            safe_print("  ✅ GEMINI_API_KEY: 형식 올바름")
        else:
            safe_print("  ⚠️  GEMINI_API_KEY: 형식이 일반적이지 않음")
    else:
        safe_print("  ❌ GEMINI_API_KEY: 미설정")
    
    # Slack Webhook URL 검증
    slack_webhook = safe_getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        if slack_webhook.startswith('https://hooks.slack.com/services/'):
            safe_print("  ✅ SLACK_WEBHOOK_URL: 형식 올바름")
        else:
            safe_print("  ⚠️  SLACK_WEBHOOK_URL: 형식 확인 필요")
    else:
        safe_print("  ❌ SLACK_WEBHOOK_URL: 미설정")

def test_dependencies():
    """Python 패키지 의존성 검증"""
    safe_print("\n📦 Python 패키지 검증:")
    
    dependencies = [
        ('googleapiclient', 'Google API Client (YouTube)'),
        ('google.generativeai', 'Google Generative AI (Gemini)'),
        ('requests', 'HTTP 클라이언트'),
        ('slack_sdk', 'Slack SDK (선택)'),
        ('dotenv', '.env 파일 처리'),
        ('pathlib', 'Path 처리 (내장)'),
    ]
    
    for module, description in dependencies:
        try:
            __import__(module)
            safe_print(f"  ✅ {module}: 설치됨 ({description})")
        except ImportError:
            if 'pathlib' in module:
                safe_print(f"  ⚠️  {module}: Python 3.4+ 필요")
            else:
                safe_print(f"  ❌ {module}: 미설치 ({description})")

def test_directories():
    """디렉토리 및 파일 시스템 검증"""
    safe_print("\n📁 디렉토리 및 권한 검증:")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # 중요 디렉토리들
    important_dirs = {
        'logs': script_dir / 'logs',
        'reports': script_dir / 'reports',
        'scripts': script_dir.parent / 'scripts',
        'utils': project_root / 'utils'
    }
    
    for name, dir_path in important_dirs.items():
        if ensure_dir(dir_path):
            safe_print(f"  ✅ {name} 디렉토리: {dir_path}")
        else:
            safe_print(f"  ❌ {name} 디렉토리 생성 실패: {dir_path}")
    
    # 파일 쓰기 권한 테스트
    test_file = script_dir / 'logs' / 'test_permission.txt'
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('권한 테스트')
        test_file.unlink()  # 삭제
        safe_print("  ✅ 파일 쓰기 권한: 정상")
    except Exception as e:
        safe_print(f"  ❌ 파일 쓰기 권한 오류: {e}")

def test_encoding():
    """인코딩 지원 테스트"""
    safe_print("\n🔤 인코딩 지원 테스트:")
    
    # 한국어 텍스트 테스트
    korean_text = "포커 트렌드 분석 시스템 테스트"
    try:
        # 콘솔 출력 테스트
        safe_print(f"  한국어 출력 테스트: {korean_text}")
        safe_print("  ✅ 한국어 콘솔 출력: 성공")
        
        # 파일 쓰기 테스트
        test_file = Path(__file__).parent / 'logs' / 'encoding_test.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(korean_text)
        test_file.unlink()
        safe_print("  ✅ 한국어 파일 저장: 성공")
        
    except Exception as e:
        safe_print(f"  ❌ 인코딩 테스트 실패: {e}")

def show_system_summary():
    """시스템 정보 요약"""
    safe_print("\n" + "=" * 60)
    safe_print("📋 시스템 검증 완료")
    safe_print("=" * 60)
    
    # 권장사항
    safe_print("\n💡 다음 단계:")
    safe_print("  1. 필수 환경 변수가 모두 설정되었는지 확인")
    safe_print("  2. API 키가 올바른 형식인지 검증")
    safe_print("  3. 누락된 패키지가 있다면 설치: pip install -r requirements.txt")
    safe_print("  4. Windows에서 인코딩 문제 시 'chcp 65001' 실행")
    safe_print("  5. 테스트 실행: python backend/data-collector/quick_test.py")

def main():
    """메인 테스트 실행"""
    test_environment_comprehensive()
    validate_api_keys()
    test_dependencies()
    test_directories()
    test_encoding()
    show_system_summary()
    
    safe_print(f"\n🐍 Python {sys.version.split()[0]} 환경 검증 완료")

if __name__ == "__main__":
    main()