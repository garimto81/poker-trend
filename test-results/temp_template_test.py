
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
                        "text": f"*분석 월:* {data.get('month', 'N/A')}\n*총 데이터 포인트:* {data.get('data_points', 'N/A')}개"
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
                        "text": f"*오류 발생:* {data.get('error_message', 'Unknown error')}\n*시간:* {data.get('error_time', 'N/A')}"
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
    print(f"\n{report_type.upper()} Template:")
    report = template_system.generate_report(report_type, data)
    print(f"  Text: {report['text']}")
    print(f"  Blocks: {len(report['blocks'])} blocks")
    print(f"  ✓ Template generated successfully")

# 잘못된 템플릿 타입 테스트
print("\nINVALID Template:")
invalid_report = template_system.generate_report("invalid_type", {})
print(f"  Error handling: {'✓' if 'Unknown report type' in invalid_report['text'] else '✗'}")

print("\nTemplate system: COMPLETED")
