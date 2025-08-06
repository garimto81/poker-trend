#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포맷 테스트 - Slack 메시지 형식 확인
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def create_test_slack_format():
    """테스트용 Slack 메시지 포맷"""
    
    # 테스트 데이터
    test_videos = [
        {
            'title': 'Naruto Mp40 VS Poker Mp40 Ethu Bestnu Sollunga Nanpargalay🔥 #shorts',
            'korean_title': '나루토 MP40 vs 포커 MP40: 어떤 게 더 나은가요, 친구들? 🔥 #shorts',
            'view_count': 525953,
            'like_count': 8420,
            'channel_title': 'மாட்டு RAVI',
            'language': 'Tamil',
            'country': 'India',
            'keyword': 'poker',
            'url': 'https://youtube.com/watch?v=test1'
        },
        {
            'title': 'QUADS vs ACES FULL #poker',
            'korean_title': '쿼드 vs 에이스 풀하우스 #포커',
            'view_count': 312112,
            'like_count': 4890,
            'channel_title': 'River Shark Poker',
            'language': 'English',
            'country': 'Global',
            'keyword': 'poker',
            'url': 'https://youtube.com/watch?v=test2'
        },
        {
            'title': 'he actually went for it 🤯 #poker #shorts',
            'korean_title': '진짜로 갔네 🤯 #포커 #shorts',
            'view_count': 117315,
            'like_count': 2340,
            'channel_title': 'Wolfgang Poker',
            'language': 'English',
            'country': 'Global',
            'keyword': 'poker',
            'url': 'https://youtube.com/watch?v=test3'
        }
    ]
    
    total_views = sum(v['view_count'] for v in test_videos)
    
    # 언어별 통계
    language_stats = {}
    for video in test_videos:
        lang = video['language']
        language_stats[lang] = language_stats.get(lang, 0) + 1
    
    lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎰 Complete Poker Analysis (Korean Translation)"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Total: {len(test_videos)} videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n🔤 Korean translations for TOP 5 completed"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🏆 TOP 5 VIDEOS WITH KOREAN TRANSLATION*"
            }
        }
    ]
    
    # TOP 5 영상 (원제 + 한글 번역)
    for i, video in enumerate(test_videos, 1):
        original_title = video['title']
        korean_title = video['korean_title']
        channel = video['channel_title']
        views = video['view_count']
        likes = video['like_count']
        language = video['language']
        country = video['country']
        keyword = video['keyword']
        url = video['url']
        
        engagement = round((likes / max(views, 1) * 100), 2)
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. <{url}|{original_title}>*\n🇰🇷 {korean_title}\n📺 {channel} | 🎯 {keyword}\n🌍 {language} ({country})\n📊 {views:,} views • 👍 {likes:,} • 📈 {engagement}%"
            }
        })
    
    # AI 인사이트 섹션
    test_insights = """**1. 핵심 트렌드**
- 가장 주목할만한 패턴: 극적인 상황과 짧은 영상이 효과적
- 언어/지역별 특징: Tamil 콘텐츠 높은 참여율, English 글로벌 어필
- 고참여율 콘텐츠: 감정적 반응 유도하는 극적 순간

**2. 포커 팬 관심사 TOP 3**
- 1위: 극적인 핸드와 놀라운 승부
- 2위: 고액 게임과 프로 플레이
- 3위: 실용적인 포커 팁과 전략

**3. 최고의 쇼츠 아이디어**
제목: "믿을 수 없는 포커 역전승! 🤯"
컨셉: 초보가 프로를 이기는 극적 순간 30초 편집
타겟: 포커 입문자 및 엔터테인먼트 시청자
예상 성과: 50만+ 조회수 (극적 요소 + 짧은 러닝타임)
해시태그: #포커 #쇼츠 #역전승 #포커입문 #대박"""
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🤖 AI INSIGHTS & BEST SHORTS IDEA*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{test_insights}```"
            }
        }
    ])
    
    return {"blocks": blocks}

def send_test_slack():
    """테스트 Slack 메시지 전송"""
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("SLACK_WEBHOOK_URL not found")
        return False
    
    message = create_test_slack_format()
    
    try:
        response = requests.post(slack_webhook, json=message, timeout=30)
        if response.status_code == 200:
            print("Test Slack message sent successfully!")
            print("Check your Slack channel to see the new format")
            return True
        else:
            print(f"Slack send failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending Slack: {e}")
        return False

if __name__ == "__main__":
    print("Testing new Slack format...")
    print("Format: Original title with hyperlink, Korean translation below")
    send_test_slack()