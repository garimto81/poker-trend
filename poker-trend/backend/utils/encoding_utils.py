#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인코딩 및 환경 변수 처리 유틸리티
Windows CP949 인코딩 문제 해결을 위한 공통 함수들
"""

import os
import sys
import json
import logging
import locale
from typing import Optional, Any, Dict
from pathlib import Path

# Windows 환경에서 콘솔 인코딩 문제 해결
if sys.platform == "win32":
    # stdout/stderr을 UTF-8으로 재설정
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.7 이하에서는 reconfigure가 없음
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def get_system_encoding() -> str:
    """시스템 인코딩 감지"""
    try:
        return locale.getpreferredencoding()
    except:
        return 'utf-8'

def safe_getenv(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    안전한 환경 변수 가져오기
    
    Args:
        key: 환경 변수 키
        default: 기본값
        required: 필수 여부
        
    Returns:
        환경 변수 값 또는 기본값
        
    Raises:
        ValueError: required=True이지만 값이 없을 때
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    # 빈 문자열이나 공백만 있는 경우 처리
    if isinstance(value, str):
        value = value.strip()
        if not value and default is not None:
            value = default
    
    return value

def safe_json_dump(data: Any, file_path: str, encoding: str = 'utf-8', 
                  ensure_ascii: bool = False, fallback_ascii: bool = True) -> bool:
    """
    안전한 JSON 파일 저장
    
    Args:
        data: 저장할 데이터
        file_path: 파일 경로
        encoding: 파일 인코딩
        ensure_ascii: ASCII 전용 모드
        fallback_ascii: 실패 시 ASCII 모드로 재시도
        
    Returns:
        성공 여부
    """
    try:
        # 디렉토리가 없으면 생성
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 첫 번째 시도: UTF-8 모드
        with open(file_path, 'w', encoding=encoding, errors='replace') as f:
            json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)
        
        return True
        
    except Exception as e:
        logging.warning(f"JSON 저장 실패 (UTF-8): {e}")
        
        if fallback_ascii:
            try:
                # 두 번째 시도: ASCII 모드
                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(data, f, indent=2, ensure_ascii=True)
                
                logging.info(f"JSON 저장 성공 (ASCII 모드): {file_path}")
                return True
                
            except Exception as e2:
                logging.error(f"JSON 저장 완전 실패: {e2}")
        
        return False

def safe_file_write(content: str, file_path: str, encoding: str = 'utf-8', 
                   fallback_encoding: str = 'cp949') -> bool:
    """
    안전한 텍스트 파일 저장
    
    Args:
        content: 저장할 내용
        file_path: 파일 경로
        encoding: 기본 인코딩
        fallback_encoding: 대체 인코딩
        
    Returns:
        성공 여부
    """
    try:
        # 디렉토리가 없으면 생성
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 첫 번째 시도: UTF-8
        with open(file_path, 'w', encoding=encoding, errors='replace') as f:
            f.write(content)
        
        return True
        
    except UnicodeEncodeError as e:
        logging.warning(f"UTF-8 저장 실패, {fallback_encoding}로 재시도: {e}")
        
        try:
            # 두 번째 시도: 시스템 기본 인코딩
            with open(file_path, 'w', encoding=fallback_encoding, errors='replace') as f:
                f.write(content)
            
            logging.info(f"파일 저장 성공 ({fallback_encoding}): {file_path}")
            return True
            
        except Exception as e2:
            logging.error(f"파일 저장 완전 실패: {e2}")
            return False
    
    except Exception as e:
        logging.error(f"파일 저장 오류: {e}")
        return False

def setup_console_encoding():
    """콘솔 인코딩 설정 (Windows 전용)"""
    if sys.platform == "win32":
        try:
            # Windows 콘솔 코드페이지를 UTF-8로 설정
            os.system('chcp 65001 > nul')
            
            # Python 환경 변수 설정
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            
            logging.info("Windows 콘솔 UTF-8 인코딩 설정 완료")
            
        except Exception as e:
            logging.warning(f"콘솔 인코딩 설정 실패: {e}")

def safe_print(*args, encoding: str = None, **kwargs):
    """
    안전한 출력 함수
    
    Args:
        *args: 출력할 내용
        encoding: 강제 인코딩
        **kwargs: print 함수 추가 인자
    """
    try:
        # 기본 print 시도
        print(*args, **kwargs)
        
    except UnicodeEncodeError:
        # 인코딩 실패시 ASCII로 변환
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', errors='replace').decode('ascii'))
            else:
                safe_args.append(str(arg))
        
        print(*safe_args, **kwargs)
        logging.warning("출력 시 인코딩 문제로 ASCII 변환됨")

def validate_environment() -> Dict[str, Any]:
    """
    환경 변수 및 시스템 검증
    
    Returns:
        검증 결과 딕셔너리
    """
    result = {
        'system_encoding': get_system_encoding(),
        'platform': sys.platform,
        'python_version': sys.version,
        'environment_variables': {},
        'issues': [],
        'recommendations': []
    }
    
    # 필수 환경 변수 목록
    required_vars = [
        'YOUTUBE_API_KEY',
        'GEMINI_API_KEY',
        'SLACK_WEBHOOK_URL'
    ]
    
    # 선택적 환경 변수 목록
    optional_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_CHANNEL_ID',
        'DEBUG',
        'ENVIRONMENT'
    ]
    
    # 환경 변수 검증
    for var in required_vars + optional_vars:
        value = os.getenv(var)
        is_required = var in required_vars
        
        if value:
            # 값이 있는 경우
            result['environment_variables'][var] = {
                'set': True,
                'length': len(value),
                'required': is_required
            }
        else:
            # 값이 없는 경우
            result['environment_variables'][var] = {
                'set': False,
                'length': 0,
                'required': is_required
            }
            
            if is_required:
                result['issues'].append(f"필수 환경 변수 '{var}'가 설정되지 않음")
    
    # 시스템별 권장사항
    if sys.platform == "win32":
        if result['system_encoding'].lower() not in ['utf-8', 'utf8']:
            result['issues'].append(f"시스템 인코딩이 UTF-8이 아님: {result['system_encoding']}")
            result['recommendations'].append("Windows 콘솔에서 'chcp 65001' 실행 권장")
    
    return result

# 모듈 로드 시 자동 설정
if sys.platform == "win32":
    setup_console_encoding()

# 로깅 설정 (UTF-8 지원)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 인코딩 확인 로그
logger = logging.getLogger(__name__)
logger.info(f"인코딩 유틸리티 로드됨 - 시스템: {sys.platform}, 인코딩: {get_system_encoding()}")