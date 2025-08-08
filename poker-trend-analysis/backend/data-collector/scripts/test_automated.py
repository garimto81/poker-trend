#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동화된 포커 트렌드 분석 테스트 (사용자 입력 없음)
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """환경 변수 확인"""
    logger.info("=" * 50)
    logger.info("Environment Check")
    logger.info("=" * 50)
    
    # .env 파일 로드
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("[OK] .env file loaded")
    
    required_vars = {
        'YOUTUBE_API_KEY': '[ERROR] YouTube Data API v3 key required',
        'GEMINI_API_KEY': '[ERROR] Google Gemini API key required',
        'SLACK_WEBHOOK_URL': '[ERROR] Slack Webhook URL required'
    }
    
    missing_vars = []
    for var, error_msg in required_vars.items():
        value = os.getenv(var)
        if value:
            logger.info(f"[OK] {var}: {value[:10]}...{value[-4:]}")
        else:
            logger.error(error_msg)
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_youtube_api():
    """YouTube API 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("YouTube API Test")
    logger.info("=" * 50)
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # 간단한 검색 테스트
        request = youtube.search().list(
            part='snippet',
            q='poker',
            type='video',
            maxResults=1,
            order='relevance'
        )
        
        response = request.execute()
        
        if response.get('items'):
            video = response['items'][0]
            logger.info(f"[SUCCESS] YouTube API connected!")
            logger.info(f"   Test video: {video['snippet']['title'][:50]}...")
            return True
        else:
            logger.error("[ERROR] YouTube API returned empty response")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] YouTube API error: {str(e)}")
        return False

def test_gemini_api():
    """Gemini API 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("Gemini AI API Test")
    logger.info("=" * 50)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 간단한 프롬프트 테스트
        response = model.generate_content("Say 'Poker trend analysis test successful!' in Korean.")
        
        logger.info("[SUCCESS] Gemini AI connected!")
        logger.info(f"   Response: {response.text[:100]}")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Gemini AI error: {str(e)}")
        return False

def test_slack_webhook():
    """Slack Webhook 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("Slack Webhook Test")
    logger.info("=" * 50)
    
    try:
        import requests
        
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        # 테스트 메시지
        test_message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*[TEST] Poker Trend Analysis System*\n:white_check_mark: All systems operational!"
                    }
                }
            ]
        }
        
        response = requests.post(webhook_url, json=test_message)
        
        if response.status_code == 200:
            logger.info("[SUCCESS] Slack message sent!")
            return True
        else:
            logger.error(f"[ERROR] Slack webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] Slack webhook error: {str(e)}")
        return False

def run_mini_analysis():
    """미니 분석 실행"""
    logger.info("\n" + "=" * 50)
    logger.info("Mini Analysis Test")
    logger.info("=" * 50)
    
    try:
        # 제한된 키워드로 미니 분석
        from googleapiclient.discovery import build
        import google.generativeai as genai
        
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 키워드 하나로만 테스트
        keyword = 'poker'
        logger.info(f"[INFO] Testing with keyword: {keyword}")
        
        # YouTube 검색
        request = youtube.search().list(
            part='snippet',
            q=keyword,
            type='video',
            maxResults=3,
            order='viewCount',
            publishedAfter='2025-01-01T00:00:00Z'
        )
        
        response = request.execute()
        videos = response.get('items', [])
        
        if videos:
            logger.info(f"[OK] Found {len(videos)} videos")
            
            # 첫 번째 영상으로 AI 분석 테스트
            video_title = videos[0]['snippet']['title']
            
            prompt = f"""
            다음 포커 관련 YouTube 영상을 분석해주세요:
            제목: {video_title}
            
            이 영상의 트렌드 요인을 한 문장으로 분석해주세요.
            """
            
            ai_response = model.generate_content(prompt)
            logger.info(f"[SUCCESS] AI Analysis: {ai_response.text[:100]}...")
            
            return True
        else:
            logger.error("[ERROR] No videos found")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] Mini analysis failed: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("Automated Poker Trend Analysis Test")
    logger.info("=" * 50)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        'environment': False,
        'youtube_api': False,
        'gemini_api': False,
        'slack_webhook': False,
        'mini_analysis': False
    }
    
    # 순차적 테스트 실행
    if check_environment():
        test_results['environment'] = True
        
        if test_youtube_api():
            test_results['youtube_api'] = True
        
        if test_gemini_api():
            test_results['gemini_api'] = True
            
        if test_slack_webhook():
            test_results['slack_webhook'] = True
            
        # 모든 API가 성공하면 미니 분석 실행
        if all([test_results['youtube_api'], test_results['gemini_api']]):
            if run_mini_analysis():
                test_results['mini_analysis'] = True
    
    # 결과 요약
    logger.info("\n" + "=" * 50)
    logger.info("Test Results Summary")
    logger.info("=" * 50)
    
    for test_name, result in test_results.items():
        status = "[SUCCESS]" if result else "[FAILED]"
        logger.info(f"{status} {test_name}")
    
    success_count = sum(test_results.values())
    total_count = len(test_results)
    
    if success_count == total_count:
        logger.info(f"\n[SUCCESS] All tests passed! ({success_count}/{total_count})")
        logger.info("System is ready for production!")
    else:
        logger.info(f"\n[PARTIAL] {success_count}/{total_count} tests passed")
        logger.info("Please fix failing tests before production use")

if __name__ == "__main__":
    main()