#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase REST API 전용 데이터 페처
Firebase SDK 없이 순수 REST API만 사용하여 인증 오류 방지
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

class FirebaseRESTFetcher:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.firebase_project_id = "poker-online-analyze"
        self.firestore_base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        
        # 인증 없이 공개 데이터만 접근
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def test_firebase_access(self) -> bool:
        """Firebase 접근 테스트"""
        try:
            test_url = f"{self.firestore_base_url}/sites"
            response = self.session.get(test_url, timeout=10)
            
            logger.info(f"Firebase 접근 테스트: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'documents' in data:
                    logger.info(f"Firebase 접근 성공: {len(data['documents'])}개 문서 확인")
                    return True
                else:
                    logger.warning("⚠️ 문서가 없거나 접근 권한 제한")
                    return False
                    
            elif response.status_code == 403:
                logger.error("❌ Firebase 접근 거부 (권한 없음)")
                return False
                
            elif response.status_code == 404:
                logger.error("❌ Firebase 프로젝트를 찾을 수 없음")
                return False
                
            else:
                logger.error(f"❌ Firebase 접근 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text[:500]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Firebase 연결 오류: {e}")
            return False
    
    def fetch_poker_sites(self) -> List[Dict]:
        """포커 사이트 목록 가져오기"""
        logger.info("포커 사이트 목록 수집 중...")
        
        sites_url = f"{self.firestore_base_url}/sites"
        
        try:
            response = self.session.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"사이트 목록 수집 실패: {response.status_code}")
                return []
            
            data = response.json()
            documents = data.get('documents', [])
            
            logger.info(f"수집된 사이트: {len(documents)}개")
            
            poker_sites = []
            
            for doc in documents:
                try:
                    doc_name = doc['name'].split('/')[-1]
                    fields = doc.get('fields', {})
                    
                    # 기본 사이트 정보
                    site_info = {
                        'id': doc_name,
                        'name': fields.get('name', {}).get('stringValue', doc_name),
                        'category': fields.get('category', {}).get('stringValue', 'unknown'),
                        'players_online': 0,
                        'cash_players': 0,
                        'peak_24h': 0,
                        'seven_day_avg': 0,
                        'last_updated': '',
                    }
                    
                    # traffic_logs에서 최신 데이터 가져오기
                    latest_traffic = self.get_site_traffic_logs(doc_name, limit=1)
                    if latest_traffic:
                        traffic = latest_traffic[0]
                        site_info.update({
                            'players_online': traffic['players_online'],
                            'cash_players': traffic['cash_players'],
                            'peak_24h': traffic['peak_24h'],
                            'seven_day_avg': traffic['seven_day_avg'],
                            'last_updated': traffic['collected_at'],
                        })
                    
                    # 디버깅: 첫 번째 사이트 정보 출력
                    if len(poker_sites) == 0:
                        logger.info(f"DEBUG 첫 번째 사이트: {site_info}")
                    
                    # 유효한 데이터만 추가
                    if site_info['players_online'] > 0 or site_info['cash_players'] > 0:
                        poker_sites.append(site_info)
                        
                except Exception as e:
                    logger.warning(f"사이트 데이터 파싱 오류 ({doc_name}): {e}")
                    continue
            
            # 온라인 플레이어 수 기준으로 정렬
            poker_sites.sort(key=lambda x: x['players_online'], reverse=True)
            
            logger.info(f"{len(poker_sites)}개 유효한 포커 사이트 수집 완료")
            return poker_sites
            
        except Exception as e:
            logger.error(f"사이트 목록 수집 중 오류: {e}")
            return []
    
    def get_site_traffic_logs(self, site_id: str, limit: int = 5) -> List[Dict]:
        """특정 사이트의 트래픽 로그 가져오기"""
        traffic_url = f"{self.firestore_base_url}/sites/{site_id}/traffic_logs"
        
        try:
            params = {
                'pageSize': limit,
                'orderBy': 'collected_at desc'
            }
            
            response = self.session.get(traffic_url, params=params, timeout=15)
            
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
                logger.info(f"{site_id}: 트래픽 로그 없음")
                return []
            else:
                logger.warning(f"{site_id}: 트래픽 로그 접근 실패 ({response.status_code})")
                return []
                
        except Exception as e:
            logger.warning(f"{site_id}: 트래픽 로그 수집 오류 - {e}")
            return []
    
    def sync_to_database(self, sites_data: List[Dict], target_date: str = None) -> int:
        """데이터를 로컬 데이터베이스에 동기화"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"데이터베이스 동기화: {target_date}")
        
        # 데이터베이스 테이블 확인/생성
        self._ensure_database_schema()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        for site in sites_data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_data 
                    (date, timestamp, site_name, players_online, cash_players, 
                     peak_24h, seven_day_avg, data_quality, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target_date,
                    timestamp,
                    site['name'],
                    site['players_online'],
                    site['cash_players'],
                    site['peak_24h'],
                    site['seven_day_avg'],
                    'firebase_rest',
                    datetime.now().isoformat()
                ))
                stored_count += 1
                
            except Exception as e:
                logger.error(f"{site['name']} 저장 실패: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"데이터베이스 동기화 완료: {stored_count}개 사이트")
        return stored_count
    
    def _ensure_database_schema(self):
        """데이터베이스 스키마 확인 및 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                site_name TEXT NOT NULL,
                players_online INTEGER DEFAULT 0,
                cash_players INTEGER DEFAULT 0,
                peak_24h INTEGER DEFAULT 0,
                seven_day_avg INTEGER DEFAULT 0,
                data_quality TEXT DEFAULT 'normal',
                created_at TEXT NOT NULL,
                UNIQUE(date, site_name)
            )
        """)
        
        conn.commit()
        conn.close()

def main():
    print("Firebase REST API 데이터 페처")
    print("=" * 50)
    
    fetcher = FirebaseRESTFetcher()
    
    # 1. Firebase 접근 테스트
    if not fetcher.test_firebase_access():
        print("[ERROR] Firebase 접근 실패 - 프로그램을 종료합니다")
        return 1
    
    # 2. 포커 사이트 데이터 수집
    sites_data = fetcher.fetch_poker_sites()
    
    if not sites_data:
        print("[ERROR] 포커 사이트 데이터 수집 실패")
        return 1
    
    # 3. 결과 출력
    print(f"\n[Firebase 포커 사이트 데이터 TOP 10]")
    print("-" * 50)
    for i, site in enumerate(sites_data[:10], 1):
        print(f"{i:2d}. {site['name']:<20} 온라인:{site['players_online']:>7,}  캐시:{site['cash_players']:>6,}")
    
    # 4. 데이터베이스 동기화
    today = datetime.now().strftime('%Y-%m-%d')
    stored = fetcher.sync_to_database(sites_data, today)
    
    print(f"\n[SUCCESS] 처리 완료: {len(sites_data)}개 수집, {stored}개 저장")
    return 0

if __name__ == "__main__":
    sys.exit(main())