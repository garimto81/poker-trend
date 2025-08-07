#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사이트별 일일 비교 데이터 표시
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

def show_daily_comparison():
    """오늘과 전일 비교 데이터 표시"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("=" * 100)
    print(f"포커 사이트 일일 비교 분석: {yesterday} vs {today}")
    print("=" * 100)
    
    conn = sqlite3.connect('poker_history.db')
    cursor = conn.cursor()
    
    # 오늘 데이터
    cursor.execute("""
        SELECT site_name, players_online, cash_players, data_quality
        FROM daily_data 
        WHERE date = ?
        ORDER BY players_online DESC
    """, (today,))
    today_data = cursor.fetchall()
    
    # 어제 데이터
    cursor.execute("""
        SELECT site_name, players_online, cash_players, data_quality
        FROM daily_data 
        WHERE date = ?
        ORDER BY players_online DESC
    """, (yesterday,))
    yesterday_data = cursor.fetchall()
    
    # 어제 데이터를 딕셔너리로 변환
    yesterday_dict = {site: (online, cash) for site, online, cash, quality in yesterday_data}
    
    print(f"{'Rank':<4} {'사이트':<20} {'오늘 온라인':<12} {'오늘 캐시':<10} {'전일 온라인':<12} {'전일 캐시':<10} {'온라인 변화':<15} {'캐시 변화':<15} {'품질':<10}")
    print("-" * 100)
    
    for rank, (site, today_online, today_cash, quality) in enumerate(today_data, 1):
        if site in yesterday_dict:
            yesterday_online, yesterday_cash = yesterday_dict[site]
            
            # 변화량 계산
            online_change = today_online - yesterday_online
            cash_change = today_cash - yesterday_cash
            
            online_change_pct = (online_change / yesterday_online * 100) if yesterday_online > 0 else 0
            cash_change_pct = (cash_change / yesterday_cash * 100) if yesterday_cash > 0 else 0
            
            # 변화량 표시
            online_change_str = f"{online_change:+,} ({online_change_pct:+.1f}%)"
            cash_change_str = f"{cash_change:+,} ({cash_change_pct:+.1f}%)"
        else:
            yesterday_online = 0
            yesterday_cash = 0
            online_change_str = "신규"
            cash_change_str = "신규"
        
        print(f"{rank:<4} {site[:19]:<20} {today_online:>11,} {today_cash:>9,} {yesterday_online:>11,} {yesterday_cash:>9,} {online_change_str:<15} {cash_change_str:<15} {quality:<10}")
    
    # 요약 통계
    print("\n" + "=" * 100)
    print("요약 통계")
    print("=" * 100)
    
    total_today_online = sum(online for _, online, _, _ in today_data)
    total_today_cash = sum(cash for _, _, cash, _ in today_data)
    
    total_yesterday_online = sum(online for _, online in yesterday_dict.values())
    total_yesterday_cash = sum(cash for _, cash in yesterday_dict.values())
    
    total_online_change = total_today_online - total_yesterday_online
    total_cash_change = total_today_cash - total_yesterday_cash
    
    print(f"총 온라인 플레이어: {total_today_online:,} (전일: {total_yesterday_online:,}, 변화: {total_online_change:+,})")
    print(f"총 캐시 플레이어: {total_today_cash:,} (전일: {total_yesterday_cash:,}, 변화: {total_cash_change:+,})")
    print(f"활성 사이트 수: {len(today_data)}개")
    
    # TOP 5 집중 분석
    print("\n" + "=" * 100)
    print("TOP 5 사이트 집중 분석")
    print("=" * 100)
    
    for i, (site, today_online, today_cash, quality) in enumerate(today_data[:5], 1):
        if site in yesterday_dict:
            yesterday_online, yesterday_cash = yesterday_dict[site]
            online_change = today_online - yesterday_online
            cash_change = today_cash - yesterday_cash
            online_change_pct = (online_change / yesterday_online * 100) if yesterday_online > 0 else 0
            cash_change_pct = (cash_change / yesterday_cash * 100) if yesterday_cash > 0 else 0
            
            # 트렌드 아이콘
            online_trend = "UP" if online_change > 0 else "DOWN" if online_change < 0 else "SAME"
            cash_trend = "UP" if cash_change > 0 else "DOWN" if cash_change < 0 else "SAME"
            
            print(f"\n{i}. {site}")
            print(f"   온라인: {today_online:,}명 → {yesterday_online:,}명 = {online_change:+,}명 ({online_change_pct:+.1f}%) {online_trend}")
            print(f"   캐시:   {today_cash:,}명 → {yesterday_cash:,}명 = {cash_change:+,}명 ({cash_change_pct:+.1f}%) {cash_trend}")
            print(f"   품질:   {quality}")
        else:
            print(f"\n{i}. {site} (신규 데이터)")
            print(f"   온라인: {today_online:,}명 NEW")
            print(f"   캐시:   {today_cash:,}명 NEW")
    
    conn.close()

if __name__ == "__main__":
    show_daily_comparison()