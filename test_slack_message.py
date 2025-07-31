#!/usr/bin/env python3
"""
슬랙 테스트 메시지 전송 스크립트
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def send_test_message():
    """슬랙 채널에 테스트 메시지 전송"""
    
    # 환경 변수 로드
    load_dotenv()
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("오류: SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        print("해결 방법:")
        print("1. .env 파일을 열어주세요")
        print("2. SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... 형식으로 추가")
        print("3. 슬랙 웹훅 URL 생성 방법은 DAILY_SCHEDULER_GUIDE.md 참조")
        return False
    
    # 테스트 메시지 구성
    message = {
        "text": "🎯 포커 트렌드 분석기 - 슬랙 연결 테스트",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 포커 트렌드 분석기 테스트 메시지"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *슬랙 연결 성공!*\n\n테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📊 *시스템 상태*\n• YouTube API: 준비됨\n• Gemini AI: 준비됨\n• 자동 스케줄러: 대기 중"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🚀 *다음 단계*\n• `python daily_scheduler.py` - 일일 자동 실행 시작\n• `python daily_scheduler.py test` - 즉시 분석 실행"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "포커 트렌드 분석 시스템 v1.0 | 매일 오전 9시 자동 실행"
                    }
                ]
            }
        ]
    }
    
    try:
        # 슬랙에 메시지 전송
        print("슬랙에 테스트 메시지 전송 중...")
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 200:
            print("테스트 메시지 전송 성공!")
            print("슬랙 채널을 확인해보세요.")
            return True
        else:
            print(f"전송 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("포커 트렌드 분석기 - 슬랙 테스트")
    print("=" * 50)
    
    success = send_test_message()
    
    if success:
        print("\n슬랙 연결 테스트 완료!")
        print("이제 daily_scheduler.py를 실행하여 자동 분석을 시작할 수 있습니다.")
    else:
        print("\n슬랙 연결 실패")
        print("위의 오류 메시지를 확인하고 설정을 다시 확인해주세요.")

if __name__ == "__main__":
    main()