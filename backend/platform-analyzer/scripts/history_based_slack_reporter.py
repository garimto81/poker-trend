#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History-based Slack Reporter
자체 히스토리 데이터를 기반으로 정확한 트렌드 분석을 Slack에 전송
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any

# Import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from history_based_analyzer import HistoryBasedAnalyzer

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoryBasedSlackReporter:
    def __init__(self, webhook_url: str, db_path: str = "poker_history.db"):
        self.webhook_url = webhook_url
        self.analyzer = HistoryBasedAnalyzer(db_path)
        
    def create_history_based_message(self, analysis_result: Dict, analysis_type: str) -> Dict:
        """Create Slack message based on historical analysis"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        alert_level = analysis_result.get('alert_level', 'none')
        
        # Determine message style based on alert level
        if alert_level == 'high':
            title_emoji = "🚨"
            title_text = "긴급 알림 - 포커 플랫폼 트렌드 분석"
            color = "#ff4444"
        elif alert_level == 'medium':
            title_emoji = "⚠️"
            title_text = "주의 - 포커 플랫폼 트렌드 분석"
            color = "#ffaa00"
        elif alert_level == 'low':
            title_emoji = "📊"
            title_text = "포커 플랫폼 트렌드 분석"
            color = "#4CAF50"
        else:
            title_emoji = "✅"
            title_text = "포커 플랫폼 안정 - 트렌드 분석"
            color = "#2196F3"
        
        # Build message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{title_emoji} {title_text}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {current_time} KST | 📊 {analysis_type.upper()} 분석 | 🏦 자체 히스토리 데이터 기반"
                    }
                ]
            }
        ]
        
        # Add summary section
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📋 분석 요약*\n{analysis_result['summary_text']}"
                }
            },
            {
                "type": "divider"
            }
        ])
        
        # Add market metrics
        metrics = analysis_result['market_metrics']
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*🌐 현재 총 플레이어*\n{metrics['total_online']:,}명"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*📈 시장 성장률*\n{metrics['market_growth']:+.2f}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🔬 분석된 플랫폼*\n{metrics['platforms_analyzed']}개"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*✅ 신뢰도*\n{metrics['reliable_comparisons']}/{metrics['platforms_analyzed']} 플랫폼"
                }
            ]
        })
        
        # Add significant changes if any
        significant_changes = analysis_result.get('significant_changes', [])
        if significant_changes:
            blocks.extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🚨 주요 변화 ({len(significant_changes)}개 플랫폼)*"
                    }
                }
            ])
            
            changes_text = ""
            for change in significant_changes[:8]:  # Top 8 changes
                direction_icon = "🚀" if change['direction'] == 'up' else "📉"
                severity_icon = "⚠️" if change['severity'] == 'extreme' else "📊"
                
                changes_text += f"{direction_icon}{severity_icon} *{change['platform']}*: {change['growth_rate']:+.1f}% "
                changes_text += f"({change['current']:,} ← {change['historical']:,})\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": changes_text.strip()
                }
            })
        
        # Add growing platforms
        growing_platforms = analysis_result.get('growing_platforms', [])
        declining_platforms = analysis_result.get('declining_platforms', [])
        
        if growing_platforms or declining_platforms:
            blocks.append({
                "type": "divider"
            })
            
            if growing_platforms:
                growing_text = "*📈 성장 플랫폼*\n"
                for platform, growth, current in growing_platforms[:5]:
                    growing_text += f"🟢 {platform}: +{growth:.1f}% ({current:,}명)\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": growing_text.strip()
                    }
                })
            
            if declining_platforms:
                declining_text = "*📉 하락 플랫폼*\n"
                for platform, growth, current in declining_platforms[:5]:
                    declining_text += f"🔴 {platform}: {growth:.1f}% ({current:,}명)\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": declining_text.strip()
                    }
                })
        
        # Add data quality info
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🔍 히스토리 기반 분석 | 안정적 플랫폼: {analysis_result.get('stable_platforms', 0)}개 | "
                        f"임계값: {analysis_result.get('thresholds_used', {}).get('major', 'N/A')}% | "
                        f"🤖 Generated by History-based Poker Analyzer"
                    }
                ]
            }
        ])
        
        return {
            "text": f"{title_emoji} {title_text}",
            "blocks": blocks,
            "color": color
        }
    
    def send_analysis_report(self, analysis_type: str = 'weekly', user_approval: bool = False) -> bool:
        """Send history-based analysis report to Slack"""
        logger.info(f"📊 히스토리 기반 {analysis_type} 분석 리포트 준비")
        
        if not user_approval:
            logger.warning("⚠️ 사용자 승인 없이는 Slack 전송을 하지 않습니다")
            return False
        
        try:
            # Perform analysis
            analysis_result = self.analyzer.analyze_with_history(analysis_type)
            
            if not analysis_result:
                logger.error("❌ 분석 결과 없음")
                return False
            
            # Create Slack message
            message = self.create_history_based_message(analysis_result, analysis_type)
            
            # Preview message
            print("=" * 80)
            print("📋 SLACK 메시지 미리보기")
            print("=" * 80)
            print(f"제목: {message['text']}")
            print(f"블록 수: {len(message['blocks'])}개")
            print(f"경고 수준: {analysis_result.get('alert_level', 'none')}")
            
            # Show key metrics
            metrics = analysis_result['market_metrics']
            print(f"\n📊 주요 지표:")
            print(f"- 현재 총 플레이어: {metrics['total_online']:,}명")
            print(f"- 시장 성장률: {metrics['market_growth']:+.2f}%")
            print(f"- 주요 변화: {len(analysis_result.get('significant_changes', []))}개 플랫폼")
            print(f"- 신뢰도: {metrics['reliable_comparisons']}/{metrics['platforms_analyzed']} 플랫폼")
            
            if analysis_result.get('significant_changes'):
                print(f"\n🚨 주요 변화:")
                for change in analysis_result['significant_changes'][:3]:
                    direction = "상승" if change['direction'] == 'up' else "하락"
                    print(f"- {change['platform']}: {direction} {abs(change['growth_rate']):.1f}%")
            
            # Send to Slack
            print(f"\n🚀 Slack으로 전송 중...")
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack 전송 성공!")
                print("✅ Slack 채널에 성공적으로 전송되었습니다!")
                return True
            else:
                logger.error(f"❌ Slack 전송 실패: {response.status_code}")
                print(f"❌ Slack 전송 실패: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 리포트 전송 중 오류: {e}")
            print(f"❌ 오류 발생: {e}")
            return False
    
    def show_analysis_preview(self, analysis_type: str = 'weekly'):
        """Show analysis preview without sending to Slack"""
        logger.info(f"👀 {analysis_type} 분석 미리보기")
        
        try:
            # Perform analysis
            analysis_result = self.analyzer.analyze_with_history(analysis_type)
            
            if not analysis_result:
                print("❌ 분석 결과를 가져올 수 없습니다")
                return None
            
            # Show preview
            print("=" * 80)
            print(f"📊 히스토리 기반 {analysis_type.upper()} 분석 미리보기")
            print("=" * 80)
            
            print(f"경고 수준: {analysis_result.get('alert_level', 'none')}")
            print(f"분석 시각: {analysis_result.get('timestamp', 'N/A')}")
            print()
            print("📋 요약:")
            print(f"  {analysis_result.get('summary_text', 'N/A')}")
            
            metrics = analysis_result['market_metrics']
            print(f"\n📈 시장 지표:")
            print(f"  현재 총 플레이어: {metrics['total_online']:,}명")
            print(f"  이전 총 플레이어: {metrics['total_historical']:,}명")
            print(f"  시장 성장률: {metrics['market_growth']:+.2f}%")
            print(f"  분석 플랫폼: {metrics['platforms_analyzed']}개")
            print(f"  신뢰도: {metrics['reliable_comparisons']}/{metrics['platforms_analyzed']}")
            
            if analysis_result.get('significant_changes'):
                print(f"\n🚨 주요 변화 ({len(analysis_result['significant_changes'])}개):")
                for change in analysis_result['significant_changes'][:5]:
                    direction_icon = "🚀" if change['direction'] == 'up' else "📉"
                    print(f"  {direction_icon} {change['platform']}: {change['growth_rate']:+.1f}% ({change['current']:,} ← {change['historical']:,})")
            
            print("\n" + "=" * 80)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 미리보기 중 오류: {e}")
            print(f"❌ 오류 발생: {e}")
            return None

def main():
    print("=" * 80)
    print("📱 히스토리 기반 Slack 리포터")
    print("=" * 80)
    
    if not SLACK_WEBHOOK_URL:
        print("❌ Slack Webhook URL이 설정되지 않았습니다")
        return
    
    reporter = HistoryBasedSlackReporter(SLACK_WEBHOOK_URL)
    
    print("\n작업을 선택하세요:")
    print("1. 일일 분석 미리보기")
    print("2. 주간 분석 미리보기")
    print("3. 월간 분석 미리보기")
    print("4. 주간 분석 Slack 전송 (승인 필요)")
    print("5. 일일 분석 Slack 전송 (승인 필요)")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == '1':
        reporter.show_analysis_preview('daily')
    elif choice == '2':
        reporter.show_analysis_preview('weekly')
    elif choice == '3':
        reporter.show_analysis_preview('monthly')
    elif choice == '4':
        result = reporter.show_analysis_preview('weekly')
        if result:
            confirm = input("\n위 분석을 Slack에 전송하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                reporter.send_analysis_report('weekly', user_approval=True)
            else:
                print("전송이 취소되었습니다.")
    elif choice == '5':
        result = reporter.show_analysis_preview('daily')
        if result:
            confirm = input("\n위 분석을 Slack에 전송하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                reporter.send_analysis_report('daily', user_approval=True)
            else:
                print("전송이 취소되었습니다.")
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()