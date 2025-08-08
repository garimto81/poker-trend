#!/usr/bin/env python3
"""
통합 트렌드 분석기 테스트 스크립트
환경 변수 설정 및 기본 기능 테스트
"""

import os
import sys
import json
import logging
from datetime import datetime
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
    logger.info("환경 변수 확인 중...")
    logger.info("=" * 50)
    
    # .env 파일 로드 (상위 디렉토리에서 찾기)
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("✅ .env 파일 로드됨")
    elif os.path.exists('.env'):
        load_dotenv()
        logger.info("✅ .env 파일 로드됨")
    
    required_vars = {
        'YOUTUBE_API_KEY': '❌ 필수: YouTube Data API v3 키',
        'GEMINI_API_KEY': '❌ 필수: Google Gemini API 키',
        'SLACK_WEBHOOK_URL': '❌ 필수: Slack Webhook URL'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # 민감한 정보는 일부만 표시
            masked_value = value[:10] + '...' + value[-5:] if len(value) > 20 else 'SET'
            logger.info(f"✅ {var}: {masked_value}")
        else:
            logger.error(f"{description}")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_youtube_api():
    """YouTube API 연결 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("YouTube API 테스트 중...")
    logger.info("=" * 50)
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # 간단한 검색 테스트
        request = youtube.search().list(
            q='poker',
            part='snippet',
            type='video',
            maxResults=1
        )
        response = request.execute()
        
        if response.get('items'):
            logger.info(f"✅ YouTube API 연결 성공!")
            video = response['items'][0]
            logger.info(f"   테스트 영상: {video['snippet']['title'][:50]}...")
            return True
        else:
            logger.error("❌ YouTube API 응답이 비어있습니다.")
            return False
            
    except Exception as e:
        logger.error(f"❌ YouTube API 오류: {str(e)}")
        return False

def test_gemini_api():
    """Gemini API 연결 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("Gemini AI API 테스트 중...")
    logger.info("=" * 50)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 간단한 프롬프트 테스트
        response = model.generate_content("Say 'Poker trend analysis test successful!' in Korean.")
        
        if response.text:
            logger.info(f"✅ Gemini AI 연결 성공!")
            logger.info(f"   응답: {response.text.strip()}")
            return True
        else:
            logger.error("❌ Gemini AI 응답이 비어있습니다.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Gemini AI 오류: {str(e)}")
        return False

def test_slack_webhook():
    """Slack Webhook 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("Slack Webhook 테스트 중...")
    logger.info("=" * 50)
    
    try:
        import requests
        
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        test_message = {
            "text": "🧪 포커 트렌드 분석 시스템 테스트",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🧪 테스트 메시지"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*테스트 시간*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                               f"*상태*: 포커 트렌드 분석 시스템이 정상적으로 설정되었습니다."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ YouTube API: 연결됨\n"
                               "✅ Gemini AI: 연결됨\n"
                               "✅ Slack Webhook: 연결됨"
                    }
                }
            ]
        }
        
        response = requests.post(
            webhook_url,
            json=test_message,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("✅ Slack 메시지 전송 성공!")
            return True
        else:
            logger.error(f"❌ Slack 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Slack 오류: {str(e)}")
        return False

def run_mini_analysis():
    """미니 분석 실행 테스트"""
    logger.info("\n" + "=" * 50)
    logger.info("미니 트렌드 분석 실행 중...")
    logger.info("=" * 50)
    
    try:
        # integrated_trend_analyzer 임포트
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from integrated_trend_analyzer import IntegratedTrendAnalyzer
        
        # 일간 리포트로 테스트
        analyzer = IntegratedTrendAnalyzer('daily', 1)
        
        # 검색 키워드 제한 (테스트용)
        analyzer.search_terms = ['poker', 'wsop']  # 2개만 테스트
        
        logger.info("🔍 데이터 수집 중...")
        analyzer.collect_videos()
        
        if analyzer.all_videos:
            logger.info(f"✅ {len(analyzer.all_videos)}개 영상 수집 완료")
            
            # 상위 3개 영상 표시
            logger.info("\n📺 수집된 영상 샘플:")
            for i, video in enumerate(analyzer.all_videos[:3], 1):
                logger.info(f"{i}. {video['title'][:50]}...")
                logger.info(f"   조회수: {video['view_count']:,}")
            
            return True
        else:
            logger.error("❌ 수집된 영상이 없습니다.")
            return False
            
    except Exception as e:
        logger.error(f"❌ 분석 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    logger.info("🚀 포커 트렌드 분석 시스템 테스트 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 결과 저장
    test_results = {
        'environment': False,
        'youtube_api': False,
        'gemini_api': False,
        'slack_webhook': False,
        'mini_analysis': False
    }
    
    # 1. 환경 변수 확인
    test_results['environment'] = check_environment()
    
    if not test_results['environment']:
        logger.error("\n❌ 환경 변수가 설정되지 않았습니다.")
        logger.info("\n다음 방법으로 환경 변수를 설정하세요:")
        logger.info("1. .env 파일 생성:")
        logger.info("   YOUTUBE_API_KEY=your_youtube_api_key")
        logger.info("   GEMINI_API_KEY=your_gemini_api_key")
        logger.info("   SLACK_WEBHOOK_URL=your_slack_webhook_url")
        logger.info("\n2. 또는 시스템 환경 변수 설정")
        logger.info("\n3. 또는 GitHub Secrets 설정 (GitHub Actions 사용 시)")
        return
    
    # 2. API 테스트
    test_results['youtube_api'] = test_youtube_api()
    test_results['gemini_api'] = test_gemini_api()
    
    # 3. Slack 테스트 (선택적)
    if input("\nSlack 테스트 메시지를 전송하시겠습니까? (y/n): ").lower() == 'y':
        test_results['slack_webhook'] = test_slack_webhook()
    else:
        logger.info("⏭️  Slack 테스트 건너뜀")
        test_results['slack_webhook'] = None
    
    # 4. 미니 분석 테스트
    if all(test_results[key] for key in ['youtube_api', 'gemini_api'] if test_results[key] is not None):
        if input("\n미니 분석을 실행하시겠습니까? (y/n): ").lower() == 'y':
            test_results['mini_analysis'] = run_mini_analysis()
    
    # 최종 결과 요약
    logger.info("\n" + "=" * 50)
    logger.info("📊 테스트 결과 요약")
    logger.info("=" * 50)
    
    for test_name, result in test_results.items():
        if result is None:
            status = "⏭️  건너뜀"
        elif result:
            status = "✅ 성공"
        else:
            status = "❌ 실패"
        logger.info(f"{test_name}: {status}")
    
    # 다음 단계 안내
    if all(result for result in test_results.values() if result is not None):
        logger.info("\n🎉 모든 테스트가 성공했습니다!")
        logger.info("\n다음 명령으로 실제 분석을 실행할 수 있습니다:")
        logger.info("python integrated_trend_analyzer.py --report-type daily")
        logger.info("\n또는 GitHub Actions를 통해 자동 실행됩니다.")
    else:
        logger.info("\n⚠️  일부 테스트가 실패했습니다. 위의 오류를 확인하세요.")

if __name__ == "__main__":
    main()