#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNG 파일을 Slack 채널에 직접 업로드하는 플랫폼 분석 보고서
"""

import requests
import os
from datetime import datetime

class SlackPNGReporter:
    def __init__(self):
        # Slack Bot Token (환경변수에서 가져오기)
        self.bot_token = os.getenv('SLACK_BOT_TOKEN', 'your-bot-token-here')
        self.channel = "#poker-analysis"  # 또는 채널 ID
        
        # 웹훅 URL (텍스트 메시지용, 환경변수에서 가져오기)
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
    
    def upload_png_to_slack(self, file_path, title, initial_comment=""):
        """PNG 파일을 Slack에 업로드"""
        if not os.path.exists(file_path):
            print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
            return False
        
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
                'initial_comment': initial_comment,
                'filetype': 'png'
            }
            
            try:
                response = requests.post(url, headers=headers, files=files, data=data)
                result = response.json()
                
                if result.get('ok'):
                    print(f"[OK] PNG 업로드 성공: {title}")
                    return True
                else:
                    print(f"[ERROR] PNG 업로드 실패: {result.get('error', 'Unknown error')}")
                    return False
                    
            except Exception as e:
                print(f"[ERROR] PNG 업로드 중 오류: {e}")
                return False
    
    def send_text_report(self, blocks, report_type):
        """텍스트 보고서만 웹훅으로 전송"""
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print(f"[OK] {report_type} 텍스트 보고서 전송 완료")
                return True
            else:
                print(f"[ERROR] {report_type} 텍스트 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {report_type} 텍스트 전송 오류: {e}")
            return False
    
    def send_daily_with_png(self):
        """일간 보고서 - PNG 없음"""
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
                    "text": f"*기간:* 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n*[온라인 플레이어]* 168,706명\n• GGNetwork: 153,008명 (89.1%)\n• IDNPoker: 5,528명 (3.2%)\n• WPT Global: 5,237명 (3.1%)\n\n*[캐시 플레이어]* 16,921명\n• GGNetwork: 10,404명 (61.5%)\n• WPT Global: 3,019명 (17.8%)\n• IDNPoker: 1,400명 (8.3%)"
                }
            }
        ]
        
        return self.send_text_report(blocks, "일간")
    
    def send_weekly_with_png(self):
        """주간 보고서 - PNG 포함"""
        # 1. PNG 업로드
        png_uploaded = self.upload_png_to_slack(
            "weekly_stacked_area.png",
            "주간 플랫폼 트렌드 (8/4-8/10)",
            "📊 [주간] 플랫폼 분석 차트 - 누적 영역형으로 트렌드 시각화"
        )
        
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
                    "text": f"*기간:* 2025-08-04 ~ 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n*[온라인 플레이어]*\n• 총 변화: 189,421 → 168,706 (-10.9%)\n• 시장 리더: GGNetwork (89.1%)\n• 주요 감소: IDNPoker (-43.8%), Pokerdom (-31.3%)\n\n*[캐시 플레이어]*\n• 총 변화: 18,234 → 16,921 (-7.2%)\n• 시장 리더: GGNetwork (61.5%)\n• 주요 감소: IDNPoker (-35.1%), Pokerdom (-32.5%)"
                }
            }
        ]
        
        text_sent = self.send_text_report(blocks, "주간")
        return png_uploaded and text_sent
    
    def send_monthly_with_png(self):
        """월간 보고서 - PNG 포함"""
        # 1. PNG 업로드
        png_uploaded = self.upload_png_to_slack(
            "monthly_stacked_area.png",
            "월간 플랫폼 트렌드 (7/30-8/10)",
            "📈 [월간] 플랫폼 분석 차트 - 12일간 누적 영역형 트렌드"
        )
        
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
                    "text": f"*기간:* 2025-07-30 ~ 2025-08-10 (12일)\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n*[온라인 플레이어]*\n• 총 변화: 306,234 → 168,706 (-44.9%)\n• 리더 진화: GGNetwork 65% → 89.1%\n• 주요 이벤트: 8/3 이후 Others 급감\n\n*[캐시 플레이어]*\n• 총 변화: 28,456 → 16,921 (-40.5%)\n• 리더 진화: GGNetwork 58.2% → 61.5%\n• 주요 이벤트: 전반적 하향 추세"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*[핵심 분석]*\n• 전체 시장 약 45% 축소\n• GGNetwork 양 시장 지배력 강화\n• Others 카테고리 급격한 변동\n• 소규모 플랫폼 지속 감소"
                }
            }
        ]
        
        text_sent = self.send_text_report(blocks, "월간")
        return png_uploaded and text_sent

def main():
    """메인 실행"""
    print("=" * 60)
    print("PNG 파일 포함 플랫폼 분석 보고서 전송")
    print("=" * 60)
    
    reporter = SlackPNGReporter()
    
    print("\n[참고] Slack Bot Token 설정 필요")
    print("현재는 테스트 토큰으로 설정되어 있습니다.")
    
    print("\n1. 일간 보고서 전송...")
    reporter.send_daily_with_png()
    
    print("\n2. 주간 보고서 + PNG 전송...")
    reporter.send_weekly_with_png()
    
    print("\n3. 월간 보고서 + PNG 전송...")
    reporter.send_monthly_with_png()
    
    print("\n" + "=" * 60)
    print("PNG 포함 보고서 전송 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()