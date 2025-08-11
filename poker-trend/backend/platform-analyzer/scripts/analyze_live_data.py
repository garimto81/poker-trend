#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live PokerScout data analysis
"""

import os
import sys
import io
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

# UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import crawler from poker-online-analyze project
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../poker-online-analyze/backend'))

try:
    import cloudscraper
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] Required packages not installed")
    print("Please run: pip install cloudscraper beautifulsoup4")
    sys.exit(1)

class LivePokerDataAnalyzer:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'linux', 'mobile': False}
        )
        
    def crawl_pokerscout_data(self):
        """Crawl live data from PokerScout"""
        logger.info("Starting PokerScout live crawling...")
        try:
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            response.raise_for_status()
            logger.info(f"Response status code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'rankTable'})
            if not table:
                logger.error("Could not find PokerScout table")
                return []
            
            logger.info("Found rankTable!")
            collected_data = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for i, row in enumerate(rows):
                try:
                    # Skip special rows
                    if 'cus_top_traffic_coin' in row.get('class', []):
                        continue
                    
                    # Find site name from brand-title span
                    brand_title = row.find('span', {'class': 'brand-title'})
                    if not brand_title:
                        continue
                    
                    site_name = brand_title.get_text(strip=True)
                    if not site_name or len(site_name) < 2:
                        continue
                    
                    # Initialize values
                    players_online, cash_players, peak_24h, seven_day_avg = 0, 0, 0, 0
                    
                    # Find online players
                    online_td = row.find('td', {'id': 'online'})
                    if online_td:
                        span = online_td.find('span')
                        if span:
                            text = span.get_text(strip=True).replace(',', '')
                            if text.isdigit():
                                raw_online = int(text)
                                # Data validation: Check for unrealistic values
                                players_online = self._validate_online_players(raw_online, site_name)
                    
                    # Find cash players
                    cash_td = row.find('td', {'id': 'cash'})
                    if cash_td:
                        text = cash_td.get_text(strip=True).replace(',', '')
                        if text.isdigit():
                            cash_players = int(text)
                    
                    # Find peak
                    peak_td = row.find('td', {'id': 'peak'})
                    if peak_td:
                        span = peak_td.find('span')
                        if span:
                            text = span.get_text(strip=True).replace(',', '')
                            if text.isdigit():
                                peak_24h = int(text)
                    
                    # Find 7-day average
                    avg_td = row.find('td', {'id': 'avg'})
                    if avg_td:
                        span = avg_td.find('span')
                        if span:
                            text = span.get_text(strip=True).replace(',', '')
                            if text.isdigit():
                                seven_day_avg = int(text)
                    
                    # Skip if all values are zero
                    if players_online == 0 and cash_players == 0 and peak_24h == 0:
                        continue
                    
                    collected_data.append({
                        'site_name': site_name,
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'peak_24h': peak_24h,
                        'seven_day_avg': seven_day_avg,
                        'collected_at': datetime.now(timezone.utc).isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing row {i+1}: {e}")
                    continue
            
            logger.info(f"Crawling completed: {len(collected_data)} sites collected")
            return collected_data
            
        except Exception as e:
            logger.error(f"Crawling failed: {e}")
            return []
    
    def _validate_online_players(self, raw_value: int, site_name: str) -> int:
        """Validate online player count for realistic values"""
        # Define platform-specific maximum realistic values
        platform_limits = {
            'PokerStars': 60000,      # PokerStars variants can exceed 55k
            'GGNetwork': 200000,      # GGNetwork can be very high
            'IDNPoker': 50000,        # IDN network is large
            'WPT': 10000,            # WPT Global maximum
            'iPoker': 5000,          # iPoker network
        }
        
        # Find applicable limit
        max_realistic = 1000000  # Default very high limit
        
        for platform, limit in platform_limits.items():
            if platform.lower() in site_name.lower():
                max_realistic = limit
                break
        
        # If value exceeds realistic limit, log warning and cap it
        if raw_value > max_realistic:
            logger.warning(f"SUSPICIOUS DATA: {site_name} shows {raw_value:,} players (limit: {max_realistic:,})")
            # Return a conservative estimate (half the limit)
            return max_realistic // 2
        
        return raw_value
    
    def analyze_data(self, data: List[Dict]):
        """Analyze crawled data"""
        if not data:
            print("[ERROR] No data to analyze")
            return
        
        # Sort by players online
        sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)
        
        # Calculate totals
        total_players = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        active_sites = len([s for s in data if s['players_online'] > 0])
        
        print("\n" + "="*80)
        print("LIVE POKER PLATFORM ANALYSIS - REAL DATA")
        print("="*80)
        print(f"Data collected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Source: PokerScout.com")
        print("="*80)
        
        print(f"\n[MARKET OVERVIEW]")
        print(f"Total Online Players: {total_players:,}")
        print(f"Total Cash Players: {total_cash:,}")
        print(f"Active Platforms: {active_sites} / {len(data)}")
        print(f"Average per Platform: {total_players // active_sites:,}" if active_sites > 0 else "N/A")
        
        # Top 10 platforms
        print("\n" + "="*80)
        print("TOP 10 POKER PLATFORMS BY ACTIVE PLAYERS")
        print("="*80)
        print(f"{'Rank':<5} {'Platform':<25} {'Online':<12} {'Cash':<12} {'Peak 24h':<12} {'7-Day Avg':<12}")
        print("-"*80)
        
        for i, site in enumerate(sorted_data[:10], 1):
            print(f"{i:<5} {site['site_name'][:24]:<25} {site['players_online']:<12,} {site['cash_players']:<12,} {site['peak_24h']:<12,} {site['seven_day_avg']:<12,}")
        
        # Market share analysis
        print("\n" + "="*80)
        print("MARKET SHARE ANALYSIS")
        print("="*80)
        
        for i, site in enumerate(sorted_data[:5], 1):
            if total_players > 0:
                share = (site['players_online'] / total_players) * 100
                bar_length = int(share)  # 1 char per percentage
                bar = "#" * bar_length
                print(f"{i}. {site['site_name'][:20]:<20} {bar:<50} {share:6.2f}% ({site['players_online']:,})")
        
        # Market concentration
        print("\n" + "="*80)
        print("MARKET CONCENTRATION")
        print("="*80)
        
        top3_players = sum(site['players_online'] for site in sorted_data[:3])
        top5_players = sum(site['players_online'] for site in sorted_data[:5])
        top10_players = sum(site['players_online'] for site in sorted_data[:10])
        
        if total_players > 0:
            print(f"Top 3 platforms: {top3_players:,} players ({top3_players/total_players*100:.1f}% of market)")
            print(f"Top 5 platforms: {top5_players:,} players ({top5_players/total_players*100:.1f}% of market)")
            print(f"Top 10 platforms: {top10_players:,} players ({top10_players/total_players*100:.1f}% of market)")
        
        # Performance metrics
        print("\n" + "="*80)
        print("PERFORMANCE METRICS")
        print("="*80)
        
        for site in sorted_data[:5]:
            if site['peak_24h'] > 0:
                utilization = (site['players_online'] / site['peak_24h']) * 100
                trend = "📈" if site['players_online'] > site['seven_day_avg'] else "📉" if site['players_online'] < site['seven_day_avg'] else "➡️"
                
                print(f"\n{site['site_name']}:")
                print(f"  Current vs Peak: {utilization:.1f}% of 24h peak")
                print(f"  Current vs 7-day avg: {site['players_online']:,} vs {site['seven_day_avg']:,} {trend}")
                
                if site['seven_day_avg'] > 0:
                    avg_diff = ((site['players_online'] - site['seven_day_avg']) / site['seven_day_avg']) * 100
                    # Cap extreme growth rates for display
                    if abs(avg_diff) > 500:
                        print(f"  [SUSPICIOUS] Growth rate capped at ±500% (calculated: {avg_diff:+.1f}%)")
                        avg_diff = 500 if avg_diff > 0 else -500
                    
                    if abs(avg_diff) > 10:
                        status = "SURGE" if avg_diff > 0 else "DECLINE"
                        print(f"  [ALERT] {status}: {avg_diff:+.1f}% from 7-day average")
        
        # Notable findings
        print("\n" + "="*80)
        print("NOTABLE FINDINGS")
        print("="*80)
        
        # Find platforms with significant changes
        significant_changes = []
        for site in sorted_data:
            if site['seven_day_avg'] > 100:  # Only consider platforms with meaningful traffic
                if site['players_online'] > 0 and site['seven_day_avg'] > 0:
                    change = ((site['players_online'] - site['seven_day_avg']) / site['seven_day_avg']) * 100
                    # Cap extreme changes for reporting (but keep original calculation for debugging)
                    display_change = min(max(change, -500), 500) if abs(change) > 500 else change
                    if abs(display_change) > 20:
                        significant_changes.append((site['site_name'], display_change, change))
        
        if significant_changes:
            print("\nPlatforms with significant changes (>20% from 7-day average):")
            for name, display_change, original_change in sorted(significant_changes, key=lambda x: abs(x[1]), reverse=True)[:5]:
                indicator = "🚀" if display_change > 0 else "⚠️"
                if abs(original_change) > 500:
                    print(f"  {indicator} {name}: {display_change:+.1f}% (capped from {original_change:+.1f}%)")
                else:
                    print(f"  {indicator} {name}: {display_change:+.1f}%")
        else:
            print("\nNo platforms with significant changes detected (market stable)")
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"live_analysis_{timestamp}.json"
        
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_players': total_players,
                'total_cash': total_cash,
                'active_platforms': active_sites,
                'top_platform': sorted_data[0]['site_name'] if sorted_data else 'N/A',
                'top_platform_players': sorted_data[0]['players_online'] if sorted_data else 0
            },
            'top_10': sorted_data[:10],
            'market_share': {
                site['site_name']: (site['players_online'] / total_players * 100) if total_players > 0 else 0
                for site in sorted_data[:10]
            },
            'significant_changes': significant_changes[:5] if significant_changes else []
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Analysis saved to {output_file}")
        
        return analysis_result

def main():
    analyzer = LivePokerDataAnalyzer()
    
    print("="*80)
    print("FETCHING LIVE POKER PLATFORM DATA")
    print("="*80)
    
    # Crawl live data
    data = analyzer.crawl_pokerscout_data()
    
    if data:
        print(f"[OK] Successfully crawled {len(data)} platforms")
        
        # Analyze the data
        result = analyzer.analyze_data(data)
        
        # ASCII chart
        print("\n" + "="*80)
        print("MARKET SHARE VISUALIZATION (ASCII)")
        print("="*80)
        
        if data:
            total = sum(site['players_online'] for site in data)
            for site in sorted(data, key=lambda x: x['players_online'], reverse=True)[:10]:
                if total > 0:
                    share = site['players_online'] / total * 100
                    bar_len = int(share * 2)  # Scale to max 100 chars
                    bar = "#" * bar_len
                    print(f"{site['site_name'][:15]:<15} |{bar:<50} {share:5.1f}% ({site['players_online']:,})")
        
        print("\n" + "="*80)
        print("[SUCCESS] Live data analysis complete!")
        print("="*80)
    else:
        print("[ERROR] Failed to crawl data")

if __name__ == "__main__":
    main()