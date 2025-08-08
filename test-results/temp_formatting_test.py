
import json
import urllib.parse

# Slack 메시지 형식화 함수
def format_poker_analysis_message(analysis_data):
    message = {
        "text": "🎯 포커 트렌드 분석 리포트",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 일일 포커 트렌드 분석 결과"
                }
            },
            {
                "type": "divider"
            }
        ]
    }
    
    # YouTube 트렌드 섹션
    if analysis_data.get("youtube"):
        youtube_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🎬 YouTube 트렌드*\n• 인기 키워드: {', '.join(analysis_data['youtube']['keywords'])}\n• 평균 조회수: {analysis_data['youtube']['avg_views']:,}회\n• 트렌드 점수: {analysis_data['youtube']['trend_score']}/10"
            }
        }
        message["blocks"].append(youtube_section)
    
    # PokerNews 섹션
    if analysis_data.get("pokernews"):
        news_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📰 PokerNews 분석*\n• 주요 토픽: {analysis_data['pokernews']['main_topic']}\n• 기사 수: {analysis_data['pokernews']['article_count']}개\n• 관심도: {analysis_data['pokernews']['interest_level']}"
            }
        }
        message["blocks"].append(news_section)
    
    # 플랫폼 분석 섹션
    if analysis_data.get("platform"):
        platform_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🏆 플랫폼 현황*\n• 온라인 플레이어: {analysis_data['platform']['online_players']:,}명\n• 일일 증가율: {analysis_data['platform']['growth_rate']:+.1f}%\n• 현금 게임 활동: {analysis_data['platform']['cash_activity']}"
            }
        }
        message["blocks"].append(platform_section)
    
    return message

# 테스트 데이터
test_analysis = {
    "youtube": {
        "keywords": ["Texas Hold'em", "포커 토너먼트", "전략"],
        "avg_views": 125000,
        "trend_score": 8.5
    },
    "pokernews": {
        "main_topic": "월드시리즈 업데이트",
        "article_count": 15,
        "interest_level": "높음"
    },
    "platform": {
        "online_players": 45230,
        "growth_rate": 5.2,
        "cash_activity": "활발"
    }
}

print("Slack Message Formatting Test:")

# 메시지 형식화
formatted_message = format_poker_analysis_message(test_analysis)

# JSON 인코딩 테스트 (한글 지원)
json_output = json.dumps(formatted_message, ensure_ascii=False, indent=2)

print("✓ Message formatting successful")
print("✓ Korean text support confirmed")
print(f"✓ Block count: {len(formatted_message['blocks'])}")

# URL 인코딩 테스트
url_encoded = urllib.parse.quote(json.dumps(formatted_message, ensure_ascii=False))
print(f"✓ URL encoding successful (length: {len(url_encoded)})")

print("\nMessage formatting: COMPLETED")
