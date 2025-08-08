#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug data mapping issues between current and historical data
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

def analyze_html_structure():
    """Analyze the exact HTML structure to understand data mapping issues"""
    print("=" * 100)
    print("🔍 HTML 구조 분석 - 현재 vs 이전 데이터 매핑 문제")
    print("=" * 100)
    
    analyzer = LivePokerDataAnalyzer()
    
    try:
        response = analyzer.scraper.get('https://www.pokerscout.com', timeout=30)
        print(f"✅ PokerScout 연결 성공 - Status: {response.status_code}")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', {'class': 'rankTable'})
        if not table:
            print("❌ rankTable을 찾을 수 없음!")
            return
        
        print(f"✅ rankTable 발견")
        
        # Get header to understand column structure
        headers = table.find('tr')
        if headers:
            print("\n📋 테이블 헤더 분석:")
            print("-" * 60)
            header_cells = headers.find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                print(f"  Column {i}: '{cell.get_text(strip=True)}'")
        
        # Get all rows for detailed analysis
        rows = table.find_all('tr')
        print(f"\n📊 총 행 개수: {len(rows)}")
        
        print("\n" + "=" * 100)
        print("🔍 주요 플랫폼 상세 HTML 구조 분석")
        print("=" * 100)
        
        # Focus on platforms with suspicious data
        suspicious_platforms = ['GGNetwork', 'PokerStars', 'Ontario']
        
        for i, row in enumerate(rows[1:], 1):  # Skip header
            # Check if this row contains suspicious platform
            row_text = row.get_text().lower()
            is_suspicious = any(platform.lower() in row_text for platform in suspicious_platforms)
            
            if is_suspicious and i <= 10:  # Only first 10 rows
                print(f"\n--- 행 {i}: 의심스러운 플랫폼 발견 ---")
                
                # Show raw HTML structure
                print("🔍 원본 HTML:")
                print(str(row)[:200] + "..." if len(str(row)) > 200 else str(row))
                
                # Parse TD elements
                tds = row.find_all('td')
                print(f"\n📋 TD 요소 분석 ({len(tds)}개):")
                
                for j, td in enumerate(tds):
                    td_id = td.get('id')
                    td_class = td.get('class')
                    td_text = td.get_text(strip=True)
                    
                    print(f"  TD[{j}]: '{td_text}' | ID='{td_id}' | Class='{td_class}'")
                    
                    # Look for nested elements
                    spans = td.find_all('span')
                    if spans:
                        for k, span in enumerate(spans):
                            span_class = span.get('class')
                            span_text = span.get_text(strip=True)
                            print(f"    └─ Span[{k}]: '{span_text}' | Class='{span_class}'")
                
                # Try to identify what each field represents
                print("\n🎯 데이터 매핑 추정:")
                
                # Current online (should be TD with id='online')
                online_td = row.find('td', {'id': 'online'})
                if online_td:
                    online_span = online_td.find('span')
                    online_value = online_span.get_text(strip=True) if online_span else online_td.get_text(strip=True)
                    print(f"  현재 온라인: '{online_value}' (TD id='online')")
                
                # Cash players (should be TD with id='cash')
                cash_td = row.find('td', {'id': 'cash'})
                if cash_td:
                    cash_value = cash_td.get_text(strip=True)
                    print(f"  현재 캐시: '{cash_value}' (TD id='cash')")
                
                # Peak 24h (should be TD with id='peak')
                peak_td = row.find('td', {'id': 'peak'})
                if peak_td:
                    peak_span = peak_td.find('span')
                    peak_value = peak_span.get_text(strip=True) if peak_span else peak_td.get_text(strip=True)
                    print(f"  24시간 피크: '{peak_value}' (TD id='peak')")
                
                # 7-day average (should be TD with id='avg')
                avg_td = row.find('td', {'id': 'avg'})
                if avg_td:
                    avg_value = avg_td.get_text(strip=True)
                    print(f"  7일 평균: '{avg_value}' (TD id='avg')")
                
                # Hours data (TD with id='hours')
                hours_td = row.find('td', {'id': 'hours'})
                if hours_td:
                    hours_value = hours_td.get_text(strip=True)[:50]  # First 50 chars
                    print(f"  시간별 데이터: '{hours_value}...' (TD id='hours')")
                
                print("\n" + "=" * 60)
        
        print("\n" + "=" * 100)
        print("🔍 데이터 매핑 이슈 분석")
        print("=" * 100)
        
        # Analyze potential mapping issues
        print("잠재적 문제점들:")
        print("1. 현재 온라인 플레이어 vs 7일 평균의 값 차이가 극심함")
        print("2. 같은 플랫폼(PokerStars)에서 동일한 현재값이 나타남")
        print("3. Peak 24h보다 현재값이 훨씬 높음")
        print("4. 일부 플랫폼의 7일 평균이 0 또는 매우 낮음")
        
        print("\n가능한 원인들:")
        print("1. PokerScout 사이트의 데이터 오류")
        print("2. HTML 파싱 시 잘못된 컬럼 매핑")
        print("3. 스크래핑 타이밍 이슈 (데이터 업데이트 중)")
        print("4. 사이트 구조 변경으로 인한 파싱 오류")
        
    except Exception as e:
        print(f"❌ 분석 중 오류: {e}")
        return

def compare_data_consistency():
    """Compare data consistency across multiple scrapes"""
    print("\n" + "=" * 100)
    print("📊 데이터 일관성 비교 (다중 스크래핑)")
    print("=" * 100)
    
    analyzer = LivePokerDataAnalyzer()
    
    print("🔄 3번 연속 데이터 수집하여 일관성 확인...")
    
    all_scrapes = []
    for i in range(3):
        print(f"\n스크래핑 #{i+1}...")
        data = analyzer.crawl_pokerscout_data()
        if data:
            all_scrapes.append(data)
            print(f"  ✅ {len(data)}개 플랫폼 수집")
        else:
            print(f"  ❌ 수집 실패")
    
    if len(all_scrapes) < 2:
        print("❌ 비교할 수 있는 충분한 데이터가 없음")
        return
    
    print("\n" + "=" * 100)
    print("🔍 스크래핑 결과 비교")
    print("=" * 100)
    
    # Compare first scrape with others
    base_scrape = all_scrapes[0]
    
    for scrape_num, scrape_data in enumerate(all_scrapes[1:], 2):
        print(f"\n스크래핑 #1 vs 스크래핑 #{scrape_num}:")
        print("-" * 50)
        
        # Create lookup for comparison
        base_lookup = {site['site_name']: site for site in base_scrape}
        compare_lookup = {site['site_name']: site for site in scrape_data}
        
        # Find common platforms
        common_platforms = set(base_lookup.keys()) & set(compare_lookup.keys())
        print(f"공통 플랫폼 수: {len(common_platforms)}")
        
        # Check for differences in key values
        differences = []
        
        for platform in common_platforms:
            base_site = base_lookup[platform]
            compare_site = compare_lookup[platform]
            
            # Check each field
            fields = ['players_online', 'cash_players', 'peak_24h', 'seven_day_avg']
            
            for field in fields:
                base_val = base_site[field]
                compare_val = compare_site[field]
                
                if base_val != compare_val:
                    differences.append({
                        'platform': platform,
                        'field': field,
                        'scrape1': base_val,
                        f'scrape{scrape_num}': compare_val,
                        'change': compare_val - base_val if base_val > 0 else 0
                    })
        
        if differences:
            print(f"발견된 차이점: {len(differences)}개")
            
            # Show top differences
            for diff in differences[:10]:
                print(f"  • {diff['platform']} - {diff['field']}: {diff['scrape1']} → {diff[f'scrape{scrape_num}']} (차이: {diff['change']})")
        else:
            print("✅ 차이점 없음 - 데이터 일관성 확인")

def analyze_historical_data_source():
    """Analyze how historical data (7-day avg, peak) is sourced"""
    print("\n" + "=" * 100)
    print("🕐 이전 데이터 소스 분석")
    print("=" * 100)
    
    print("7일 평균 및 24시간 피크 데이터의 출처를 분석합니다:")
    print()
    
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("❌ 데이터 수집 실패")
        return
    
    # Analyze patterns in historical data
    print("📋 이전 데이터 패턴 분석:")
    print("-" * 60)
    
    platforms_with_zero_avg = []
    platforms_with_unrealistic_ratios = []
    platforms_with_consistent_data = []
    
    for site in data:
        current = site['players_online']
        avg_7day = site['seven_day_avg']
        peak_24h = site['peak_24h']
        
        # Check for zero 7-day average
        if avg_7day == 0 and current > 0:
            platforms_with_zero_avg.append(site['site_name'])
        
        # Check for unrealistic current vs peak ratio
        if peak_24h > 0 and current > peak_24h * 3:
            ratio = current / peak_24h
            platforms_with_unrealistic_ratios.append({
                'name': site['site_name'],
                'current': current,
                'peak': peak_24h,
                'ratio': ratio
            })
        
        # Check for consistent data
        if avg_7day > 0 and peak_24h > 0 and current > 0:
            # Reasonable ranges: current should be 0.5x to 2x of 7-day avg
            if 0.5 <= current / avg_7day <= 2.0:
                platforms_with_consistent_data.append(site['site_name'])
    
    print(f"❌ 7일 평균이 0인 플랫폼: {len(platforms_with_zero_avg)}개")
    for platform in platforms_with_zero_avg[:5]:
        print(f"   • {platform}")
    
    print(f"\n⚠️ 비현실적인 현재/피크 비율: {len(platforms_with_unrealistic_ratios)}개")
    for item in platforms_with_unrealistic_ratios[:5]:
        print(f"   • {item['name']}: {item['current']:,} / {item['peak']:,} = {item['ratio']:.1f}x")
    
    print(f"\n✅ 일관성 있는 데이터: {len(platforms_with_consistent_data)}개")
    for platform in platforms_with_consistent_data[:5]:
        print(f"   • {platform}")
    
    print("\n" + "=" * 100)
    print("💡 결론")
    print("=" * 100)
    
    total_platforms = len(data)
    problematic_ratio = (len(platforms_with_zero_avg) + len(platforms_with_unrealistic_ratios)) / total_platforms * 100
    
    print(f"전체 플랫폼: {total_platforms}개")
    print(f"문제 있는 플랫폼: {len(platforms_with_zero_avg) + len(platforms_with_unrealistic_ratios)}개 ({problematic_ratio:.1f}%)")
    print(f"정상 데이터: {len(platforms_with_consistent_data)}개 ({len(platforms_with_consistent_data)/total_platforms*100:.1f}%)")
    
    if problematic_ratio > 50:
        print("\n🚨 문제 심각도: 높음")
        print("   - PokerScout 사이트 자체의 데이터 품질 이슈로 보임")
        print("   - 이전 데이터(7일 평균, 24시간 피크)의 신뢰성이 낮음")
    elif problematic_ratio > 25:
        print("\n⚠️ 문제 심각도: 중간")
        print("   - 일부 플랫폼의 데이터 품질 이슈")
    else:
        print("\n✅ 문제 심각도: 낮음")
        print("   - 대부분의 데이터가 일관성 있음")

def main():
    print("=" * 100)
    print("🐛 데이터 매핑 문제 분석 도구")
    print("📅 " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 100)
    
    # 1. HTML 구조 분석
    analyze_html_structure()
    
    # 2. 데이터 일관성 확인
    compare_data_consistency()
    
    # 3. 이전 데이터 소스 분석
    analyze_historical_data_source()
    
    print("\n" + "=" * 100)
    print("🎯 최종 진단")
    print("=" * 100)
    print("문제의 근본 원인은 다음 중 하나일 가능성이 높습니다:")
    print()
    print("1. 🌐 PokerScout 사이트 자체의 데이터 오류")
    print("   - 현재 플레이어 수가 실제보다 높게 표시됨")
    print("   - 7일 평균이 업데이트되지 않거나 잘못된 값")
    print("   - 같은 값이 여러 플랫폼에 중복 표시")
    print()
    print("2. 📊 데이터 업데이트 타이밍 이슈")
    print("   - 현재 데이터는 실시간 업데이트")
    print("   - 이전 데이터는 지연되거나 수동 업데이트")
    print()
    print("3. 🔧 HTML 구조 변경")
    print("   - PokerScout이 사이트 구조를 변경")
    print("   - 파싱 로직이 예전 구조에 맞춰져 있음")
    print("=" * 100)

if __name__ == "__main__":
    main()