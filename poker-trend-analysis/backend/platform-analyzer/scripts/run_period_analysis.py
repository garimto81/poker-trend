#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Period Analysis Runner
다기간 포커 분석 시스템 실행 스크립트
"""

import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 필요한 모듈들 import
from daily_comparison_analyzer import DailyComparisonAnalyzer
from weekly_comparison_analyzer import WeeklyComparisonAnalyzer
from monthly_comparison_analyzer import MonthlyComparisonAnalyzer
from report_generator import ReportGenerator
from slack_report_sender import SlackReportSender
from integrated_period_analysis_test import IntegratedAnalysisTest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🚀 다기간 포커 시장 분석 시스템")
    print("=" * 60)
    print("요구사항: 전일과 오늘, 지난주와 이번주, 지난달과 이번달 비교 분석")
    print("=" * 60)
    
    print("\n작업을 선택하세요:")
    print("1. 📅 일일 분석 (전일 vs 오늘)")
    print("2. 📊 주간 분석 (지난주 vs 이번주)")  
    print("3. 📈 월간 분석 (지난달 vs 이번달)")
    print("4. 📋 보고서 생성 (모든 형식)")
    print("5. 💬 Slack 보고서 전송")
    print("6. 🧪 시스템 통합 테스트")
    print("7. 🎯 모든 분석 실행")
    
    try:
        choice = input("\n선택 (1-7): ").strip()
        
        if choice == '1':
            print("\n📅 일일 비교 분석 실행...")
            analyzer = DailyComparisonAnalyzer()
            result = analyzer.run_daily_analysis()
            insights = analyzer.get_trend_insights(result)
            
            print(f"\n💡 주요 인사이트:")
            print(f"• {insights['overall_trend']}")
            print(f"• {insights['market_concentration_trend']}")
            print(f"• {insights['data_quality_assessment']}")
            
        elif choice == '2':
            print("\n📊 주간 비교 분석 실행...")
            analyzer = WeeklyComparisonAnalyzer()
            result = analyzer.run_weekly_analysis()
            trends = analyzer.get_weekly_trends(result)
            
            print(f"\n📈 주간 트렌드:")
            print(f"• 성장 동향: {trends['growth_trend']}")
            print(f"• 변동성: {trends['volatility_assessment']}")
            print(f"• 시장 역학: {trends['market_dynamics']}")
            
        elif choice == '3':
            print("\n📈 월간 비교 분석 실행...")
            analyzer = MonthlyComparisonAnalyzer()
            result = analyzer.run_monthly_analysis()
            trends = analyzer.get_monthly_trends(result)
            
            print(f"\n🎯 월간 성과:")
            print(f"• {trends['monthly_performance']}")
            print(f"• 시장 성숙도: {trends['market_maturity']}")
            print(f"• 경쟁 환경: {trends['competitive_landscape']}")
            
        elif choice == '4':
            print("\n📋 모든 형식 보고서 생성...")
            generator = ReportGenerator()
            
            print("  📅 일일 보고서 (Slack 형식)...")
            daily_report = generator.generate_daily_report(format_type='slack')
            print("    ✅ 생성 완료")
            
            print("  📊 주간 보고서 (Slack 형식)...")
            weekly_report = generator.generate_weekly_report(format_type='slack')
            print("    ✅ 생성 완료")
            
            print("  📈 월간 보고서 (Plain 형식)...")
            monthly_report = generator.generate_monthly_report(format_type='plain')
            print("    ✅ 생성 완료")
            
            print(f"\n📄 샘플 - 일일 보고서 (Slack 형식):")
            print("-" * 50)
            print(daily_report['formatted_report'])
            
        elif choice == '5':
            print("\n💬 Slack 보고서 전송 시스템...")
            sender = SlackReportSender()
            
            # Webhook URL 확인
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                print("⚠️ SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
                webhook_input = input("Webhook URL을 입력하세요 (엔터시 건너뛰기): ").strip()
                if webhook_input:
                    os.environ['SLACK_WEBHOOK_URL'] = webhook_input
                    sender = SlackReportSender(webhook_input)
                else:
                    print("❌ Slack 전송을 건너뜁니다.")
                    return
            
            print("  📅 일일 보고서 전송...")
            daily_success = sender.send_daily_report()
            print(f"    {'✅ 성공' if daily_success else '❌ 실패'}")
            
            print("  📊 주간 보고서 전송...")
            weekly_success = sender.send_weekly_report()
            print(f"    {'✅ 성공' if weekly_success else '❌ 실패'}")
            
            print("  📈 월간 보고서 전송...")
            monthly_success = sender.send_monthly_report()
            print(f"    {'✅ 성공' if monthly_success else '❌ 실패'}")
            
        elif choice == '6':
            print("\n🧪 시스템 통합 테스트 실행...")
            tester = IntegratedAnalysisTest()
            test_results = tester.run_comprehensive_test()
            
            success_rate = test_results['success_rate']
            if success_rate >= 80:
                print(f"\n🎉 테스트 완료! 성공률: {success_rate:.1f}%")
            else:
                print(f"\n⚠️ 일부 테스트 실패. 성공률: {success_rate:.1f}%")
            
        elif choice == '7':
            print("\n🎯 모든 분석 실행 (전체 시스템 동작 확인)...")
            
            # 1. 데이터베이스 상태 확인
            print("\n1️⃣ 데이터베이스 상태 확인...")
            analyzer = DailyComparisonAnalyzer()
            db_status = analyzer.analyzer._get_database_status()
            print(f"   📊 총 레코드: {db_status['total_records']:,}개")
            print(f"   🏢 추적 사이트: {db_status['total_sites']}개")
            print(f"   📅 수집 기간: {db_status['date_range']['start']} ~ {db_status['date_range']['end']}")
            
            # 2. 일일 분석
            print("\n2️⃣ 일일 분석 실행...")
            daily_result = analyzer.run_daily_analysis()
            daily_insights = analyzer.get_trend_insights(daily_result)
            print(f"   💡 {daily_insights['overall_trend']}")
            
            # 3. 주간 분석
            print("\n3️⃣ 주간 분석 실행...")
            weekly_analyzer = WeeklyComparisonAnalyzer()
            weekly_result = weekly_analyzer.run_weekly_analysis()
            weekly_trends = weekly_analyzer.get_weekly_trends(weekly_result)
            print(f"   📊 {weekly_trends['growth_trend']}")
            
            # 4. 월간 분석
            print("\n4️⃣ 월간 분석 실행...")
            monthly_analyzer = MonthlyComparisonAnalyzer()
            monthly_result = monthly_analyzer.run_monthly_analysis()
            monthly_trends = monthly_analyzer.get_monthly_trends(monthly_result)
            print(f"   🎯 {monthly_trends['monthly_performance']}")
            
            # 5. 보고서 생성
            print("\n5️⃣ 보고서 생성...")
            generator = ReportGenerator()
            daily_report = generator.generate_daily_report(format_type='slack')
            print(f"   📋 일일 보고서 생성 완료")
            
            # 6. 요약
            print("\n" + "=" * 60)
            print("🎉 전체 시스템 분석 완료!")
            print("=" * 60)
            print(f"✅ 일일 분석: 전일 vs 오늘 비교 완료")
            print(f"✅ 주간 분석: 지난주 vs 이번주 비교 완료") 
            print(f"✅ 월간 분석: 지난달 vs 이번달 비교 완료")
            print(f"✅ 보고서 생성: Slack/Plain/Markdown 형식 지원")
            print(f"✅ 시스템 통합: Firebase 히스토리 + 로컬 수집 데이터")
            
            print(f"\n📊 현재 시스템 상태:")
            print(f"   • 데이터베이스: {db_status['total_records']:,}개 레코드")
            print(f"   • 추적 사이트: {db_status['total_sites']}개")
            print(f"   • 수집 기간: {db_status['date_range']['start']} ~ {db_status['date_range']['end']}")
            print(f"   • 일일 분석: {'✅ 가능' if daily_result['yesterday']['data_count'] > 0 or daily_result['today']['data_count'] > 0 else '⚠️ 제한적'}")
            print(f"   • 주간 분석: {'✅ 가능' if weekly_result['last_week']['data_count'] + weekly_result['this_week']['data_count'] > 0 else '⚠️ 제한적'}")
            print(f"   • 월간 분석: {'✅ 가능' if monthly_result['last_month']['data_count'] + monthly_result['this_month']['data_count'] > 0 else '⚠️ 제한적'}")
            
        else:
            print("❌ 잘못된 선택입니다.")
            return
            
        # 실행 완료 메시지
        print(f"\n✅ 작업이 완료되었습니다! ({datetime.now().strftime('%H:%M:%S')})")
        
        # 다음 단계 안내
        if choice not in ['6', '7']:  # 테스트가 아닌 경우
            print(f"\n💡 다음 단계:")
            print(f"   • Slack 전송을 원한다면 SLACK_WEBHOOK_URL 환경변수를 설정하세요")
            print(f"   • 정기 실행을 위해 cron job이나 Windows 작업 스케줄러를 설정하세요")
            print(f"   • 시스템 전체 테스트: python run_period_analysis.py → 6번 선택")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
        print(f"\n❌ 오류 발생: {e}")
        print(f"   로그를 확인하거나 시스템 테스트(6번)를 실행해보세요.")

if __name__ == "__main__":
    main()