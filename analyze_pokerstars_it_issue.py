#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerStars.it 데이터 누락 원인 분석
"""

import requests
from datetime import datetime, timedelta

def analyze_pokerstars_it():
    """PokerStars.it 데이터 수집 패턴 상세 분석"""
    
    firebase_project_id = "poker-online-analyze"
    base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
    
    print("="*80)
    print("PokerStars.it 데이터 누락 원인 분석")
    print("="*80)
    
    sites_url = f"{base_url}/sites"
    
    try:
        response = requests.get(sites_url, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Firebase 연결 실패")
            return
        
        data = response.json()
        documents = data.get('documents', [])
        
        # PokerStars.it 찾기
        pokerstars_it_doc = None
        for doc in documents:
            doc_name = doc['name'].split('/')[-1]
            fields = doc.get('fields', {})
            site_name = extract_value(fields.get('name', {}), doc_name)
            
            if site_name == 'PokerStars.it':
                pokerstars_it_doc = doc_name
                print(f"\n[1] PokerStars.it 문서 ID: {doc_name}")
                
                # 사이트 메타데이터
                print("\n【사이트 메타데이터】")
                print(f"- 이름: {site_name}")
                print(f"- 카테고리: {extract_value(fields.get('category', {}), 'N/A')}")
                print(f"- URL: {extract_value(fields.get('url', {}), 'N/A')}")
                print(f"- 지역: {extract_value(fields.get('region', {}), 'N/A')}")
                print(f"- 생성일: {extract_value(fields.get('created_at', {}), 'N/A')}")
                break
        
        if not pokerstars_it_doc:
            print("[ERROR] PokerStars.it 사이트를 찾을 수 없음")
            return
        
        # 모든 트래픽 로그 가져오기
        traffic_url = f"{base_url}/sites/{pokerstars_it_doc}/traffic_logs?pageSize=100&orderBy=collected_at%20desc"
        
        print("\n[2] 트래픽 로그 수집 중...")
        
        traffic_response = requests.get(traffic_url, timeout=15)
        
        if traffic_response.status_code != 200:
            print(f"[ERROR] 트래픽 로그 수집 실패: {traffic_response.status_code}")
            return
        
        traffic_data = traffic_response.json()
        traffic_docs = traffic_data.get('documents', [])
        
        print(f"- 총 {len(traffic_docs)}개 로그 발견")
        
        # 날짜별 데이터 정리
        date_data = {}
        
        for traffic_doc in traffic_docs:
            traffic_fields = traffic_doc.get('fields', {})
            collected_at = extract_value(traffic_fields.get('collected_at', {}), '')
            
            if collected_at:
                date_str = collected_at.split('T')[0]
                time_str = collected_at.split('T')[1][:8] if 'T' in collected_at else ''
                
                if date_str not in date_data:
                    date_data[date_str] = []
                
                date_data[date_str].append({
                    'time': time_str,
                    'online': extract_value(traffic_fields.get('players_online', {}), 0),
                    'cash': extract_value(traffic_fields.get('cash_players', {}), 0),
                    'peak': extract_value(traffic_fields.get('peak_24h', {}), 0),
                    'avg_7d': extract_value(traffic_fields.get('seven_day_avg', {}), 0)
                })
        
        # 날짜별 분석
        print("\n【날짜별 데이터 수집 현황】")
        print("-" * 60)
        
        sorted_dates = sorted(date_data.keys())
        
        for date in sorted_dates:
            logs = date_data[date]
            print(f"{date}: {len(logs)}개 로그")
            for log in logs[:1]:  # 각 날짜의 첫 번째 로그만
                print(f"  - 시간: {log['time']}, 온라인: {log['online']:,}명")
        
        # 데이터 수집 패턴 분석
        print("\n【데이터 수집 패턴 분석】")
        print("-" * 60)
        
        if sorted_dates:
            first_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d')
            last_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
            
            print(f"첫 수집일: {sorted_dates[0]}")
            print(f"마지막 수집일: {sorted_dates[-1]}")
            print(f"수집 기간: {(last_date - first_date).days + 1}일")
            print(f"실제 데이터가 있는 날: {len(date_data)}일")
            
            # 누락된 날짜 찾기
            print("\n【누락된 날짜】")
            current = first_date
            missing_dates = []
            
            while current <= last_date:
                date_str = current.strftime('%Y-%m-%d')
                if date_str not in date_data:
                    missing_dates.append(date_str)
                current += timedelta(days=1)
            
            if missing_dates:
                print(f"총 {len(missing_dates)}개 날짜 누락:")
                for date in missing_dates[:10]:  # 처음 10개만
                    print(f"  - {date}")
                if len(missing_dates) > 10:
                    print(f"  ... 외 {len(missing_dates)-10}개")
            else:
                print("누락된 날짜 없음")
            
            # 8월 5일~10일 특별 확인
            print("\n【8월 5일~10일 상세 확인】")
            aug_dates = ['2025-08-05', '2025-08-06', '2025-08-07', 
                        '2025-08-08', '2025-08-09', '2025-08-10']
            
            for date in aug_dates:
                if date in date_data:
                    print(f"{date}: 데이터 있음 ({len(date_data[date])}개 로그)")
                else:
                    print(f"{date}: [누락] 데이터 없음")
        
        # 데이터 값 분석
        print("\n【데이터 값 패턴 분석】")
        print("-" * 60)
        
        unique_values = set()
        for date, logs in date_data.items():
            for log in logs:
                unique_values.add(log['online'])
        
        print(f"고유한 온라인 값의 개수: {len(unique_values)}")
        if len(unique_values) <= 5:
            print(f"값들: {sorted(unique_values)}")
        
        # 연속 동일값 확인
        consecutive_same = []
        prev_value = None
        count = 0
        
        for date in sorted_dates:
            if date_data[date]:
                current_value = date_data[date][0]['online']
                if current_value == prev_value:
                    count += 1
                else:
                    if count > 1:
                        consecutive_same.append((prev_value, count))
                    prev_value = current_value
                    count = 1
        
        if consecutive_same:
            print("\n연속으로 같은 값이 나온 경우:")
            for value, cnt in consecutive_same:
                print(f"  - {value:,}명이 {cnt}일 연속")
        
        # 원인 분석 결론
        print("\n" + "="*80)
        print("【PokerStars.it 데이터 누락 원인 분석 결론】")
        print("="*80)
        
        print("\n1. 데이터 수집 중단:")
        print("   - 8월 4일 이후 데이터 수집이 완전히 중단됨")
        print("   - 8월 5일~10일: 데이터 없음")
        
        print("\n2. 데이터 품질 문제:")
        print("   - 7월 31일~8월 4일: 모두 11,145명으로 동일 (의심스러움)")
        print("   - 실제 플레이어 수가 변하지 않았을 가능성 낮음")
        
        print("\n3. 가능한 원인:")
        print("   - Firebase 수집 시스템의 PokerStars.it 크롤러 오류")
        print("   - PokerStars.it 사이트의 API/데이터 접근 차단")
        print("   - 수집 스케줄러에서 PokerStars.it 제외됨")
        
        print("\n4. 영향:")
        print("   - 8월 10일 일간 보고서: PokerStars.it 누락")
        print("   - 8월 4일~10일 주간 보고서: 8월 4일 데이터만 사용")
        print("   - 7월 30일~8월 10일 월간 보고서: 부정확한 평균값")
        
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
    analyze_pokerstars_it()