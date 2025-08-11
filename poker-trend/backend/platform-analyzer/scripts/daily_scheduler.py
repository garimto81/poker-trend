#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Data Collection Scheduler
매일 자동으로 데이터를 수집하고 분석하는 스케줄러
"""

import os
import sys
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_data_collector import DailyDataCollector
from history_based_analyzer import HistoryBasedAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyScheduler:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.collector = DailyDataCollector(db_path)
        self.analyzer = HistoryBasedAnalyzer(db_path)
        self.schedule_time = "09:00"  # 매일 오전 9시
    
    def collect_daily_data(self):
        """Daily data collection job"""
        logger.info("🕘 일일 데이터 수집 작업 시작")
        
        try:
            # Collect data
            result = self.collector.collect_daily_data()
            
            if result['status'] == 'success':
                logger.info(f"✅ 데이터 수집 성공: {result['platforms_stored']}개 플랫폼")
                
                # Perform daily analysis after collection
                self.run_daily_analysis()
                
            elif result['status'] == 'already_exists':
                logger.info(f"ℹ️ 오늘 데이터 이미 존재: {result['date']}")
                
            else:
                logger.error(f"❌ 데이터 수집 실패: {result}")
                
        except Exception as e:
            logger.error(f"❌ 일일 수집 작업 중 오류: {e}")
    
    def run_daily_analysis(self):
        """Run daily analysis after data collection"""
        logger.info("📊 일일 분석 시작")
        
        try:
            # Check if we have enough historical data
            summary = self.collector.get_collection_summary(days=30)
            
            if summary['collection_days'] >= 2:
                # Run daily analysis (compare with yesterday)
                daily_result = self.analyzer.analyze_with_history('daily')
                logger.info(f"✅ 일일 분석 완료 - 경고 수준: {daily_result.get('alert_level', 'none')}")
                
                # If we have a week of data, also run weekly analysis
                if summary['collection_days'] >= 7:
                    weekly_result = self.analyzer.analyze_with_history('weekly')
                    logger.info(f"✅ 주간 분석 완료 - 경고 수준: {weekly_result.get('alert_level', 'none')}")
                    
                    # Check if we need to send alerts
                    if weekly_result.get('alert_level') in ['medium', 'high']:
                        logger.warning(f"🚨 주의 필요: {weekly_result.get('summary_text')}")
                        # Here you could add Slack notification logic
                
                # If we have a month of data, run monthly analysis on 1st of month
                if summary['collection_days'] >= 30 and datetime.now().day == 1:
                    monthly_result = self.analyzer.analyze_with_history('monthly')
                    logger.info(f"✅ 월간 분석 완료 - 경고 수준: {monthly_result.get('alert_level', 'none')}")
                    
            else:
                logger.info("ℹ️ 히스토리 데이터 부족 - 분석 건너뜀")
                
        except Exception as e:
            logger.error(f"❌ 일일 분석 중 오류: {e}")
    
    def cleanup_old_data(self, keep_days: int = 90):
        """Clean up old data (optional, runs weekly)"""
        logger.info(f"🧹 {keep_days}일 이전 데이터 정리")
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y-%m-%d')
            
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old daily data
                cursor.execute("DELETE FROM daily_data WHERE date < ?", (cutoff_date,))
                deleted_daily = cursor.rowcount
                
                # Delete old collection logs
                cursor.execute("DELETE FROM collection_log WHERE date < ?", (cutoff_date,))
                deleted_logs = cursor.rowcount
                
                # Keep analysis results longer (6 months)
                analysis_cutoff = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
                cursor.execute("DELETE FROM analysis_results WHERE date < ?", (analysis_cutoff,))
                deleted_analysis = cursor.rowcount
                
                conn.commit()
                
            logger.info(f"✅ 정리 완료 - 일일 데이터: {deleted_daily}개, 로그: {deleted_logs}개, 분석: {deleted_analysis}개 삭제")
            
        except Exception as e:
            logger.error(f"❌ 데이터 정리 중 오류: {e}")
    
    def show_status(self):
        """Show current status"""
        try:
            summary = self.collector.get_collection_summary(days=7)
            
            print("=" * 80)
            print("📅 일일 스케줄러 상태")
            print("=" * 80)
            print(f"데이터베이스: {self.db_path}")
            print(f"스케줄 시간: 매일 {self.schedule_time}")
            print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print("📊 수집 현황:")
            print(f"  총 데이터 포인트: {summary['total_data_points']:,}개")
            print(f"  추적 플랫폼: {summary['unique_platforms']}개")
            print(f"  수집 기간: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
            print(f"  최근 수집: {summary['collection_days']}일")
            
            if summary['recent_collections']:
                print("\n📋 최근 수집 내역:")
                for collection in summary['recent_collections'][:5]:
                    status_icon = "✅" if collection['status'] == 'completed' else "❌"
                    flagged_text = f" (수정: {collection['platforms_flagged']}개)" if collection['platforms_flagged'] > 0 else ""
                    print(f"  {status_icon} {collection['date']}: {collection['platforms_validated']}개 플랫폼{flagged_text}")
            
            print()
            print("⏰ 예정된 작업:")
            print(f"  다음 수집: 매일 {self.schedule_time}")
            print(f"  데이터 정리: 매주 일요일")
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ 상태 표시 중 오류: {e}")
    
    def run_scheduler(self):
        """Run the scheduler"""
        logger.info("🚀 일일 스케줄러 시작")
        
        # Schedule daily data collection
        schedule.every().day.at(self.schedule_time).do(self.collect_daily_data)
        
        # Schedule weekly cleanup (Sunday at 02:00)
        schedule.every().sunday.at("02:00").do(self.cleanup_old_data)
        
        # Show initial status
        self.show_status()
        
        logger.info(f"⏰ 스케줄 등록 완료 - 매일 {self.schedule_time}에 데이터 수집")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ 스케줄러 중지됨")
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {e}")
    
    def manual_collect(self):
        """Manual data collection for testing"""
        logger.info("🔧 수동 데이터 수집 실행")
        self.collect_daily_data()
    
    def backfill_data(self, days: int = 7):
        """Backfill data for recent days (for initial setup)"""
        logger.info(f"📅 최근 {days}일 데이터 백필")
        
        for i in range(days, 0, -1):
            target_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            try:
                # Check if data already exists
                if self.collector._data_exists_for_date(target_date):
                    logger.info(f"ℹ️ 데이터 이미 존재: {target_date}")
                    continue
                
                logger.info(f"🔄 백필 수집: {target_date}")
                result = self.collector.collect_daily_data(target_date)
                
                if result['status'] == 'success':
                    logger.info(f"✅ {target_date}: {result['platforms_stored']}개 플랫폼")
                else:
                    logger.warning(f"⚠️ {target_date}: {result['status']}")
                    
                # Small delay between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ 백필 중 오류 ({target_date}): {e}")
        
        logger.info("✅ 백필 완료")

def main():
    print("=" * 80)
    print("⏰ 포커 플랫폼 일일 스케줄러")
    print("=" * 80)
    
    scheduler = DailyScheduler()
    
    print("\n작업을 선택하세요:")
    print("1. 스케줄러 시작 (지속 실행)")
    print("2. 수동 데이터 수집")
    print("3. 상태 확인")
    print("4. 백필 데이터 수집 (최근 7일)")
    print("5. 히스토리 기반 분석 실행")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == '1':
        print("\n🚀 스케줄러를 시작합니다...")
        print("Ctrl+C로 중지할 수 있습니다.")
        scheduler.run_scheduler()
        
    elif choice == '2':
        print("\n🔧 수동 데이터 수집을 실행합니다...")
        scheduler.manual_collect()
        
    elif choice == '3':
        scheduler.show_status()
        
    elif choice == '4':
        days = input("백필할 일수 (기본값 7): ").strip()
        days = int(days) if days.isdigit() else 7
        print(f"\n📅 최근 {days}일 데이터 백필을 시작합니다...")
        scheduler.backfill_data(days)
        
    elif choice == '5':
        print("\n📊 히스토리 기반 분석을 실행합니다...")
        result = scheduler.analyzer.show_comprehensive_analysis('weekly')
        
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()