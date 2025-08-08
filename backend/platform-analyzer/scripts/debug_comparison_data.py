#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug comparison data to identify parsing issues
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

def debug_raw_html_parsing():
    """Debug the actual HTML parsing to see what's going wrong"""
    print("="*100)
    print("🔍 DEBUGGING RAW HTML PARSING")
    print("="*100)
    
    analyzer = LivePokerDataAnalyzer()
    
    # Let's inspect the HTML structure
    try:
        response = analyzer.scraper.get('https://www.pokerscout.com', timeout=30)
        print(f"✅ Connected to PokerScout - Status: {response.status_code}")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', {'class': 'rankTable'})
        if not table:
            print("❌ No rankTable found!")
            return
        
        print(f"✅ Found rankTable")
        
        # Get first few rows to examine structure
        rows = table.find_all('tr')
        print(f"📊 Total rows found: {len(rows)}")
        
        print("\n" + "="*100)
        print("🔍 EXAMINING FIRST 5 DATA ROWS")
        print("="*100)
        
        for i, row in enumerate(rows[1:6]):  # Skip header, show first 5 data rows
            print(f"\n--- ROW {i+1} ---")
            
            # Show all TD elements
            tds = row.find_all('td')
            print(f"TDs found: {len(tds)}")
            
            for j, td in enumerate(tds):
                print(f"  TD[{j}]: '{td.get_text(strip=True)}' | ID: {td.get('id')} | Classes: {td.get('class')}")
            
            # Try to find brand-title
            brand_title = row.find('span', {'class': 'brand-title'})
            if brand_title:
                print(f"  ✅ Brand Title: '{brand_title.get_text(strip=True)}'")
            else:
                print(f"  ❌ No brand-title span found")
            
            # Try to find specific IDs
            online_td = row.find('td', {'id': 'online'})
            cash_td = row.find('td', {'id': 'cash'})
            peak_td = row.find('td', {'id': 'peak'})
            avg_td = row.find('td', {'id': 'avg'})
            
            print(f"  Online TD: {online_td.get_text(strip=True) if online_td else 'Not found'}")
            print(f"  Cash TD: {cash_td.get_text(strip=True) if cash_td else 'Not found'}")
            print(f"  Peak TD: {peak_td.get_text(strip=True) if peak_td else 'Not found'}")
            print(f"  Avg TD: {avg_td.get_text(strip=True) if avg_td else 'Not found'}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return

def show_comparison_data_details():
    """Show detailed comparison data with calculations"""
    print("\n" + "="*100)
    print("📊 DETAILED COMPARISON DATA ANALYSIS")
    print("="*100)
    
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("❌ No data available")
        return
    
    print(f"✅ Collected {len(data)} platforms")
    
    print("\n" + "="*100)
    print("🔍 SUSPICIOUS GROWTH RATE ANALYSIS")
    print("="*100)
    
    print(f"{'Platform':<25} {'Current':<12} {'7-Day Avg':<12} {'Peak 24h':<12} {'Growth %':<12} {'Issue?'}")
    print("-"*100)
    
    suspicious_platforms = []
    
    for site in data:
        if site['players_online'] > 0 or site['seven_day_avg'] > 0:
            current = site['players_online']
            avg_7day = site['seven_day_avg']
            peak_24h = site['peak_24h']
            
            # Calculate growth rate
            if avg_7day > 0:
                growth_rate = ((current - avg_7day) / avg_7day) * 100
            else:
                growth_rate = 0 if current == 0 else float('inf')
            
            # Identify issues
            issues = []
            
            # Check for unrealistic growth
            if abs(growth_rate) > 1000:
                issues.append("Extreme growth")
            
            # Check for unrealistic 7-day average
            if avg_7day > current * 10 and current > 1000:
                issues.append("7-day avg too high")
            
            # Check if current is way higher than peak
            if current > peak_24h * 5 and peak_24h > 0:
                issues.append("Current > 5x peak")
            
            # Check if 7-day avg is unrealistically high
            if avg_7day > 1000000:
                issues.append("Unrealistic 7-day avg")
            
            issue_text = ", ".join(issues) if issues else "OK"
            
            if issues:
                suspicious_platforms.append({
                    'name': site['site_name'],
                    'current': current,
                    'avg': avg_7day,
                    'peak': peak_24h,
                    'growth': growth_rate,
                    'issues': issues
                })
            
            # Show all platforms with details
            growth_display = f"{growth_rate:+.1f}" if growth_rate != float('inf') else "INF"
            print(f"{site['site_name'][:24]:<25} {current:<12,} {avg_7day:<12,} {peak_24h:<12,} {growth_display:<11}% {issue_text}")
    
    print(f"\n⚠️ Found {len(suspicious_platforms)} suspicious platforms")
    
    if suspicious_platforms:
        print("\n" + "="*100)
        print("🚨 MOST SUSPICIOUS PLATFORMS")
        print("="*100)
        
        # Sort by absolute growth rate
        suspicious_platforms.sort(key=lambda x: abs(x['growth']) if x['growth'] != float('inf') else 999999, reverse=True)
        
        for i, platform in enumerate(suspicious_platforms[:10], 1):
            print(f"\n{i}. {platform['name']}:")
            print(f"   Current Players: {platform['current']:,}")
            print(f"   7-Day Average: {platform['avg']:,}")
            print(f"   Peak 24h: {platform['peak']:,}")
            print(f"   Growth Rate: {platform['growth']:+.1f}%")
            print(f"   Issues: {', '.join(platform['issues'])}")
            
            # Calculate what the growth rate SHOULD be for realistic scenarios
            if platform['avg'] > 0 and platform['current'] > 0:
                # Realistic growth would be -50% to +200% for weekly comparison
                realistic_min = platform['avg'] * 0.5  # -50%
                realistic_max = platform['avg'] * 3.0  # +200%
                
                print(f"   Realistic range: {realistic_min:,.0f} - {realistic_max:,.0f}")
                
                if platform['current'] < realistic_min:
                    print(f"   → Likely issue: 7-day average is TOO HIGH")
                elif platform['current'] > realistic_max:
                    print(f"   → Likely issue: Current value is TOO HIGH or 7-day avg is TOO LOW")

def analyze_data_source_issues():
    """Analyze potential data source parsing issues"""
    print("\n" + "="*100)
    print("🔍 DATA SOURCE ANALYSIS")
    print("="*100)
    
    print("Potential issues:")
    print("1. Wrong column mapping in HTML parsing")
    print("2. 7-day average field contains wrong data")
    print("3. Mixed up current vs historical data")
    print("4. Wrong HTML elements being parsed")
    print("5. PokerScout changed their HTML structure")
    
    print("\n📋 RECOMMENDED FIXES:")
    print("1. Inspect actual PokerScout HTML manually")
    print("2. Check if column positions have changed")
    print("3. Verify that 'seven_day_avg' is parsing the right field")
    print("4. Cross-reference with PokerScout website directly")
    print("5. Add data validation rules (max realistic growth rate)")

def main():
    print("="*100)
    print("🐛 COMPARISON DATA DEBUG ANALYSIS")
    print("📅 " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*100)
    
    # Step 1: Debug raw HTML parsing
    debug_raw_html_parsing()
    
    # Step 2: Show detailed comparison analysis
    show_comparison_data_details()
    
    # Step 3: Analyze potential source issues
    analyze_data_source_issues()
    
    print("\n" + "="*100)
    print("🎯 SUMMARY OF FINDINGS")
    print("="*100)
    print("The extreme growth rates suggest that:")
    print("1. The 7-day average values are likely being parsed incorrectly")
    print("2. They might be too small (causing huge growth rates)")
    print("3. Or the current values are being parsed from wrong fields")
    print("4. HTML structure might have changed on PokerScout")
    print()
    print("👆 Please check the raw HTML structure above and let me know")
    print("   what you see that looks wrong!")
    print("="*100)

if __name__ == "__main__":
    main()