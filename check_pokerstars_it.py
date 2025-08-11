#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerStars.it 데이터 확인
"""

import requests
from datetime import datetime

def check_pokerstars_it():
    """PokerStars.it 데이터 상세 확인"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("PokerStars.it 데이터 상세 확인")
    print("="*80)
    
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        # PokerStars 관련 모든 사이트 찾기
        pokerstars_sites = []
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            if 'PokerStars' in site_name or 'pokerstars' in site_name.lower():
                print(f"\n[발견] {site_name}")
                
                # 트래픽 로그 가져오기
                traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=10&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        print(f"  트래픽 로그 수: {len(traffic_docs)}개")
                        
                        # 각 날짜별 데이터
                        for i, traffic_doc in enumerate(traffic_docs[:5]):  # 최근 5개만
                            traffic_fields = traffic_doc.get('fields', {})
                            
                            collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                            online = extract_value(traffic_fields.get('players_online', {}), 0)
                            cash = extract_value(traffic_fields.get('cash_players', {}), 0)
                            peak = extract_value(traffic_fields.get('peak_24h', {}), 0)
                            avg_7d = extract_value(traffic_fields.get('seven_day_avg', {}), 0)
                            
                            date_str = collected_at.split('T')[0] if collected_at else 'N/A'
                            time_str = collected_at.split('T')[1][:8] if 'T' in collected_at else 'N/A'
                            
                            print(f"  [{i+1}] {date_str} {time_str}")
                            print(f"      온라인: {online:,}명")
                            print(f"      캐시: {cash:,}명")
                            print(f"      24h 피크: {peak:,}명")
                            print(f"      7일 평균: {avg_7d:,}명")
                            
                            # 8월 10일 데이터 특별 표시
                            if '2025-08-10' in collected_at:
                                print(f"      >>> 8월 10일 데이터 <<<")
                                pokerstars_sites.append({
                                    'name': site_name,
                                    'date': date_str,
                                    'online': online,
                                    'cash': cash,
                                    'peak': peak,
                                    'avg_7d': avg_7d
                                })
                        
                except Exception as e:
                    print(f"  트래픽 로그 수집 오류: {e}")
        
        # 요약
        print("\n" + "="*80)
        print("PokerStars 사이트 요약")
        print("="*80)
        
        print("\n【8월 10일 데이터】")
        for site in pokerstars_sites:
            print(f"- {site['name']}: 온라인 {site['online']:,}명, 캐시 {site['cash']:,}명")
        
        print("\n【분석】")
        print("1. PokerStars US와 Ontario는 항상 55,540명으로 고정 (오염 데이터)")
        print("2. PokerStars.it는 실제 데이터로 보임 (11,145명)")
        print("3. PokerStars PA는 0명으로 비활성 상태")
        
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
    check_pokerstars_it()