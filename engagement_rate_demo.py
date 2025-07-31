#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
참여율 계산 설명 데모
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def send_engagement_demo():
    """참여율 계산 설명 데모"""
    load_dotenv()
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL not found")
        return
    
    # 예시 데이터
    example_video = {
        "title": "WSOP Final Table - Amazing Bluff!",
        "views": 206584,
        "likes": 4961,
        "comments": 287
    }
    
    # 참여율 계산
    engagement_rate = (example_video['likes'] + example_video['comments']) / example_video['views'] * 100
    
    # 메시지 구성
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 참여율 계산 방식 설명"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*참여율(Engagement Rate)이란?*\n"
                            f"시청자가 영상을 시청한 후 적극적으로 반응한 비율을 나타내는 지표입니다."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📐 계산 공식*\n"
                            f"```참여율 = (좋아요 + 댓글) ÷ 조회수 × 100```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 실제 계산 예시*\n"
                            f"비디오: \"{example_video['title']}\"\n\n"
                            f"• 조회수: {example_video['views']:,}\n"
                            f"• 좋아요: {example_video['likes']:,}\n"
                            f"• 댓글: {example_video['comments']:,}\n\n"
                            f"*계산 과정:*\n"
                            f"1️⃣ 좋아요 + 댓글 = {example_video['likes']:,} + {example_video['comments']:,} = {example_video['likes'] + example_video['comments']:,}\n"
                            f"2️⃣ 참여 수 ÷ 조회수 = {example_video['likes'] + example_video['comments']:,} ÷ {example_video['views']:,} = {(example_video['likes'] + example_video['comments']) / example_video['views']:.6f}\n"
                            f"3️⃣ × 100 = *{engagement_rate:.2f}%*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 참여율 기준 해석*\n"
                            f"• 1% 미만: 낮음 😐\n"
                            f"• 1-3%: 보통 🙂\n"
                            f"• 3-5%: 높음 😊\n"
                            f"• 5% 이상: 매우 높음 🔥\n\n"
                            f"*위 예시 ({engagement_rate:.2f}%)는 '보통' 수준입니다.*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎯 참여율이 중요한 이유*\n"
                            f"• 조회수가 높아도 참여율이 낮으면 시청자의 관심도가 낮음\n"
                            f"• 참여율이 높으면 YouTube 알고리즘이 더 많이 추천\n"
                            f"• 진정한 콘텐츠 품질을 나타내는 지표"
                }
            }
        ]
    }
    
    # 슬랙 전송
    print("\n참여율 설명 전송 중...")
    try:
        response = requests.post(slack_webhook_url, json=message)
        if response.status_code == 200:
            print("✅ 슬랙 전송 성공!")
            
            print("\n" + "="*60)
            print("참여율 계산 예시")
            print("="*60)
            print(f"\n비디오: {example_video['title']}")
            print(f"조회수: {example_video['views']:,}")
            print(f"좋아요: {example_video['likes']:,}")
            print(f"댓글: {example_video['comments']:,}")
            print(f"\n계산: ({example_video['likes']:,} + {example_video['comments']:,}) ÷ {example_video['views']:,} × 100")
            print(f"결과: {engagement_rate:.2f}%")
            
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    send_engagement_demo()