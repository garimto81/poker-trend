#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 영상 검증 도구
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def check_video_simple(video_id):
    """영상 간단 검증"""
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    
    print(f"Checking Video: {video_id}")
    
    try:
        response = youtube.videos().list(
            part='snippet,status,statistics',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            print("Video not found")
            return False
        
        video = response['items'][0]
        snippet = video.get('snippet', {})
        status = video.get('status', {})
        stats = video.get('statistics', {})
        
        # 제목을 ASCII로 변환하여 출력
        title = snippet.get('title', 'N/A')
        title_safe = title.encode('ascii', 'ignore').decode('ascii')
        
        print(f"Title (ASCII): {title_safe}")
        print(f"Original Title Length: {len(title)} chars")
        print(f"Channel: {snippet.get('channelTitle', 'N/A')}")
        print(f"Views: {stats.get('viewCount', 'N/A')}")
        print(f"Upload Status: {status.get('uploadStatus', 'N/A')}")
        print(f"Privacy Status: {status.get('privacyStatus', 'N/A')}")
        print(f"Embeddable: {status.get('embeddable', 'N/A')}")
        
        # URL 테스트
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"URL: {video_url}")
        
        try:
            response = requests.head(video_url, timeout=5)
            print(f"HTTP Status: {response.status_code}")
        except Exception as e:
            print(f"URL test failed: {e}")
        
        # 실제 제목 반환 (원본 언어)
        return title
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # 문제 영상들 확인
    video_ids = [
        "ACOcPP4CGLE",  # 나루토 MP40 vs 포커 MP40
        "k5o45jPZn6g",  # QUADS vs ACES FULL
        "kx9EsZRdPJM"   # 다른 영상
    ]
    
    for vid in video_ids:
        print("=" * 50)
        title = check_video_simple(vid)
        if title:
            print(f"Original Title: {repr(title)}")
        print()