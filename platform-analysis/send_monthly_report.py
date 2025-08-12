#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
월간 플랫폼 분석 보고서 Slack 전송 (누적 영역형 차트 포함)
"""

import requests
import json
import base64
from datetime import datetime

class MonthlySlackReporter:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
        self.chart_path = "monthly_stacked_area.png"
        
        # 월간 데이터 (7/30-8/10)
        self.monthly_data = {
            'period': '2025-07-30 ~ 2025-08-10',
            'online': {
                'start': 306234,
                'end': 168706,
                'change': -44.9,
                'leader_evolution': 'GGNetwork: 65.0% → 89.1%',
                'market_concentration': '상당히 증가',
                'major_events': [
                    '8/3 이후 Others 플랫폼 급격한 감소',
                    'GGNetwork 시장지배력 강화',
                    'IDNPoker 지속적 하락 추세'
                ]
            },
            'cash': {
                'start': 28456,
                'end': 16921,
                'change': -40.5,
                'leader_evolution': 'GGNetwork: 58.2% → 61.5%',
                'market_concentration': '점진적 증가',
                'major_events': [
                    'WPT Global 상대적 안정성 유지',
                    '전체적인 하향 추세',
                    'Pokerdom 캐시 시장 축소'
                ]
            }
        }
    
    def create_monthly_blocks(self):
        """월간 보고서 Slack 블록 생성"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[월간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* {self.monthly_data['period']} (12일)\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # 온라인 플레이어 섹션
        online = self.monthly_data['online']
        online_text = f"*총 변화:* {online['start']:,} → {online['end']:,} ({online['change']:+.1f}%)\n"
        online_text += f"*리더 진화:* {online['leader_evolution']}\n"
        online_text += f"*시장 집중도:* {online['market_concentration']}\n\n"
        online_text += "*주요 이벤트:*\n"
        
        for event in online['major_events']:
            online_text += f"• {event}\n"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*[온라인 플레이어]*\n{online_text}"
            }
        })
        
        # 캐시 플레이어 섹션
        cash = self.monthly_data['cash']
        cash_text = f"*총 변화:* {cash['start']:,} → {cash['end']:,} ({cash['change']:+.1f}%)\n"
        cash_text += f"*리더 진화:* {cash['leader_evolution']}\n"
        cash_text += f"*시장 집중도:* {cash['market_concentration']}\n\n"
        cash_text += "*주요 이벤트:*\n"
        
        for event in cash['major_events']:
            cash_text += f"• {event}\n"
        
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
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[분석 요약]*\n• 전체 시장 규모 약 45% 축소\n• GGNetwork 양 시장에서 지배력 강화\n• 소규모 플랫폼들의 지속적 감소\n• Others 카테고리의 급격한 변동 후 안정화"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"[차트] {self.chart_path} | 12일간 누적 영역형 트렌드 분석"
                    }
                ]
            }
        ])
        
        return blocks
    
    def send_monthly_report(self):
        """월간 보고서 전송"""
        blocks = self.create_monthly_blocks()
        
        payload = {
            "blocks": blocks
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("[OK] 월간 플랫폼 분석 보고서 Slack 전송 완료")
                print(f"    - 온라인: {self.monthly_data['online']['start']:,} → {self.monthly_data['online']['end']:,} ({self.monthly_data['online']['change']:+.1f}%)")
                print(f"    - 캐시: {self.monthly_data['cash']['start']:,} → {self.monthly_data['cash']['end']:,} ({self.monthly_data['cash']['change']:+.1f}%)")
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
    print("월간 플랫폼 분석 보고서 Slack 전송")
    print("=" * 60)
    
    reporter = MonthlySlackReporter()
    success = reporter.send_monthly_report()
    
    if success:
        print("\n[완료] 월간 보고서가 Slack으로 전송되었습니다.")
    else:
        print("\n[실패] 보고서 전송에 실패했습니다.")

if __name__ == "__main__":
    main()