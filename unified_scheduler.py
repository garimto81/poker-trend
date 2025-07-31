#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 포커 트렌드 분석 스케줄러
- 일간: 매일 오전 10시 (24시간)
- 주간: 매주 월요일 오전 10시 (7일)
- 월간: 매월 1일 오전 10시 (30일)
"""

import os
import schedule
import time
from datetime import datetime
import subprocess
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class UnifiedPokerScheduler:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def run_daily_analysis(self):
        """일간 분석 실행"""
        print(f"\n{'='*60}")
        print(f"🌅 일간 포커 트렌드 분석 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 일간 분석기 실행
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.script_dir, 'multi_keyword_analyzer_v2.py')
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ 일간 분석 완료!")
                print(f"출력: {result.stdout}")
            else:
                print(f"❌ 일간 분석 실패: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 일간 분석 실행 오류: {str(e)}")
    
    def run_weekly_analysis(self):
        """주간 분석 실행"""
        print(f"\n{'='*60}")
        print(f"📊 주간 포커 트렌드 분석 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 주간 분석기 실행
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.script_dir, 'weekly_multi_keyword_analyzer.py')
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ 주간 분석 완료!")
                print(f"출력: {result.stdout}")
            else:
                print(f"❌ 주간 분석 실패: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 주간 분석 실행 오류: {str(e)}")
    
    def run_monthly_analysis(self):
        """월간 분석 실행"""
        print(f"\n{'='*60}")
        print(f"📈 월간 포커 트렌드 분석 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 월간 분석기 실행
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.script_dir, 'monthly_multi_keyword_analyzer.py')
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ 월간 분석 완료!")
                print(f"출력: {result.stdout}")
            else:
                print(f"❌ 월간 분석 실패: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 월간 분석 실행 오류: {str(e)}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        print("📅 포커 트렌드 분석 스케줄 설정 중...")
        
        # 일간 분석: 매일 오전 10시
        schedule.every().day.at("10:00").do(self.run_daily_analysis)
        print("   ✓ 일간 분석: 매일 오전 10:00")
        
        # 주간 분석: 매주 월요일 오전 10시
        schedule.every().monday.at("10:00").do(self.run_weekly_analysis)
        print("   ✓ 주간 분석: 매주 월요일 오전 10:00")
        
        # 월간 분석: 매월 1일 오전 10시 (근사치)
        schedule.every().day.at("10:00").do(self.check_monthly_schedule)
        print("   ✓ 월간 분석: 매월 1일 오전 10:00")
        
        print("\n🚀 스케줄러 시작!")
        print("📋 예정된 분석:")
        print("   🌅 일간: 매일 10:00 (최근 24시간)")
        print("   📊 주간: 매주 월요일 10:00 (최근 7일)")
        print("   📈 월간: 매월 1일 10:00 (최근 30일)")
    
    def check_monthly_schedule(self):
        """매월 1일인지 확인하고 월간 분석 실행"""
        if datetime.now().day == 1:
            self.run_monthly_analysis()
    
    def run_scheduler(self):
        """스케줄러 실행"""
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 확인
                
        except KeyboardInterrupt:
            print("\n\n🛑 스케줄러가 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 스케줄러 오류: {str(e)}")

def run_immediate_test():
    """즉시 테스트 실행"""
    scheduler = UnifiedPokerScheduler()
    
    print("🧪 즉시 테스트 실행")
    print("어떤 분석을 실행하시겠습니까?")
    print("1. 일간 분석 (24시간)")
    print("2. 주간 분석 (7일)")
    print("3. 월간 분석 (30일)")
    print("4. 모든 분석")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        scheduler.run_daily_analysis()
    elif choice == "2":
        scheduler.run_weekly_analysis()
    elif choice == "3":
        scheduler.run_monthly_analysis()
    elif choice == "4":
        print("\n🚀 모든 분석 실행 중...")
        scheduler.run_daily_analysis()
        scheduler.run_weekly_analysis()
        scheduler.run_monthly_analysis()
    else:
        print("❌ 잘못된 선택입니다.")

def main():
    print("="*80)
    print("통합 포커 트렌드 분석 스케줄러")
    print("="*80)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_immediate_test()
    else:
        scheduler = UnifiedPokerScheduler()
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()