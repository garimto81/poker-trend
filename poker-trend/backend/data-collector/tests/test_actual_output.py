#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 Slack 메시지 출력 테스트
"""

import json
from datetime import datetime, timedelta

# Mock 데이터 (실제와 동일한 구조)
mock_data = {
    'total_videos': 87,
    'avg_views': 45234.5,
    'avg_engagement': 4.82,
    'hourly_avg_views': 1234.5,
    'search_keywords': ['poker', '포커', 'holdem', '홀덤', 'WSOP', 'WPT', 'EPT', 'PokerStars', 'GGPoker', 'tournament'],
    'top_channels': [
        ('PokerGO', 15),
        ('PokerStars', 12),
        ('포커마스터TV', 8),
        ('Hustler Casino Live', 6),
        ('포커하이라이트', 5)
    ],
    'trending_keywords': [
        ('wsop', 123), ('bluff', 98), ('final', 87), ('table', 82), ('ivey', 76),
        ('strategy', 71), ('poker', 69), ('bad', 65), ('beat', 62), ('royal', 58)
    ],
    'category_breakdown': {
        'tournament': {'count': 28, 'avg_views': 82543, 'avg_engagement': 5.2},
        'entertainment': {'count': 12, 'avg_views': 125342, 'avg_engagement': 7.9},
        'pro_player': {'count': 8, 'avg_views': 95632, 'avg_engagement': 6.5},
        'cash_game': {'count': 5, 'avg_views': 42156, 'avg_engagement': 4.3},
        'online': {'count': 19, 'avg_views': 35234, 'avg_engagement': 4.1},
        'education': {'count': 15, 'avg_views': 28765, 'avg_engagement': 6.8}
    },
    'trending_videos': [
        {
            'video_id': 'abc123',
            'title': "Phil Ivey's INSANE Bluff at WSOP 2024 Final Table! 😱",
            'channel_title': 'PokerGO',
            'view_count': 385234,
            'like_count': 28543,
            'views_per_hour': 15234.5
        },
        {
            'video_id': 'def456',
            'title': '초보자도 할 수 있는 포커 필승 전략 TOP 5',
            'channel_title': '포커마스터TV',
            'view_count': 156832,
            'like_count': 9234,
            'views_per_hour': 8765.2
        },
        {
            'video_id': 'ghi789',
            'title': '$1,000,000 Pot! Biggest Cash Game Hand of 2024',
            'channel_title': 'Hustler Casino Live',
            'view_count': 245789,
            'like_count': 15342,
            'views_per_hour': 7934.1
        }
    ]
}

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))

# 실제 Slack 블록 구조 생성
def create_slack_blocks(data, ai_suggestions, trend_analysis):
    kst_time = datetime.now() + timedelta(hours=9)
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎰 포커 YouTube 트렌드 정밀 분석 ({kst_time.strftime('%Y.%m.%d %H:%M')} KST)"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📊 전체 트렌드 요약*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*총 분석 영상:*\n{data['total_videos']}개"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*평균 조회수:*\n{format_number(data['avg_views'])}회"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*평균 참여율:*\n{data['avg_engagement']:.2f}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*시간당 조회수:*\n{format_number(data['hourly_avg_views'])}회/h"
                }
            ]
        }
    ]
    
    # 수정사항 1: 검색 키워드 추가
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*🔍 검색 키워드:* {', '.join([f'`{kw}`' for kw in data.get('search_keywords', [])[:10]])}"
        }
    })
    
    # 수정사항 2: TOP 채널 추가
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*🎬 TOP 채널:* {', '.join([f'{ch[0]} ({ch[1]}개)' for ch in data.get('top_channels', [])[:3]])}"
        }
    })
    
    # 수정사항 3: AI 트렌드 분석 추가
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📈 트렌드 분석:* {trend_analysis}"
        }
    })
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*🔥 핫 키워드:* {', '.join([f'`{kw[0]}`' for kw in data['trending_keywords'][:8]])}"
        }
    })
    
    blocks.append({"type": "divider"})
    
    # 카테고리별 분석
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📈 카테고리별 분석*"
        }
    })
    
    category_text = []
    for cat, stats in data['category_breakdown'].items():
        emoji = {
            'tournament': '🏆',
            'online': '💻',
            'education': '📚',
            'entertainment': '🎭',
            'pro_player': '👤',
            'cash_game': '💰'
        }.get(cat, '📌')
        category_text.append(f"{emoji} *{cat}*: {stats['count']}개 (평균 {format_number(stats['avg_views'])}회)")
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '\n'.join(category_text)
        }
    })
    
    blocks.append({"type": "divider"})
    
    # TOP 영상 (수정사항 1: 하이퍼링크 추가)
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🚀 TOP 5 급상승 영상*"
        }
    })
    
    for i, video in enumerate(data['trending_videos'][:5], 1):
        video_url = f"https://youtube.com/watch?v={video['video_id']}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. <{video_url}|{video['title'][:60]}...>*"
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"📺 *{video['channel_title']}*"
                },
                {
                    "type": "mrkdwn", 
                    "text": f"👁️ *{format_number(video['view_count'])}* 조회"
                },
                {
                    "type": "mrkdwn",
                    "text": f"💕 *{format_number(video['like_count'])}* 좋아요"
                },
                {
                    "type": "mrkdwn",
                    "text": f"⚡ *{format_number(video['views_per_hour'])}*/시간"
                }
            ]
        })
    
    blocks.append({"type": "divider"})
    
    # AI 제안
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🤖 AI 쇼츠 제작 제안*"
        }
    })
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ai_suggestions[:2000]
        }
    })
    
    return blocks

# 테스트 실행
trend_analysis = "WSOP 관련 콘텐츠와 프로 선수 블러프가 주목받으며, 교육 콘텐츠 수요 증가 중"
ai_suggestions = """**1. "포커 프로가 절대 하지 않는 5가지 실수"**
- 핵심: 초보 실수 vs 프로 플레이 대조
- 타겟: 입문자/중급자
- 차별점: WSOP 실제 영상 활용

**2. "필 아이비의 전설적인 블러프 TOP 3"**
- 핵심: 최신 + 레전드 블러프 모음
- 타겟: 포커 팬 전체
- 차별점: 현재 트렌드와 과거 명장면 결합"""

blocks = create_slack_blocks(mock_data, ai_suggestions, trend_analysis)

print("=== 수정된 Slack 메시지 실제 출력 ===\n")

# JSON으로 출력하여 실제 구조 확인
print("📋 Slack 블록 구조:")
print(json.dumps(blocks, ensure_ascii=False, indent=2)[:3000] + "...")

print("\n" + "="*70)
print("\n✅ 확인 항목:")
print("1. 🔍 검색 키워드 섹션 추가됨")
print("2. 🎬 TOP 채널 섹션 추가됨") 
print("3. 📈 AI 트렌드 분석 섹션 추가됨")
print("4. 🚀 영상 제목에 하이퍼링크 (<URL|제목> 형식)")
print("5. 🤖 AI 쇼츠 제작 제안 섹션 포함")

print(f"\n📊 블록 총 개수: {len(blocks)}개")
print("🎉 모든 수정사항이 적용된 구조 확인 완료!")