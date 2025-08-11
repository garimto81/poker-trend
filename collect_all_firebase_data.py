#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 전체 데이터 수집 및 분석
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

def fetch_all_firebase_data():
    """Firebase에서 모든 포커 사이트 데이터 수집"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("FIREBASE 전체 데이터 수집")
    print("="*80)
    print(f"프로젝트: {firebase_project_id}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. 모든 사이트 목록 가져오기
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] 사이트 목록 수집 실패: {response.status_code}")
            return []
        
        data = response.json()
        documents = data.get('documents', [])
        
        print(f"\n[SUCCESS] 수집된 사이트: {len(documents)}개\n")
        
        all_sites = []
        
        # 2. 각 사이트 정보 파싱
        for doc in documents:
            try:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                
                # 기본 정보 추출
                site_info = {
                    'id': doc_name,
                    'name': extract_value(fields.get('name', {}), doc_name),
                    'category': extract_value(fields.get('category', {}), 'UNKNOWN'),
                    'url': extract_value(fields.get('url', {}), ''),
                    'network': extract_value(fields.get('network', {}), ''),
                    'region': extract_value(fields.get('region', {}), 'Global'),
                    'created_at': extract_value(fields.get('created_at', {}), ''),
                    'players_online': 0,
                    'cash_players': 0,
                    'peak_24h': 0,
                    'seven_day_avg': 0,
                    'traffic_logs': []
                }
                
                # 3. 각 사이트의 트래픽 로그 가져오기
                traffic_url = f"{base_url}/sites/{doc_name}/traffic_logs?pageSize=5&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        for traffic_doc in traffic_docs:
                            traffic_fields = traffic_doc.get('fields', {})
                            
                            log_data = {
                                'collected_at': extract_value(traffic_fields.get('collected_at', {}), ''),
                                'players_online': extract_value(traffic_fields.get('players_online', {}), 0),
                                'cash_players': extract_value(traffic_fields.get('cash_players', {}), 0),
                                'peak_24h': extract_value(traffic_fields.get('peak_24h', {}), 0),
                                'seven_day_avg': extract_value(traffic_fields.get('seven_day_avg', {}), 0),
                            }
                            
                            site_info['traffic_logs'].append(log_data)
                            
                            # 최신 데이터를 사이트 정보에 반영
                            if len(site_info['traffic_logs']) == 1:
                                site_info['players_online'] = log_data['players_online']
                                site_info['cash_players'] = log_data['cash_players']
                                site_info['peak_24h'] = log_data['peak_24h']
                                site_info['seven_day_avg'] = log_data['seven_day_avg']
                                
                except Exception as e:
                    # 트래픽 로그가 없어도 사이트 정보는 저장
                    pass
                
                all_sites.append(site_info)
                
            except Exception as e:
                print(f"[WARNING] 사이트 데이터 파싱 오류 ({doc_name}): {e}")
                continue
        
        return all_sites
        
    except Exception as e:
        print(f"[ERROR] Firebase 연결 오류: {e}")
        return []

def extract_value(field_data: Dict, default_value=''):
    """Firebase 필드에서 값 추출"""
    if not field_data:
        return default_value
    
    # 각 필드 타입별 처리
    if 'stringValue' in field_data:
        return field_data['stringValue']
    elif 'integerValue' in field_data:
        return int(field_data['integerValue'])
    elif 'doubleValue' in field_data:
        return float(field_data['doubleValue'])
    elif 'timestampValue' in field_data:
        return field_data['timestampValue']
    elif 'booleanValue' in field_data:
        return field_data['booleanValue']
    else:
        return default_value

def analyze_and_display(sites: List[Dict]):
    """수집된 데이터 분석 및 표시"""
    
    # 수집 기간 분석
    all_timestamps = []
    for site in sites:
        for log in site.get('traffic_logs', []):
            timestamp = log.get('collected_at', '')
            if timestamp:
                all_timestamps.append(timestamp)
    
    if all_timestamps:
        all_timestamps.sort()
        earliest = all_timestamps[0]
        latest = all_timestamps[-1]
        
        # 날짜별 집계
        date_counts = {}
        for ts in all_timestamps:
            date_only = ts.split('T')[0] if 'T' in ts else ts
            date_counts[date_only] = date_counts.get(date_only, 0) + 1
        
        print("\n" + "="*80)
        print("[데이터 수집 기간 분석]")
        print("="*80)
        print(f"최초 수집: {earliest}")
        print(f"최종 수집: {latest}")
        print(f"총 로그 수: {len(all_timestamps)}개")
        print(f"\n날짜별 수집 현황:")
        for date, count in sorted(date_counts.items()):
            print(f"  {date}: {count}개 로그")
    
    # 카테고리별 분류
    categories = {}
    for site in sites:
        category = site['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(site)
    
    # 네트워크별 분류
    networks = {}
    for site in sites:
        network = site.get('network', 'Independent')
        if not network:
            network = 'Independent'
        if network not in networks:
            networks[network] = []
        networks[network].append(site)
    
    # 지역별 분류
    regions = {}
    for site in sites:
        region = site.get('region', 'Global')
        if region not in regions:
            regions[region] = []
        regions[region].append(site)
    
    # 전체 통계
    print("\n" + "="*80)
    print("[전체 통계]")
    print("="*80)
    
    total_online = sum(site['players_online'] for site in sites)
    total_cash = sum(site['cash_players'] for site in sites)
    active_sites = [s for s in sites if s['players_online'] > 0]
    
    print(f"총 사이트 수: {len(sites)}개")
    print(f"활성 사이트: {len(active_sites)}개")
    print(f"총 온라인 플레이어: {total_online:,}명")
    print(f"총 캐시 플레이어: {total_cash:,}명")
    
    # 카테고리별 통계
    print("\n" + "="*80)
    print("[카테고리별 분류]")
    print("="*80)
    
    for category, cat_sites in sorted(categories.items()):
        online = sum(s['players_online'] for s in cat_sites)
        print(f"\n{category}: {len(cat_sites)}개 사이트 | {online:,}명")
        for site in sorted(cat_sites, key=lambda x: x['players_online'], reverse=True)[:5]:
            if site['players_online'] > 0:
                print(f"  - {site['name']:<25} {site['players_online']:>7,}명")
    
    # 네트워크별 통계
    print("\n" + "="*80)
    print("[네트워크별 분류]")
    print("="*80)
    
    for network, net_sites in sorted(networks.items(), key=lambda x: sum(s['players_online'] for s in x[1]), reverse=True):
        online = sum(s['players_online'] for s in net_sites)
        if online > 0:
            print(f"\n{network}: {len(net_sites)}개 사이트 | {online:,}명")
            for site in sorted(net_sites, key=lambda x: x['players_online'], reverse=True)[:3]:
                if site['players_online'] > 0:
                    print(f"  - {site['name']:<25} {site['players_online']:>7,}명")
    
    # 지역별 통계
    print("\n" + "="*80)
    print("[지역별 분류]")
    print("="*80)
    
    for region, reg_sites in sorted(regions.items()):
        online = sum(s['players_online'] for s in reg_sites)
        if online > 0:
            print(f"\n{region}: {len(reg_sites)}개 사이트 | {online:,}명")
    
    # TOP 20 사이트 (온라인 플레이어 기준)
    print("\n" + "="*80)
    print("[TOP 20 사이트 - 온라인 플레이어 기준]")
    print("="*80)
    
    sorted_sites = sorted(sites, key=lambda x: x['players_online'], reverse=True)
    
    print(f"\n{'순위':<4} {'사이트명':<25} {'온라인':<10} {'캐시':<10} {'피크':<10} {'7일평균':<10} {'카테고리':<15}")
    print("-" * 100)
    
    for i, site in enumerate(sorted_sites[:20], 1):
        print(f"{i:>3}. {site['name']:<25} {site['players_online']:>9,} {site['cash_players']:>9,} {site['peak_24h']:>9,} {site['seven_day_avg']:>9,} {site['category']:<15}")
    
    # 데이터 품질 분석
    print("\n" + "="*80)
    print("[데이터 품질 분석]")
    print("="*80)
    
    # 중복 값 확인
    value_patterns = {}
    for site in sites:
        if site['players_online'] > 0:
            key = f"{site['players_online']}_{site['cash_players']}"
            if key not in value_patterns:
                value_patterns[key] = []
            value_patterns[key].append(site['name'])
    
    duplicates_found = False
    for pattern, site_names in value_patterns.items():
        if len(site_names) > 1:
            duplicates_found = True
            online, cash = pattern.split('_')
            print(f"\n동일한 값 발견 (온라인: {online}, 캐시: {cash}):")
            for name in site_names:
                print(f"  - {name}")
    
    if not duplicates_found:
        print("중복 값 없음")
    
    # 연속 동일 값 확인
    print("\n연속 동일 값 확인:")
    for site in sites[:5]:  # 상위 5개 사이트만
        if len(site['traffic_logs']) > 1:
            values = [log['players_online'] for log in site['traffic_logs']]
            if len(set(values)) == 1:
                print(f"  {site['name']}: 모든 로그가 {values[0]:,}명으로 동일")
            elif len(set(values)) < len(values):
                print(f"  {site['name']}: 일부 중복 값 존재")
    
    # 모든 사이트 목록 (알파벳 순)
    print("\n" + "="*80)
    print("[전체 사이트 목록 - 알파벳 순]")
    print("="*80)
    
    sorted_by_name = sorted(sites, key=lambda x: x['name'])
    
    for i, site in enumerate(sorted_by_name, 1):
        status = "[ON]" if site['players_online'] > 0 else "[OFF]"
        logs_info = f"로그: {len(site['traffic_logs'])}개" if site['traffic_logs'] else "로그 없음"
        print(f"{i:>3}. {status} {site['name']:<30} | 온라인: {site['players_online']:>7,} | {logs_info}")
    
    # JSON 파일로 저장
    filename = f"firebase_all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'collected_at': datetime.now().isoformat(),
            'total_sites': len(sites),
            'active_sites': len(active_sites),
            'total_online': total_online,
            'total_cash': total_cash,
            'sites': sites
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVED] 데이터 저장: {filename}")
    
    return sites

def main():
    """메인 실행 함수"""
    
    # Firebase 데이터 수집
    sites = fetch_all_firebase_data()
    
    if sites:
        # 분석 및 표시
        analyze_and_display(sites)
    else:
        print("[ERROR] 데이터 수집 실패")
    
    return sites

if __name__ == "__main__":
    main()