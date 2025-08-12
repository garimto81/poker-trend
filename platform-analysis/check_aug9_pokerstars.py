#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8월 9일 PokerStars.it 및 전체 데이터 확인
"""

import requests
from datetime import datetime

def check_aug9_data():
    """8월 9일 전체 데이터 확인"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("8월 9일 전체 데이터 확인")
    print("="*80)
    
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        aug9_data = []
        pokerstars_data = []
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            # 트래픽 로그 가져오기
            traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=100&orderBy=collected_at%20desc"
            
            try:
                traffic_response = requests.get(traffic_url, timeout=15)
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    traffic_docs = traffic_data.get('documents', [])
                    
                    for traffic_doc in traffic_docs:
                        traffic_fields = traffic_doc.get('fields', {})
                        collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                        
                        # 8월 9일 데이터만
                        if collected_at and '2025-08-09' in collected_at:
                            site_data = {
                                'platform': site_name,
                                'date': collected_at.split('T')[0],
                                'time': collected_at.split('T')[1][:8] if 'T' in collected_at else '',
                                'online': extract_value(traffic_fields.get('players_online', {}), 0),
                                'cash': extract_value(traffic_fields.get('cash_players', {}), 0),
                                'peak_24h': extract_value(traffic_fields.get('peak_24h', {}), 0),
                                'seven_day_avg': extract_value(traffic_fields.get('seven_day_avg', {}), 0)
                            }
                            aug9_data.append(site_data)
                            
                            # PokerStars 관련 사이트 특별 추적
                            if 'PokerStars' in site_name or 'pokerstars' in site_name.lower():
                                pokerstars_data.append(site_data)
                            
                            break  # 첫 번째 8월 9일 데이터만
                            
            except Exception as e:
                pass
        
        # PokerStars 사이트들 먼저 출력
        print("\n【8월 9일 PokerStars 관련 사이트】")
        print("-" * 80)
        
        if pokerstars_data:
            for site in pokerstars_data:
                print(f"사이트: {site['platform']}")
                print(f"  시간: {site['time']}")
                print(f"  온라인: {site['online']:,}명")
                print(f"  캐시: {site['cash']:,}명")
                print(f"  24h 피크: {site['peak_24h']:,}명")
                print()
        else:
            print("PokerStars 관련 사이트 데이터 없음")
        
        # 전체 데이터 요약
        print("\n【8월 9일 전체 데이터 요약】")
        print(f"총 {len(aug9_data)}개 사이트 데이터 수집")
        
        # 온라인 플레이어 기준 TOP 10
        online_sorted = sorted(aug9_data, key=lambda x: x['online'], reverse=True)
        
        print("\n【온라인 플레이어 TOP 10】")
        print(f"{'순위':<5} {'플랫폼':<25} {'온라인':<12} {'캐시':<10} {'시간':<10}")
        print("-" * 75)
        
        for i, site in enumerate(online_sorted[:10], 1):
            print(f"{i:<5} {site['platform']:<25} {site['online']:<12,} {site['cash']:<10,} {site['time']:<10}")
        
        # PokerStars.it 특별 확인
        print("\n【PokerStars.it 상세 확인】")
        pokerstars_it_found = False
        for site in aug9_data:
            if site['platform'] == 'PokerStars.it':
                pokerstars_it_found = True
                print(f"O PokerStars.it 발견!")
                print(f"  날짜: {site['date']}")
                print(f"  시간: {site['time']}")
                print(f"  온라인: {site['online']:,}명")
                print(f"  캐시: {site['cash']:,}명")
                break
        
        if not pokerstars_it_found:
            print("X PokerStars.it 데이터 없음")
            
            # 마지막으로 수집된 PokerStars.it 데이터 찾기
            print("\n【PokerStars.it 최근 데이터 확인】")
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                site_name = extract_value(fields.get('name', {}), doc_name)
                
                if site_name == 'PokerStars.it':
                    traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=10&orderBy=collected_at%20desc"
                    
                    try:
                        traffic_response = requests.get(traffic_url, timeout=15)
                        if traffic_response.status_code == 200:
                            traffic_data = traffic_response.json()
                            traffic_docs = traffic_data.get('documents', [])
                            
                            if traffic_docs:
                                print("최근 5개 데이터:")
                                for i, traffic_doc in enumerate(traffic_docs[:5]):
                                    traffic_fields = traffic_doc.get('fields', {})
                                    collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                                    online = extract_value(traffic_fields.get('players_online', {}), 0)
                                    
                                    date_str = collected_at.split('T')[0] if collected_at else 'N/A'
                                    print(f"  {i+1}. {date_str}: {online:,}명")
                            break
                    except:
                        pass
        
        # 총계
        total_online = sum(s['online'] for s in aug9_data)
        total_cash = sum(s['cash'] for s in aug9_data)
        
        print(f"\n【8월 9일 전체 통계】")
        print(f"- 총 사이트 수: {len(aug9_data)}개")
        print(f"- 총 온라인: {total_online:,}명")
        print(f"- 총 캐시: {total_cash:,}명")
        
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
    check_aug9_data()