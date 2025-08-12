#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 분석 슬랙 리포터
일간/주간/월간 보고서를 슬랙으로 전송
"""

import os
import json
import requests
from datetime import datetime, timedelta
import subprocess
import sys

class SlackPlatformReporter:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            print("[경고] SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
            
    def send_to_slack(self, message: dict):
        """슬랙으로 메시지 전송"""
        if not self.webhook_url:
            print("[슬랙 미리보기]")
            print(json.dumps(message, ensure_ascii=False, indent=2))
            return True
            
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[오류] 슬랙 전송 실패: {e}")
            return False
    
    def run_analyzer(self, report_type: str) -> dict:
        """플랫폼 분석기 실행"""
        env = os.environ.copy()
        env['REPORT_TYPE'] = report_type
        
        try:
            # 분석기 실행
            result = subprocess.run(
                [sys.executable, 'firebase_platform_analyzer.py'],
                env=env,
                capture_output=True,
                text=True,
                cwd='C:\\claude03\\platform-analysis'
            )
            
            # 생성된 보고서 파일 읽기
            timestamp = datetime.now().strftime('%Y%m%d')
            report_file = f'C:\\claude03\\platform-analysis\\firebase_platform_report_{report_type}_{timestamp}*.json'
            
            import glob
            files = glob.glob(report_file)
            if files:
                with open(files[-1], 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        except Exception as e:
            print(f"[오류] 분석기 실행 실패: {e}")
            
        return None
    
    def format_daily_report(self, data: dict) -> dict:
        """일간 보고서 포맷"""
        summary = data.get('summary', {})
        top5 = data.get('top_5_platforms', [])[:5]
        
        # 플랫폼 리스트 생성
        platform_blocks = []
        for i, p in enumerate(top5, 1):
            online = p.get('online_players', 0)
            cash = p.get('cash_players', 0)
            share = p.get('market_share', 0)
            
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
            
            platform_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{i}. {p['name']}*\n"
                           f"• 온라인: *{online:,}명* ({share:.1f}%)\n"
                           f"• 캐시: *{cash:,}명*"
                }
            })
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 일간 플랫폼 분석 보고서"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{data.get('date', '')}* | 총 {summary.get('total_platforms', 0)}개 플랫폼 분석"
                        }
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🌍 전체 시장 현황*\n"
                               f"• 총 온라인: *{summary.get('total_online', 0):,}명*\n"
                               f"• 총 캐시: *{summary.get('total_cash', 0):,}명*\n"
                               f"• HHI 지수: *{summary.get('hhi', 0):.0f}* (시장 집중도)"
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🏆 TOP 5 플랫폼*"
                    }
                },
                *platform_blocks
            ]
        }
        
        return message
    
    def format_weekly_report(self, data: dict) -> dict:
        """주간 보고서 포맷"""
        changes = data.get('significant_changes', {})
        online_changes = changes.get('online_players', [])[:5]
        cash_changes = changes.get('cash_players', [])[:5]
        
        # 온라인 변화 블록
        online_blocks = []
        for p in online_changes:
            change = p.get('change_percent', 0)
            emoji = "📈" if change > 0 else "📉"
            color = "🟢" if change > 0 else "🔴"
            
            online_blocks.append(
                f"{emoji} *{p['platform']}*: {change:+.1f}% "
                f"({p.get('start_value', 0):,} → {p.get('end_value', 0):,})"
            )
        
        # 캐시 변화 블록
        cash_blocks = []
        for p in cash_changes:
            change = p.get('change_percent', 0)
            emoji = "📈" if change > 0 else "📉"
            
            cash_blocks.append(
                f"{emoji} *{p['platform']}*: {change:+.1f}% "
                f"({p.get('start_value', 0):,} → {p.get('end_value', 0):,})"
            )
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 주간 플랫폼 분석 보고서"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{data.get('period', '')}* | 주요 변화 분석"
                        }
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📈 온라인 플레이어 주요 변화*\n" + "\n".join(online_blocks[:3])
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💰 캐시 플레이어 주요 변화*\n" + "\n".join(cash_blocks[:3])
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 주간 시장 동향*\n"
                               f"• 전체 시장: {data.get('market_trend', {}).get('overall_change', 0):+.1f}%\n"
                               f"• 최대 성장: {data.get('market_trend', {}).get('biggest_gainer', 'N/A')}\n"
                               f"• 최대 하락: {data.get('market_trend', {}).get('biggest_loser', 'N/A')}"
                    }
                }
            ]
        }
        
        return message
    
    def format_monthly_report(self, data: dict) -> dict:
        """월간 보고서 포맷"""
        changes = data.get('significant_changes', {})
        analysis = data.get('relative_performance', {})
        
        # TOP 5 성장/하락 플랫폼
        top_gainers = []
        top_losers = []
        
        for p in changes.get('online_players', [])[:10]:
            change = p.get('change_percent', 0)
            if change > 0:
                top_gainers.append(p)
            else:
                top_losers.append(p)
        
        gainers_text = []
        for p in top_gainers[:3]:
            gainers_text.append(
                f"📈 *{p['platform']}*: {p.get('change_percent', 0):+.1f}% "
                f"({p.get('end_value', 0):,}명)"
            )
        
        losers_text = []
        for p in top_losers[:3]:
            losers_text.append(
                f"📉 *{p['platform']}*: {p.get('change_percent', 0):.1f}% "
                f"({p.get('end_value', 0):,}명)"
            )
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 월간 플랫폼 분석 보고서"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{data.get('period', '')}* | 월간 종합 분석"
                        }
                    ]
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🚀 월간 TOP 성장 플랫폼*\n" + "\n".join(gainers_text)
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*⚠️ 월간 TOP 하락 플랫폼*\n" + "\n".join(losers_text)
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📊 월간 시장 요약*\n"
                               f"• 전체 시장 변화: {data.get('market_summary', {}).get('total_change', 0):+.1f}%\n"
                               f"• 시장 집중도 변화: {data.get('market_summary', {}).get('hhi_change', 0):+.0f}\n"
                               f"• 활성 플랫폼 수: {data.get('market_summary', {}).get('active_platforms', 0)}개"
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💡 핵심 인사이트*\n{data.get('key_insights', '시장 분석 중...')}"
                    }
                }
            ]
        }
        
        return message
    
    def send_all_reports(self):
        """모든 보고서 전송"""
        reports = ['daily', 'weekly', 'monthly']
        
        for report_type in reports:
            print(f"\n{'='*60}")
            print(f"{report_type.upper()} 보고서 생성 중...")
            print(f"{'='*60}")
            
            # 분석기 실행
            data = self.run_analyzer(report_type)
            
            if data:
                # 포맷팅
                if report_type == 'daily':
                    message = self.format_daily_report(data)
                elif report_type == 'weekly':
                    message = self.format_weekly_report(data)
                else:
                    message = self.format_monthly_report(data)
                
                # 슬랙 전송
                if self.send_to_slack(message):
                    print(f"[OK] {report_type.upper()} 보고서 전송 완료")
                else:
                    print(f"[ERROR] {report_type.upper()} 보고서 전송 실패")
            else:
                print(f"[ERROR] {report_type.upper()} 데이터 생성 실패")

def main():
    """메인 실행"""
    reporter = SlackPlatformReporter()
    reporter.send_all_reports()
    
    print("\n" + "="*60)
    print("모든 보고서 처리 완료")
    print("="*60)

if __name__ == "__main__":
    main()