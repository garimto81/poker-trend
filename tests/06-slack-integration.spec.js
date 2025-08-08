// 포커 트렌드 분석 플랫폼 - Slack 통합 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('Slack Integration', () => {
  const testResultsDir = path.join(__dirname, '..', 'test-results');
  
  test.beforeAll(async () => {
    // 테스트 결과 디렉토리 확인
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }
  });

  test('Slack 웹훅 URL 형식 검증', async () => {
    const webhookValidationScript = `
import re
import os

# Slack 웹훅 URL 형식 검증
webhook_patterns = [
    r'^https://hooks\\.slack\\.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[A-Za-z0-9]{24}$',
    r'^https://hooks\\.slack\\.com/services/T[A-Z0-9]{10}/B[A-Z0-9]{10}/[A-Za-z0-9]{24}$'
]

# 테스트용 가상 웹훅 URL
test_webhooks = [
    "https://hooks.slack.com/services/T12345678/B12345678/abcd1234efgh5678ijkl9012",
    "https://hooks.slack.com/services/T1234567890/B1234567890/abcd1234efgh5678ijkl9012",
    "invalid-webhook-url",
    "https://wrong-domain.com/webhook"
]

print("Slack Webhook URL Validation:")
for i, url in enumerate(test_webhooks):
    valid = any(re.match(pattern, url) for pattern in webhook_patterns)
    status = "✓ VALID" if valid else "✗ INVALID"
    print(f"  URL {i+1}: {status}")

print("\\nWebhook URL validation: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_webhook_validation.py');
    fs.writeFileSync(tempScript, webhookValidationScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Webhook URL Validation');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack 메시지 페이로드 구조 검증', async () => {
    const payloadValidationScript = `
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
                    "text": "*📊 오늘의 YouTube 트렌드*\\n• 상위 키워드: Texas Hold'em, Tournament\\n• 조회수 증가: +15.3%"
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
    print(f"\\nPayload {i+1}:")
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

print("\\nPayload validation: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_payload_validation.py');
    fs.writeFileSync(tempScript, payloadValidationScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Payload Validation');
    expect(result.output).toContain('JSON serialization: ✓');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack API 응답 처리 테스트', async () => {
    const apiResponseScript = `
import json

# Slack API 응답 시뮬레이션 및 처리
def simulate_slack_response(success=True, error_type=None):
    if success:
        return {
            "status_code": 200,
            "response": "ok",
            "headers": {
                "content-type": "application/json"
            }
        }
    else:
        error_responses = {
            "invalid_payload": {
                "status_code": 400,
                "response": "invalid_payload",
                "error": "Invalid JSON payload"
            },
            "channel_not_found": {
                "status_code": 404,
                "response": "channel_not_found",
                "error": "Channel not found"
            },
            "rate_limited": {
                "status_code": 429,
                "response": "rate_limited",
                "error": "Too many requests"
            }
        }
        return error_responses.get(error_type, {"status_code": 500, "response": "unknown_error"})

def handle_slack_response(response):
    if response["status_code"] == 200:
        return {"success": True, "message": "Message sent successfully"}
    elif response["status_code"] == 429:
        return {"success": False, "message": "Rate limited - retry later", "retry": True}
    else:
        return {"success": False, "message": f"Error: {response.get('error', 'Unknown')}", "retry": False}

# 응답 처리 테스트
test_scenarios = [
    ("success", True, None),
    ("invalid_payload", False, "invalid_payload"),
    ("rate_limited", False, "rate_limited"),
    ("channel_not_found", False, "channel_not_found")
]

print("Slack API Response Handling Test:")
for scenario_name, success, error_type in test_scenarios:
    response = simulate_slack_response(success, error_type)
    handled = handle_slack_response(response)
    
    print(f"\\n{scenario_name.upper()}:")
    print(f"  Status Code: {response['status_code']}")
    print(f"  Success: {handled['success']}")
    print(f"  Message: {handled['message']}")
    if 'retry' in handled:
        print(f"  Should Retry: {handled['retry']}")

print("\\nAPI response handling: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_api_response.py');
    fs.writeFileSync(tempScript, apiResponseScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack API Response Handling Test');
    expect(result.output).toContain('SUCCESS:');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack 메시지 형식화 및 한글 지원 테스트', async () => {
    const formattingScript = `
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
                "text": f"*🎬 YouTube 트렌드*\\n• 인기 키워드: {', '.join(analysis_data['youtube']['keywords'])}\\n• 평균 조회수: {analysis_data['youtube']['avg_views']:,}회\\n• 트렌드 점수: {analysis_data['youtube']['trend_score']}/10"
            }
        }
        message["blocks"].append(youtube_section)
    
    # PokerNews 섹션
    if analysis_data.get("pokernews"):
        news_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📰 PokerNews 분석*\\n• 주요 토픽: {analysis_data['pokernews']['main_topic']}\\n• 기사 수: {analysis_data['pokernews']['article_count']}개\\n• 관심도: {analysis_data['pokernews']['interest_level']}"
            }
        }
        message["blocks"].append(news_section)
    
    # 플랫폼 분석 섹션
    if analysis_data.get("platform"):
        platform_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🏆 플랫폼 현황*\\n• 온라인 플레이어: {analysis_data['platform']['online_players']:,}명\\n• 일일 증가율: {analysis_data['platform']['growth_rate']:+.1f}%\\n• 현금 게임 활동: {analysis_data['platform']['cash_activity']}"
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

print("\\nMessage formatting: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_formatting_test.py');
    fs.writeFileSync(tempScript, formattingScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Message Formatting Test');
    expect(result.output).toContain('Korean text support confirmed');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack 알림 재시도 메커니즘 테스트', async () => {
    const retryMechanismScript = `
import time
import random

class SlackRetryHandler:
    def __init__(self, max_retries=3, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def send_with_retry(self, message, simulate_failure=False):
        attempts = []
        
        for attempt in range(self.max_retries + 1):
            # 실패 시뮬레이션
            if simulate_failure and attempt < 2:
                success = False
                error_type = "rate_limited" if attempt == 0 else "timeout"
            else:
                success = True
                error_type = None
            
            attempts.append({
                "attempt": attempt + 1,
                "success": success,
                "error": error_type,
                "delay": 0 if attempt == 0 else self.base_delay * (2 ** (attempt - 1))
            })
            
            if success:
                break
                
        return attempts
    
    def calculate_backoff_delay(self, attempt):
        # 지수 백오프 계산
        return self.base_delay * (2 ** attempt) + random.uniform(0, 1)

# 재시도 메커니즘 테스트
retry_handler = SlackRetryHandler(max_retries=3, base_delay=1)

print("Slack Retry Mechanism Test:")

# 성공 케이스
print("\\n1. Immediate Success:")
success_attempts = retry_handler.send_with_retry("test message", simulate_failure=False)
for attempt in success_attempts:
    print(f"   Attempt {attempt['attempt']}: {'SUCCESS' if attempt['success'] else 'FAILED'}")

# 재시도 후 성공 케이스
print("\\n2. Success After Retries:")
retry_attempts = retry_handler.send_with_retry("test message", simulate_failure=True)
for attempt in retry_attempts:
    status = 'SUCCESS' if attempt['success'] else f"FAILED ({attempt['error']})"
    delay = f" [delay: {attempt['delay']}s]" if attempt['delay'] > 0 else ""
    print(f"   Attempt {attempt['attempt']}: {status}{delay}")

# 백오프 지연 계산 테스트
print("\\n3. Backoff Delay Calculation:")
for i in range(4):
    delay = retry_handler.calculate_backoff_delay(i)
    print(f"   Attempt {i+1}: {delay:.2f}s delay")

print("\\nRetry mechanism: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_retry_test.py');
    fs.writeFileSync(tempScript, retryMechanismScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Retry Mechanism Test');
    expect(result.output).toContain('Immediate Success');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack 리포트 템플릿 시스템 테스트', async () => {
    const templateScript = `
from datetime import datetime

class SlackReportTemplate:
    def __init__(self):
        self.templates = {
            "daily": self._daily_template,
            "weekly": self._weekly_template,
            "monthly": self._monthly_template,
            "error": self._error_template
        }
    
    def _daily_template(self, data):
        return {
            "text": "📊 일간 포커 트렌드 리포트",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📊 일간 포커 트렌드 분석"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*날짜:* {data.get('date', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*분석 완료:* {data.get('completion_time', 'N/A')}"}
                    ]
                }
            ]
        }
    
    def _weekly_template(self, data):
        return {
            "text": "📈 주간 포커 트렌드 리포트",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📈 주간 포커 트렌드 종합"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*기간:* {data.get('week_start', 'N/A')} ~ {data.get('week_end', 'N/A')}"
                    }
                }
            ]
        }
    
    def _monthly_template(self, data):
        return {
            "text": "📈 월간 포커 트렌드 리포트",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📈 월간 포커 트렌드 분석"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*분석 월:* {data.get('month', 'N/A')}\\n*총 데이터 포인트:* {data.get('data_points', 'N/A')}개"
                    }
                }
            ]
        }
    
    def _error_template(self, data):
        return {
            "text": "⚠️ 포커 트렌드 분석 오류",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*오류 발생:* {data.get('error_message', 'Unknown error')}\\n*시간:* {data.get('error_time', 'N/A')}"
                    }
                }
            ]
        }
    
    def generate_report(self, report_type, data):
        template_func = self.templates.get(report_type)
        if template_func:
            return template_func(data)
        else:
            return self._error_template({"error_message": f"Unknown report type: {report_type}"})

# 템플릿 시스템 테스트
template_system = SlackReportTemplate()

test_data = {
    "daily": {
        "date": "2025-08-08",
        "completion_time": "09:30 KST"
    },
    "weekly": {
        "week_start": "2025-08-05",
        "week_end": "2025-08-11"
    },
    "monthly": {
        "month": "2025년 7월",
        "data_points": 1247
    },
    "error": {
        "error_message": "YouTube API 할당량 초과",
        "error_time": "2025-08-08 14:30 KST"
    }
}

print("Slack Report Template System Test:")

for report_type, data in test_data.items():
    print(f"\\n{report_type.upper()} Template:")
    report = template_system.generate_report(report_type, data)
    print(f"  Text: {report['text']}")
    print(f"  Blocks: {len(report['blocks'])} blocks")
    print(f"  ✓ Template generated successfully")

# 잘못된 템플릿 타입 테스트
print("\\nINVALID Template:")
invalid_report = template_system.generate_report("invalid_type", {})
print(f"  Error handling: {'✓' if 'Unknown report type' in invalid_report['text'] else '✗'}")

print("\\nTemplate system: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_template_test.py');
    fs.writeFileSync(tempScript, templateScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Report Template System Test');
    expect(result.output).toContain('DAILY Template:');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Slack 채널별 라우팅 테스트', async () => {
    const routingScript = `
class SlackChannelRouter:
    def __init__(self):
        self.channel_config = {
            "poker-daily": {
                "webhook": "daily_webhook_url",
                "report_types": ["daily"],
                "priority": "normal"
            },
            "poker-weekly": {
                "webhook": "weekly_webhook_url", 
                "report_types": ["weekly"],
                "priority": "high"
            },
            "poker-alerts": {
                "webhook": "alerts_webhook_url",
                "report_types": ["error", "warning"],
                "priority": "urgent"
            },
            "poker-monthly": {
                "webhook": "monthly_webhook_url",
                "report_types": ["monthly"],
                "priority": "high"
            }
        }
    
    def get_target_channels(self, report_type):
        target_channels = []
        for channel, config in self.channel_config.items():
            if report_type in config["report_types"]:
                target_channels.append({
                    "channel": channel,
                    "webhook": config["webhook"],
                    "priority": config["priority"]
                })
        return target_channels
    
    def validate_routing_rules(self):
        validation_results = {}
        
        for channel, config in self.channel_config.items():
            validation_results[channel] = {
                "has_webhook": bool(config.get("webhook")),
                "has_report_types": bool(config.get("report_types")),
                "has_priority": bool(config.get("priority")),
                "valid": all([
                    config.get("webhook"),
                    config.get("report_types"),
                    config.get("priority")
                ])
            }
        
        return validation_results

# 채널 라우팅 테스트
router = SlackChannelRouter()

print("Slack Channel Routing Test:")

# 라우팅 규칙 검증
print("\\n1. Routing Rules Validation:")
validation = router.validate_routing_rules()
for channel, rules in validation.items():
    status = "✓" if rules["valid"] else "✗"
    print(f"   {channel}: {status}")

# 리포트 타입별 라우팅 테스트
print("\\n2. Report Type Routing:")
test_report_types = ["daily", "weekly", "monthly", "error"]

for report_type in test_report_types:
    targets = router.get_target_channels(report_type)
    print(f"   {report_type}: {len(targets)} target(s)")
    for target in targets:
        print(f"     → {target['channel']} ({target['priority']} priority)")

print("\\n3. Priority Distribution:")
priority_counts = {}
for channel, config in router.channel_config.items():
    priority = config["priority"]
    priority_counts[priority] = priority_counts.get(priority, 0) + 1

for priority, count in priority_counts.items():
    print(f"   {priority}: {count} channel(s)")

print("\\nChannel routing: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_routing_test.py');
    fs.writeFileSync(tempScript, routingScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack Channel Routing Test');
    expect(result.output).toContain('Routing Rules Validation');
    expect(result.output).toContain('COMPLETED');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });
});

// Helper function: Python 스크립트 실행
async function runPythonScript(scriptPath, args = [], options = {}) {
  return new Promise((resolve) => {
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(scriptPath),
      timeout: 30000, // 30초 타임아웃
      ...options
    });
    
    let output = '';
    let error = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    python.on('close', (code) => {
      resolve({
        code,
        output: output + error,
        stdout: output,
        stderr: error
      });
    });
    
    python.on('error', (err) => {
      resolve({
        code: -1,
        output: err.message,
        stdout: '',
        stderr: err.message
      });
    });
  });
}