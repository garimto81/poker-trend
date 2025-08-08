#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Slack reporter preview
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from history_based_slack_reporter import HistoryBasedSlackReporter

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def main():
    print("🧪 Slack 리포터 미리보기 테스트...")
    
    reporter = HistoryBasedSlackReporter(SLACK_WEBHOOK_URL)
    
    # Test daily preview
    print("\n📊 일일 분석 미리보기:")
    result = reporter.show_analysis_preview('daily')
    
    print("\n" + "="*80)
    
    if result:
        print("✅ 미리보기 성공!")
        print("\n승인하면 Slack으로 전송할 수 있는 상태입니다.")
    else:
        print("❌ 미리보기 실패!")

if __name__ == "__main__":
    main()