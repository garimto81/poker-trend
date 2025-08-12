#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 PNG 업로드 테스트
"""

import requests
import os

def upload_png_simple(file_path, webhook_url):
    """간단한 PNG 업로드 시도"""
    print(f"파일 업로드 시도: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 파일이 존재하지 않음: {file_path}")
        return False
    
    # 파일 크기 확인
    file_size = os.path.getsize(file_path)
    print(f"파일 크기: {file_size:,} bytes")
    
    # Discord webhook이나 다른 서비스 테스트
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            
            # Slack 웹훅으로는 파일 업로드 불가능
            # 대신 파일 정보만 출력
            print("[INFO] Slack 웹훅은 파일 업로드를 지원하지 않습니다.")
            print("[INFO] Slack Bot API 토큰이 필요합니다.")
            print(f"[INFO] 파일 준비 완료: {os.path.basename(file_path)}")
            return True
            
    except Exception as e:
        print(f"[ERROR] 파일 처리 오류: {e}")
        return False

def main():
    """메인 실행"""
    webhook_url = "your-webhook-url-here"
    
    print("=" * 50)
    print("PNG 파일 업로드 테스트")
    print("=" * 50)
    
    # 주간 차트
    print("\n1. 주간 차트 업로드 테스트")
    upload_png_simple("weekly_stacked_area.png", webhook_url)
    
    # 월간 차트  
    print("\n2. 월간 차트 업로드 테스트")
    upload_png_simple("monthly_stacked_area.png", webhook_url)
    
    print("\n" + "=" * 50)
    print("결론: Slack 웹훅으로는 파일 업로드 불가")
    print("해결방법:")
    print("1. Slack Bot Token 사용 (files.upload API)")
    print("2. 외부 이미지 호스팅 + 이미지 URL")
    print("3. ASCII 차트 (현재 사용 중)")
    print("=" * 50)

if __name__ == "__main__":
    main()