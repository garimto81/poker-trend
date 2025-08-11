#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated Period Analysis System Test
다기간 비교 분석 시스템 통합 테스트
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_comparison_analyzer import DailyComparisonAnalyzer
from weekly_comparison_analyzer import WeeklyComparisonAnalyzer  
from monthly_comparison_analyzer import MonthlyComparisonAnalyzer
from report_generator import ReportGenerator
from slack_report_sender import SlackReportSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedAnalysisTest:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.daily_analyzer = DailyComparisonAnalyzer(db_path)
        self.weekly_analyzer = WeeklyComparisonAnalyzer(db_path)
        self.monthly_analyzer = MonthlyComparisonAnalyzer(db_path)
        self.report_generator = ReportGenerator(db_path)
        self.slack_sender = SlackReportSender()
        
        self.test_results = {
            'database_check': False,
            'daily_analysis': False,
            'weekly_analysis': False,
            'monthly_analysis': False,
            'report_generation': False,
            'slack_integration': False,
            'performance_check': False
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """포괄적인 시스템 테스트 실행"""
        logger.info("🧪 통합 시스템 테스트 시작...")
        
        test_summary = {
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_results': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        # 1. 데이터베이스 상태 확인
        print("\\n" + "=" * 80)
        print("1️⃣ 데이터베이스 상태 확인")
        print("=" * 80)
        db_result = self._test_database_status()
        test_summary['test_results']['database'] = db_result
        test_summary['tests_run'] += 1
        if db_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 2. 일일 분석 테스트
        print("\\n" + "=" * 80)
        print("2️⃣ 일일 비교 분석 테스트")
        print("=" * 80)
        daily_result = self._test_daily_analysis()
        test_summary['test_results']['daily_analysis'] = daily_result
        test_summary['tests_run'] += 1
        if daily_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 3. 주간 분석 테스트  
        print("\\n" + "=" * 80)
        print("3️⃣ 주간 비교 분석 테스트")
        print("=" * 80)
        weekly_result = self._test_weekly_analysis()
        test_summary['test_results']['weekly_analysis'] = weekly_result
        test_summary['tests_run'] += 1
        if weekly_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 4. 월간 분석 테스트
        print("\\n" + "=" * 80)
        print("4️⃣ 월간 비교 분석 테스트")
        print("=" * 80)
        monthly_result = self._test_monthly_analysis()
        test_summary['test_results']['monthly_analysis'] = monthly_result
        test_summary['tests_run'] += 1
        if monthly_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 5. 보고서 생성 테스트
        print("\\n" + "=" * 80)
        print("5️⃣ 보고서 생성 시스템 테스트")
        print("=" * 80)
        report_result = self._test_report_generation()
        test_summary['test_results']['report_generation'] = report_result
        test_summary['tests_run'] += 1
        if report_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 6. Slack 통합 테스트
        print("\\n" + "=" * 80)
        print("6️⃣ Slack 통합 테스트")
        print("=" * 80)
        slack_result = self._test_slack_integration()
        test_summary['test_results']['slack_integration'] = slack_result
        test_summary['tests_run'] += 1
        if slack_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 7. 성능 벤치마크
        print("\\n" + "=" * 80)
        print("7️⃣ 성능 벤치마크 테스트")
        print("=" * 80)
        perf_result = self._test_performance()
        test_summary['test_results']['performance'] = perf_result
        test_summary['performance_metrics'] = perf_result.get('metrics', {})
        test_summary['tests_run'] += 1
        if perf_result['passed']:
            test_summary['tests_passed'] += 1
        else:
            test_summary['tests_failed'] += 1
        
        # 최종 결과 및 권장사항
        test_summary['end_time'] = datetime.now().isoformat()
        test_summary['success_rate'] = (test_summary['tests_passed'] / test_summary['tests_run']) * 100
        test_summary['recommendations'] = self._generate_recommendations(test_summary)
        
        # 결과 출력
        self._print_final_results(test_summary)
        
        return test_summary
    
    def _test_database_status(self) -> Dict[str, Any]:
        """데이터베이스 상태 테스트"""
        result = {
            'name': 'Database Status Check',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            # 데이터베이스 상태 조회
            db_status = self.daily_analyzer.analyzer._get_database_status()
            
            print(f"📊 총 레코드: {db_status['total_records']:,}개")
            print(f"🏢 추적 사이트: {db_status['total_sites']}개")
            print(f"📅 수집 일수: {db_status['total_dates']}일")
            print(f"📈 수집 기간: {db_status['date_range']['start']} ~ {db_status['date_range']['end']}")
            
            # 품질 분포
            print("\\n🔍 데이터 품질 분포:")
            for quality, count in db_status['quality_distribution'].items():
                percentage = (count / db_status['total_records']) * 100
                print(f"  • {quality}: {count:,}개 ({percentage:.1f}%)")
            
            result['details'] = db_status
            
            # 검증 기준
            if db_status['total_records'] >= 100:  # 최소 100개 레코드
                if db_status['total_sites'] >= 10:  # 최소 10개 사이트
                    if db_status['total_dates'] >= 3:  # 최소 3일치 데이터
                        result['passed'] = True
                        print("\\n✅ 데이터베이스 상태 양호")
                    else:
                        result['issues'].append("수집 일수가 부족합니다 (최소 3일 필요)")
                else:
                    result['issues'].append("추적 사이트 수가 부족합니다 (최소 10개 필요)")
            else:
                result['issues'].append("총 레코드 수가 부족합니다 (최소 100개 필요)")
                
            if result['issues']:
                print("\\n⚠️ 발견된 문제:")
                for issue in result['issues']:
                    print(f"  • {issue}")
                    
        except Exception as e:
            result['issues'].append(f"데이터베이스 조회 실패: {e}")
            print(f"❌ 데이터베이스 조회 실패: {e}")
        
        return result
    
    def _test_daily_analysis(self) -> Dict[str, Any]:
        """일일 분석 기능 테스트"""
        result = {
            'name': 'Daily Analysis Test',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            start_time = datetime.now()
            
            # 일일 분석 실행
            analysis_result = self.daily_analyzer.run_daily_analysis()
            insights = self.daily_analyzer.get_trend_insights(analysis_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"⏱️ 실행 시간: {execution_time:.2f}초")
            print(f"📊 분석 기간: {analysis_result['period']}")
            print(f"📈 전일 데이터: {analysis_result['yesterday']['data_count']}개")
            print(f"📈 오늘 데이터: {analysis_result['today']['data_count']}개")
            print(f"💡 인사이트: {insights['overall_trend']}")
            
            result['details'] = {
                'execution_time': execution_time,
                'period': analysis_result['period'],
                'data_counts': {
                    'yesterday': analysis_result['yesterday']['data_count'],
                    'today': analysis_result['today']['data_count']
                },
                'insights_generated': len([v for v in insights.values() if v])
            }
            
            # 검증 기준
            if execution_time < 30:  # 30초 이내
                if analysis_result['yesterday']['data_count'] > 0 or analysis_result['today']['data_count'] > 0:
                    result['passed'] = True
                    print("\\n✅ 일일 분석 테스트 통과")
                else:
                    result['issues'].append("분석할 데이터가 없습니다")
            else:
                result['issues'].append(f"실행 시간이 너무 깁니다 ({execution_time:.1f}초)")
                
        except Exception as e:
            result['issues'].append(f"일일 분석 실행 실패: {e}")
            print(f"❌ 일일 분석 실패: {e}")
        
        return result
    
    def _test_weekly_analysis(self) -> Dict[str, Any]:
        """주간 분석 기능 테스트"""
        result = {
            'name': 'Weekly Analysis Test',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            start_time = datetime.now()
            
            # 주간 분석 실행
            analysis_result = self.weekly_analyzer.run_weekly_analysis()
            trends = self.weekly_analyzer.get_weekly_trends(analysis_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"⏱️ 실행 시간: {execution_time:.2f}초")
            print(f"📊 분석 기간: {analysis_result['period']}")
            print(f"📈 지난주 데이터: {analysis_result['last_week']['data_count']}개")
            print(f"📈 이번주 데이터: {analysis_result['this_week']['data_count']}개")
            print(f"📊 성장 트렌드: {trends['growth_trend']}")
            
            result['details'] = {
                'execution_time': execution_time,
                'period': analysis_result['period'],
                'data_counts': {
                    'last_week': analysis_result['last_week']['data_count'],
                    'this_week': analysis_result['this_week']['data_count']
                },
                'trends_generated': len([v for v in trends.values() if v])
            }
            
            # 검증 기준
            if execution_time < 45:  # 45초 이내
                total_data = analysis_result['last_week']['data_count'] + analysis_result['this_week']['data_count']
                if total_data > 0:
                    result['passed'] = True
                    print("\\n✅ 주간 분석 테스트 통과")
                else:
                    result['issues'].append("주간 분석할 데이터가 없습니다")
            else:
                result['issues'].append(f"실행 시간이 너무 깁니다 ({execution_time:.1f}초)")
                
        except Exception as e:
            result['issues'].append(f"주간 분석 실행 실패: {e}")
            print(f"❌ 주간 분석 실패: {e}")
        
        return result
    
    def _test_monthly_analysis(self) -> Dict[str, Any]:
        """월간 분석 기능 테스트"""
        result = {
            'name': 'Monthly Analysis Test',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            start_time = datetime.now()
            
            # 월간 분석 실행
            analysis_result = self.monthly_analyzer.run_monthly_analysis()
            trends = self.monthly_analyzer.get_monthly_trends(analysis_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"⏱️ 실행 시간: {execution_time:.2f}초")
            print(f"📊 분석 기간: {analysis_result['period']}")
            print(f"📈 지난달 데이터: {analysis_result['last_month']['data_count']}개")
            print(f"📈 이번달 데이터: {analysis_result['this_month']['data_count']}개")
            print(f"🎯 월간 성과: {trends['monthly_performance']}")
            
            result['details'] = {
                'execution_time': execution_time,
                'period': analysis_result['period'],
                'data_counts': {
                    'last_month': analysis_result['last_month']['data_count'],
                    'this_month': analysis_result['this_month']['data_count']
                },
                'trends_generated': len([v for v in trends.values() if v])
            }
            
            # 검증 기준
            if execution_time < 60:  # 60초 이내
                total_data = analysis_result['last_month']['data_count'] + analysis_result['this_month']['data_count']
                if total_data > 0:
                    result['passed'] = True
                    print("\\n✅ 월간 분석 테스트 통과")
                else:
                    result['issues'].append("월간 분석할 데이터가 없습니다")
            else:
                result['issues'].append(f"실행 시간이 너무 깁니다 ({execution_time:.1f}초)")
                
        except Exception as e:
            result['issues'].append(f"월간 분석 실행 실패: {e}")
            print(f"❌ 월간 분석 실패: {e}")
        
        return result
    
    def _test_report_generation(self) -> Dict[str, Any]:
        """보고서 생성 기능 테스트"""
        result = {
            'name': 'Report Generation Test',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            start_time = datetime.now()
            
            # 각 유형별 보고서 생성 테스트
            formats_tested = []
            
            print("📋 일일 보고서 생성 테스트...")
            daily_report = self.report_generator.generate_daily_report(format_type='slack')
            if daily_report['formatted_report']:
                formats_tested.append('daily_slack')
                print("  ✅ 일일 Slack 보고서 생성 성공")
            
            print("📋 주간 보고서 생성 테스트...")
            weekly_report = self.report_generator.generate_weekly_report(format_type='slack')
            if weekly_report['formatted_report']:
                formats_tested.append('weekly_slack')
                print("  ✅ 주간 Slack 보고서 생성 성공")
            
            print("📋 월간 보고서 생성 테스트...")
            monthly_report = self.report_generator.generate_monthly_report(format_type='plain')
            if monthly_report['formatted_report']:
                formats_tested.append('monthly_plain')
                print("  ✅ 월간 Plain 보고서 생성 성공")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\\n⏱️ 총 실행 시간: {execution_time:.2f}초")
            print(f"🎯 생성된 보고서: {len(formats_tested)}개")
            
            result['details'] = {
                'execution_time': execution_time,
                'formats_tested': formats_tested,
                'reports_generated': len(formats_tested)
            }
            
            # 검증 기준
            if len(formats_tested) >= 3 and execution_time < 90:
                result['passed'] = True
                print("\\n✅ 보고서 생성 테스트 통과")
            else:
                if len(formats_tested) < 3:
                    result['issues'].append("일부 보고서 생성에 실패했습니다")
                if execution_time >= 90:
                    result['issues'].append("보고서 생성 시간이 너무 깁니다")
                    
        except Exception as e:
            result['issues'].append(f"보고서 생성 실패: {e}")
            print(f"❌ 보고서 생성 실패: {e}")
        
        return result
    
    def _test_slack_integration(self) -> Dict[str, Any]:
        """Slack 통합 기능 테스트"""
        result = {
            'name': 'Slack Integration Test',
            'passed': False,
            'details': {},
            'issues': []
        }
        
        try:
            # Webhook URL 확인
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            
            print(f"🔗 Webhook URL 설정: {'✅' if webhook_url else '❌'}")
            
            if not webhook_url:
                result['issues'].append("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다")
                print("⚠️ Slack 테스트를 건너뜁니다 (Webhook URL 없음)")
                result['details']['webhook_configured'] = False
                result['passed'] = True  # 옵션이므로 패스 처리
                return result
            
            # 연결 테스트
            print("🧪 Slack 연결 테스트 실행...")
            connection_test = self.slack_sender.test_connection()
            
            result['details'] = {
                'webhook_configured': True,
                'connection_test': connection_test,
                'test_message_sent': connection_test
            }
            
            if connection_test:
                result['passed'] = True
                print("\\n✅ Slack 통합 테스트 통과")
            else:
                result['issues'].append("Slack 연결 테스트 실패")
                
        except Exception as e:
            result['issues'].append(f"Slack 통합 테스트 실패: {e}")
            print(f"❌ Slack 통합 테스트 실패: {e}")
        
        return result
    
    def _test_performance(self) -> Dict[str, Any]:
        """성능 벤치마크 테스트"""
        result = {
            'name': 'Performance Benchmark',
            'passed': False,
            'details': {},
            'metrics': {},
            'issues': []
        }
        
        try:
            print("⚡ 성능 벤치마크 실행 중...")
            
            # 다양한 작업의 성능 측정
            benchmarks = {}
            
            # 1. 데이터베이스 조회 성능
            start_time = datetime.now()
            db_status = self.daily_analyzer.analyzer._get_database_status()
            benchmarks['db_query'] = (datetime.now() - start_time).total_seconds()
            
            # 2. 일일 분석 성능
            start_time = datetime.now()
            self.daily_analyzer.run_daily_analysis()
            benchmarks['daily_analysis'] = (datetime.now() - start_time).total_seconds()
            
            # 3. 보고서 생성 성능
            start_time = datetime.now()
            self.report_generator.generate_daily_report(format_type='slack')
            benchmarks['report_generation'] = (datetime.now() - start_time).total_seconds()
            
            print("\\n📊 성능 측정 결과:")
            for operation, time_taken in benchmarks.items():
                status = "✅" if time_taken < 10 else "⚠️" if time_taken < 30 else "❌"
                print(f"  {status} {operation}: {time_taken:.2f}초")
            
            result['metrics'] = benchmarks
            result['details'] = {
                'total_operations': len(benchmarks),
                'average_time': sum(benchmarks.values()) / len(benchmarks),
                'max_time': max(benchmarks.values()),
                'min_time': min(benchmarks.values())
            }
            
            # 성능 기준 (모든 작업이 30초 이내)
            if all(time < 30 for time in benchmarks.values()):
                result['passed'] = True
                print("\\n✅ 성능 벤치마크 통과")
            else:
                slow_operations = [op for op, time in benchmarks.items() if time >= 30]
                result['issues'].append(f"느린 작업: {', '.join(slow_operations)}")
                
        except Exception as e:
            result['issues'].append(f"성능 테스트 실패: {e}")
            print(f"❌ 성능 테스트 실패: {e}")
        
        return result
    
    def _generate_recommendations(self, test_summary: Dict[str, Any]) -> List[str]:
        """테스트 결과 기반 권장사항 생성"""
        recommendations = []
        
        # 성공률 기반 권장사항
        success_rate = test_summary['success_rate']
        if success_rate == 100:
            recommendations.append("🎉 모든 테스트가 통과했습니다! 시스템이 정상적으로 작동하고 있습니다.")
        elif success_rate >= 80:
            recommendations.append("👍 대부분의 기능이 정상 작동합니다. 일부 이슈만 해결하면 완벽합니다.")
        elif success_rate >= 60:
            recommendations.append("⚠️ 일부 핵심 기능에 문제가 있습니다. 우선 수정이 필요합니다.")
        else:
            recommendations.append("🚨 시스템에 심각한 문제가 있습니다. 전면적인 점검이 필요합니다.")
        
        # 개별 테스트 결과 기반 권장사항
        test_results = test_summary['test_results']
        
        if not test_results.get('database', {}).get('passed', False):
            recommendations.append("📊 데이터베이스에 충분한 데이터가 축적될 때까지 더 많은 수집이 필요합니다.")
        
        if not test_results.get('slack_integration', {}).get('passed', False):
            recommendations.append("💬 Slack 통합을 원한다면 SLACK_WEBHOOK_URL 환경변수를 설정해주세요.")
        
        # 성능 관련 권장사항
        perf_metrics = test_summary.get('performance_metrics', {})
        if perf_metrics:
            max_time = max(perf_metrics.values()) if perf_metrics else 0
            if max_time > 20:
                recommendations.append("⚡ 일부 작업이 느립니다. 데이터베이스 인덱스 최적화를 고려해보세요.")
        
        return recommendations
    
    def _print_final_results(self, test_summary: Dict[str, Any]):
        """최종 테스트 결과 출력"""
        print("\\n" + "=" * 80)
        print("🏆 통합 테스트 최종 결과")
        print("=" * 80)
        
        print(f"\\n📊 테스트 요약:")
        print(f"  • 총 테스트: {test_summary['tests_run']}개")
        print(f"  • 성공: {test_summary['tests_passed']}개")
        print(f"  • 실패: {test_summary['tests_failed']}개")
        print(f"  • 성공률: {test_summary['success_rate']:.1f}%")
        
        # 개별 테스트 결과
        print(f"\\n🔍 개별 테스트 결과:")
        for test_name, test_result in test_summary['test_results'].items():
            status = "✅" if test_result.get('passed', False) else "❌"
            print(f"  {status} {test_result.get('name', test_name)}")
            
            if test_result.get('issues'):
                for issue in test_result['issues']:
                    print(f"    ⚠️ {issue}")
        
        # 성능 지표
        if test_summary.get('performance_metrics'):
            print(f"\\n⚡ 성능 지표:")
            for operation, time_taken in test_summary['performance_metrics'].items():
                print(f"  • {operation}: {time_taken:.2f}초")
        
        # 권장사항
        print(f"\\n💡 권장사항:")
        for recommendation in test_summary['recommendations']:
            print(f"  • {recommendation}")
        
        # 실행 시간
        start_time = datetime.fromisoformat(test_summary['start_time'])
        end_time = datetime.fromisoformat(test_summary['end_time'])
        total_time = (end_time - start_time).total_seconds()
        print(f"\\n⏱️ 총 실행 시간: {total_time:.2f}초")

def main():
    print("🧪 다기간 포커 분석 시스템 통합 테스트")
    print("=" * 60)
    
    tester = IntegratedAnalysisTest()
    
    try:
        test_results = tester.run_comprehensive_test()
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"integrated_test_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n💾 테스트 결과가 저장되었습니다: {output_file}")
        
        # 성공률에 따른 종료 코드
        if test_results['success_rate'] >= 80:
            print("\\n🎉 테스트 완료! 시스템이 정상적으로 작동합니다.")
            sys.exit(0)
        else:
            print("\\n⚠️ 일부 테스트가 실패했습니다. 문제를 해결해주세요.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\n\\n⏹️ 사용자가 테스트를 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"테스트 실행 중 치명적 오류: {e}")
        print(f"❌ 치명적 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()