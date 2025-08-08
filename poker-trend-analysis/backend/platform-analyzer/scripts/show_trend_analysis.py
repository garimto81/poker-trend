#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show current trend analysis results for review
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

def show_raw_parsing_debug(data: List[Dict]):
    """Show raw parsing results for debugging"""
    print("="*100)
    print("🔍 RAW PARSING DEBUG - CHECKING DATA ACCURACY")
    print("="*100)
    
    print("\n📋 SAMPLE RAW DATA (First 5 entries):")
    print("-"*100)
    for i, site in enumerate(data[:5]):
        print(f"\n{i+1}. RAW ENTRY:")
        print(f"   Site Name: '{site['site_name']}'")
        print(f"   Online Players: {site['players_online']:,}")
        print(f"   Cash Players: {site['cash_players']:,}")
        print(f"   Peak 24h: {site['peak_24h']:,}")
        print(f"   7-Day Avg: {site['seven_day_avg']:,}")
        print(f"   Collected At: {site['collected_at']}")
    
    print(f"\n📊 PARSING SUMMARY:")
    print(f"   Total Sites Found: {len(data)}")
    print(f"   Sites with Online Players > 0: {len([s for s in data if s['players_online'] > 0])}")
    print(f"   Sites with Cash Players > 0: {len([s for s in data if s['cash_players'] > 0])}")
    
    # Check for suspicious data
    print(f"\n⚠️  SUSPICIOUS DATA CHECK:")
    suspicious = []
    
    for site in data:
        issues = []
        
        # Check if site name looks like a number
        if site['site_name'].replace(',', '').replace('.', '').isdigit():
            issues.append("Site name is numeric")
        
        # Check for extremely high 7-day averages
        if site['seven_day_avg'] > 1000000:
            issues.append(f"Unrealistic 7-day avg: {site['seven_day_avg']:,}")
        
        # Check for zero cash but high online
        if site['players_online'] > 10000 and site['cash_players'] == 0:
            issues.append("High online but zero cash players")
        
        if issues:
            suspicious.append({
                'site': site['site_name'],
                'issues': issues,
                'data': site
            })
    
    if suspicious:
        print(f"   Found {len(suspicious)} suspicious entries:")
        for item in suspicious[:3]:  # Show first 3
            print(f"   • {item['site']}: {', '.join(item['issues'])}")
    else:
        print("   No suspicious data patterns found")

def show_current_analysis():
    """Show current trend analysis with all details"""
    print("="*100)
    print("🎮 CURRENT ONLINE POKER PLATFORM TREND ANALYSIS")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Data Source: PokerScout.com (Live Crawling)")
    print("="*100)
    
    # Fetch live data
    analyzer = LivePokerDataAnalyzer()
    print("\n🔄 Crawling live data from PokerScout.com...")
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("❌ Failed to fetch data")
        return
    
    print(f"✅ Successfully collected {len(data)} platform entries")
    
    # Show raw parsing debug
    show_raw_parsing_debug(data)
    
    # Basic statistics
    total_online = sum(site['players_online'] for site in data)
    total_cash = sum(site['cash_players'] for site in data)
    active_platforms = len([s for s in data if s['players_online'] > 0])
    
    print("\n" + "="*100)
    print("📈 MARKET OVERVIEW")
    print("="*100)
    print(f"🌐 Total Online Players: {total_online:,}")
    print(f"💰 Total Cash Players: {total_cash:,}")
    print(f"🏢 Total Platforms Tracked: {len(data)}")
    print(f"⚡ Active Platforms (>0 players): {active_platforms}")
    print(f"📊 Average Players per Active Platform: {total_online // active_platforms if active_platforms > 0 else 0:,}")
    print(f"💵 Cash/Online Ratio: {(total_cash / total_online * 100) if total_online > 0 else 0:.2f}%")
    
    # Sort by online players
    sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)
    
    print("\n" + "="*100)
    print("🏆 TOP 15 PLATFORMS BY ONLINE PLAYERS")
    print("="*100)
    print(f"{'#':<3} {'Platform Name':<25} {'Online':<12} {'Cash':<10} {'Cash%':<8} {'Peak 24h':<12} {'7-Day Avg':<12}")
    print("-"*100)
    
    for i, site in enumerate(sorted_data[:15], 1):
        cash_pct = (site['cash_players'] / site['players_online'] * 100) if site['players_online'] > 0 else 0
        print(f"{i:<3} {site['site_name'][:24]:<25} {site['players_online']:<12,} {site['cash_players']:<10,} {cash_pct:<7.1f}% {site['peak_24h']:<12,} {site['seven_day_avg']:<12,}")
    
    # Market share analysis
    print("\n" + "="*100)
    print("📊 MARKET SHARE ANALYSIS")
    print("="*100)
    
    for i, site in enumerate(sorted_data[:10], 1):
        if total_online > 0:
            share = (site['players_online'] / total_online) * 100
            bar_length = int(share * 2)  # Scale to 100 chars max
            bar = "█" * min(bar_length, 50)
            print(f"{i:2}. {site['site_name'][:20]:<20} │{bar:<50}│ {share:6.2f}% ({site['players_online']:,})")
    
    # Cash player focus
    cash_sorted = sorted(data, key=lambda x: x['cash_players'], reverse=True)
    print("\n" + "="*100)
    print("💰 TOP 10 PLATFORMS BY CASH PLAYERS")
    print("="*100)
    print(f"{'#':<3} {'Platform Name':<25} {'Cash Players':<15} {'Online Players':<15} {'Ratio':<8}")
    print("-"*80)
    
    for i, site in enumerate(cash_sorted[:10], 1):
        if site['cash_players'] > 0:
            ratio = (site['cash_players'] / site['players_online'] * 100) if site['players_online'] > 0 else 0
            print(f"{i:<3} {site['site_name'][:24]:<25} {site['cash_players']:<15,} {site['players_online']:<15,} {ratio:<7.1f}%")
    
    # Growth analysis (7-day comparison)
    print("\n" + "="*100)
    print("📈 GROWTH ANALYSIS (vs 7-Day Average)")
    print("="*100)
    
    growth_data = []
    for site in data:
        if site['seven_day_avg'] > 100 and site['players_online'] > 0:  # Only meaningful data
            growth_rate = ((site['players_online'] - site['seven_day_avg']) / site['seven_day_avg']) * 100
            growth_data.append({
                'name': site['site_name'],
                'current': site['players_online'],
                'avg': site['seven_day_avg'],
                'growth': growth_rate
            })
    
    # Sort by growth rate
    growth_sorted = sorted(growth_data, key=lambda x: abs(x['growth']), reverse=True)
    
    print("🚀 BIGGEST MOVERS (by absolute % change):")
    print(f"{'Platform':<25} {'Current':<12} {'7-Day Avg':<12} {'Change':<12} {'Status'}")
    print("-"*80)
    
    for item in growth_sorted[:10]:
        status = "🚀 SURGE" if item['growth'] > 50 else "📈 UP" if item['growth'] > 0 else "📉 DOWN" if item['growth'] > -50 else "⚠️ CRASH"
        print(f"{item['name'][:24]:<25} {item['current']:<12,} {item['avg']:<12,} {item['growth']:+10.1f}% {status}")
    
    # Market concentration
    top3_online = sum(site['players_online'] for site in sorted_data[:3])
    top5_online = sum(site['players_online'] for site in sorted_data[:5])
    top10_online = sum(site['players_online'] for site in sorted_data[:10])
    
    print("\n" + "="*100)
    print("🎯 MARKET CONCENTRATION ANALYSIS")
    print("="*100)
    print(f"🥇 TOP 3 Platforms Control: {top3_online:,} players ({(top3_online/total_online*100) if total_online > 0 else 0:.1f}% of market)")
    print(f"🏅 TOP 5 Platforms Control: {top5_online:,} players ({(top5_online/total_online*100) if total_online > 0 else 0:.1f}% of market)")
    print(f"🏆 TOP 10 Platforms Control: {top10_online:,} players ({(top10_online/total_online*100) if total_online > 0 else 0:.1f}% of market)")
    
    # Key insights
    print("\n" + "="*100)
    print("💡 KEY INSIGHTS & FINDINGS")
    print("="*100)
    
    # Market leader analysis
    leader = sorted_data[0] if sorted_data else None
    if leader:
        leader_share = (leader['players_online'] / total_online * 100) if total_online > 0 else 0
        print(f"👑 Market Leader: {leader['site_name']} with {leader['players_online']:,} players ({leader_share:.1f}% market share)")
    
    # Growth insights
    major_growth = [item for item in growth_data if item['growth'] > 100]
    major_decline = [item for item in growth_data if item['growth'] < -50]
    
    if major_growth:
        print(f"📊 {len(major_growth)} platforms experiencing major growth (>100%)")
        for item in major_growth[:3]:
            print(f"   • {item['name']}: +{item['growth']:.1f}%")
    
    if major_decline:
        print(f"⚠️  {len(major_decline)} platforms experiencing major decline (<-50%)")
        for item in major_decline[:3]:
            print(f"   • {item['name']}: {item['growth']:.1f}%")
    
    # Cash player insights
    high_cash_ratio = [(s['site_name'], (s['cash_players']/s['players_online']*100)) 
                      for s in data if s['players_online'] > 100 and s['cash_players']/s['players_online'] > 0.3]
    
    if high_cash_ratio:
        high_cash_ratio.sort(key=lambda x: x[1], reverse=True)
        print(f"💰 Platforms with High Cash Player Ratios (>30%):")
        for name, ratio in high_cash_ratio[:5]:
            print(f"   • {name}: {ratio:.1f}% cash conversion")
    
    print("\n" + "="*100)
    print("🔍 PLEASE REVIEW THE ABOVE DATA")
    print("="*100)
    print("👆 Check if:")
    print("   1. Platform names look correct (not numbers)")
    print("   2. Player counts seem realistic")
    print("   3. Growth rates make sense")
    print("   4. Market shares add up correctly")
    print("   5. Any suspicious patterns in the data")
    print()
    print("🐛 If you spot issues, please let me know what's wrong!")
    print("="*100)
    
    return data, growth_data

if __name__ == "__main__":
    show_current_analysis()