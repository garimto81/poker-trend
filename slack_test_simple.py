#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def send_slack_test():
    """Send test message to Slack"""
    
    # Load environment variables
    load_dotenv()
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("ERROR: SLACK_WEBHOOK_URL not set in .env file")
        print("Please add: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...")
        return False
    
    # Test message
    message = {
        "text": "Poker Trend Analyzer - Slack Connection Test",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Poker Trend Analyzer Test Message"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Slack Connection Successful!*\n\nTest time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*System Status*\n• YouTube API: Ready\n• Gemini AI: Ready\n• Auto Scheduler: Standby"
                }
            }
        ]
    }
    
    try:
        print("Sending test message to Slack...")
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 200:
            print("SUCCESS: Test message sent!")
            print("Check your Slack channel.")
            return True
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Poker Trend Analyzer - Slack Test")
    print("=" * 50)
    
    if send_slack_test():
        print("\nSlack connection test completed!")
        print("You can now run daily_scheduler.py")
    else:
        print("\nSlack connection failed.")
        print("Please check your SLACK_WEBHOOK_URL in .env file")