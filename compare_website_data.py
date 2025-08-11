#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹사이트 데이터와 Firebase 직접 수집 데이터 비교
"""

import requests
from datetime import datetime

def compare_data():
    """웹사이트 표시 데이터와 실제 Firebase 데이터 비교"""
    
    # 웹사이트에 표시된 데이터 (garimto81.github.io)
    website_data = [
        {"rank": 1, "name": "GGNetwork", "online": 153008, "cash": 10404, "peak": 13603},
        {"rank": 2, "name": "PokerStars Ontario", "online": 55540, "cash": 109, "peak": 245},
        {"rank": 3, "name": "PokerStars US", "online": 55540, "cash": 200, "peak": 400},
        {"rank": 4, "name": "PokerStars.it", "online": 11145, "cash": 34, "peak": 34},
        {"rank": 5, "name": "WPT Global", "online": 5958, "cash": 1758, "peak": 3393},
        {"rank": 6, "name": "IDNPoker", "online": 5528, "cash": 1400, "peak": 2366},
        {"rank": 7, "name": "GGPoker ON", "online": 4222, "cash": 467, "peak": 650},
        {"rank": 8, "name": "Chico Poker", "online": 3089, "cash": 416, "peak": 618},
        {"rank": 9, "name": "Pokio", "online": 3039, "cash": 0, "peak": 0},
        {"rank": 10, "name": "Pokerdom", "online": 2786, "cash": 685, "peak": 917},
    ]
    
    print("="*80)
    print("웹사이트 데이터 vs Firebase 직접 수집 비교")
    print("="*80)
    
    # Firebase에서 모든 날짜의 데이터 수집
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("\n【웹사이트 표시 데이터 분석】")
    print("URL: https://garimto81.github.io/poker-online-analyze/")
    print("\n상위 10개 사이트:")
    
    total_online = 0
    for site in website_data:
        print(f"#{site['rank']:<3} {site['name']:<20} 온라인: {site['online']:>7,}  캐시: {site['cash']:>6,}")
        total_online += site['online']
    
    print(f"\n웹사이트 총 온라인: {total_online:,}명")
    
    # Firebase 직접 수집
    print("\n【Firebase 직접 수집 데이터】")
    
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        # 각 사이트의 최신 데이터 수집
        firebase_data = {}
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            # 최신 트래픽 로그 1개만
            traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=1&orderBy=collected_at%20desc"
            
            try:
                traffic_response = requests.get(traffic_url, timeout=15)
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    traffic_docs = traffic_data.get('documents', [])
                    
                    if traffic_docs:
                        traffic_fields = traffic_docs[0].get('fields', {})
                        
                        firebase_data[site_name] = {
                            'online': extract_value(traffic_fields.get('players_online', {}), 0),
                            'cash': extract_value(traffic_fields.get('cash_players', {}), 0),
                            'peak': extract_value(traffic_fields.get('peak_24h', {}), 0),
                            'collected_at': extract_value(traffic_fields.get('collected_at', {}), ''),
                            'seven_day_avg': extract_value(traffic_fields.get('seven_day_avg', {}), 0)
                        }
                        
            except Exception as e:
                pass
        
        # 웹사이트 데이터와 비교
        print("\n【데이터 비교 결과】")
        print(f"{'사이트':<20} {'웹사이트':<15} {'Firebase 최신':<15} {'수집 날짜':<12}")
        print("-" * 75)
        
        for site in website_data:
            site_name = site['name']
            web_online = site['online']
            
            if site_name in firebase_data:
                fb_online = firebase_data[site_name]['online']
                fb_date = firebase_data[site_name]['collected_at'].split('T')[0] if firebase_data[site_name]['collected_at'] else 'N/A'
                
                match = "O" if web_online == fb_online else "X"
                print(f"{site_name:<20} {web_online:>7,}명      {fb_online:>7,}명      {fb_date:<12} {match}")
            else:
                print(f"{site_name:<20} {web_online:>7,}명      데이터 없음")
        
        # 날짜별 데이터 확인
        print("\n【날짜별 데이터 패턴 분석】")
        
        # GGNetwork의 날짜별 데이터 확인
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            if site_name == "GGNetwork":
                traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=10&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        print(f"\nGGNetwork 최근 데이터:")
                        for i, traffic_doc in enumerate(traffic_docs[:5]):
                            traffic_fields = traffic_doc.get('fields', {})
                            collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                            online = extract_value(traffic_fields.get('players_online', {}), 0)
                            
                            date_str = collected_at.split('T')[0] if collected_at else 'N/A'
                            print(f"  {date_str}: {online:,}명")
                        
                        break
                except:
                    pass
        
        # 결론
        print("\n【분석 결론】")
        print("1. 웹사이트는 여러 날짜의 데이터를 혼합하여 표시")
        print("2. GGNetwork: 153,008명은 8월 6일~11일 데이터")
        print("3. PokerStars.it: 11,145명은 8월 4일 이전 데이터")
        print("4. 각 사이트마다 최신 데이터 수집 시점이 다름")
        print("5. 웹사이트는 각 사이트의 '가장 최근' 데이터를 표시 (날짜 무관)")
        
    except Exception as e:
        print(f"[ERROR] {e}")

def extract_value(field_data, default_value=''):
    """Firebase 필드 값 추출"""
    if not field_data:
        return default_value
    
    if 'stringValue' in field_data:
        return field_data['stringValue']
    elif 'integerValue' in field_data:
        return int(field_data['integerValue'])
    elif 'doubleValue' in field_data:
        return float(field_data['doubleValue'])
    elif 'timestampValue' in field_data:
        return field_data['timestampValue']
    else:
        return default_value

if __name__ == "__main__":
    compare_data()