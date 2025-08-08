#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send online poker platform trend analysis to Slack
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

# Slack webhook URL from environment
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

class SlackReporter:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def detect_significant_changes(self, data: List[Dict]) -> Dict:
        """Detect significant market changes"""
        significant_changes = []
        platforms_with_change = 0
        
        for site in data:
            if site['seven_day_avg'] > 100:  # Only consider platforms with meaningful traffic
                if site['players_online'] > 0 and site['seven_day_avg'] > 0:
                    change = ((site['players_online'] - site['seven_day_avg']) / site['seven_day_avg']) * 100
                    
                    if abs(change) > 20:  # 20% threshold
                        platforms_with_change += 1
                        change_type = "surge" if change > 0 else "decline"
                        icon = "🚀" if change > 50 else "📈" if change > 0 else "⚠️" if change < -50 else "📉"
                        
                        significant_changes.append({
                            'platform': site['site_name'],
                            'change': change,
                            'type': change_type,
                            'icon': icon,
                            'current': site['players_online'],
                            'avg': site['seven_day_avg']
                        })
        
        # Sort by absolute change
        significant_changes.sort(key=lambda x: abs(x['change']), reverse=True)
        
        has_issue = platforms_with_change >= 3
        issue_level = 'high' if platforms_with_change >= 5 else 'medium' if platforms_with_change >= 3 else 'none'
        
        return {
            'has_issue': has_issue,
            'issue_level': issue_level,
            'platforms_with_change': platforms_with_change,
            'significant_changes': significant_changes[:5]  # Top 5
        }
    
    def create_slack_message(self, data: List[Dict], analysis_result: Dict) -> Dict:
        """Create formatted Slack message"""
        sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)
        total_online = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        active_platforms = len([s for s in data if s['players_online'] > 0])
        
        # Detect changes
        changes = self.detect_significant_changes(data)
        
        # Market concentration
        top3_share = sum(site['players_online'] for site in sorted_data[:3]) / total_online * 100
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        if changes['has_issue']:
            # Issue detected - detailed report
            message = {
                "text": "🚨 Online Poker Platform Trend Analysis - Significant Changes Detected",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🎮 Online Poker Platform Analysis Report"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"📅 {current_time} KST | 📊 Data Source: PokerScout.com"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"⚠️ *Significant Market Changes Detected*\\n_{changes['platforms_with_change']} platforms showing major movement (>20% change)_"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*🌐 Total Online Players*\\n{total_online:,}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*💰 Total Cash Players*\\n{total_cash:,}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*📊 Active Platforms*\\n{active_platforms} platforms"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*🎯 Market Concentration*\\nTOP 3: {top3_share:.1f}%"
                            }
                        ]
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*📈 Major Changes (vs 7-day avg):*"
                        }
                    }
                ]
            }
            
            # Add significant changes
            changes_text = ""
            for change in changes['significant_changes']:
                changes_text += f"{change['icon']} *{change['platform']}*: {change['change']:+.1f}% ({change['current']:,} → {change['avg']:,})\\n"
            
            if changes_text:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": changes_text.strip()
                    }
                })
            
            # Add TOP 5 platforms
            top5_text = ""
            for i, site in enumerate(sorted_data[:5], 1):
                share = (site['players_online'] / total_online * 100) if total_online > 0 else 0
                cash_ratio = (site['cash_players'] / site['players_online'] * 100) if site['players_online'] > 0 else 0
                top5_text += f"{i}. *{site['site_name']}*: {site['players_online']:,} online ({share:.1f}%) | {site['cash_players']:,} cash ({cash_ratio:.1f}%)\\n"
            
            message["blocks"].extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🏆 TOP 5 Platforms:*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": top5_text.strip()
                    }
                }
            ])
            
        else:
            # No issues - simple report
            message = {
                "text": "✅ Online Poker Platform Analysis - Market Stable",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🎮 Online Poker Platform Analysis Report"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"📅 {current_time} KST | 📊 Data Source: PokerScout.com"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *Market Status: STABLE*\\n_No significant changes detected. Market operating normally._"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*🌐 Total Players*\\n{total_online:,} online"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*💰 Cash Players*\\n{total_cash:,} active"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*🎯 Market Leader*\\n{sorted_data[0]['site_name']} ({sorted_data[0]['players_online']:,})"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*📊 Platforms*\\n{active_platforms} active"
                            }
                        ]
                    }
                ]
            }
        
        # Add footer
        message["blocks"].extend([
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 Generated by Poker Platform Analyzer | Real-time data from PokerScout.com"
                    }
                ]
            }
        ])
        
        return message
    
    def send_to_slack(self, message: Dict) -> bool:
        """Send message to Slack"""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Successfully sent to Slack!")
                return True
            else:
                print(f"❌ Slack API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send to Slack: {e}")
            return False
    
    def send_analysis_report(self, data: List[Dict], analysis_result: Dict) -> bool:
        """Send complete analysis report to Slack"""
        print("="*80)
        print("PREPARING SLACK REPORT")
        print("="*80)
        
        message = self.create_slack_message(data, analysis_result)
        
        # Preview the message
        print("\n📋 SLACK MESSAGE PREVIEW:")
        print("-"*50)
        print(f"Title: {message['text']}")
        print(f"Blocks: {len(message['blocks'])} sections")
        
        # Show key stats
        total_online = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        top_platform = max(data, key=lambda x: x['players_online'])
        
        print(f"\n📊 Key Stats:")
        print(f"- Total Online: {total_online:,}")
        print(f"- Total Cash: {total_cash:,}")
        print(f"- Top Platform: {top_platform['site_name']} ({top_platform['players_online']:,})")
        
        # Detect and show changes
        changes = self.detect_significant_changes(data)
        print(f"- Significant Changes: {changes['platforms_with_change']} platforms")
        
        if changes['significant_changes']:
            print("- Top Changes:")
            for change in changes['significant_changes'][:3]:
                print(f"  • {change['platform']}: {change['change']:+.1f}%")
        
        print("\n" + "="*80)
        print("SENDING TO SLACK")
        print("="*80)
        
        return self.send_to_slack(message)

def main():
    print("="*80)
    print("ONLINE POKER PLATFORM SLACK REPORTER")
    print("="*80)
    
    # Check webhook URL
    if not SLACK_WEBHOOK_URL:
        print("❌ Slack webhook URL not configured")
        return
    
    print(f"📡 Slack webhook: {SLACK_WEBHOOK_URL[:50]}...")
    
    # Fetch live data
    print("\n🔄 Fetching live data...")
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("❌ No data available")
        return
    
    print(f"✅ Collected data from {len(data)} platforms")
    
    # Generate analysis
    analysis_result = analyzer.analyze_data(data)
    
    # Create Slack reporter and send
    reporter = SlackReporter(SLACK_WEBHOOK_URL)
    success = reporter.send_analysis_report(data, analysis_result)
    
    if success:
        print("\n" + "="*80)
        print("🎉 SLACK REPORT SENT SUCCESSFULLY!")
        print("="*80)
        print("Check your Slack channel for the analysis report.")
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO SEND SLACK REPORT")
        print("="*80)
        print("Please check your webhook URL and network connection.")

if __name__ == "__main__":
    main()