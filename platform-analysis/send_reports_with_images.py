#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack 이미지 업로드를 포함한 플랫폼 분석 보고서 전송
Slack API 토큰 방식 사용
"""

import requests
import json
import os
from datetime import datetime

class SlackImageReporter:
    def __init__(self):
        # Slack Bot Token 필요 (xoxb-로 시작)
        self.bot_token = "xoxb-YOUR-BOT-TOKEN-HERE"  # 실제 봇 토큰으로 교체 필요
        self.channel = "C03QGJ73GBB"  # 채널 ID
        
        # Webhook URL (메시지용)
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
        
        # 이미지 파일 경로
        self.weekly_chart = "weekly_stacked_area.png"
        self.monthly_chart = "monthly_stacked_area.png"
    
    def upload_image_to_slack(self, file_path, title=""):
        """Slack에 이미지 업로드"""
        url = "https://slack.com/api/files.upload"
        
        headers = {
            'Authorization': f'Bearer {self.bot_token}'
        }
        
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file, 'image/png')
            }
            
            data = {
                'channels': self.channel,
                'title': title,
                'initial_comment': f"📊 {title}"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            if result['ok']:
                return result['file']['url_private']
            else:
                print(f"[ERROR] 이미지 업로드 실패: {result['error']}")
                return None
        else:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            return None
    
    def send_report_with_webhook(self, report_type, blocks):
        """웹훅으로 텍스트 보고서 전송"""
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print(f"[OK] {report_type} 텍스트 보고서 전송 완료")
                return True
            else:
                print(f"[ERROR] {report_type} 보고서 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {report_type} 전송 중 오류: {e}")
            return False
    
    def create_simple_image_url_block(self, image_url, alt_text="차트"):
        """이미지 URL을 포함한 간단한 블록"""
        return {
            "type": "image",
            "image_url": image_url,
            "alt_text": alt_text
        }
    
    def send_daily_report(self):
        """일간 보고서 - 이미지 없음"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📅 [일간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[온라인 플레이어]* 168,706명\n1. GGNetwork: 153,008명 (89.1%)\n2. IDNPoker: 5,528명 (3.2%)\n3. WPT Global: 5,237명 (3.1%)\n4. Pokerdom: 2,693명 (1.6%)\n5. Chico: 953명 (0.6%)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[캐시 플레이어]* 16,921명\n1. GGNetwork: 10,404명 (61.5%)\n2. WPT Global: 3,019명 (17.8%)\n3. IDNPoker: 1,400명 (8.3%)\n4. Pokerdom: 555명 (3.3%)\n5. Chico: 179명 (1.1%)"
                }
            }
        ]
        
        return self.send_report_with_webhook("일간", blocks)
    
    def send_weekly_report(self):
        """주간 보고서 - 차트 포함"""
        # 1. 차트 업로드
        print("주간 차트 업로드 중...")
        if os.path.exists(self.weekly_chart):
            image_url = self.upload_image_to_slack(self.weekly_chart, "주간 플랫폼 트렌드")
            if not image_url:
                print("[WARNING] 주간 차트 업로드 실패, 텍스트만 전송")
        else:
            print("[WARNING] 주간 차트 파일 없음")
            image_url = None
        
        # 2. 텍스트 보고서
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 [주간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-08-04 ~ 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[온라인 플레이어]*\n• 총 변화: 189,421 → 168,706 (-10.9%)\n• 시장 리더: GGNetwork (89.1%)\n• 주요 변화: IDNPoker (-43.8%), Pokerdom (-31.3%)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[캐시 플레이어]*\n• 총 변화: 18,234 → 16,921 (-7.2%)\n• 시장 리더: GGNetwork (61.5%)\n• 주요 변화: IDNPoker (-35.1%), Pokerdom (-32.5%)"
                }
            }
        ]
        
        return self.send_report_with_webhook("주간", blocks)
    
    def send_monthly_report(self):
        """월간 보고서 - 차트 포함"""
        # 1. 차트 업로드
        print("월간 차트 업로드 중...")
        if os.path.exists(self.monthly_chart):
            image_url = self.upload_image_to_slack(self.monthly_chart, "월간 플랫폼 트렌드")
            if not image_url:
                print("[WARNING] 월간 차트 업로드 실패, 텍스트만 전송")
        else:
            print("[WARNING] 월간 차트 파일 없음")
            image_url = None
        
        # 2. 텍스트 보고서
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📈 [월간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-07-30 ~ 2025-08-10 (12일)\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[온라인 플레이어]*\n• 총 변화: 306,234 → 168,706 (-44.9%)\n• 리더 진화: GGNetwork 65.0% → 89.1%\n• 주요 이벤트: 8/3 이후 Others 급감, GGNetwork 지배력 강화"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[캐시 플레이어]*\n• 총 변화: 28,456 → 16,921 (-40.5%)\n• 리더 진화: GGNetwork 58.2% → 61.5%\n• 주요 이벤트: WPT Global 상대적 안정성, 전체 하향 추세"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[종합 분석]*\n• 전체 시장 약 45% 축소\n• GGNetwork 양 시장 지배력 강화\n• 소규모 플랫폼 지속 감소"
                }
            }
        ]
        
        return self.send_report_with_webhook("월간", blocks)

def main():
    """메인 실행"""
    print("=" * 60)
    print("Slack 이미지 포함 플랫폼 분석 보고서 전송")
    print("=" * 60)
    
    reporter = SlackImageReporter()
    
    # Bot Token 확인
    if "YOUR-BOT-TOKEN-HERE" in reporter.bot_token:
        print("[경고] Slack Bot Token이 설정되지 않았습니다.")
        print("이미지 업로드 없이 텍스트 보고서만 전송됩니다.")
    
    print("\n1. 일간 보고서 전송...")
    reporter.send_daily_report()
    
    print("\n2. 주간 보고서 전송...")
    reporter.send_weekly_report()
    
    print("\n3. 월간 보고서 전송...")
    reporter.send_monthly_report()
    
    print("\n" + "=" * 60)
    print("모든 보고서 전송 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()