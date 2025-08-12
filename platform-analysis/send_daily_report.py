#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일간 플랫폼 분석 보고서 Slack 전송
"""

import requests
import json
from datetime import datetime

class DailySlackReporter:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
        
        # 일간 데이터 (2025-08-10)
        self.daily_data = {
            'date': '2025-08-10',
            'online': {
                'total': 168706,
                'platforms': {
                    'GGNetwork': {'count': 153008, 'share': 89.1},
                    'IDNPoker': {'count': 5528, 'share': 3.2},
                    'WPT Global': {'count': 5237, 'share': 3.1},
                    'Pokerdom': {'count': 2693, 'share': 1.6},
                    'Chico': {'count': 953, 'share': 0.6}
                }
            },
            'cash': {
                'total': 16921,
                'platforms': {
                    'GGNetwork': {'count': 10404, 'share': 61.5},
                    'WPT Global': {'count': 3019, 'share': 17.8},
                    'IDNPoker': {'count': 1400, 'share': 8.3},
                    'Pokerdom': {'count': 555, 'share': 3.3},
                    'Chico': {'count': 179, 'share': 1.1}
                }
            }
        }
    
    def create_daily_blocks(self):
        """일간 보고서 Slack 블록 생성"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[일간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* {self.daily_data['date']}\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # 온라인 플레이어 섹션
        online_text = f"*총 플레이어:* {self.daily_data['online']['total']:,}명\n\n"
        online_text += "*상위 5개 플랫폼:*\n"
        
        for i, (platform, data) in enumerate(self.daily_data['online']['platforms'].items(), 1):
            online_text += f"{i}. {platform}: {data['count']:,}명 ({data['share']:.1f}%)\n"
        
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*[온라인 플레이어]*\n{online_text}"
                }
            }
        ])
        
        # 캐시 플레이어 섹션
        cash_text = f"*총 플레이어:* {self.daily_data['cash']['total']:,}명\n\n"
        cash_text += "*상위 5개 플랫폼:*\n"
        
        for i, (platform, data) in enumerate(self.daily_data['cash']['platforms'].items(), 1):
            cash_text += f"{i}. {platform}: {data['count']:,}명 ({data['share']:.1f}%)\n"
        
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*[캐시 플레이어]*\n{cash_text}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "[INFO] 일간 보고서는 차트 미포함 | 데이터 소스: Firebase 실시간 수집"
                    }
                ]
            }
        ])
        
        return blocks
    
    def send_daily_report(self):
        """일간 보고서 전송"""
        blocks = self.create_daily_blocks()
        
        payload = {
            "blocks": blocks
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("[OK] 일간 플랫폼 분석 보고서 Slack 전송 완료")
                print(f"    - 온라인 플레이어: {self.daily_data['online']['total']:,}명")
                print(f"    - 캐시 플레이어: {self.daily_data['cash']['total']:,}명")
                print(f"    - 온라인 리더: GGNetwork ({self.daily_data['online']['platforms']['GGNetwork']['share']:.1f}%)")
                print(f"    - 캐시 리더: GGNetwork ({self.daily_data['cash']['platforms']['GGNetwork']['share']:.1f}%)")
                return True
            else:
                print(f"[ERROR] Slack 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] 전송 중 오류: {e}")
            return False

def main():
    """메인 실행"""
    print("=" * 60)
    print("일간 플랫폼 분석 보고서 Slack 전송")
    print("=" * 60)
    
    reporter = DailySlackReporter()
    success = reporter.send_daily_report()
    
    if success:
        print("\n[완료] 일간 보고서가 Slack으로 전송되었습니다.")
    else:
        print("\n[실패] 보고서 전송에 실패했습니다.")

if __name__ == "__main__":
    main()