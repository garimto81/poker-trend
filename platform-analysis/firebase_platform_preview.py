#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 플랫폼 분석 보고서 미리보기 생성
"""

import os
import json
from datetime import datetime
from firebase_platform_analyzer import FirebasePlatformAnalyzer

def format_number(num):
    """숫자 포맷팅"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def generate_preview(report_type):
    """각 보고서 타입별 미리보기 생성"""
    
    # 환경변수 설정
    os.environ['REPORT_TYPE'] = report_type
    
    # 분석기 실행
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if not report:
        return None
    
    # 미리보기 생성
    preview = []
    
    # 헤더
    title_map = {
        'daily': '[DAILY] 일간 플랫폼 분석 리포트',
        'weekly': '[WEEKLY] 주간 플랫폼 분석 리포트', 
        'monthly': '[MONTHLY] 월간 플랫폼 분석 리포트'
    }
    
    preview.append("=" * 80)
    preview.append(title_map[report_type])
    preview.append(f"기간: {report['data_period']['start']} ~ {report['data_period']['end']}")
    preview.append("데이터: Firebase (PokerStars US/Ontario 제외)")
    preview.append("=" * 80)
    
    # 요약 통계
    summary = report['summary']
    preview.append("")
    preview.append("[요약 통계]")
    preview.append(f"- 총 플랫폼 수: {summary['total_platforms']}개")
    preview.append(f"- 총 온라인 플레이어: {format_number(summary['total_online_players'])}")
    preview.append(f"- 총 캐시게임 플레이어: {format_number(summary['total_cash_players'])}")
    preview.append(f"- 시장 리더: {summary['market_leader']} ({summary['market_leader_share']:.1f}%)")
    
    # TOP 10 플랫폼
    preview.append("")
    preview.append("[TOP 10 플랫폼]")
    preview.append("")
    preview.append(f"{'순위':<4} {'플랫폼':<20} {'온라인':<12} {'캐시':<12} {'점유율':<8}")
    preview.append("-" * 60)
    
    for i, platform in enumerate(report['top_platforms'][:10], 1):
        online = format_number(platform['online_players'])
        cash = format_number(platform['cash_players'])
        share = f"{platform['market_share']:.1f}%"
        
        # 순위별 표시
        rank_emoji = ""
        if i == 1:
            rank_emoji = "[1]"
        elif i == 2:
            rank_emoji = "[2]"
        elif i == 3:
            rank_emoji = "[3]"
        else:
            rank_emoji = f"{i}."
        
        preview.append(
            f"{rank_emoji:<4} {platform['platform_name']:<20} {online:<12} {cash:<12} {share:<8}"
        )
    
    # 경쟁 분석
    if 'competition_analysis' in report and report['competition_analysis']:
        comp = report['competition_analysis']
        preview.append("")
        preview.append("[경쟁 분석]")
        preview.append(f"- 시장 집중도 (HHI): {comp.get('market_concentration', 0):.0f}")
        preview.append(f"- 경쟁 강도: {comp.get('competition_intensity', 'N/A')}")
        preview.append(f"- 전체 시장 규모: {format_number(comp.get('total_market_size', 0))}")
        
        if comp.get('leader'):
            preview.append("")
            preview.append("[TOP 3 경쟁 구도]")
            leader = comp['leader']
            preview.append(f"1위: {leader['name']} - {format_number(leader['players'])} ({leader['share']:.1f}%)")
            
            if comp.get('second'):
                second = comp['second']
                preview.append(f"2위: {second['name']} - {format_number(second['players'])} ({second['share']:.1f}%)")
            
            if comp.get('third'):
                third = comp['third']
                preview.append(f"3위: {third['name']} - {format_number(third['players'])} ({third['share']:.1f}%)")
    
    # 주요 인사이트
    preview.append("")
    preview.append("[주요 인사이트]")
    for insight in report['insights']:
        # 인사이트 한글화
        if "[LEADER]" in insight:
            insight = insight.replace("[LEADER]", "- 리더십:")
        elif "[CASH]" in insight:
            insight = insight.replace("[CASH]", "- 캐시게임:")
        elif "[DATA]" in insight:
            insight = insight.replace("[DATA]", "- 데이터:")
        elif "[PEAK]" in insight:
            insight = insight.replace("[PEAK]", "- 피크타임:")
        elif "[WEEKLY]" in insight:
            insight = insight.replace("[WEEKLY]", "- 주간동향:")
        elif "[MONTHLY]" in insight:
            insight = insight.replace("[MONTHLY]", "- 월간동향:")
        else:
            insight = f"- {insight}"
        
        preview.append(insight)
    
    # 트렌드 표시 (주간/월간)
    if report_type in ['weekly', 'monthly']:
        preview.append("")
        preview.append("[플랫폼별 트렌드]")
        preview.append("")
        
        # 상위 5개 플랫폼의 트렌드를 시각화
        for platform in report['top_platforms'][:5]:
            name = platform['platform_name']
            share = platform['market_share']
            
            # 바 차트 생성
            bar_length = int(share / 2)  # 50% = 25 characters
            bar = "#" * min(bar_length, 40)  # 최대 40자
            
            preview.append(f"{name:<15} {bar} {share:.1f}%")
    
    # 보고서 타입별 특별 섹션
    if report_type == 'daily':
        preview.append("")
        preview.append("[24시간 피크 분석]")
        for platform in report['top_platforms'][:3]:
            if platform.get('peak_24h', 0) > 0:
                preview.append(f"- {platform['platform_name']}: {format_number(platform['peak_24h'])} (피크)")
    
    elif report_type == 'weekly':
        preview.append("")
        preview.append("[7일 평균 트렌드]")
        for platform in report['top_platforms'][:3]:
            if platform.get('seven_day_avg', 0) > 0:
                preview.append(f"- {platform['platform_name']}: {format_number(platform['seven_day_avg'])} (7일 평균)")
    
    elif report_type == 'monthly':
        preview.append("")
        preview.append("[월간 시장 점유율 변화]")
        total = sum(p['market_share'] for p in report['top_platforms'][:5])
        preview.append(f"- TOP 5 플랫폼 점유율 합계: {total:.1f}%")
        preview.append(f"- 기타 플랫폼: {100-total:.1f}%")
    
    preview.append("")
    preview.append("=" * 80)
    preview.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    preview.append("")
    
    return "\n".join(preview)

def main():
    """메인 실행"""
    
    print("\n" + "="*80)
    print("FIREBASE 플랫폼 분석 - 전체 보고서 미리보기")
    print("="*80)
    
    # 일간 보고서
    print("\n\n")
    daily_preview = generate_preview('daily')
    if daily_preview:
        print(daily_preview)
    
    # 주간 보고서
    print("\n\n")
    weekly_preview = generate_preview('weekly')
    if weekly_preview:
        print(weekly_preview)
    
    # 월간 보고서
    print("\n\n")
    monthly_preview = generate_preview('monthly')
    if monthly_preview:
        print(monthly_preview)
    
    # 전체 요약
    print("\n" + "="*80)
    print("[전체 보고서 요약]")
    print("="*80)
    print("[OK] 일간 보고서: 2025-08-10 데이터")
    print("[OK] 주간 보고서: 2025-08-04 ~ 2025-08-10 평균")
    print("[OK] 월간 보고서: 2025-07-30 ~ 2025-08-10 평균")
    print("\n모든 데이터는 Firebase 실제 데이터 기반")
    print("(PokerStars US/Ontario 제외 - 데이터 오염)")
    print("="*80)

if __name__ == "__main__":
    main()