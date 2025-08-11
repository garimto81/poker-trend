#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 분석 로직 디버깅 - 왜 PokerStars.it를 못 찾았는지 확인
"""

import requests
from datetime import datetime

def debug_firebase_analysis():
    """Firebase 분석 로직의 문제점 찾기"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("Firebase 분석 로직 디버깅")
    print("="*80)
    
    # 1. 전체 사이트 목록 확인
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        print(f"\n[1] 전체 사이트 수: {len(documents)}개")
        
        # 2. PokerStars 관련 모든 사이트 찾기
        pokerstars_sites = []
        
        print(f"\n[2] PokerStars 관련 사이트 검색:")
        print("-" * 60)
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            if 'pokerstars' in site_name.lower() or 'PokerStars' in site_name:
                pokerstars_sites.append({
                    'doc_id': doc_name,
                    'name': site_name
                })
                print(f"발견: {site_name} (ID: {doc_name})")
        
        # 3. 각 PokerStars 사이트의 최신 데이터 확인
        print(f"\n[3] 각 사이트의 최신 데이터 확인:")
        print("-" * 60)
        
        for site in pokerstars_sites:
            print(f"\n>>> {site['name']} <<<")
            
            # 최신 데이터 1개만 가져오기
            traffic_url = f"{base_url}/sites/{site['doc_id']}/traffic_logs?pageSize=1&orderBy=collected_at%20desc"
            
            try:
                traffic_response = requests.get(traffic_url, timeout=15)
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    traffic_docs = traffic_data.get('documents', [])
                    
                    if traffic_docs:
                        traffic_fields = traffic_docs[0].get('fields', {})
                        
                        collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                        online = extract_value(traffic_fields.get('players_online', {}), 0)
                        cash = extract_value(traffic_fields.get('cash_players', {}), 0)
                        
                        date_str = collected_at.split('T')[0] if collected_at else 'N/A'
                        time_str = collected_at.split('T')[1][:8] if 'T' in collected_at else 'N/A'
                        
                        print(f"  최신 데이터: {date_str} {time_str}")
                        print(f"  온라인: {online:,}명")
                        print(f"  캐시: {cash:,}명")
                        
                        # 웹사이트 데이터와 비교
                        if site['name'] == 'PokerStars.it' and online == 11145:
                            print(f"  -> 웹사이트와 일치! (11,145명)")
                        elif site['name'] in ['PokerStars Ontario', 'PokerStars US'] and online == 55540:
                            print(f"  -> 웹사이트와 일치! (55,540명)")
                    else:
                        print(f"  트래픽 데이터 없음")
                else:
                    print(f"  트래픽 로그 접근 실패: {traffic_response.status_code}")
                    
            except Exception as e:
                print(f"  오류: {e}")
        
        # 4. 8월 10일 데이터 수집 로직 재현
        print(f"\n[4] 8월 10일 데이터 수집 로직 재현:")
        print("-" * 60)
        
        excluded_sites = ['PokerStars US', 'PokerStars Ontario']
        aug10_data = []
        
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            # 제외 사이트 체크
            if site_name in excluded_sites:
                continue
            
            # 8월 10일 데이터 찾기
            traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=20&orderBy=collected_at%20desc"
            
            try:
                traffic_response = requests.get(traffic_url, timeout=10)
                
                if traffic_response.status_code == 200:
                    traffic_data = traffic_response.json()
                    traffic_docs = traffic_data.get('documents', [])
                    
                    # 8월 10일 데이터 찾기
                    found_aug10 = False
                    for traffic_doc in traffic_docs:
                        traffic_fields = traffic_doc.get('fields', {})
                        collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                        
                        if '2025-08-10' in collected_at:
                            online = extract_value(traffic_fields.get('players_online', {}), 0)
                            cash = extract_value(traffic_fields.get('cash_players', {}), 0)
                            
                            aug10_data.append({
                                'name': site_name,
                                'online': online,
                                'cash': cash,
                                'time': collected_at.split('T')[1][:8] if 'T' in collected_at else ''
                            })
                            found_aug10 = True
                            break
                    
                    # PokerStars.it 특별 확인
                    if site_name == 'PokerStars.it':
                        if found_aug10:
                            print(f"O PokerStars.it 8월 10일 데이터 발견!")
                        else:
                            print(f"X PokerStars.it 8월 10일 데이터 없음")
                            print(f"   최신 데이터들:")
                            for i, traffic_doc in enumerate(traffic_docs[:3]):
                                traffic_fields = traffic_doc.get('fields', {})
                                collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
                                date_str = collected_at.split('T')[0] if collected_at else 'N/A'
                                print(f"   {i+1}. {date_str}")
                            
            except Exception as e:
                pass
        
        # 5. 결과 분석
        print(f"\n[5] 8월 10일 데이터 수집 결과:")
        print("-" * 60)
        
        # 온라인 플레이어 기준 정렬
        aug10_data.sort(key=lambda x: x['online'], reverse=True)
        
        print(f"총 {len(aug10_data)}개 사이트 데이터 수집")
        
        print(f"\nTOP 10:")
        for i, site in enumerate(aug10_data[:10], 1):
            print(f"{i:2}. {site['name']:<25} {site['online']:>8,}명")
        
        # PokerStars.it가 있는지 확인
        pokerstars_it_in_aug10 = [s for s in aug10_data if s['name'] == 'PokerStars.it']
        
        print(f"\n[결론]")
        if pokerstars_it_in_aug10:
            site = pokerstars_it_in_aug10[0]
            print(f"O PokerStars.it는 8월 10일 데이터가 있습니다!")
            print(f"  온라인: {site['online']:,}명")
            print(f"  캐시: {site['cash']:,}명")
            print(f"  시간: {site['time']}")
            print(f"  -> 제 분석기에서 놓쳤습니다.")
        else:
            print(f"X PokerStars.it는 8월 10일 데이터가 없습니다.")
            print(f"  -> 웹사이트는 다른 날짜 데이터를 표시 중")
        
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
    debug_firebase_analysis()