#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""초간단 YouTube API 테스트"""

import os
import sys

def test_youtube():
    print("=== Simple YouTube Test ===")
    
    # 환경변수 확인
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not set")
        return
    
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        # YouTube API 호출
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 간단한 검색 수행
        request = youtube.search().list(
            q='poker',
            part='snippet',
            type='video',
            maxResults=1
        )
        response = request.execute()
        
        if response.get('items'):
            video = response['items'][0]
            print(f"\nFound video: {video['snippet']['title']}")
            print("✓ YouTube API is working!")
        else:
            print("No videos found")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_slack():
    print("\n=== Simple Slack Test ===")
    
    token = os.getenv('SLACK_BOT_TOKEN')
    channel = os.getenv('SLACK_CHANNEL_ID')
    
    if not token or not channel:
        print("ERROR: Slack credentials not set")
        return
        
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        
        # 간단한 메시지 전송
        result = client.chat_postMessage(
            channel=channel,
            text="✅ GitHub Actions 테스트 성공!"
        )
        
        if result['ok']:
            print("✓ Slack message sent!")
        else:
            print(f"Slack error: {result}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    
    test_youtube()
    test_slack()
    
    print("\n✅ Test completed!")