#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Poker Platform Data Collector
매일 데이터를 수집하여 자체 히스토리 데이터베이스 구축
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyDataCollector:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.analyzer = LivePokerDataAnalyzer()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing daily data"""
        logger.info(f"데이터베이스 초기화: {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create daily_data table
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
            
            # Create collection_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    platforms_collected INTEGER DEFAULT 0,
                    platforms_validated INTEGER DEFAULT 0,
                    platforms_flagged INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create analysis_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    total_online INTEGER DEFAULT 0,
                    total_cash INTEGER DEFAULT 0,
                    active_platforms INTEGER DEFAULT 0,
                    market_leader TEXT,
                    significant_changes INTEGER DEFAULT 0,
                    alert_level TEXT DEFAULT 'none',
                    summary_text TEXT,
                    data_json TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("✅ 데이터베이스 테이블 초기화 완료")
    
    def collect_daily_data(self, target_date: str = None) -> Dict:
        """Collect and store daily data"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"🔄 일일 데이터 수집 시작: {target_date}")
        
        # Check if data already exists for this date
        if self._data_exists_for_date(target_date):
            logger.warning(f"⚠️ 데이터가 이미 존재함: {target_date}")
            return {'status': 'already_exists', 'date': target_date}
        
        # Collect live data
        raw_data = self.analyzer.crawl_pokerscout_data()
        
        if not raw_data:
            logger.error("❌ 데이터 수집 실패")
            return {'status': 'failed', 'date': target_date}
        
        logger.info(f"✅ 원본 데이터 수집: {len(raw_data)}개 플랫폼")
        
        # Validate and clean data
        validated_data = self._validate_and_clean_data(raw_data)
        
        # Store in database
        stored_count = self._store_daily_data(target_date, timestamp, validated_data)
        
        # Log collection
        self._log_collection(target_date, timestamp, raw_data, validated_data)
        
        logger.info(f"✅ 일일 데이터 수집 완료: {stored_count}개 플랫폼 저장")
        
        return {
            'status': 'success',
            'date': target_date,
            'platforms_collected': len(raw_data),
            'platforms_stored': stored_count,
            'timestamp': timestamp
        }
    
    def _data_exists_for_date(self, date: str) -> bool:
        """Check if data already exists for the given date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_data WHERE date = ?", (date,))
            count = cursor.fetchone()[0]
            return count > 0
    
    def _validate_and_clean_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Validate and clean raw data"""
        logger.info("🔍 데이터 검증 및 정리")
        
        validated_data = []
        flagged_platforms = []
        
        for site in raw_data:
            # Apply validation rules
            original_online = site['players_online']
            validated_online = self.analyzer._validate_online_players(original_online, site['site_name'])
            
            # Determine data quality
            data_quality = 'normal'
            if validated_online != original_online:
                data_quality = 'corrected'
                flagged_platforms.append(site['site_name'])
            
            # Check for suspicious historical data
            if site['seven_day_avg'] == 0 and site['players_online'] > 100:
                data_quality = 'suspicious_history'
            
            # Store validated data
            validated_site = {
                'site_name': site['site_name'],
                'players_online': validated_online,
                'cash_players': site['cash_players'],
                'peak_24h': site['peak_24h'],
                'seven_day_avg': site['seven_day_avg'],  # Keep original for reference
                'data_quality': data_quality,
                'original_online': original_online
            }
            
            validated_data.append(validated_site)
        
        logger.info(f"✅ 데이터 검증 완료: {len(validated_data)}개 플랫폼, {len(flagged_platforms)}개 수정됨")
        
        if flagged_platforms:
            logger.warning(f"🚨 수정된 플랫폼: {', '.join(flagged_platforms[:5])}")
        
        return validated_data
    
    def _store_daily_data(self, date: str, timestamp: str, data: List[Dict]) -> int:
        """Store validated data in database"""
        logger.info("💾 데이터베이스에 저장")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stored_count = 0
            
            for site in data:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO daily_data 
                        (date, timestamp, site_name, players_online, cash_players, 
                         peak_24h, seven_day_avg, data_quality, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date,
                        timestamp,
                        site['site_name'],
                        site['players_online'],
                        site['cash_players'],
                        site['peak_24h'],
                        site['seven_day_avg'],
                        site['data_quality'],
                        datetime.now().isoformat()
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ 저장 실패 - {site['site_name']}: {e}")
            
            conn.commit()
        
        return stored_count
    
    def _log_collection(self, date: str, timestamp: str, raw_data: List[Dict], validated_data: List[Dict]):
        """Log collection process"""
        flagged_count = len([d for d in validated_data if d['data_quality'] != 'normal'])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO collection_log 
                (date, timestamp, platforms_collected, platforms_validated, 
                 platforms_flagged, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                timestamp,
                len(raw_data),
                len(validated_data),
                flagged_count,
                'completed',
                f"정상 수집: {len(validated_data) - flagged_count}개, 수정됨: {flagged_count}개",
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def get_historical_data(self, site_name: str, days: int = 7) -> List[Dict]:
        """Get historical data for a specific platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, players_online, cash_players, peak_24h, data_quality
                FROM daily_data
                WHERE site_name = ?
                ORDER BY date DESC
                LIMIT ?
            """, (site_name, days))
            
            rows = cursor.fetchall()
            
            return [{
                'date': row[0],
                'players_online': row[1],
                'cash_players': row[2],
                'peak_24h': row[3],
                'data_quality': row[4]
            } for row in rows]
    
    def calculate_growth_from_history(self, current_data: List[Dict], days_back: int = 7) -> List[Dict]:
        """Calculate growth rates using our historical data"""
        logger.info(f"📊 히스토리 기반 성장률 계산 (지난 {days_back}일)")
        
        growth_results = []
        target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for site in current_data:
                site_name = site['site_name']
                current_online = site['players_online']
                
                # Get historical data
                cursor.execute("""
                    SELECT players_online FROM daily_data
                    WHERE site_name = ? AND date = ?
                """, (site_name, target_date))
                
                historical_row = cursor.fetchone()
                
                if historical_row:
                    historical_online = historical_row[0]
                    
                    if historical_online > 0:
                        growth_rate = ((current_online - historical_online) / historical_online) * 100
                        growth_type = 'calculated'
                    else:
                        growth_rate = 0 if current_online == 0 else float('inf')
                        growth_type = 'infinite'
                else:
                    # No historical data - use PokerScout's 7-day avg as fallback
                    pokerscount_avg = site.get('seven_day_avg', 0)
                    if pokerscount_avg > 0:
                        growth_rate = ((current_online - pokerscount_avg) / pokerscount_avg) * 100
                        growth_type = 'fallback'
                    else:
                        growth_rate = 0
                        growth_type = 'no_data'
                
                growth_results.append({
                    'site_name': site_name,
                    'current_online': current_online,
                    'historical_online': historical_row[0] if historical_row else site.get('seven_day_avg', 0),
                    'growth_rate': growth_rate,
                    'growth_type': growth_type,
                    'days_back': days_back,
                    'comparison_date': target_date if historical_row else 'pokerscount_avg'
                })
        
        return growth_results
    
    def get_collection_summary(self, days: int = 7) -> Dict:
        """Get collection summary for recent days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get recent collections
            cursor.execute("""
                SELECT date, platforms_collected, platforms_validated, platforms_flagged, status
                FROM collection_log
                ORDER BY date DESC
                LIMIT ?
            """, (days,))
            
            recent_collections = cursor.fetchall()
            
            # Get total data points
            cursor.execute("SELECT COUNT(*) FROM daily_data")
            total_data_points = cursor.fetchone()[0]
            
            # Get unique platforms
            cursor.execute("SELECT COUNT(DISTINCT site_name) FROM daily_data")
            unique_platforms = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM daily_data")
            date_range = cursor.fetchone()
            
            return {
                'total_data_points': total_data_points,
                'unique_platforms': unique_platforms,
                'date_range': {
                    'start': date_range[0],
                    'end': date_range[1]
                },
                'recent_collections': [{
                    'date': row[0],
                    'platforms_collected': row[1],
                    'platforms_validated': row[2],
                    'platforms_flagged': row[3],
                    'status': row[4]
                } for row in recent_collections],
                'collection_days': len(recent_collections)
            }

def main():
    print("=" * 80)
    print("📅 일일 포커 플랫폼 데이터 수집기")
    print("=" * 80)
    
    collector = DailyDataCollector()
    
    # Collect today's data
    result = collector.collect_daily_data()
    
    print(f"\n📊 수집 결과:")
    print(f"상태: {result['status']}")
    print(f"날짜: {result['date']}")
    
    if result['status'] == 'success':
        print(f"수집된 플랫폼: {result['platforms_collected']}개")
        print(f"저장된 플랫폼: {result['platforms_stored']}개")
        print(f"타임스탬프: {result['timestamp']}")
    
    # Show summary
    summary = collector.get_collection_summary()
    
    print(f"\n📈 수집 현황:")
    print(f"총 데이터 포인트: {summary['total_data_points']:,}개")
    print(f"추적 플랫폼: {summary['unique_platforms']}개")
    print(f"수집 기간: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
    print(f"최근 수집 일수: {summary['collection_days']}일")
    
    print("\n" + "=" * 80)
    print("✅ 일일 데이터 수집 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()