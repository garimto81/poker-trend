#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개별 영상 상세 검증 도구
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

def check_video_detailed(video_id):
    """영상 상세 검증"""
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    
    print(f"=== Checking Video: {video_id} ===")
    
    try:
        # 1. 기본 정보 확인
        response = youtube.videos().list(
            part='snippet,status,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            print("Video not found in YouTube API")
            return False
        
        video = response['items'][0]
        snippet = video.get('snippet', {})
        status = video.get('status', {})
        stats = video.get('statistics', {})
        content = video.get('contentDetails', {})
        
        print(f"Title: {snippet.get('title', 'N/A')}")
        print(f"Published: {snippet.get('publishedAt', 'N/A')}")
        print(f"Channel: {snippet.get('channelTitle', 'N/A')}")
        print(f"Views: {stats.get('viewCount', 'N/A')}")
        print(f"Likes: {stats.get('likeCount', 'N/A')}")
        print(f"Comments: {stats.get('commentCount', 'N/A')}")
        print()
        
        print("=== STATUS CHECKS ===")
        print(f"Upload Status: {status.get('uploadStatus', 'N/A')}")
        print(f"Privacy Status: {status.get('privacyStatus', 'N/A')}")
        print(f"License: {status.get('license', 'N/A')}")
        print(f"Embeddable: {status.get('embeddable', 'N/A')}")
        print(f"Public Stats Viewable: {status.get('publicStatsViewable', 'N/A')}")
        print(f"Made for Kids: {status.get('madeForKids', 'N/A')}")
        print()
        
        # 2. URL 직접 접근 테스트
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"=== URL ACCESS TEST ===")
        print(f"URL: {video_url}")
        
        try:
            response = requests.head(video_url, timeout=10)
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                print("URL accessible")
            else:
                print(f"URL returned status {response.status_code}")
        except Exception as e:
            print(f"URL access failed: {e}")
        
        print()
        
        # 3. 임베드 URL 테스트
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        print(f"=== EMBED TEST ===")
        print(f"Embed URL: {embed_url}")
        
        try:
            response = requests.head(embed_url, timeout=10)
            print(f"Embed HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                print("Embed accessible")
            else:
                print(f"Embed returned status {response.status_code}")
        except Exception as e:
            print(f"Embed access failed: {e}")
        
        print()
        
        # 4. 종합 판정
        print("=== FINAL VERDICT ===")
        issues = []
        
        if status.get('uploadStatus') != 'processed':
            issues.append(f"Upload not processed: {status.get('uploadStatus')}")
        
        if status.get('privacyStatus') not in ['public', 'unlisted']:
            issues.append(f"Not public: {status.get('privacyStatus')}")
        
        if status.get('embeddable') == False:
            issues.append("Not embeddable")
        
        if int(stats.get('viewCount', 0)) == 0:
            issues.append("Zero views")
        
        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("VIDEO APPEARS VALID")
            return True
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # 문제가 된 영상 ID 확인
    video_id = "ACOcPP4CGLE"  # 나루토 MP40 vs 포커 MP40 영상
    check_video_detailed(video_id)