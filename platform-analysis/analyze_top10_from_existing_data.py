#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 변화 감지 결과에서 상위 10위권 플랫폼 변화 분석
"""

import json
from datetime import datetime

def analyze_top10_changes():
    """기존 데이터에서 상위 10위권 변화 분석"""
    
    # 상위 10위권 플랫폼 (이전 분석 결과 기반)
    top10_platforms = [
        'GGNetwork',
        'IDNPoker', 
        'Chico Poker',
        'Winamax',
        'iPoker Europe',
        'iPoker.it',
        'PokerStars.it',
        'BetMGM Poker',
        'WPT Global',
        'GGPoker ON'
    ]
    
    print("="*80)
    print("상위 10위권 플랫폼 변화 분석 - 정량화 수치")
    print("="*80)
    print(f"분석 대상: {len(top10_platforms)}개 플랫폼")
    print("대상 플랫폼:", ", ".join(top10_platforms[:5]) + " 외 5개")
    
    # 월간 변화 데이터 로드
    try:
        with open('change_detection_monthly_20250811_183320.json', 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] 월간 데이터 파일을 찾을 수 없습니다")
        return
    
    # 주간 변화 데이터 로드
    try:
        with open('change_detection_weekly_20250811_183255.json', 'r', encoding='utf-8') as f:
            weekly_data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] 주간 데이터 파일을 찾을 수 없습니다")
        return
    
    # 정량화 수치 먼저 표시
    monthly_top10_changes = [
        change for change in monthly_data['changes'] 
        if change['platform'] in top10_platforms
    ]
    
    weekly_top10_changes = [
        change for change in weekly_data['changes']
        if change['platform'] in top10_platforms
    ]
    
    print("\n[정량화 수치 요약]")
    print("="*60)
    print(f"[DATA] 월간 상위 10위권 변화: {len(monthly_top10_changes)}건 감지")
    print(f"[DATA] 주간 상위 10위권 변화: {len(weekly_top10_changes)}건 감지")
    
    # 변화량 통계
    monthly_changes = [abs(c['change_percent']) for c in monthly_top10_changes]
    weekly_changes = [abs(c['change_percent']) for c in weekly_top10_changes]
    
    if monthly_changes:
        print(f"[DATA] 월간 평균 변화율: {sum(monthly_changes)/len(monthly_changes):.1f}%")
        print(f"[DATA] 월간 최대 변화율: {max(monthly_changes):.1f}%")
    
    if weekly_changes:
        print(f"[DATA] 주간 평균 변화율: {sum(weekly_changes)/len(weekly_changes):.1f}%")
        print(f"[DATA] 주간 최대 변화율: {max(weekly_changes):.1f}%")
    
    # 심각도별 통계
    monthly_major = len([c for c in monthly_top10_changes if c['severity'] == 'major'])
    weekly_major = len([c for c in weekly_top10_changes if c['severity'] == 'major'])
    
    print(f"[DATA] 주요 변화(major): 월간 {monthly_major}건, 주간 {weekly_major}건")
    
    # 증감 통계
    monthly_inc = len([c for c in monthly_top10_changes if c['direction'] == 'increase'])
    monthly_dec = len([c for c in monthly_top10_changes if c['direction'] == 'decrease'])
    weekly_inc = len([c for c in weekly_top10_changes if c['direction'] == 'increase'])
    weekly_dec = len([c for c in weekly_top10_changes if c['direction'] == 'decrease'])
    
    print(f"[DATA] 증감 비율:")
    print(f"   월간 - 증가: {monthly_inc}건, 감소: {monthly_dec}건")
    print(f"   주간 - 증가: {weekly_inc}건, 감소: {weekly_dec}건")
    
    print("\n[상세 분석]")
    print("="*60)
    print("\n1. 월간 변화 분석 (상위 10위권 내)")
    print("-" * 40)
    
    if monthly_top10_changes:
        for i, change in enumerate(monthly_top10_changes[:5], 1):
            direction = "증가" if change['direction'] == 'increase' else "감소"
            severity = change.get('severity_kr', change['severity'])
            
            print(f"\n{i}. {change['platform']} - {change['metric']}")
            print(f"   [CHANGE] {change['start_value']:,} → {change['end_value']:,} ({change['change_percent']:+.1f}%)")
            print(f"   [LEVEL] 심각도: {severity} | 방향: {direction}")
    else:
        print("상위 10위권 내에서 유의미한 월간 변화 없음")
    
    print("\n2. 주간 변화 분석 (상위 10위권 내)")
    print("-" * 40)
    
    if weekly_top10_changes:
        for i, change in enumerate(weekly_top10_changes[:5], 1):
            direction = "증가" if change['direction'] == 'increase' else "감소"
            severity = change.get('severity_kr', change['severity'])
            
            print(f"\n{i}. {change['platform']} - {change['metric']}")
            print(f"   [CHANGE] {change['start_value']:,} → {change['end_value']:,} ({change['change_percent']:+.1f}%)")
            print(f"   [LEVEL] 심각도: {severity} | 방향: {direction}")
    else:
        print("상위 10위권 내에서 유의미한 주간 변화 없음")
    
    # 핵심 인사이트 및 결론
    print("\n[핵심 인사이트 & 결론]")
    print("="*60)
    
    # 시장 리더십 변화
    gg_monthly = next((c for c in monthly_top10_changes if c['platform'] == 'GGNetwork'), None)
    idn_weekly = next((c for c in weekly_top10_changes if c['platform'] == 'IDNPoker'), None) 
    chico_weekly = next((c for c in weekly_top10_changes if c['platform'] == 'Chico Poker'), None)
    
    total_major_changes = monthly_major + weekly_major
    total_changes = len(monthly_top10_changes) + len(weekly_top10_changes)
    
    print(f"[METRIC] 상위권 안정성 지수: {((10-total_major_changes)/10*100):.0f}%")
    
    if gg_monthly:
        player_loss = gg_monthly['start_value'] - gg_monthly['end_value']
        print(f"[LEADER] 시장 리더 GGNetwork: {player_loss:,}명 감소 ({gg_monthly['change_percent']:+.1f}%)")
    
    if idn_weekly:
        idn_loss = idn_weekly['start_value'] - idn_weekly['end_value'] 
        print(f"[RANK2] 2위권 IDNPoker: {idn_loss:,}명 감소 ({idn_weekly['change_percent']:+.1f}%)")
    
    if chico_weekly and chico_weekly['metric'] == 'online_players':
        chico_loss = chico_weekly['start_value'] - chico_weekly['end_value']
        print(f"[RANK3] 3위권 Chico Poker: {chico_loss:,}명 감소 ({chico_weekly['change_percent']:+.1f}%)")
    
    # 시장 전체 평가
    total_decrease_ratio = (monthly_dec + weekly_dec) / total_changes * 100 if total_changes > 0 else 0
    
    print(f"\n[SUMMARY] 상위권 변화 요약:")
    print(f"   - 총 변화 감지: {total_changes}건")
    print(f"   - 주요 변화: {total_major_changes}건 ({total_major_changes/total_changes*100:.0f}%)")
    print(f"   - 감소 비중: {total_decrease_ratio:.0f}%")
    
    # 결론
    print(f"\n[ASSESSMENT] 최종 평가:")
    if total_major_changes > 5:
        stability = "높은 변동성 - 상위권 경쟁 구도 대변화"
        risk_level = "[HIGH RISK]"
    elif total_major_changes > 3:
        stability = "중간 변동성 - 일부 플랫폼 순위 변동 가능"
        risk_level = "[MEDIUM RISK]"
    else:
        stability = "안정적 - 큰 변화 없음"
        risk_level = "[LOW RISK]"
    
    print(f"   위험도: {risk_level}")
    print(f"   상태: {stability}")
    
    if total_decrease_ratio > 60:
        print(f"   트렌드: [DOWN] 상위권 전반 위축세")
    elif total_decrease_ratio < 40:
        print(f"   트렌드: [UP] 상위권 전반 성장세")
    else:
        print(f"   트렌드: [STABLE] 균형 상태")
    
    print(f"\n[COMPLETED] 분석 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    analyze_top10_changes()