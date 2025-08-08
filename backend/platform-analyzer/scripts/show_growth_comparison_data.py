#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show all growth comparison data categories used in analysis
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

def show_all_comparison_data_sources():
    """Show all data sources used for growth rate calculations"""
    print("="*120)
    print("🔍 GROWTH RATE COMPARISON DATA ANALYSIS")
    print("📊 Showing ALL data categories used for growth calculations")
    print("="*120)
    
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("❌ No data available")
        return
    
    print(f"✅ Collected data from {len(data)} platforms")
    print(f"📅 Data collected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sort by current online players for better readability
    sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)
    
    print("\n" + "="*120)
    print("📋 COMPLETE COMPARISON DATA TABLE")
    print("="*120)
    print("🔵 Current Data = Real-time scraped from PokerScout")
    print("🟡 7-Day Avg = Historical average from PokerScout")  
    print("🟢 Peak 24h = 24-hour peak from PokerScout")
    print("🔴 Growth Rate = (Current - 7-Day Avg) / 7-Day Avg * 100")
    print("="*120)
    
    print(f"{'Rank':<4} {'Platform':<25} {'🔵Current Online':<15} {'💰Current Cash':<15} {'🟡7-Day Avg':<12} {'🟢Peak 24h':<12} {'🔴Growth %':<12} {'Issues':<20}")
    print("-"*120)
    
    for i, site in enumerate(sorted_data, 1):
        current_online = site['players_online']
        current_cash = site['cash_players']
        seven_day_avg = site['seven_day_avg']
        peak_24h = site['peak_24h']
        
        # Calculate growth rate exactly as done in analysis
        if seven_day_avg > 0:
            growth_rate = ((current_online - seven_day_avg) / seven_day_avg) * 100
            growth_display = f"{growth_rate:+.1f}%"
        else:
            growth_rate = float('inf') if current_online > 0 else 0
            growth_display = "INF%" if current_online > 0 else "0%"
        
        # Identify issues
        issues = []
        if abs(growth_rate) > 1000 and growth_rate != float('inf'):
            issues.append("Extreme")
        if seven_day_avg == 0 and current_online > 0:
            issues.append("No-7day-data")
        if current_online > peak_24h * 5 and peak_24h > 0:
            issues.append("Current>>Peak")
        if seven_day_avg > current_online * 10 and current_online > 100:
            issues.append("7day>>Current")
            
        issue_text = ",".join(issues) if issues else "OK"
        
        print(f"{i:<4} {site['site_name'][:24]:<25} {current_online:<15,} {current_cash:<15,} {seven_day_avg:<12,} {peak_24h:<12,} {growth_display:<12} {issue_text:<20}")
    
    print("\n" + "="*120)
    print("📊 DATA SOURCE BREAKDOWN")
    print("="*120)
    
    # Analyze data sources
    total_platforms = len(data)
    platforms_with_current = len([s for s in data if s['players_online'] > 0])
    platforms_with_7day = len([s for s in data if s['seven_day_avg'] > 0])
    platforms_with_peak = len([s for s in data if s['peak_24h'] > 0])
    platforms_with_cash = len([s for s in data if s['cash_players'] > 0])
    
    print(f"📈 CURRENT ONLINE PLAYERS:")
    print(f"   • Total platforms with current data: {platforms_with_current}/{total_platforms}")
    print(f"   • Source: Real-time scraping from PokerScout.com")
    print(f"   • Update frequency: Live (every request)")
    print(f"   • Data reliability: High ✅")
    
    print(f"\n🕐 7-DAY AVERAGE DATA:")
    print(f"   • Total platforms with 7-day avg: {platforms_with_7day}/{total_platforms}")
    print(f"   • Source: PokerScout's calculated 7-day rolling average")
    print(f"   • Update frequency: Updated by PokerScout (unknown interval)")
    print(f"   • Data reliability: Dependent on PokerScout ⚠️")
    
    print(f"\n⏰ 24-HOUR PEAK DATA:")
    print(f"   • Total platforms with peak data: {platforms_with_peak}/{total_platforms}")
    print(f"   • Source: PokerScout's 24-hour maximum")
    print(f"   • Update frequency: Rolling 24-hour window")
    print(f"   • Data reliability: Medium ⚠️")
    
    print(f"\n💰 CASH PLAYERS DATA:")
    print(f"   • Total platforms with cash data: {platforms_with_cash}/{total_platforms}")
    print(f"   • Source: Real-time cash game players from PokerScout")
    print(f"   • Update frequency: Live (every request)")
    print(f"   • Data reliability: High ✅")
    
    print("\n" + "="*120)
    print("🔍 GROWTH CALCULATION METHOD ANALYSIS")
    print("="*120)
    
    print("Current method uses:")
    print("🔴 Growth Rate = (Current Online Players - 7-Day Average) / 7-Day Average × 100")
    print()
    print("📊 Alternative comparison methods we COULD use:")
    print("   1. vs Previous Hour: (Current - 1hr ago) / 1hr ago × 100")
    print("   2. vs Yesterday: (Current - 24hr ago) / 24hr ago × 100") 
    print("   3. vs Peak 24h: (Current - Peak 24h) / Peak 24h × 100")
    print("   4. vs Weekly Peak: (Current - Week Peak) / Week Peak × 100")
    print("   5. Cash Growth: (Current Cash - Previous Cash) / Previous Cash × 100")
    
    print("\n" + "="*120)
    print("⚠️ IDENTIFIED ISSUES WITH CURRENT METHOD")
    print("="*120)
    
    # Find specific problematic cases
    extreme_cases = []
    missing_7day = []
    unrealistic_ratios = []
    
    for site in data:
        current = site['players_online']
        seven_day = site['seven_day_avg']
        peak = site['peak_24h']
        
        if seven_day > 0:
            growth = ((current - seven_day) / seven_day) * 100
            if abs(growth) > 1000:
                extreme_cases.append({
                    'name': site['site_name'],
                    'current': current,
                    'seven_day': seven_day,
                    'growth': growth,
                    'peak': peak
                })
        
        if seven_day == 0 and current > 0:
            missing_7day.append({
                'name': site['site_name'],
                'current': current
            })
        
        if current > peak * 3 and peak > 0:
            unrealistic_ratios.append({
                'name': site['site_name'],
                'current': current,
                'peak': peak,
                'ratio': current / peak
            })
    
    print(f"❌ EXTREME GROWTH RATES (>1000%):")
    if extreme_cases:
        extreme_cases.sort(key=lambda x: abs(x['growth']), reverse=True)
        for case in extreme_cases[:5]:
            print(f"   • {case['name']}: {case['current']:,} vs {case['seven_day']:,} = {case['growth']:+.1f}%")
            print(f"     → Possible issue: 7-day avg ({case['seven_day']:,}) seems too low vs current ({case['current']:,})")
    else:
        print("   ✅ None found")
    
    print(f"\n❌ MISSING 7-DAY DATA (causing INF growth):")
    if missing_7day:
        for case in missing_7day[:5]:
            print(f"   • {case['name']}: Current={case['current']:,}, 7-day avg=0")
            print(f"     → Issue: Cannot calculate growth rate when 7-day avg is 0")
    else:
        print("   ✅ None found")
    
    print(f"\n❌ CURRENT > 3× PEAK (unrealistic):")
    if unrealistic_ratios:
        unrealistic_ratios.sort(key=lambda x: x['ratio'], reverse=True)
        for case in unrealistic_ratios[:5]:
            print(f"   • {case['name']}: Current={case['current']:,}, Peak={case['peak']:,} (ratio: {case['ratio']:.1f}×)")
            print(f"     → Issue: Current players cannot realistically be {case['ratio']:.1f}× the 24h peak")
    else:
        print("   ✅ None found")
    
    print("\n" + "="*120)
    print("💡 RECOMMENDATIONS")
    print("="*120)
    print("1. 🔍 Validate 7-day average data source")
    print("   • Check if PokerScout's 7-day avg is calculated correctly")
    print("   • Some platforms may have 0 or very low historical data")
    print()
    print("2. 📊 Use alternative growth metrics")
    print("   • Compare current vs 24-hour peak instead")
    print("   • Use percentage of peak capacity as growth indicator")
    print()
    print("3. ⚠️ Add data validation rules")
    print("   • Cap maximum realistic growth at ±500% for weekly comparison")
    print("   • Flag platforms where current > 3× peak as suspicious")
    print()
    print("4. 🕐 Implement historical data collection")
    print("   • Store our own historical snapshots")
    print("   • Calculate growth from our stored previous values")
    print("="*120)

def show_raw_scraped_data():
    """Show exactly what was scraped from HTML"""
    print("\n" + "="*120)
    print("🌐 RAW SCRAPED DATA FROM POKERSCOUT.COM")
    print("="*120)
    print("This is EXACTLY what was extracted from PokerScout HTML:")
    print()
    
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    # Show first few entries with all raw data
    print("📋 SAMPLE RAW ENTRIES:")
    print("-"*80)
    
    for i, site in enumerate(data[:10]):
        print(f"\n{i+1}. {site['site_name']}:")
        print(f"   Raw online players: '{site['players_online']}'")
        print(f"   Raw cash players: '{site['cash_players']}'")
        print(f"   Raw peak 24h: '{site['peak_24h']}'")
        print(f"   Raw 7-day avg: '{site['seven_day_avg']}'")
        print(f"   Collected at: {site['collected_at']}")

def main():
    print("="*120)
    print("📊 GROWTH RATE COMPARISON DATA ANALYSIS")
    print("🔍 Detailed breakdown of ALL data sources used for growth calculations")
    print("="*120)
    
    # Show comprehensive comparison data
    show_all_comparison_data_sources()
    
    # Show raw scraped data
    show_raw_scraped_data()

if __name__ == "__main__":
    main()