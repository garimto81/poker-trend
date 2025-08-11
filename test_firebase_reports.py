#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 플랫폼 분석 테스트 - 일간/주간/월간
"""

import os
import sys
import json
from datetime import datetime

def test_report(report_type):
    """각 리포트 타입 테스트"""
    print(f"\n{'='*80}")
    print(f"{report_type.upper()} REPORT TEST")
    print(f"{'='*80}")
    
    # 환경변수 설정
    os.environ['REPORT_TYPE'] = report_type
    
    # firebase_platform_analyzer 임포트 및 실행
    from firebase_platform_analyzer import FirebasePlatformAnalyzer
    
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if report:
        print(f"\nData Period: {report['data_period']['start']} ~ {report['data_period']['end']}")
        print(f"Total Platforms: {report['summary']['total_platforms']}")
        print(f"Total Online: {report['summary']['total_online_players']:,}")
        print(f"Market Leader: {report['summary']['market_leader']} ({report['summary']['market_leader_share']}%)")
        
        print(f"\nTop 10 Platforms:")
        print(f"{'Rank':<5} {'Platform':<25} {'Online':<10} {'Cash':<10} {'Market %':<10}")
        print("-" * 65)
        
        for i, platform in enumerate(report['top_platforms'], 1):
            print(f"{i:<5} {platform['platform_name']:<25} {platform['online_players']:<10,} {platform['cash_players']:<10,} {platform['market_share']:<10.2f}")
        
        print(f"\nInsights:")
        for insight in report['insights']:
            print(f"  - {insight}")
        
        return report
    else:
        print("[ERROR] Report generation failed")
        return None

def main():
    """메인 실행"""
    print("Firebase Platform Analysis - All Report Types")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 일간 리포트
    daily_report = test_report('daily')
    
    # 주간 리포트
    weekly_report = test_report('weekly')
    
    # 월간 리포트
    monthly_report = test_report('monthly')
    
    # 요약
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    if daily_report:
        print(f"Daily Report: {daily_report['summary']['total_online_players']:,} players")
    if weekly_report:
        print(f"Weekly Report: {weekly_report['summary']['total_online_players']:,} players (avg)")
    if monthly_report:
        print(f"Monthly Report: {monthly_report['summary']['total_online_players']:,} players (avg)")

if __name__ == "__main__":
    main()