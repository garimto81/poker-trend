#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 분석 미리보기 생성
일일/주간/월간 모든 리포트 타입 미리보기
"""

import os
import sys
import json
from datetime import datetime, timedelta

# 플랫폼 분석 모듈 경로 추가
sys.path.append('backend/platform-analyzer/scripts')
from automated_platform_analyzer import AutomatedPlatformAnalyzer

def generate_preview(report_type):
    """리포트 타입별 미리보기 생성"""
    print("\n" + "="*80)
    print(f"[{report_type.upper()}] PLATFORM ANALYSIS PREVIEW")
    print("="*80)
    
    # 환경 변수 설정
    current_date = datetime.now()
    
    if report_type == 'daily':
        os.environ['REPORT_TYPE'] = 'daily'
        os.environ['DATA_PERIOD_START'] = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
        os.environ['DATA_PERIOD_END'] = os.environ['DATA_PERIOD_START']
    elif report_type == 'weekly':
        os.environ['REPORT_TYPE'] = 'weekly'
        os.environ['DATA_PERIOD_START'] = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')
        os.environ['DATA_PERIOD_END'] = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    else:  # monthly
        os.environ['REPORT_TYPE'] = 'monthly'
        os.environ['DATA_PERIOD_START'] = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        os.environ['DATA_PERIOD_END'] = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 분석기 실행
    analyzer = AutomatedPlatformAnalyzer()
    report = analyzer.generate_report()
    
    # 미리보기 출력
    print(f"\nPeriod: {report['data_period']['start']} ~ {report['data_period']['end']}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Analyzed Platforms: {report['summary']['total_platforms']}")
    print(f"Total Online: {report['summary']['total_online_players']:,} players")
    print(f"Total Cash: {report['summary']['total_cash_players']:,} players")
    print(f"Market Leader: {report['summary']['market_leader']} ({report['summary']['market_leader_share']:.1f}%)")
    
    print("\n[TOP 10 PLATFORMS]")
    print("-" * 70)
    
    for i, platform in enumerate(report['top_platforms'][:10], 1):
        # 순위별 표시
        medal = {1: '#1', 2: '#2', 3: '#3'}.get(i, f'#{i}')
        
        # 성장률에 따른 트렌드
        growth = platform['growth_rate']
        if growth >= 5:
            trend = '[UP]'
        elif growth >= -5:
            trend = '[=]'
        else:
            trend = '[DOWN]'
        
        print(f"{medal} {platform['platform_name']:<15} | Online: {platform['online_players']:>6,} ({platform['market_share']:>5.1f}%)")
        
        if report_type == 'daily':
            print(f"   Cash: {platform['cash_players']:>6,} | 24h Peak: {platform['peak_24h']:>6,} | {trend} {growth:+.1f}%")
        elif report_type == 'weekly':
            print(f"   Cash: {platform['cash_players']:>6,} | 7-day Avg: {platform['seven_day_avg']:>6,} | {trend} {growth:+.1f}%")
        else:  # monthly
            print(f"   Cash: {platform['cash_players']:>6,} | Tournament: {platform['tournament_players']:>6,} | {trend} {growth:+.1f}%")
    
    # 경쟁 분석
    competition = report['competition_analysis']
    print("\n[COMPETITION ANALYSIS]")
    print("-" * 70)
    print(f"Market Structure: {competition['competition_intensity']}")
    print(f"HHI Index: {competition['market_concentration']:.0f}")
    print(f"2nd Place: {competition['second']['name']} ({competition['second']['share']:.1f}%) - {competition['second']['players']:,} players")
    print(f"3rd Place: {competition['third']['name']} ({competition['third']['share']:.1f}%) - {competition['third']['players']:,} players")
    print(f"2nd-3rd Gap: {competition['gap_2_3']:,} players ({competition['gap_2_3_percentage']:.1f}%)")
    
    # 핵심 인사이트
    print("\n[KEY INSIGHTS]")
    print("-" * 70)
    for insight in report['insights']:
        print(f"- {insight}")
    
    # Slack 메시지 형식 미리보기
    print("\n[SLACK MESSAGE PREVIEW]")
    print("-" * 70)
    
    if report_type == 'daily':
        slack_header = "Platform Daily Analysis Report"
        special_info = f"24-hour peak traffic analysis included"
    elif report_type == 'weekly':
        slack_header = "Platform Weekly Analysis Report"
        special_info = f"7-day average trend analysis included"
    else:  # monthly
        slack_header = "Platform Monthly Analysis Report"
        special_info = f"Long-term market trend analysis included"
    
    print(f"{slack_header}")
    print(f"Analysis Period: {report['data_period']['start']} ~ {report['data_period']['end']}")
    print(f"Total Online: {report['summary']['total_online_players']:,} players")
    print(f"Total Cash: {report['summary']['total_cash_players']:,} players")
    print(f"Special: {special_info}")
    
    return report

def main():
    """메인 실행 함수"""
    print("="*80)
    print("PLATFORM ANALYSIS PREVIEW - ALL REPORT TYPES")
    print("="*80)
    
    # 모든 리포트 타입 생성
    reports = {}
    for report_type in ['daily', 'weekly', 'monthly']:
        reports[report_type] = generate_preview(report_type)
    
    # 요약 비교
    print("\n" + "="*80)
    print("REPORT TYPE COMPARISON SUMMARY")
    print("="*80)
    
    print("\n[Market Size Comparison]")
    print("-" * 50)
    for report_type in ['daily', 'weekly', 'monthly']:
        r = reports[report_type]
        print(f"{report_type.upper():8} | Online: {r['summary']['total_online_players']:>7,} | Cash: {r['summary']['total_cash_players']:>6,}")
    
    print("\n[Market Leader Share]")
    print("-" * 50)
    for report_type in ['daily', 'weekly', 'monthly']:
        r = reports[report_type]
        leader = r['competition_analysis']['leader']
        print(f"{report_type.upper():8} | {leader['name']}: {leader['share']:.1f}% ({leader['players']:,} players)")
    
    print("\n[Competition Intensity]")
    print("-" * 50)
    for report_type in ['daily', 'weekly', 'monthly']:
        r = reports[report_type]
        comp = r['competition_analysis']
        print(f"{report_type.upper():8} | HHI: {comp['market_concentration']:>4.0f} | 2nd-3rd Gap: {comp['gap_2_3_percentage']:>5.1f}%")
    
    print("\n" + "="*80)
    print("[COMPLETE] Platform Analysis Preview")
    print("="*80)

if __name__ == "__main__":
    main()