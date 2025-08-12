#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 플랫폼 분석 보고서 Slack 전송 (누적 영역형 차트 포함)
"""

import requests
import json
import base64
from datetime import datetime

class WeeklySlackReporter:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
        self.chart_path = "weekly_stacked_area.png"
        
        # 주간 데이터 (8/4-8/10)
        self.weekly_data = {
            'period': '2025-08-04 ~ 2025-08-10',
            'online': {
                'start': 189421,
                'end': 168706,
                'change': -10.9,
                'leader': 'GGNetwork',
                'leader_share': 89.1,
                'top_changes': [
                    ('IDNPoker', -43.8),
                    ('Pokerdom', -31.3),
                    ('WPT Global', -30.4),
                    ('Chico', -39.2),
                    ('GGNetwork', -7.4)
                ]
            },
            'cash': {
                'start': 18234,
                'end': 16921,
                'change': -7.2,
                'leader': 'GGNetwork',
                'leader_share': 61.5,
                'top_changes': [
                    ('IDNPoker', -35.1),
                    ('Pokerdom', -32.5),
                    ('WPT Global', -14.2),
                    ('Chico', -37.6),
                    ('GGNetwork', -7.4)
                ]
            }
        }
    
    def create_weekly_blocks(self):
        """주간 보고서 Slack 블록 생성"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[주간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* {self.weekly_data['period']}\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # 온라인 플레이어 섹션
        online = self.weekly_data['online']
        online_text = f"*총 변화:* {online['start']:,} → {online['end']:,} ({online['change']:+.1f}%)\n"
        online_text += f"*시장 리더:* {online['leader']} ({online['leader_share']:.1f}%)\n\n"
        online_text += "*주요 플랫폼 변화:*\n"
        
        for platform, change in online['top_changes']:
            emoji = "📈" if change > 0 else "📉"
            online_text += f"{emoji} {platform}: {change:+.1f}%\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*[온라인 플레이어]*\n{online_text}"
            }
        })
        
        # 캐시 플레이어 섹션
        cash = self.weekly_data['cash']
        cash_text = f"*총 변화:* {cash['start']:,} → {cash['end']:,} ({cash['change']:+.1f}%)\n"
        cash_text += f"*시장 리더:* {cash['leader']} ({cash['leader_share']:.1f}%)\n\n"
        cash_text += "*주요 플랫폼 변화:*\n"
        
        for platform, change in cash['top_changes']:
            emoji = "📈" if change > 0 else "📉"
            cash_text += f"{emoji} {platform}: {change:+.1f}%\n"
        
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
                        "text": f"[차트] {self.chart_path} | 누적 영역형 차트로 트렌드 시각화"
                    }
                ]
            }
        ])
        
        return blocks
    
    def send_weekly_report(self):
        """주간 보고서 전송"""
        blocks = self.create_weekly_blocks()
        
        payload = {
            "blocks": blocks
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("[OK] 주간 플랫폼 분석 보고서 Slack 전송 완료")
                print(f"    - 온라인: {self.weekly_data['online']['start']:,} → {self.weekly_data['online']['end']:,} ({self.weekly_data['online']['change']:+.1f}%)")
                print(f"    - 캐시: {self.weekly_data['cash']['start']:,} → {self.weekly_data['cash']['end']:,} ({self.weekly_data['cash']['change']:+.1f}%)")
                print(f"    - 차트: {self.chart_path}")
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
    print("주간 플랫폼 분석 보고서 Slack 전송")
    print("=" * 60)
    
    reporter = WeeklySlackReporter()
    success = reporter.send_weekly_report()
    
    if success:
        print("\n[완료] 주간 보고서가 Slack으로 전송되었습니다.")
    else:
        print("\n[실패] 보고서 전송에 실패했습니다.")

if __name__ == "__main__":
    main()