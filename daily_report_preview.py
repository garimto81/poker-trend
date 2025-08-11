#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 일간 분석 미리보기 생성
"""

import os
from firebase_platform_analyzer import FirebasePlatformAnalyzer

def generate_daily_preview():
    """일간 보고서 미리보기"""
    
    # 환경변수 설정
    os.environ['REPORT_TYPE'] = 'daily'
    
    # 분석기 실행
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if not report:
        print("[ERROR] 일간 보고서 생성 실패")
        return
    
    # 미리보기 생성
    print("=" * 80)
    print("Firebase 일간 플랫폼 분석 미리보기")
    print("=" * 80)
    print(f"기간: {report['data_period']['start']}")
    print(f"데이터: Firebase (PokerStars US/Ontario 제외)")
    print("=" * 80)
    
    # 기본 통계
    summary = report['summary']
    platforms = report['top_platforms']
    
    print(f"\n총 플랫폼 수: {summary['total_platforms']}개")
    print(f"총 온라인 플레이어: {summary['total_online_players']:,}명")
    
    # 온라인 TOP 3
    print(f"\n[온라인 플레이어 TOP 3]")
    for i, platform in enumerate(platforms[:3], 1):
        print(f"TOP {i} {platform['platform_name']:<20} {platform['online_players']:>10,}명")
    
    print(f"\n총 캐시 플레이어: {summary['total_cash_players']:,}명")
    
    # 캐시게임 TOP 3
    cash_sorted = sorted(platforms, key=lambda x: x['cash_players'], reverse=True)
    print(f"\n[캐시게임 플레이어 TOP 3]")
    for i, platform in enumerate(cash_sorted[:3], 1):
        print(f"TOP {i} {platform['platform_name']:<20} {platform['cash_players']:>10,}명")
    
    # AI 분석 결과
    print(f"\n[AI 분석 결과]")
    
    # 1. 시장 지배력 분석
    leader = platforms[0]
    if leader['online_players'] > 100000:
        print(f"1. 시장 지배: {leader['platform_name']}가 {leader['online_players']:,}명으로 압도적 우위")
    else:
        print(f"1. 시장 분산: 1위 {leader['platform_name']}도 {leader['online_players']:,}명에 불과")
    
    # 2. 캐시게임 분석
    cash_leader = cash_sorted[0]
    if cash_leader['cash_players'] > 5000:
        print(f"2. 캐시게임 강세: {cash_leader['platform_name']}가 {cash_leader['cash_players']:,}명 확보")
    else:
        print(f"2. 캐시게임 미약: 최대 {cash_leader['platform_name']}도 {cash_leader['cash_players']:,}명")
    
    # 3. 시장 규모
    total_online = summary['total_online_players']
    if total_online > 500000:
        print(f"3. 대형 시장: 전체 {total_online:,}명의 대규모 시장")
    elif total_online > 200000:
        print(f"3. 중형 시장: 전체 {total_online:,}명의 활성 시장")
    else:
        print(f"3. 소형 시장: 전체 {total_online:,}명의 제한적 시장")
    
    # 4. 특이사항
    active_platforms = len([p for p in platforms if p['online_players'] > 0])
    print(f"4. 활성 플랫폼: {active_platforms}개 사이트가 실제 운영 중")
    
    # 5. 데이터 신뢰성
    print(f"5. 데이터 품질: Firebase 실시간 데이터 기반 (오염 데이터 제외)")
    
    print("\n" + "=" * 80)
    print("생성 완료")
    print("=" * 80)

if __name__ == "__main__":
    generate_daily_preview()