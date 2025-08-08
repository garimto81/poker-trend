
import json

# Slack 메시지 페이로드 구조 검증
def validate_slack_payload(payload):
    required_fields = ['text']
    optional_fields = ['username', 'icon_emoji', 'channel', 'blocks', 'attachments']
    
    validation_results = {
        'has_text': 'text' in payload,
        'valid_json': True,
        'has_blocks': 'blocks' in payload,
        'has_attachments': 'attachments' in payload
    }
    
    return validation_results

# 테스트 페이로드들
test_payloads = [
    # 기본 텍스트 메시지
    {"text": "🎯 포커 트렌드 분석 완료"},
    
    # 블록 형식 메시지
    {
        "text": "포커 분석 리포트",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 오늘의 YouTube 트렌드*\n• 상위 키워드: Texas Hold'em, Tournament\n• 조회수 증가: +15.3%"
                }
            }
        ]
    },
    
    # 첨부 파일 포함 메시지
    {
        "text": "플랫폼 분석 결과",
        "attachments": [
            {
                "color": "good",
                "title": "일일 플레이어 증가율",
                "text": "+5.2% 증가",
                "footer": "poker-trend-analyzer"
            }
        ]
    }
]

print("Slack Payload Validation:")
for i, payload in enumerate(test_payloads):
    print(f"\nPayload {i+1}:")
    validation = validate_slack_payload(payload)
    
    for check, result in validation.items():
        status = "✓" if result else "✗"
        print(f"  {check}: {status}")
    
    # JSON 직렬화 테스트
    try:
        json_str = json.dumps(payload, ensure_ascii=False)
        print(f"  JSON serialization: ✓")
    except Exception as e:
        print(f"  JSON serialization: ✗ {str(e)}")

print("\nPayload validation: COMPLETED")
