#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch real-time poker platform data from Firebase
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Firebase REST API endpoint
FIREBASE_PROJECT_ID = "poker-online-analyze"
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

def fetch_firebase_data():
    """Fetch real data from Firebase REST API"""
    print("=" * 70)
    print("FETCHING REAL-TIME POKER PLATFORM DATA")
    print("=" * 70)
    
    try:
        # Fetch sites data
        sites_url = f"{FIRESTORE_BASE_URL}/sites"
        print(f"\n[INFO] Connecting to Firebase: {FIREBASE_PROJECT_ID}")
        
        response = requests.get(sites_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'documents' in data:
                documents = data['documents']
                print(f"[OK] Found {len(documents)} poker platforms")
                
                platform_data = {}
                total_players = 0
                
                for doc in documents:
                    # Extract document name (site name)
                    doc_name = doc['name'].split('/')[-1]
                    
                    # Extract fields
                    fields = doc.get('fields', {})
                    
                    # Parse data from Firestore fields format
                    site_data = {
                        'name': doc_name,
                        'category': fields.get('category', {}).get('stringValue', 'Unknown'),
                        'players_online': int(fields.get('players_online', {}).get('integerValue', 0)),
                        'cash_players': int(fields.get('cash_players', {}).get('integerValue', 0)),
                        'peak_24h': int(fields.get('peak_24h', {}).get('integerValue', 0)),
                        'seven_day_avg': int(fields.get('seven_day_avg', {}).get('integerValue', 0)),
                        'last_updated': fields.get('last_updated', {}).get('timestampValue', '')
                    }
                    
                    if site_data['players_online'] > 0:
                        platform_data[doc_name] = site_data
                        total_players += site_data['players_online']
                
                # Sort by players online
                sorted_platforms = sorted(
                    platform_data.items(), 
                    key=lambda x: x[1]['players_online'], 
                    reverse=True
                )
                
                print(f"\n[STATS] Total Active Players: {total_players:,}")
                print(f"[STATS] Active Platforms: {len(platform_data)}")
                
                print("\n" + "=" * 70)
                print("TOP 10 POKER PLATFORMS BY ACTIVE PLAYERS")
                print("=" * 70)
                
                print(f"{'Rank':<5} {'Platform':<20} {'Online':<10} {'Cash':<10} {'Peak 24h':<10} {'7-Day Avg':<10}")
                print("-" * 70)
                
                for i, (name, data) in enumerate(sorted_platforms[:10], 1):
                    print(f"{i:<5} {name[:19]:<20} {data['players_online']:<10,} {data['cash_players']:<10,} {data['peak_24h']:<10,} {data['seven_day_avg']:<10,}")
                
                # Calculate market share
                print("\n" + "=" * 70)
                print("MARKET SHARE ANALYSIS")
                print("=" * 70)
                
                for i, (name, data) in enumerate(sorted_platforms[:5], 1):
                    share = (data['players_online'] / total_players) * 100
                    bar_length = int(share / 2)  # Scale to 50 chars max
                    bar = "#" * bar_length
                    print(f"{i}. {name[:15]:<15} {bar:<50} {share:5.1f}%")
                
                # Fetch traffic logs for top platform
                if sorted_platforms:
                    top_platform = sorted_platforms[0][0]
                    print(f"\n[INFO] Fetching historical data for {top_platform}...")
                    
                    traffic_url = f"{FIRESTORE_BASE_URL}/sites/{top_platform}/traffic_logs"
                    traffic_response = requests.get(traffic_url)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        if 'documents' in traffic_data:
                            print(f"[OK] Found {len(traffic_data['documents'])} traffic logs")
                            
                            # Show recent trend
                            print("\n" + "=" * 70)
                            print(f"RECENT TREND FOR {top_platform}")
                            print("=" * 70)
                            
                            logs = traffic_data['documents'][:7]  # Last 7 entries
                            for log in logs:
                                fields = log.get('fields', {})
                                timestamp = fields.get('collected_at', {}).get('timestampValue', '')
                                players = int(fields.get('players_online', {}).get('integerValue', 0))
                                
                                if timestamp:
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    print(f"{dt.strftime('%Y-%m-%d %H:%M')} - {players:,} players")
                
                return platform_data
                
            else:
                print("[WARN] No documents found in response")
                return None
                
        elif response.status_code == 403:
            print("[ERROR] Access denied. Firebase security rules may be blocking public access.")
            print("[INFO] Trying alternative approach...")
            
            # Try fetching from the public website
            return fetch_from_github_pages()
            
        else:
            print(f"[ERROR] Failed to fetch data. Status code: {response.status_code}")
            print(f"[ERROR] Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch Firebase data: {e}")
        return None

def fetch_from_github_pages():
    """Fetch data from GitHub Pages as alternative"""
    try:
        print("\n[INFO] Fetching from GitHub Pages...")
        
        # The GitHub Pages site that displays Firebase data
        gh_pages_url = "https://garimto81.github.io/poker-online-analyze/"
        
        response = requests.get(gh_pages_url)
        if response.status_code == 200:
            print("[OK] GitHub Pages accessible")
            print("[INFO] Note: GitHub Pages shows Firebase data through frontend")
            print("[INFO] For real-time data, Firebase access is required")
            
            # Parse HTML to find data
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for data in script tags or data attributes
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'firebase' in script.string.lower():
                    print("[INFO] Found Firebase configuration in page")
                    break
            
            return None
        else:
            print(f"[ERROR] GitHub Pages returned status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch from GitHub Pages: {e}")
        return None

def generate_analysis(platform_data: Dict):
    """Generate analysis from real data"""
    if not platform_data:
        print("\n[WARN] No data available for analysis")
        return
    
    print("\n" + "=" * 70)
    print("PLATFORM ANALYSIS")
    print("=" * 70)
    
    # Find significant changes (would need historical data for real comparison)
    total_players = sum(p['players_online'] for p in platform_data.values())
    
    print(f"\n[SUMMARY]")
    print(f"- Total platforms tracked: {len(platform_data)}")
    print(f"- Total active players: {total_players:,}")
    print(f"- Average players per platform: {total_players // len(platform_data):,}")
    
    # Identify market leaders
    sorted_platforms = sorted(
        platform_data.items(), 
        key=lambda x: x[1]['players_online'], 
        reverse=True
    )
    
    top_3 = sorted_platforms[:3]
    top_3_share = sum(p[1]['players_online'] for p in top_3) / total_players * 100
    
    print(f"\n[MARKET CONCENTRATION]")
    print(f"- Top 3 platforms control {top_3_share:.1f}% of market")
    
    for name, data in top_3:
        share = (data['players_online'] / total_players) * 100
        print(f"  • {name}: {share:.1f}% ({data['players_online']:,} players)")
    
    # Peak analysis
    print(f"\n[PEAK PERFORMANCE]")
    for name, data in sorted_platforms[:5]:
        if data['peak_24h'] > 0:
            utilization = (data['players_online'] / data['peak_24h']) * 100
            print(f"- {name}: Currently at {utilization:.1f}% of 24h peak")

if __name__ == "__main__":
    print("POKER PLATFORM REAL-TIME DATA FETCHER")
    print("Source: poker-online-analyze Firebase Project")
    print("=" * 70)
    
    # Fetch real data
    data = fetch_firebase_data()
    
    if data:
        # Generate analysis
        generate_analysis(data)
        
        # Save to file
        output_file = f"real_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Data saved to {output_file}")
    else:
        print("\n[INFO] Unable to fetch real-time data")
        print("[INFO] Firebase security rules may require authentication")
        print("[INFO] Using demo data for visualization...")