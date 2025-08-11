#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 처리 유틸리티 (Windows 호환성 개선)
임시 파일 생성/삭제 및 권한 문제 해결
"""

import os
import sys
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional, Union, List
import time

logger = logging.getLogger(__name__)

class SafeFileHandler:
    """안전한 파일 처리를 위한 클래스"""
    
    def __init__(self):
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []
    
    def create_temp_file(self, suffix: str = '', prefix: str = 'poker_', 
                        text: bool = True, delete: bool = False) -> str:
        """
        안전한 임시 파일 생성
        
        Args:
            suffix: 파일 확장자
            prefix: 파일 접두사
            text: 텍스트 모드 여부
            delete: 자동 삭제 여부
            
        Returns:
            임시 파일 경로
        """
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                text=text,
                delete=delete
            )
            
            # 파일 디스크립터 닫기
            os.close(fd)
            
            # 추적 목록에 추가
            self.temp_files.append(temp_path)
            
            logger.debug(f"임시 파일 생성: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"임시 파일 생성 실패: {e}")
            raise
    
    def create_temp_dir(self, suffix: str = '', prefix: str = 'poker_') -> str:
        """
        안전한 임시 디렉토리 생성
        
        Args:
            suffix: 디렉토리 접미사
            prefix: 디렉토리 접두사
            
        Returns:
            임시 디렉토리 경로
        """
        try:
            temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix)
            
            # 추적 목록에 추가
            self.temp_dirs.append(temp_dir)
            
            logger.debug(f"임시 디렉토리 생성: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"임시 디렉토리 생성 실패: {e}")
            raise
    
    def safe_remove_file(self, file_path: Union[str, Path], 
                        retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        안전한 파일 삭제 (Windows 파일 락 문제 해결)
        
        Args:
            file_path: 삭제할 파일 경로
            retry_count: 재시도 횟수
            retry_delay: 재시도 간격 (초)
            
        Returns:
            삭제 성공 여부
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return True
        
        for attempt in range(retry_count):
            try:
                # Windows에서 읽기 전용 속성 제거
                if sys.platform == "win32":
                    os.chmod(file_path, 0o777)
                
                file_path.unlink()
                logger.debug(f"파일 삭제 성공: {file_path}")
                return True
                
            except PermissionError as e:
                if attempt < retry_count - 1:
                    logger.warning(f"파일 삭제 재시도 {attempt + 1}/{retry_count}: {e}")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"파일 삭제 최종 실패: {file_path} - {e}")
                    return False
                    
            except Exception as e:
                logger.error(f"파일 삭제 오류: {file_path} - {e}")
                return False
        
        return False
    
    def safe_remove_dir(self, dir_path: Union[str, Path], 
                       retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        안전한 디렉토리 삭제
        
        Args:
            dir_path: 삭제할 디렉토리 경로
            retry_count: 재시도 횟수
            retry_delay: 재시도 간격 (초)
            
        Returns:
            삭제 성공 여부
        """
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            return True
        
        for attempt in range(retry_count):
            try:
                # Windows에서 하위 파일들의 권한 수정
                if sys.platform == "win32":
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            file_path = Path(root) / file
                            try:
                                os.chmod(file_path, 0o777)
                            except:
                                pass
                
                shutil.rmtree(dir_path)
                logger.debug(f"디렉토리 삭제 성공: {dir_path}")
                return True
                
            except PermissionError as e:
                if attempt < retry_count - 1:
                    logger.warning(f"디렉토리 삭제 재시도 {attempt + 1}/{retry_count}: {e}")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"디렉토리 삭제 최종 실패: {dir_path} - {e}")
                    return False
                    
            except Exception as e:
                logger.error(f"디렉토리 삭제 오류: {dir_path} - {e}")
                return False
        
        return False
    
    def ensure_dir(self, dir_path: Union[str, Path], mode: int = 0o755) -> bool:
        """
        디렉토리 존재 확인 및 생성
        
        Args:
            dir_path: 생성할 디렉토리 경로
            mode: 디렉토리 권한
            
        Returns:
            생성/존재 확인 성공 여부
        """
        try:
            dir_path = Path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True, mode=mode)
            
            logger.debug(f"디렉토리 확인/생성: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"디렉토리 생성 실패: {dir_path} - {e}")
            return False
    
    def safe_copy(self, src: Union[str, Path], dst: Union[str, Path], 
                 preserve_metadata: bool = True) -> bool:
        """
        안전한 파일 복사
        
        Args:
            src: 원본 파일 경로
            dst: 대상 파일 경로
            preserve_metadata: 메타데이터 보존 여부
            
        Returns:
            복사 성공 여부
        """
        try:
            src = Path(src)
            dst = Path(dst)
            
            # 대상 디렉토리 생성
            self.ensure_dir(dst.parent)
            
            # 파일 복사
            if preserve_metadata:
                shutil.copy2(src, dst)
            else:
                shutil.copy(src, dst)
            
            logger.debug(f"파일 복사 성공: {src} -> {dst}")
            return True
            
        except Exception as e:
            logger.error(f"파일 복사 실패: {src} -> {dst} - {e}")
            return False
    
    def safe_move(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """
        안전한 파일 이동
        
        Args:
            src: 원본 파일 경로
            dst: 대상 파일 경로
            
        Returns:
            이동 성공 여부
        """
        try:
            src = Path(src)
            dst = Path(dst)
            
            # 대상 디렉토리 생성
            self.ensure_dir(dst.parent)
            
            # 파일 이동
            shutil.move(src, dst)
            
            logger.debug(f"파일 이동 성공: {src} -> {dst}")
            return True
            
        except Exception as e:
            logger.error(f"파일 이동 실패: {src} -> {dst} - {e}")
            return False
    
    def get_safe_filename(self, filename: str, replacement_char: str = '_') -> str:
        """
        안전한 파일명 생성 (Windows 금지 문자 제거)
        
        Args:
            filename: 원본 파일명
            replacement_char: 대체 문자
            
        Returns:
            안전한 파일명
        """
        # Windows에서 금지된 문자들
        forbidden_chars = '<>:"/\\|?*'
        
        safe_name = filename
        for char in forbidden_chars:
            safe_name = safe_name.replace(char, replacement_char)
        
        # 예약된 이름들 처리
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        base_name = Path(safe_name).stem.upper()
        if base_name in reserved_names:
            safe_name = f"_{safe_name}"
        
        # 길이 제한 (Windows 경로 제한 고려)
        if len(safe_name) > 200:
            name_part = Path(safe_name).stem
            ext_part = Path(safe_name).suffix
            safe_name = name_part[:200-len(ext_part)] + ext_part
        
        return safe_name
    
    def cleanup_temp_files(self) -> int:
        """
        생성된 임시 파일들 정리
        
        Returns:
            정리된 파일 수
        """
        cleaned_count = 0
        
        # 임시 파일 정리
        for temp_file in self.temp_files[:]:  # 복사본으로 반복
            if self.safe_remove_file(temp_file):
                self.temp_files.remove(temp_file)
                cleaned_count += 1
        
        # 임시 디렉토리 정리
        for temp_dir in self.temp_dirs[:]:  # 복사본으로 반복
            if self.safe_remove_dir(temp_dir):
                self.temp_dirs.remove(temp_dir)
                cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"임시 파일 정리 완료: {cleaned_count}개")
        
        return cleaned_count
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료 시 자동 정리"""
        self.cleanup_temp_files()

# 전역 인스턴스
default_file_handler = SafeFileHandler()

# 편의 함수들
def create_temp_file(*args, **kwargs) -> str:
    """임시 파일 생성"""
    return default_file_handler.create_temp_file(*args, **kwargs)

def create_temp_dir(*args, **kwargs) -> str:
    """임시 디렉토리 생성"""
    return default_file_handler.create_temp_dir(*args, **kwargs)

def safe_remove(path: Union[str, Path]) -> bool:
    """안전한 파일/디렉토리 삭제"""
    path = Path(path)
    if path.is_file():
        return default_file_handler.safe_remove_file(path)
    elif path.is_dir():
        return default_file_handler.safe_remove_dir(path)
    else:
        return True

def ensure_dir(dir_path: Union[str, Path]) -> bool:
    """디렉토리 생성 확인"""
    return default_file_handler.ensure_dir(dir_path)

def get_safe_filename(filename: str) -> str:
    """안전한 파일명 생성"""
    return default_file_handler.get_safe_filename(filename)

def cleanup_temp_files() -> int:
    """임시 파일 정리"""
    return default_file_handler.cleanup_temp_files()

# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup_temp_files)