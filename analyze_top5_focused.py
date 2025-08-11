#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상위 5위권 플랫폼 변화 분석 (온라인/캐시 플레이어 수치 중심)
"""

import json
from datetime import datetime, timedelta

def calculate_days_between(start_date_str, end_date_str):
    """두 날짜 사이의 일수 계산"""
    try:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
        end = datetime.strptime(end_date_str, '%Y-%m-%d')
        return (end - start).days + 1
    except:
        return 0

def analyze_top5_changes():
    """상위 5위권 플랫폼 온라인/캐시 플레이어 수치 변화 분석"""
    
    # 상위 5위권 플랫폼 (이전 분석 결과 기반)
    top5_platforms = [
        'GGNetwork',      # 1위
        'IDNPoker',       # 2위
        'Chico Poker',    # 3위
        'Winamax',        # 4위
        'iPoker Europe'   # 5위
    ]
    
    print("="*80)
    print("상위 5위권 플랫폼 수치 변화 분석 (온라인/캐시 플레이어)")
    print("="*80)
    print(f"분석 대상: {len(top5_platforms)}개 플랫폼")
    print("대상 플랫폼:", ", ".join(top5_platforms))
    
    # 월간/주간 변화 데이터 로드
    try:
        with open('change_detection_monthly_20250811_183320.json', 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] 월간 데이터 파일을 찾을 수 없습니다")
        return
    
    try:
        with open('change_detection_weekly_20250811_183255.json', 'r', encoding='utf-8') as f:
            weekly_data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] 주간 데이터 파일을 찾을 수 없습니다")
        return
    
    # 상위 5위권 변화만 필터링
    monthly_top5_changes = [
        change for change in monthly_data['changes'] 
        if change['platform'] in top5_platforms
    ]
    
    weekly_top5_changes = [
        change for change in weekly_data['changes']
        if change['platform'] in top5_platforms
    ]
    
    # 정량화 수치 요약
    print("\n[정량화 수치 요약]")
    print("="*60)
    print(f"[PERIOD] 분석 기간")
    print(f"  월간 분석: 2025-07-30 ~ 2025-08-10 (12일간)")
    print(f"  주간 분석: 2025-08-04 ~ 2025-08-10 (7일간)")
    print(f"[DATA] 월간 상위 5위권 변화: {len(monthly_top5_changes)}건 감지")
    print(f"[DATA] 주간 상위 5위권 변화: {len(weekly_top5_changes)}건 감지")
    
    # 온라인/캐시 플레이어 변화량 통계
    monthly_online = [c for c in monthly_top5_changes if c['metric'] == 'online_players']
    monthly_cash = [c for c in monthly_top5_changes if c['metric'] == 'cash_players']
    weekly_online = [c for c in weekly_top5_changes if c['metric'] == 'online_players']
    weekly_cash = [c for c in weekly_top5_changes if c['metric'] == 'cash_players']
    
    print(f"[DATA] 온라인 플레이어 변화: 월간 {len(monthly_online)}건, 주간 {len(weekly_online)}건")
    print(f"[DATA] 캐시 플레이어 변화: 월간 {len(monthly_cash)}건, 주간 {len(weekly_cash)}건")
    
    if monthly_online:
        avg_monthly_online = sum(abs(c['change_percent']) for c in monthly_online) / len(monthly_online)
        print(f"[DATA] 월간 온라인 평균 변화율: {avg_monthly_online:.1f}%")
    
    if weekly_online:
        avg_weekly_online = sum(abs(c['change_percent']) for c in weekly_online) / len(weekly_online)
        print(f"[DATA] 주간 온라인 평균 변화율: {avg_weekly_online:.1f}%")
    
    # 상위 5위권 개별 플랫폼 수치 변화
    print("\n[상위 5위권 플랫폼별 수치 변화]")
    print("="*60)
    
    for i, platform in enumerate(top5_platforms, 1):
        print(f"\n{i}위. {platform}")
        print("-" * 40)
        
        # 월간 변화 찾기
        platform_monthly_online = next((c for c in monthly_online if c['platform'] == platform), None)
        platform_monthly_cash = next((c for c in monthly_cash if c['platform'] == platform), None)
        
        # 주간 변화 찾기
        platform_weekly_online = next((c for c in weekly_online if c['platform'] == platform), None)
        platform_weekly_cash = next((c for c in weekly_cash if c['platform'] == platform), None)
        
        # 온라인 플레이어 수치
        print("온라인 플레이어:")
        if platform_monthly_online:
            start_date = platform_monthly_online['start_date']
            end_date = platform_monthly_online['end_date']
            print(f"  월간 ({start_date} ~ {end_date}): {platform_monthly_online['start_value']:,} → {platform_monthly_online['end_value']:,} ({platform_monthly_online['change_percent']:+.1f}%)")
            print(f"    [기간] {calculate_days_between(start_date, end_date)}일간 변화")
        else:
            print(f"  월간 (2025-07-30 ~ 2025-08-10): 변화 없음 (임계값 미만)")
            
        if platform_weekly_online:
            start_date = platform_weekly_online['start_date']
            end_date = platform_weekly_online['end_date']
            print(f"  주간 ({start_date} ~ {end_date}): {platform_weekly_online['start_value']:,} → {platform_weekly_online['end_value']:,} ({platform_weekly_online['change_percent']:+.1f}%)")
            print(f"    [기간] {calculate_days_between(start_date, end_date)}일간 변화")
        else:
            print(f"  주간 (2025-08-04 ~ 2025-08-10): 변화 없음 (임계값 미만)")
        
        # 캐시 플레이어 수치
        print("캐시 플레이어:")
        if platform_monthly_cash:
            start_date = platform_monthly_cash['start_date']
            end_date = platform_monthly_cash['end_date']
            print(f"  월간 ({start_date} ~ {end_date}): {platform_monthly_cash['start_value']:,} → {platform_monthly_cash['end_value']:,} ({platform_monthly_cash['change_percent']:+.1f}%)")
            print(f"    [기간] {calculate_days_between(start_date, end_date)}일간 변화")
        else:
            print(f"  월간 (2025-07-30 ~ 2025-08-10): 변화 없음 (임계값 미만)")
            
        if platform_weekly_cash:
            start_date = platform_weekly_cash['start_date']
            end_date = platform_weekly_cash['end_date']
            print(f"  주간 ({start_date} ~ {end_date}): {platform_weekly_cash['start_value']:,} → {platform_weekly_cash['end_value']:,} ({platform_weekly_cash['change_percent']:+.1f}%)")
            print(f"    [기간] {calculate_days_between(start_date, end_date)}일간 변화")
        else:
            print(f"  주간 (2025-08-04 ~ 2025-08-10): 변화 없음 (임계값 미만)")
    
    # 전체 시장 대비 상대적 성과 분석
    print("\n[전체 시장 대비 리더십 변화 분석]")
    print("="*60)
    
    # 전체 시장 변화율 계산 (상위 5위권 합계 기준)
    def calculate_market_performance():
        # 월간/주간 각각의 전체 시장 변화 계산
        monthly_total_start = 0
        monthly_total_end = 0
        weekly_total_start = 0
        weekly_total_end = 0
        
        # 기존 데이터에서 전체 변화량 추정 (상위 변화들의 절대값 합계)
        for change in monthly_top5_changes:
            if change['metric'] == 'online_players':
                monthly_total_start += change['start_value']
                monthly_total_end += change['end_value']
        
        for change in weekly_top5_changes:
            if change['metric'] == 'online_players':
                weekly_total_start += change['start_value'] 
                weekly_total_end += change['end_value']
        
        # 전체 시장 변화율 계산
        monthly_market_change = 0
        weekly_market_change = 0
        
        if monthly_total_start > 0:
            monthly_market_change = ((monthly_total_end - monthly_total_start) / monthly_total_start) * 100
            
        if weekly_total_start > 0:
            weekly_market_change = ((weekly_total_end - weekly_total_start) / weekly_total_start) * 100
            
        return monthly_market_change, weekly_market_change, monthly_total_start, monthly_total_end, weekly_total_start, weekly_total_end
    
    monthly_market_change, weekly_market_change, m_start, m_end, w_start, w_end = calculate_market_performance()
    
    print(f"[MARKET] 전체 시장 변화 (상위 5위권 합계 기준)")
    if monthly_market_change != 0:
        print(f"  월간 시장: {m_start:,}명 → {m_end:,}명 ({monthly_market_change:+.1f}%)")
    if weekly_market_change != 0:
        print(f"  주간 시장: {w_start:,}명 → {w_end:,}명 ({weekly_market_change:+.1f}%)")
    
    # 각 플랫폼의 시장 대비 상대적 성과
    print(f"\n[RELATIVE PERFORMANCE] 시장 대비 상대적 성과")
    print("-" * 50)
    
    # 1위 GGNetwork 상대적 성과
    gg_monthly = next((c for c in monthly_top5_changes if c['platform'] == 'GGNetwork'), None)
    if gg_monthly and monthly_market_change != 0:
        player_loss = gg_monthly['start_value'] - gg_monthly['end_value']
        days = calculate_days_between(gg_monthly['start_date'], gg_monthly['end_date'])
        relative_performance = gg_monthly['change_percent'] - monthly_market_change
        
        performance_status = ""
        if relative_performance > 5:
            performance_status = "시장 대비 선방 (아웃퍼폼)"
        elif relative_performance > -5:
            performance_status = "시장과 비슷한 수준"
        else:
            performance_status = "시장 대비 부진 (언더퍼폼)"
            
        print(f"[LEADER] 1위 GGNetwork: {gg_monthly['change_percent']:+.1f}% (시장: {monthly_market_change:+.1f}%)")
        print(f"  상대적 성과: {relative_performance:+.1f}%p → {performance_status}")
        print(f"  변화 기간: {gg_monthly['start_date']} ~ {gg_monthly['end_date']} ({days}일간)")
        
        if relative_performance > 0:
            print(f"  [분석] 시장 전반 하락 속에서도 리더십 유지력 보여줌")
        else:
            print(f"  [분석] 시장보다 더 큰 타격으로 리더십 약화")
    
    # 2위 IDNPoker 상대적 성과
    idn_change = next((c for c in weekly_top5_changes if c['platform'] == 'IDNPoker'), None)
    if idn_change and weekly_market_change != 0:
        idn_loss = idn_change['start_value'] - idn_change['end_value']
        days = calculate_days_between(idn_change['start_date'], idn_change['end_date'])
        relative_performance = idn_change['change_percent'] - weekly_market_change
        
        performance_status = ""
        if relative_performance > 5:
            performance_status = "시장 대비 선방"
        elif relative_performance > -5:
            performance_status = "시장 평균 수준"
        else:
            performance_status = "시장 대비 부진"
            
        print(f"\n[RANK2] 2위 IDNPoker: {idn_change['change_percent']:+.1f}% (시장: {weekly_market_change:+.1f}%)")
        print(f"  상대적 성과: {relative_performance:+.1f}%p → {performance_status}")
        print(f"  변화 기간: {idn_change['start_date']} ~ {idn_change['end_date']} ({days}일간)")
        
        if relative_performance > 0:
            print(f"  [분석] 2위 지위 강화 가능성")
        else:
            print(f"  [분석] 순위 하락 위험 증가")
    
    # 3위 Chico Poker 상대적 성과
    chico_online = next((c for c in weekly_top5_changes if c['platform'] == 'Chico Poker' and c['metric'] == 'online_players'), None)
    if chico_online and weekly_market_change != 0:
        chico_loss = chico_online['start_value'] - chico_online['end_value']
        days = calculate_days_between(chico_online['start_date'], chico_online['end_date'])
        relative_performance = chico_online['change_percent'] - weekly_market_change
        
        performance_status = ""
        if relative_performance > 5:
            performance_status = "시장 대비 선방"
        elif relative_performance > -5:
            performance_status = "시장 평균 수준"
        else:
            performance_status = "시장 대비 부진"
            
        print(f"\n[RANK3] 3위 Chico Poker: {chico_online['change_percent']:+.1f}% (시장: {weekly_market_change:+.1f}%)")
        print(f"  상대적 성과: {relative_performance:+.1f}%p → {performance_status}")
        print(f"  변화 기간: {chico_online['start_date']} ~ {chico_online['end_date']} ({days}일간)")
        
        if relative_performance > 0:
            print(f"  [분석] 3위 지위 안정적 유지")
        else:
            print(f"  [분석] 중위권으로 하락 가능성")
            
    # 시장 점유율 변화 분석 (월간 기준)
    if gg_monthly and monthly_market_change != 0:
        old_market_share = (gg_monthly['start_value'] / m_start) * 100
        new_market_share = (gg_monthly['end_value'] / m_end) * 100
        market_share_change = new_market_share - old_market_share
        
        print(f"\n[MARKET SHARE] GGNetwork 시장 점유율 변화")
        print(f"  {gg_monthly['start_date']}: {old_market_share:.1f}% → {gg_monthly['end_date']}: {new_market_share:.1f}%")
        print(f"  점유율 변화: {market_share_change:+.1f}%p")
        
        if market_share_change > 0:
            print(f"  [결과] 시장 지배력 강화")
        else:
            print(f"  [결과] 시장 지배력 약화")
    
    # 큰 변화가 일어난 날짜 구간 분석
    print("\n[주요 변화 구간 타임라인]")
    print("="*60)
    
    all_changes = monthly_top5_changes + weekly_top5_changes
    major_changes = [c for c in all_changes if c['severity'] == 'major']
    
    # 변화율 기준으로 정렬
    major_changes_sorted = sorted(major_changes, key=lambda x: abs(x['change_percent']), reverse=True)
    
    for i, change in enumerate(major_changes_sorted[:3], 1):
        days = calculate_days_between(change['start_date'], change['end_date'])
        metric_kr = "온라인 플레이어" if change['metric'] == 'online_players' else "캐시 플레이어"
        direction_kr = "증가" if change['direction'] == 'increase' else "감소"
        
        print(f"\n{i}. {change['platform']} - {metric_kr}")
        print(f"   변화 구간: {change['start_date']} ~ {change['end_date']} ({days}일간)")
        print(f"   변화량: {change['start_value']:,} → {change['end_value']:,} ({change['change_percent']:+.1f}%)")
        print(f"   방향: {direction_kr} | 절대값: {abs(change['change_absolute']):,}명")
        
        # 일평균 변화량 계산
        if days > 0:
            daily_avg_change = abs(change['change_absolute']) / days
            print(f"   일평균 변화: {daily_avg_change:,.0f}명/일")
    
    # 전체 상위 5위권 안정성 평가
    total_major_changes = len([c for c in monthly_top5_changes + weekly_top5_changes if c['severity'] == 'major'])
    total_changes = len(monthly_top5_changes) + len(weekly_top5_changes)
    decrease_count = len([c for c in monthly_top5_changes + weekly_top5_changes if c['direction'] == 'decrease'])
    
    stability_index = ((5 - min(total_major_changes, 5)) / 5 * 100)
    decrease_ratio = decrease_count / total_changes * 100 if total_changes > 0 else 0
    
    print(f"\n[종합 평가]")
    print("="*60)
    print(f"[METRIC] 상위 5위권 안정성 지수: {stability_index:.0f}%")
    print(f"[METRIC] 총 변화 감지: {total_changes}건")
    print(f"[METRIC] 주요 변화: {total_major_changes}건")
    print(f"[METRIC] 감소 비중: {decrease_ratio:.0f}%")
    
    # 위험도 평가
    if total_major_changes >= 4:
        risk_level = "[CRITICAL]"
        stability = "매우 높은 변동성 - 상위권 대격변"
    elif total_major_changes >= 2:
        risk_level = "[HIGH]"
        stability = "높은 변동성 - 상위권 경쟁 구도 변화"
    elif total_major_changes >= 1:
        risk_level = "[MEDIUM]"
        stability = "중간 변동성 - 일부 플랫폼 변동"
    else:
        risk_level = "[LOW]"
        stability = "안정적 - 큰 변화 없음"
    
    print(f"\n[ASSESSMENT] 최종 평가:")
    print(f"   위험도: {risk_level}")
    print(f"   상태: {stability}")
    
    if decrease_ratio > 70:
        print(f"   트렌드: [DOWN] 상위 5위권 전반 급격한 위축")
    elif decrease_ratio > 50:
        print(f"   트렌드: [DOWN] 상위 5위권 위축세")
    elif decrease_ratio < 30:
        print(f"   트렌드: [UP] 상위 5위권 성장세")
    else:
        print(f"   트렌드: [STABLE] 균형 상태")
    
    # 핵심 인사이트
    print(f"\n[핵심 인사이트]")
    print("-" * 40)
    
    online_decreases = len([c for c in monthly_online + weekly_online if c['direction'] == 'decrease'])
    total_online_changes = len(monthly_online + weekly_online)
    
    if total_online_changes > 0:
        online_decrease_ratio = online_decreases / total_online_changes * 100
        if online_decrease_ratio > 60:
            print("- 상위 5위권 온라인 플레이어 수 전반적 감소 추세")
        else:
            print("- 상위 5위권 온라인 플레이어 수 혼재된 상황")
    
    if gg_monthly and abs(gg_monthly['change_percent']) > 40:
        print("- 시장 리더 GGNetwork 대폭 변화로 전체 시장 불안정")
    
    if total_major_changes > 3:
        print("- 상위권 전체적 변동성 증가로 순위 재편 가능성")
    
    print(f"\n[COMPLETED] 분석 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    analyze_top5_changes()