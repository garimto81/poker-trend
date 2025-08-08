#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Comparison Analyzer
지난주 vs 이번주 주간 비교 분석 전용 스크립트
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_period_analyzer import MultiPeriodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyComparisonAnalyzer:
    def __init__(self, db_path: str = "poker_history.db"):
        self.analyzer = MultiPeriodAnalyzer(db_path)
    
    def run_weekly_analysis(self, target_week_start: str = None) -> dict:
        """주간 분석 실행 및 결과 반환"""
        logger.info("📊 주간 비교 분석 시작...")
        
        # 분석 실행
        result = self.analyzer.weekly_comparison_analysis(target_week_start)
        
        # 결과 요약
        self._print_weekly_summary(result)
        
        return result
    
    def _print_weekly_summary(self, result: dict):
        """주간 분석 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📊 주간 포커 시장 비교 분석 결과")
        print("=" * 80)
        
        last_week = result['last_week']
        this_week = result['this_week']
        changes = result['changes']
        
        print(f"\n📅 기간: {result['period']}")
        print(f"분석 시간: {result['analysis_timestamp']}")
        
        print("\n🏆 주요 지표 비교:")
        print("-" * 50)
        
        # 총 플레이어 수 변화
        total_change = changes['total_players']
        print(f"총 플레이어 수:")
        print(f"  지난주: {total_change['old']:,}명")
        print(f"  이번주: {total_change['new']:,}명")
        print(f"  변화: {total_change['change']:+,}명 ({total_change['change_pct']:+.1f}%)")
        
        # 일평균 플레이어 수 변화
        avg_change = changes['avg_players']
        print(f"\n일평균 플레이어 수:")
        print(f"  지난주: {avg_change['old']:,.1f}명")
        print(f"  이번주: {avg_change['new']:,.1f}명")
        print(f"  변화: {avg_change['change']:+,.1f}명 ({avg_change['change_pct']:+.1f}%)")
        
        # 캐시 플레이어 변화
        cash_change = changes['total_cash_players']
        print(f"\n총 캐시 플레이어:")
        print(f"  지난주: {cash_change['old']:,}명")
        print(f"  이번주: {cash_change['new']:,}명")
        print(f"  변화: {cash_change['change']:+,}명 ({cash_change['change_pct']:+.1f}%)")
        
        # 시장 집중도 변화
        concentration_change = changes['market_concentration']
        print(f"\n시장 집중도 (상위3개):")
        print(f"  지난주: {concentration_change['old']:.1f}%")
        print(f"  이번주: {concentration_change['new']:.1f}%")
        print(f"  변화: {concentration_change['change']:+.1f}%p")
        
        # 추적 사이트 수
        sites_change = changes['unique_sites']
        print(f"\n추적 사이트 수:")
        print(f"  지난주: {sites_change['old']}개")
        print(f"  이번주: {sites_change['new']}개")
        print(f"  변화: {sites_change['change']:+d}개")
        
        # 데이터 수집 일수
        last_week_dates = last_week['summary']['unique_dates']
        this_week_dates = this_week['summary']['unique_dates']
        print(f"\n데이터 수집 현황:")
        print(f"  지난주: {last_week_dates}일 수집")
        print(f"  이번주: {this_week_dates}일 수집")
        
        # 상위 증가/감소 사이트
        site_comparison = result['site_comparison']
        
        if site_comparison['top_gainers']:
            print(f"\n📈 주간 상위 성장 사이트:")
            print("-" * 35)
            for i, site in enumerate(site_comparison['top_gainers'][:5], 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        if site_comparison['top_losers']:
            print(f"\n📉 주간 상위 감소 사이트:")
            print("-" * 35)
            for i, site in enumerate(reversed(site_comparison['top_losers'][-5:]), 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        # 데이터 품질 정보
        print(f"\n📊 데이터 현황:")
        print(f"  지난주 데이터: {last_week['data_count']}개 레코드")
        print(f"  이번주 데이터: {this_week['data_count']}개 레코드")
    
    def get_weekly_trends(self, result: dict) -> dict:
        """주간 트렌드 분석"""
        changes = result['changes']
        site_comparison = result['site_comparison']
        last_week = result['last_week']
        this_week = result['this_week']
        
        trends = {
            'growth_trend': '',
            'volatility_assessment': '',
            'market_dynamics': '',
            'data_completeness': '',
            'weekly_insights': []
        }
        
        # 성장 트렌드 분석
        total_change_pct = changes['total_players']['change_pct']
        if total_change_pct > 10:
            trends['growth_trend'] = f"포커 시장이 지난주 대비 {total_change_pct:.1f}%의 강한 성장세를 보였습니다."
        elif total_change_pct > 3:
            trends['growth_trend'] = f"포커 시장이 지난주 대비 {total_change_pct:.1f}%의 양호한 성장을 기록했습니다."
        elif total_change_pct > -3:
            trends['growth_trend'] = f"포커 시장이 지난주와 비슷한 수준을 유지하고 있습니다 ({total_change_pct:+.1f}%)."
        elif total_change_pct > -10:
            trends['growth_trend'] = f"포커 시장이 지난주 대비 {abs(total_change_pct):.1f}% 감소했습니다."
        else:
            trends['growth_trend'] = f"포커 시장이 지난주 대비 {abs(total_change_pct):.1f}%의 큰 폭 감소를 기록했습니다."
        
        # 변동성 평가
        if site_comparison['top_gainers'] and site_comparison['top_losers']:
            top_gain = site_comparison['top_gainers'][0]['change_pct']
            top_loss = abs(site_comparison['top_losers'][-1]['change_pct'])
            volatility = (top_gain + top_loss) / 2
            
            if volatility > 20:
                trends['volatility_assessment'] = f"시장 변동성이 높습니다 (평균 {volatility:.1f}%)"
            elif volatility > 10:
                trends['volatility_assessment'] = f"시장 변동성이 보통입니다 (평균 {volatility:.1f}%)"
            else:
                trends['volatility_assessment'] = f"시장이 안정적입니다 (평균 {volatility:.1f}%)"
        
        # 시장 역학 분석
        concentration_change = changes['market_concentration']['change']
        if concentration_change > 3:
            trends['market_dynamics'] = "시장이 상위 사이트로 집중되는 경향을 보입니다."
        elif concentration_change < -3:
            trends['market_dynamics'] = "플레이어가 다양한 사이트로 분산되는 경향을 보입니다."
        else:
            trends['market_dynamics'] = "시장 집중도가 안정적으로 유지되고 있습니다."
        
        # 데이터 완전성 평가
        last_week_dates = last_week['summary']['unique_dates']
        this_week_dates = this_week['summary']['unique_dates']
        
        if last_week_dates >= 6 and this_week_dates >= 3:
            trends['data_completeness'] = "데이터 수집이 양호합니다."
        elif last_week_dates < 4 or this_week_dates < 2:
            trends['data_completeness'] = "데이터 수집이 부족하여 분석 신뢰도에 주의가 필요합니다."
        else:
            trends['data_completeness'] = "데이터 수집이 보통 수준입니다."
        
        # 주요 인사이트
        if site_comparison['top_gainers']:
            winner = site_comparison['top_gainers'][0]
            trends['weekly_insights'].append(
                f"주간 최대 성장: {winner['site_name']} (+{winner['change_pct']:.1f}%)"
            )
        
        if site_comparison['top_losers']:
            loser = site_comparison['top_losers'][-1]
            trends['weekly_insights'].append(
                f"주간 최대 감소: {loser['site_name']} ({loser['change_pct']:.1f}%)"
            )
        
        # 캐시 vs 총 플레이어 비교
        total_pct = changes['total_players']['change_pct']
        cash_pct = changes['total_cash_players']['change_pct']
        
        if abs(cash_pct - total_pct) > 5:
            if cash_pct > total_pct:
                trends['weekly_insights'].append("캐시 게임 참여가 전체 대비 더 활발해졌습니다.")
            else:
                trends['weekly_insights'].append("토너먼트 참여가 캐시 게임 대비 더 활발해졌습니다.")
        
        return trends
    
    def save_weekly_report(self, result: dict, output_path: str = None) -> str:
        """주간 분석 결과를 JSON 파일로 저장"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"weekly_analysis_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 주간 분석 결과가 저장되었습니다: {output_path}")
        return output_path

def main():
    analyzer = WeeklyComparisonAnalyzer()
    
    print("📊 주간 포커 시장 비교 분석 시스템")
    print("-" * 50)
    
    week_input = input("분석할 주의 시작일을 입력하세요 (YYYY-MM-DD, 엔터시 이번주): ").strip()
    target_week_start = week_input if week_input else None
    
    try:
        # 분석 실행
        result = analyzer.run_weekly_analysis(target_week_start)
        
        # 트렌드 분석
        trends = analyzer.get_weekly_trends(result)
        
        print(f"\n📈 주간 트렌드 인사이트:")
        print("-" * 40)
        print(f"• 성장 동향: {trends['growth_trend']}")
        print(f"• 변동성: {trends['volatility_assessment']}")
        print(f"• 시장 역학: {trends['market_dynamics']}")
        print(f"• 데이터 품질: {trends['data_completeness']}")
        
        if trends['weekly_insights']:
            print(f"\n💡 주요 발견:")
            for insight in trends['weekly_insights']:
                print(f"  • {insight}")
        
        # 결과 저장 여부 확인
        save_choice = input("\n결과를 파일로 저장하시겠습니까? (y/N): ").strip().lower()
        if save_choice == 'y':
            output_file = analyzer.save_weekly_report(result)
            print(f"✅ 저장 완료: {output_file}")
            
    except Exception as e:
        logger.error(f"주간 분석 실패: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()