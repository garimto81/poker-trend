#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase Data Importer
poker-online-analyze 프로젝트의 Firebase 데이터를 가져와서 
로컬 SQLite 히스토리 데이터베이스에 통합
"""

import os
import sys
import json
import sqlite3
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_data_collector import DailyDataCollector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseDataImporter:
    def __init__(self, firebase_project_id: str = "poker-online-analyze", db_path: str = "poker_history.db"):
        self.firebase_project_id = firebase_project_id
        self.db_path = db_path
        self.collector = DailyDataCollector(db_path)
        
        # Firebase REST API 엔드포인트
        self.firebase_base_url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents"
        
    def fetch_firebase_sites(self) -> List[str]:
        """Firebase에서 사이트 목록 가져오기"""
        logger.info("🔥 Firebase에서 사이트 목록 조회")
        
        try:
            sites_url = f"{self.firebase_base_url}/sites"
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                sites = []
                
                if 'documents' in data:
                    for doc in data['documents']:
                        # 문서 이름에서 사이트명 추출 (sites/{site_name} 형식)
                        site_name = doc['name'].split('/')[-1]
                        sites.append(site_name)
                
                logger.info(f"✅ Firebase 사이트 목록: {len(sites)}개")
                return sorted(sites)
                
            else:
                logger.error(f"❌ Firebase API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Firebase 연결 실패: {e}")
            return []
    
    def fetch_site_traffic_logs(self, site_name: str, days_back: int = 30) -> List[Dict]:
        """특정 사이트의 트래픽 로그 가져오기"""
        logger.info(f"📊 {site_name} 트래픽 로그 조회 (최근 {days_back}일)")
        
        try:
            # Firebase의 traffic_logs 컬렉션 접근
            logs_url = f"{self.firebase_base_url}/sites/{site_name}/traffic_logs"
            response = requests.get(logs_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                traffic_logs = []
                
                if 'documents' in data:
                    for doc in data['documents']:
                        # 문서 데이터 파싱
                        fields = doc.get('fields', {})
                        
                        # ISO timestamp에서 날짜 추출
                        timestamp_str = doc['name'].split('/')[-1]
                        
                        try:
                            # 다양한 타임스탬프 형식 처리
                            timestamp = None
                            
                            # Firebase 문서 이름에서 타임스탬프 추출 시도
                            if 'T' in timestamp_str and len(timestamp_str) > 10:
                                # ISO 형식 시도
                                clean_timestamp = timestamp_str.replace('Z', '+00:00')
                                # 공백 제거 (잘못된 형식 수정)
                                clean_timestamp = clean_timestamp.replace(' 00:00', '+00:00')
                                # +00:00 중복 제거
                                if '+00:00+00:00' in clean_timestamp:
                                    clean_timestamp = clean_timestamp.replace('+00:00+00:00', '+00:00')
                                
                                try:
                                    timestamp = datetime.fromisoformat(clean_timestamp)
                                except:
                                    # 마지막 +00:00만 유지
                                    if '+00:00' in clean_timestamp:
                                        parts = clean_timestamp.split('+00:00')
                                        clean_timestamp = parts[0] + '+00:00'
                                        timestamp = datetime.fromisoformat(clean_timestamp)
                            
                            if not timestamp:
                                # 타임스탬프 파싱 실패 시 건너뛰기
                                logger.debug(f"🔍 타임스탬프 형식 인식 불가: {timestamp_str}")
                                continue
                            
                            date_str = timestamp.strftime('%Y-%m-%d')
                            
                            # 데이터 필드 추출
                            log_data = {
                                'site_name': site_name,
                                'date': date_str,
                                'timestamp': timestamp.isoformat(),
                                'players_online': self._extract_firebase_value(fields.get('players_online', {})),
                                'cash_players': self._extract_firebase_value(fields.get('cash_players', {})),
                                'peak_24h': self._extract_firebase_value(fields.get('peak_24h', {})),
                                'seven_day_avg': self._extract_firebase_value(fields.get('seven_day_avg', {})),
                                'market_share_online': self._extract_firebase_value(fields.get('market_share_online', {}), 0.0),
                                'market_share_cash': self._extract_firebase_value(fields.get('market_share_cash', {}), 0.0)
                            }
                            
                            # 최근 N일 필터링 (타임존 인식 대응)
                            now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
                            if (now - timestamp).days <= days_back:
                                traffic_logs.append(log_data)
                            
                        except Exception as parse_error:
                            logger.debug(f"🔍 타임스탬프 파싱 실패: {timestamp_str} - {parse_error}")
                            continue
                
                logger.info(f"✅ {site_name}: {len(traffic_logs)}개 로그 수집")
                return sorted(traffic_logs, key=lambda x: x['timestamp'])
                
            else:
                logger.warning(f"⚠️ {site_name} 트래픽 로그 없음: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ {site_name} 트래픽 로그 조회 실패: {e}")
            return []
    
    def _extract_firebase_value(self, field_data: Dict, default_value: Any = 0) -> Any:
        """Firebase 필드 데이터에서 값 추출"""
        if not field_data:
            return default_value
        
        # Firebase Firestore 데이터 타입별 처리
        if 'integerValue' in field_data:
            return int(field_data['integerValue'])
        elif 'doubleValue' in field_data:
            return float(field_data['doubleValue'])
        elif 'stringValue' in field_data:
            return field_data['stringValue']
        elif 'booleanValue' in field_data:
            return field_data['booleanValue']
        else:
            return default_value
    
    def import_firebase_data(self, days_back: int = 30) -> Dict[str, int]:
        """Firebase 데이터를 로컬 데이터베이스로 가져오기"""
        logger.info(f"🚀 Firebase 데이터 가져오기 시작 (최근 {days_back}일)")
        
        # 사이트 목록 가져오기
        sites = self.fetch_firebase_sites()
        if not sites:
            logger.error("❌ Firebase 사이트 목록을 가져올 수 없습니다")
            return {'imported': 0, 'skipped': 0, 'errors': 0}
        
        import_stats = {'imported': 0, 'skipped': 0, 'errors': 0}
        
        # 각 사이트별 데이터 가져오기
        for i, site_name in enumerate(sites, 1):
            logger.info(f"📊 진행률: {i}/{len(sites)} - {site_name}")
            
            try:
                # 트래픽 로그 가져오기
                traffic_logs = self.fetch_site_traffic_logs(site_name, days_back)
                
                if not traffic_logs:
                    import_stats['skipped'] += 1
                    continue
                
                # 날짜별로 그룹화 (같은 날 여러 로그가 있을 경우 최신 것 사용)
                daily_data = {}
                for log in traffic_logs:
                    date = log['date']
                    if date not in daily_data or log['timestamp'] > daily_data[date]['timestamp']:
                        daily_data[date] = log
                
                # SQLite에 저장
                imported_count = self._save_firebase_data_to_sqlite(list(daily_data.values()))
                import_stats['imported'] += imported_count
                
                # API 레이트 리밋 방지를 위한 딜레이
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ {site_name} 가져오기 실패: {e}")
                import_stats['errors'] += 1
        
        logger.info(f"✅ Firebase 데이터 가져오기 완료")
        logger.info(f"📊 통계: 가져옴 {import_stats['imported']}개, 건너뜀 {import_stats['skipped']}개, 오류 {import_stats['errors']}개")
        
        return import_stats
    
    def _save_firebase_data_to_sqlite(self, firebase_logs: List[Dict]) -> int:
        """Firebase 로그를 SQLite에 저장"""
        if not firebase_logs:
            return 0
        
        imported_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for log in firebase_logs:
                try:
                    # 중복 확인
                    cursor.execute("""
                        SELECT COUNT(*) FROM daily_data 
                        WHERE date = ? AND site_name = ?
                    """, (log['date'], log['site_name']))
                    
                    exists = cursor.fetchone()[0] > 0
                    
                    if not exists:
                        # 새로운 데이터 삽입
                        cursor.execute("""
                            INSERT INTO daily_data 
                            (date, timestamp, site_name, players_online, cash_players, 
                             peak_24h, seven_day_avg, data_quality, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            log['date'],
                            log['timestamp'],
                            log['site_name'],
                            log['players_online'],
                            log['cash_players'],
                            log['peak_24h'],
                            log['seven_day_avg'],
                            'firebase_import',  # Firebase에서 가져온 데이터임을 표시
                            datetime.now().isoformat()
                        ))
                        imported_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ SQLite 저장 실패 - {log['site_name']} {log['date']}: {e}")
            
            conn.commit()
        
        return imported_count
    
    def show_import_preview(self, sample_sites: int = 5) -> Dict:
        """가져올 데이터의 미리보기 표시"""
        logger.info(f"👀 Firebase 데이터 미리보기 ({sample_sites}개 사이트)")
        
        sites = self.fetch_firebase_sites()[:sample_sites]
        preview_data = {}
        
        for site_name in sites:
            traffic_logs = self.fetch_site_traffic_logs(site_name, days_back=7)
            if traffic_logs:
                preview_data[site_name] = {
                    'total_logs': len(traffic_logs),
                    'date_range': f"{traffic_logs[0]['date']} ~ {traffic_logs[-1]['date']}" if traffic_logs else "없음",
                    'latest_players': traffic_logs[-1]['players_online'] if traffic_logs else 0,
                    'sample_log': traffic_logs[-1] if traffic_logs else {}
                }
        
        return preview_data
    
    def show_comparison_with_current(self):
        """현재 시스템과 Firebase 데이터 비교"""
        logger.info("🔍 현재 시스템 vs Firebase 데이터 비교")
        
        # 현재 로컬 DB 통계
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM daily_data")
            local_total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT site_name) FROM daily_data")
            local_sites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT date) FROM daily_data")
            local_dates = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(date), MAX(date) FROM daily_data")
            local_range = cursor.fetchone()
        
        # Firebase 통계
        firebase_sites = self.fetch_firebase_sites()
        
        print("=" * 80)
        print("📊 시스템 데이터 비교")
        print("=" * 80)
        print(f"🏠 로컬 SQLite DB:")
        print(f"   총 레코드: {local_total:,}개")
        print(f"   추적 사이트: {local_sites}개")
        print(f"   수집 일수: {local_dates}일")
        print(f"   수집 기간: {local_range[0]} ~ {local_range[1]}")
        
        print(f"\n🔥 Firebase DB:")
        print(f"   추적 사이트: {len(firebase_sites)}개")
        print(f"   주요 사이트: {', '.join(firebase_sites[:10])}")
        
        print(f"\n💡 Firebase 통합 시 예상 효과:")
        print(f"   사이트 확장: {local_sites}개 → {len(firebase_sites)}개")
        print(f"   데이터 풍부성: 기존 히스토리 + Firebase 장기 데이터")
        print(f"   신뢰도 향상: PokerScout 의존성 → 자체/Firebase 조합")
        
        return {
            'local': {'total': local_total, 'sites': local_sites, 'dates': local_dates, 'range': local_range},
            'firebase': {'sites': len(firebase_sites), 'site_list': firebase_sites}
        }

def main():
    print("=" * 80)
    print("🔥 Firebase 데이터 가져오기 시스템")
    print("=" * 80)
    
    importer = FirebaseDataImporter()
    
    print("\n작업을 선택하세요:")
    print("1. Firebase 데이터 미리보기")
    print("2. 현재 시스템과 Firebase 비교")
    print("3. Firebase 데이터 가져오기 (최근 30일)")
    print("4. Firebase 데이터 가져오기 (최근 7일)")
    print("5. 전체 시스템 통합 테스트")
    
    try:
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == '1':
            print("\n👀 Firebase 데이터 미리보기...")
            preview = importer.show_import_preview(sample_sites=5)
            
            print("\n📋 미리보기 결과:")
            for site_name, info in preview.items():
                print(f"\n🎯 {site_name}:")
                print(f"   총 로그: {info['total_logs']}개")
                print(f"   기간: {info['date_range']}")
                print(f"   최신 플레이어: {info['latest_players']:,}명")
                
        elif choice == '2':
            comparison = importer.show_comparison_with_current()
            
        elif choice == '3':
            print("\n🚀 Firebase 데이터 가져오기 (최근 30일)...")
            confirm = input("계속 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                stats = importer.import_firebase_data(days_back=30)
                print(f"\n✅ 완료: {stats}")
                
        elif choice == '4':
            print("\n🚀 Firebase 데이터 가져오기 (최근 7일)...")
            confirm = input("계속 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                stats = importer.import_firebase_data(days_back=7)
                print(f"\n✅ 완료: {stats}")
                
        elif choice == '5':
            print("\n🧪 전체 시스템 통합 테스트...")
            
            # 1. 비교 분석
            comparison = importer.show_comparison_with_current()
            
            # 2. 미리보기
            preview = importer.show_import_preview(3)
            
            # 3. 소량 가져오기 테스트
            print("\n🔬 소량 테스트 가져오기...")
            stats = importer.import_firebase_data(days_back=3)
            print(f"테스트 결과: {stats}")
            
        else:
            print("잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()