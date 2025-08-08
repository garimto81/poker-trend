#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Comparison Analyzer
지난달 vs 이번달 월간 비교 분석 전용 스크립트
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import json
import calendar

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_period_analyzer import MultiPeriodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonthlyComparisonAnalyzer:
    def __init__(self, db_path: str = "poker_history.db"):
        self.analyzer = MultiPeriodAnalyzer(db_path)
    
    def run_monthly_analysis(self, target_month: str = None) -> dict:
        """월간 분석 실행 및 결과 반환"""
        logger.info("📈 월간 비교 분석 시작...")
        
        # 분석 실행
        result = self.analyzer.monthly_comparison_analysis(target_month)
        
        # 결과 요약
        self._print_monthly_summary(result)
        
        return result
    
    def _print_monthly_summary(self, result: dict):
        """월간 분석 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📈 월간 포커 시장 비교 분석 결과")
        print("=" * 80)
        
        last_month = result['last_month']
        this_month = result['this_month']
        changes = result['changes']
        
        print(f"\n📅 기간: {result['period']}")
        print(f"분석 시간: {result['analysis_timestamp']}")
        
        # 월간 기간 정보
        last_period = last_month['period'].split('~')
        this_period = this_month['period'].split('~')
        
        last_month_name = datetime.strptime(last_period[0], '%Y-%m-%d').strftime('%Y년 %m월')
        this_month_name = datetime.strptime(this_period[0], '%Y-%m-%d').strftime('%Y년 %m월')
        
        print(f"\n🗓️ 비교 기간:")
        print(f"  지난달: {last_month_name} ({last_period[0]} ~ {last_period[1]})")
        print(f"  이번달: {this_month_name} ({this_period[0]} ~ {this_period[1]})")
        
        print("\n🏆 주요 지표 비교:")
        print("-" * 50)
        
        # 총 플레이어 수 변화
        total_change = changes['total_players']
        print(f"총 플레이어 수:")
        print(f"  지난달: {total_change['old']:,}명")
        print(f"  이번달: {total_change['new']:,}명")
        print(f"  변화: {total_change['change']:+,}명 ({total_change['change_pct']:+.1f}%)")
        
        # 일평균 플레이어 수 변화
        avg_change = changes['avg_players']
        print(f"\n일평균 플레이어 수:")
        print(f"  지난달: {avg_change['old']:,.1f}명")
        print(f"  이번달: {avg_change['new']:,.1f}명")
        print(f"  변화: {avg_change['change']:+,.1f}명 ({avg_change['change_pct']:+.1f}%)")
        
        # 캐시 플레이어 변화
        cash_change = changes['total_cash_players']
        avg_cash_change = changes['avg_cash_players']
        print(f"\n캐시 플레이어:")
        print(f"  지난달 총계: {cash_change['old']:,}명")
        print(f"  이번달 총계: {cash_change['new']:,}명")
        print(f"  변화: {cash_change['change']:+,}명 ({cash_change['change_pct']:+.1f}%)")
        print(f"  일평균 변화: {avg_cash_change['change']:+,.1f}명 ({avg_cash_change['change_pct']:+.1f}%)")
        
        # 시장 집중도 변화
        concentration_change = changes['market_concentration']
        print(f"\n시장 집중도 (상위3개):")
        print(f"  지난달: {concentration_change['old']:.1f}%")
        print(f"  이번달: {concentration_change['new']:.1f}%")
        print(f"  변화: {concentration_change['change']:+.1f}%p")
        
        # 추적 사이트 수
        sites_change = changes['unique_sites']
        print(f"\n추적 사이트 수:")
        print(f"  지난달: {sites_change['old']}개")
        print(f"  이번달: {sites_change['new']}개")
        print(f"  변화: {sites_change['change']:+d}개")
        
        # 데이터 수집 현황
        last_month_dates = last_month['summary']['unique_dates']
        this_month_dates = this_month['summary']['unique_dates']
        
        # 이번달 예상 총 일수
        current_date = datetime.now()
        if result['period'].endswith(current_date.strftime('%Y-%m')):
            expected_days = current_date.day
        else:
            # 지난달의 경우
            month_year = result['period'].split(' vs ')[0]
            year, month = map(int, month_year.split('-'))
            expected_days = calendar.monthrange(year, month)[1]
        
        print(f"\n📊 데이터 수집 현황:")
        print(f"  지난달: {last_month_dates}일 수집")
        print(f"  이번달: {this_month_dates}일 수집 (예상: {expected_days}일)")
        print(f"  이번달 수집율: {(this_month_dates/expected_days*100):.1f}%")
        
        # 월간 상위 증가/감소 사이트
        site_comparison = result['site_comparison']
        
        if site_comparison['top_gainers']:
            print(f"\n📈 월간 상위 성장 사이트:")
            print("-" * 35)
            for i, site in enumerate(site_comparison['top_gainers'][:5], 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        if site_comparison['top_losers']:
            print(f"\n📉 월간 상위 감소 사이트:")
            print("-" * 35)
            for i, site in enumerate(reversed(site_comparison['top_losers'][-5:]), 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        # 데이터 품질 정보
        print(f"\n📊 데이터 통계:")
        print(f"  지난달 레코드: {last_month['data_count']:,}개")
        print(f"  이번달 레코드: {this_month['data_count']:,}개")
    
    def get_monthly_trends(self, result: dict) -> dict:
        """월간 트렌드 분석"""
        changes = result['changes']
        site_comparison = result['site_comparison']
        last_month = result['last_month']
        this_month = result['this_month']
        
        trends = {
            'monthly_performance': '',
            'market_maturity': '',
            'seasonal_effects': '',
            'competitive_landscape': '',
            'data_reliability': '',
            'key_findings': []
        }
        
        # 월간 성과 분석
        total_change_pct = changes['total_players']['change_pct']
        avg_change_pct = changes['avg_players']['change_pct']
        
        if total_change_pct > 15:
            trends['monthly_performance'] = f"포커 시장이 {total_change_pct:.1f}%의 강력한 월간 성장을 기록했습니다."
        elif total_change_pct > 5:
            trends['monthly_performance'] = f"포커 시장이 {total_change_pct:.1f}%의 건전한 월간 성장을 보였습니다."
        elif total_change_pct > -5:
            trends['monthly_performance'] = f"포커 시장이 안정적인 수준을 유지하고 있습니다 ({total_change_pct:+.1f}%)."
        elif total_change_pct > -15:
            trends['monthly_performance'] = f"포커 시장이 {abs(total_change_pct):.1f}%의 월간 감소를 기록했습니다."
        else:
            trends['monthly_performance'] = f"포커 시장이 {abs(total_change_pct):.1f}%의 큰 폭 월간 감소를 겪었습니다."
        
        # 시장 성숙도 분석
        concentration_change = changes['market_concentration']['change']
        sites_change = changes['unique_sites']['change']
        
        if concentration_change > 5 and sites_change < 0:
            trends['market_maturity'] = "시장이 성숙해지며 상위 브랜드로 집중되는 현상을 보입니다."
        elif concentration_change < -5 and sites_change > 0:
            trends['market_maturity'] = "새로운 플레이어 진입으로 시장 경쟁이 활발해지고 있습니다."
        else:
            trends['market_maturity'] = "시장 구조가 안정적인 상태를 유지하고 있습니다."
        
        # 계절적 효과 분석 (월별 패턴)
        period_info = result['period']
        if '01' in period_info or '12' in period_info:
            trends['seasonal_effects'] = "연말연시 시즌의 영향이 있을 수 있습니다."
        elif '06' in period_info or '07' in period_info or '08' in period_info:
            trends['seasonal_effects'] = "여름 휴가철의 영향이 있을 수 있습니다."
        else:
            trends['seasonal_effects'] = "일반적인 활동 패턴을 보이고 있습니다."
        
        # 경쟁 환경 분석
        if site_comparison['top_gainers'] and site_comparison['top_losers']:
            top_gainer_pct = site_comparison['top_gainers'][0]['change_pct']
            top_loser_pct = abs(site_comparison['top_losers'][-1]['change_pct'])
            
            if top_gainer_pct > 30 or top_loser_pct > 30:
                trends['competitive_landscape'] = "시장에서 급격한 점유율 변화가 발생하고 있습니다."
            elif top_gainer_pct > 15 or top_loser_pct > 15:
                trends['competitive_landscape'] = "경쟁사 간 적당한 수준의 변동이 있습니다."
            else:
                trends['competitive_landscape'] = "전반적으로 안정적인 경쟁 환경입니다."
        
        # 데이터 신뢰성 평가
        last_month_dates = last_month['summary']['unique_dates']
        this_month_dates = this_month['summary']['unique_dates']
        
        # 예상 수집 일수 계산
        current_date = datetime.now()
        expected_days = current_date.day if period_info.endswith(current_date.strftime('%Y-%m')) else 30
        
        collection_rate = this_month_dates / expected_days
        
        if collection_rate > 0.8 and last_month_dates > 25:
            trends['data_reliability'] = "데이터 수집이 매우 양호하여 분석 신뢰도가 높습니다."
        elif collection_rate > 0.5 and last_month_dates > 15:
            trends['data_reliability'] = "데이터 수집이 보통 수준으로 분석에 참고할 만합니다."
        else:
            trends['data_reliability'] = "데이터 수집이 제한적이어서 분석 해석에 주의가 필요합니다."
        
        # 주요 발견사항
        if abs(total_change_pct - avg_change_pct) > 5:
            trends['key_findings'].append("총계와 일평균 변화율에 차이가 있어 수집 패턴 변화가 있었습니다.")
        
        cash_vs_total = changes['avg_cash_players']['change_pct'] - changes['avg_players']['change_pct']
        if cash_vs_total > 5:
            trends['key_findings'].append("캐시 게임 참여가 전체 대비 더 활발해졌습니다.")
        elif cash_vs_total < -5:
            trends['key_findings'].append("토너먼트 참여가 캐시 게임 대비 더 활발해졌습니다.")
        
        if site_comparison['top_gainers']:
            winner = site_comparison['top_gainers'][0]
            trends['key_findings'].append(
                f"월간 최대 성장: {winner['site_name']} (+{winner['change_pct']:.1f}%)"
            )
        
        if site_comparison['top_losers']:
            loser = site_comparison['top_losers'][-1]
            trends['key_findings'].append(
                f"월간 최대 감소: {loser['site_name']} ({loser['change_pct']:.1f}%)"
            )
        
        return trends
    
    def save_monthly_report(self, result: dict, output_path: str = None) -> str:
        """월간 분석 결과를 JSON 파일로 저장"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"monthly_analysis_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 월간 분석 결과가 저장되었습니다: {output_path}")
        return output_path
    
    def generate_monthly_executive_summary(self, result: dict, trends: dict) -> str:
        """경영진용 월간 요약 보고서 생성"""
        changes = result['changes']
        
        summary = f"""
📈 월간 포커 시장 분석 - 경영진 요약 보고서
==============================================

📅 분석 기간: {result['period']}
📊 분석 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

🎯 핵심 지표
-----------
• 총 플레이어 수: {changes['total_players']['change']:+,}명 ({changes['total_players']['change_pct']:+.1f}%)
• 일평균 플레이어: {changes['avg_players']['change']:+,.0f}명 ({changes['avg_players']['change_pct']:+.1f}%)
• 시장 집중도 변화: {changes['market_concentration']['change']:+.1f}%p

💡 주요 인사이트
---------------
• 성과: {trends['monthly_performance']}
• 시장 구조: {trends['market_maturity']}
• 경쟁 환경: {trends['competitive_landscape']}
• 데이터 품질: {trends['data_reliability']}

🔍 주요 발견
-----------
"""
        
        for finding in trends['key_findings']:
            summary += f"• {finding}\n"
        
        site_comparison = result['site_comparison']
        if site_comparison['top_gainers']:
            summary += f"\n📈 성장 리더: {site_comparison['top_gainers'][0]['site_name']} "
            summary += f"(+{site_comparison['top_gainers'][0]['change_pct']:.1f}%)\n"
        
        if site_comparison['top_losers']:
            summary += f"📉 주의 대상: {site_comparison['top_losers'][-1]['site_name']} "
            summary += f"({site_comparison['top_losers'][-1]['change_pct']:.1f}%)\n"
        
        return summary

def main():
    analyzer = MonthlyComparisonAnalyzer()
    
    print("📈 월간 포커 시장 비교 분석 시스템")
    print("-" * 50)
    
    month_input = input("분석할 월을 입력하세요 (YYYY-MM, 엔터시 이번달): ").strip()
    target_month = month_input if month_input else None
    
    try:
        # 분석 실행
        result = analyzer.run_monthly_analysis(target_month)
        
        # 트렌드 분석
        trends = analyzer.get_monthly_trends(result)
        
        print(f"\n📊 월간 트렌드 분석:")
        print("-" * 50)
        print(f"• 월간 성과: {trends['monthly_performance']}")
        print(f"• 시장 성숙도: {trends['market_maturity']}")
        print(f"• 계절적 요인: {trends['seasonal_effects']}")
        print(f"• 경쟁 환경: {trends['competitive_landscape']}")
        print(f"• 데이터 신뢰성: {trends['data_reliability']}")
        
        if trends['key_findings']:
            print(f"\n💎 핵심 발견사항:")
            for finding in trends['key_findings']:
                print(f"  • {finding}")
        
        # 경영진 요약 보고서
        print("\n" + "=" * 80)
        executive_summary = analyzer.generate_monthly_executive_summary(result, trends)
        print(executive_summary)
        
        # 결과 저장 여부 확인
        save_choice = input("\n결과를 파일로 저장하시겠습니까? (y/N): ").strip().lower()
        if save_choice == 'y':
            output_file = analyzer.save_monthly_report(result)
            print(f"✅ 저장 완료: {output_file}")
            
    except Exception as e:
        logger.error(f"월간 분석 실패: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()