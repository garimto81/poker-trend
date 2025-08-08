#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase Data Fetcher
Firebase에서 포커 사이트 데이터를 가져와서 로컬 데이터베이스와 통합
"""

import os
import sys
import json
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseDataFetcher:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.firebase_project_id = "poker-online-analyze"
        self.firestore_base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        
    def fetch_latest_data(self) -> List[Dict]:
        """Firebase에서 최신 데이터 가져오기"""
        logger.info("Firebase에서 최신 데이터 수집 중...")
        
        sites_url = f"{self.firestore_base_url}/sites"
        
        try:
            response = requests.get(sites_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Firebase 접근 실패: {response.status_code}")
                return []
            
            data = response.json()
            documents = data.get('documents', [])
            
            logger.info(f"{len(documents)}개 사이트 발견")
            
            poker_data = []
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                site_name = doc.get('fields', {}).get('name', {}).get('stringValue', doc_name)
                
                # 각 사이트의 최신 traffic_log 가져오기
                traffic_data = self._fetch_site_traffic_logs(doc_name, limit=1)
                
                if traffic_data:
                    latest = traffic_data[0]
                    poker_data.append({
                        'site_name': site_name,
                        'players_online': latest['players_online'],
                        'cash_players': latest['cash_players'],
                        'peak_24h': latest.get('peak_24h', 0),
                        'seven_day_avg': latest.get('seven_day_avg', 0),
                        'collected_at': latest['collected_at'],
                        'data_quality': 'firebase'
                    })
            
            # 플레이어 수 기준으로 정렬
            poker_data.sort(key=lambda x: x['players_online'], reverse=True)
            
            logger.info(f"{len(poker_data)}개 사이트 데이터 수집 완료")
            return poker_data
            
        except Exception as e:
            logger.error(f"Firebase 데이터 수집 실패: {e}")
            return []
    
    def _fetch_site_traffic_logs(self, site_doc_id: str, limit: int = 5) -> List[Dict]:
        """특정 사이트의 트래픽 로그 가져오기"""
        traffic_url = f"{self.firestore_base_url}/sites/{site_doc_id}/traffic_logs"
        
        try:
            # 최신 데이터부터 정렬하여 가져오기
            params = {
                'pageSize': limit,
                'orderBy': 'collected_at desc'
            }
            
            response = requests.get(traffic_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                traffic_logs = []
                for doc in documents:
                    fields = doc.get('fields', {})
                    
                    log_data = {
                        'collected_at': fields.get('collected_at', {}).get('timestampValue', ''),
                        'players_online': int(fields.get('players_online', {}).get('integerValue', 0)),
                        'cash_players': int(fields.get('cash_players', {}).get('integerValue', 0)),
                        'peak_24h': int(fields.get('peak_24h', {}).get('integerValue', 0)),
                        'seven_day_avg': int(fields.get('seven_day_avg', {}).get('integerValue', 0)),
                    }
                    
                    traffic_logs.append(log_data)
                
                return traffic_logs
                
            elif response.status_code == 404:
                # 사이트에 트래픽 로그가 없음
                return []
            else:
                logger.warning(f"{site_doc_id} 트래픽 로그 접근 실패: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"{site_doc_id} 트래픽 로그 수집 오류: {e}")
            return []
    
    def sync_to_database(self, firebase_data: List[Dict], target_date: str = None) -> int:
        """Firebase 데이터를 로컬 데이터베이스에 동기화"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"Firebase 데이터를 데이터베이스에 동기화: {target_date}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        for site in firebase_data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_data 
                    (date, timestamp, site_name, players_online, cash_players, 
                     peak_24h, seven_day_avg, data_quality, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target_date,
                    timestamp,
                    site['site_name'],
                    site['players_online'],
                    site['cash_players'],
                    site['peak_24h'],
                    site['seven_day_avg'],
                    'firebase',
                    datetime.now().isoformat()
                ))
                stored_count += 1
                
            except Exception as e:
                logger.error(f"{site['site_name']} 저장 실패: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Firebase 데이터 동기화 완료: {stored_count}개 사이트")
        return stored_count
    
    def get_historical_firebase_data(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """Firebase에서 과거 데이터 가져오기"""
        logger.info(f"Firebase 히스토리 데이터 수집: 최근 {days_back}일")
        
        # 주요 사이트들만 히스토리 수집 (성능상 이유)
        major_sites = ['GGNetwork', 'IDNPoker', 'WPT-Global', 'PokerStars-US', 'PokerStars-Ontario']
        
        historical_data = {}
        
        for site_id in major_sites:
            traffic_logs = self._fetch_site_traffic_logs(site_id, limit=days_back * 2)
            
            if traffic_logs:
                historical_data[site_id] = traffic_logs
                logger.info(f"{site_id}: {len(traffic_logs)}개 로그 수집")
        
        return historical_data

def main():
    print("Firebase Data Fetcher")
    print("=" * 60)
    
    fetcher = FirebaseDataFetcher()
    
    try:
        # 1. Firebase에서 최신 데이터 가져오기
        firebase_data = fetcher.fetch_latest_data()
        
        if not firebase_data:
            print("[ERROR] Firebase 데이터 수집 실패")
            return
        
        # 2. TOP 10 출력
        print("\n[Firebase TOP 10 - 온라인 플레이어]")
        print("-" * 60)
        for i, site in enumerate(firebase_data[:10], 1):
            print(f"{i:2d}. {site['site_name']:<20} 온라인:{site['players_online']:>7,}  캐시:{site['cash_players']:>6,}")
        
        # 3. 캐시 플레이어 TOP 5
        cash_sorted = sorted(firebase_data, key=lambda x: x['cash_players'], reverse=True)
        print("\n[Firebase TOP 5 - 캐시 플레이어]")
        print("-" * 60)
        for i, site in enumerate(cash_sorted[:5], 1):
            if site['cash_players'] > 0:
                print(f"{i:2d}. {site['site_name']:<20} 캐시:{site['cash_players']:>6,}  온라인:{site['players_online']:>7,}")
        
        # 4. 데이터베이스 동기화
        today = datetime.now().strftime('%Y-%m-%d')
        stored = fetcher.sync_to_database(firebase_data, today)
        print(f"\n[데이터베이스 동기화 완료] {stored}개 사이트")
        
        # 5. 히스토리 데이터 샘플
        print("\n[주요 사이트 최근 데이터]")
        historical = fetcher.get_historical_firebase_data(3)
        
        for site_id, logs in historical.items():
            if logs:
                latest = logs[0]
                print(f"  {site_id}: {latest['players_online']:,}명 (캐시: {latest['cash_players']:,}명)")
        
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
        print(f"[ERROR] 오류: {e}")

if __name__ == "__main__":
    main()