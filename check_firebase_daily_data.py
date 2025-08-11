#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 일간 데이터 전체 확인
"""

import requests
from datetime import datetime

def check_daily_data():
    """8월 10일 Firebase 실제 데이터 확인"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("Firebase 8월 10일 전체 데이터 확인")
    print("="*80)
    
    # 제외 사이트
    excluded = ['PokerStars Ontario', 'PokerStars US']
    
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        all_data = []
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            if site_name in excluded:
                continue
            
            # 8월 10일 트래픽 로그만 가져오기
            traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=100&orderBy=collected_at%20desc"
            
            try:
                traffic_response = requests.get(traffic_url, timeout=15)
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    traffic_docs = traffic_data.get('documents', [])
                    
                    for traffic_doc in traffic_docs:
                        traffic_fields = traffic_doc.get('fields', {})
                        collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                        
                        # 8월 10일 데이터만
                        if collected_at and '2025-08-10' in collected_at:
                            site_data = {
                                'platform': site_name,
                                'date': collected_at.split('T')[0],
                                'time': collected_at.split('T')[1] if 'T' in collected_at else '',
                                'online': extract_value(traffic_fields.get('players_online', {}), 0),
                                'cash': extract_value(traffic_fields.get('cash_players', {}), 0),
                                'peak_24h': extract_value(traffic_fields.get('peak_24h', {}), 0),
                                'seven_day_avg': extract_value(traffic_fields.get('seven_day_avg', {}), 0)
                            }
                            all_data.append(site_data)
                            break  # 첫 번째 8월 10일 데이터만
                            
            except Exception as e:
                pass
        
        # 데이터 정렬 및 출력
        print(f"\n총 {len(all_data)}개 사이트 데이터 수집 (PokerStars US/Ontario 제외)\n")
        
        # 온라인 플레이어 기준 정렬
        online_sorted = sorted(all_data, key=lambda x: x['online'], reverse=True)
        
        print("【온라인 플레이어 TOP 10】")
        print(f"{'순위':<5} {'플랫폼':<25} {'온라인':<10} {'캐시':<10} {'피크':<10}")
        print("-" * 65)
        
        for i, site in enumerate(online_sorted[:10], 1):
            print(f"{i:<5} {site['platform']:<25} {site['online']:<10,} {site['cash']:<10,} {site['peak_24h']:<10,}")
        
        # 캐시 플레이어 기준 정렬
        cash_sorted = sorted(all_data, key=lambda x: x['cash'], reverse=True)
        
        print("\n【캐시 플레이어 TOP 10】")
        print(f"{'순위':<5} {'플랫폼':<25} {'캐시':<10} {'온라인':<10} {'비율':<10}")
        print("-" * 65)
        
        for i, site in enumerate(cash_sorted[:10], 1):
            ratio = f"{(site['cash']/site['online']*100):.1f}%" if site['online'] > 0 else "N/A"
            print(f"{i:<5} {site['platform']:<25} {site['cash']:<10,} {site['online']:<10,} {ratio:<10}")
        
        # 실제 활성 사이트 (온라인 > 0)
        active_sites = [s for s in all_data if s['online'] > 0]
        
        print(f"\n【활성 사이트 (온라인 > 0)】: {len(active_sites)}개")
        for site in active_sites:
            print(f"- {site['platform']}: 온라인 {site['online']:,}명, 캐시 {site['cash']:,}명")
        
        # 총계
        total_online = sum(s['online'] for s in all_data)
        total_cash = sum(s['cash'] for s in all_data)
        
        print(f"\n【전체 통계】")
        print(f"- 총 온라인: {total_online:,}명")
        print(f"- 총 캐시: {total_cash:,}명")
        print(f"- 캐시 비율: {(total_cash/total_online*100):.1f}%" if total_online > 0 else "N/A")
        
        # 데이터 이상 현상
        print(f"\n【데이터 이상 현상】")
        anomalies = [s for s in all_data if s['online'] == 0 and s['cash'] > 0]
        print(f"온라인=0, 캐시>0인 사이트: {len(anomalies)}개")
        for site in anomalies[:5]:
            print(f"- {site['platform']}: 온라인 0명, 캐시 {site['cash']:,}명")
        
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
    check_daily_data()