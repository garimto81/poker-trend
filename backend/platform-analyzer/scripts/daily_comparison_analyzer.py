#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Comparison Analyzer
전일 vs 오늘 일일 비교 분석 전용 스크립트
"""

import os
import sys
import logging
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_period_analyzer import MultiPeriodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyComparisonAnalyzer:
    def __init__(self, db_path: str = "poker_history.db"):
        self.analyzer = MultiPeriodAnalyzer(db_path)
    
    def run_daily_analysis(self, target_date: str = None) -> dict:
        """일일 분석 실행 및 결과 반환"""
        logger.info("🔍 일일 비교 분석 시작...")
        
        # 분석 실행
        result = self.analyzer.daily_comparison_analysis(target_date)
        
        # 결과 요약
        self._print_daily_summary(result)
        
        return result
    
    def _print_daily_summary(self, result: dict):
        """일일 분석 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📅 일일 포커 시장 비교 분석 결과")
        print("=" * 80)
        
        yesterday = result['yesterday']
        today = result['today']
        changes = result['changes']
        
        print(f"\n📊 기간: {result['period']}")
        print(f"분석 시간: {result['analysis_timestamp']}")
        
        print("\n🏆 주요 지표 비교:")
        print("-" * 50)
        
        # 총 플레이어 수 변화
        total_change = changes['total_players']
        print(f"총 플레이어 수:")
        print(f"  전일: {total_change['old']:,}명")
        print(f"  오늘: {total_change['new']:,}명")
        print(f"  변화: {total_change['change']:+,}명 ({total_change['change_pct']:+.1f}%)")
        
        # 평균 플레이어 수 변화
        avg_change = changes['avg_players']
        print(f"\n평균 플레이어 수:")
        print(f"  전일: {avg_change['old']:,.1f}명")
        print(f"  오늘: {avg_change['new']:,.1f}명")
        print(f"  변화: {avg_change['change']:+,.1f}명 ({avg_change['change_pct']:+.1f}%)")
        
        # 시장 집중도 변화
        concentration_change = changes['market_concentration']
        print(f"\n시장 집중도 (상위3개):")
        print(f"  전일: {concentration_change['old']:.1f}%")
        print(f"  오늘: {concentration_change['new']:.1f}%")
        print(f"  변화: {concentration_change['change']:+.1f}%p")
        
        # 추적 사이트 수
        sites_change = changes['unique_sites']
        print(f"\n추적 사이트 수:")
        print(f"  전일: {sites_change['old']}개")
        print(f"  오늘: {sites_change['new']}개")
        print(f"  변화: {sites_change['change']:+d}개")
        
        # 상위 증가/감소 사이트
        site_comparison = result['site_comparison']
        
        if site_comparison['top_gainers']:
            print(f"\n📈 상위 증가 사이트:")
            print("-" * 30)
            for i, site in enumerate(site_comparison['top_gainers'][:3], 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        if site_comparison['top_losers']:
            print(f"\n📉 상위 감소 사이트:")
            print("-" * 30)
            for i, site in enumerate(reversed(site_comparison['top_losers'][-3:]), 1):
                print(f"{i}. {site['site_name']}: {site['old_avg']:.0f} → {site['new_avg']:.0f} "
                      f"({site['change_pct']:+.1f}%)")
        
        # 데이터 품질 정보
        print(f"\n📊 데이터 현황:")
        print(f"  전일 데이터: {yesterday['data_count']}개 레코드")
        print(f"  오늘 데이터: {today['data_count']}개 레코드")
    
    def save_analysis_report(self, result: dict, output_path: str = None) -> str:
        """분석 결과를 JSON 파일로 저장"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"daily_analysis_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 일일 분석 결과가 저장되었습니다: {output_path}")
        return output_path
    
    def get_trend_insights(self, result: dict) -> dict:
        """트렌드 인사이트 추출"""
        changes = result['changes']
        site_comparison = result['site_comparison']
        
        insights = {
            'overall_trend': '',
            'market_concentration_trend': '',
            'key_movers': [],
            'data_quality_assessment': ''
        }
        
        # 전체 트렌드 분석
        total_change_pct = changes['total_players']['change_pct']
        if total_change_pct > 5:
            insights['overall_trend'] = f"포커 시장이 전일 대비 {total_change_pct:.1f}% 큰 폭으로 성장했습니다."
        elif total_change_pct > 1:
            insights['overall_trend'] = f"포커 시장이 전일 대비 {total_change_pct:.1f}% 소폭 성장했습니다."
        elif total_change_pct > -1:
            insights['overall_trend'] = "포커 시장이 전일과 비슷한 수준을 유지하고 있습니다."
        elif total_change_pct > -5:
            insights['overall_trend'] = f"포커 시장이 전일 대비 {abs(total_change_pct):.1f}% 소폭 감소했습니다."
        else:
            insights['overall_trend'] = f"포커 시장이 전일 대비 {abs(total_change_pct):.1f}% 큰 폭으로 감소했습니다."
        
        # 시장 집중도 트렌드
        concentration_change = changes['market_concentration']['change']
        if concentration_change > 2:
            insights['market_concentration_trend'] = "시장 집중도가 높아졌습니다 (상위 사이트로의 집중)"
        elif concentration_change < -2:
            insights['market_concentration_trend'] = "시장 집중도가 낮아졌습니다 (플레이어 분산)"
        else:
            insights['market_concentration_trend'] = "시장 집중도는 안정적입니다"
        
        # 주요 변동 사이트
        if site_comparison['top_gainers']:
            top_gainer = site_comparison['top_gainers'][0]
            insights['key_movers'].append(f"최대 증가: {top_gainer['site_name']} (+{top_gainer['change_pct']:.1f}%)")
        
        if site_comparison['top_losers']:
            top_loser = site_comparison['top_losers'][-1]
            insights['key_movers'].append(f"최대 감소: {top_loser['site_name']} ({top_loser['change_pct']:.1f}%)")
        
        # 데이터 품질 평가
        yesterday_count = result['yesterday']['data_count']
        today_count = result['today']['data_count']
        
        if yesterday_count == 0:
            insights['data_quality_assessment'] = "전일 데이터가 없어 정확한 비교가 어렵습니다"
        elif today_count == 0:
            insights['data_quality_assessment'] = "오늘 데이터가 아직 수집되지 않았습니다"
        elif abs(yesterday_count - today_count) > yesterday_count * 0.2:
            insights['data_quality_assessment'] = "데이터 수집량에 큰 차이가 있어 주의가 필요합니다"
        else:
            insights['data_quality_assessment'] = "데이터 품질이 양호합니다"
        
        return insights

def main():
    analyzer = DailyComparisonAnalyzer()
    
    print("🔍 일일 포커 시장 비교 분석 시스템")
    print("-" * 50)
    
    target_date = input("분석할 날짜를 입력하세요 (YYYY-MM-DD, 엔터시 오늘): ").strip()
    if not target_date:
        target_date = None
    
    try:
        # 분석 실행
        result = analyzer.run_daily_analysis(target_date)
        
        # 인사이트 추출
        insights = analyzer.get_trend_insights(result)
        
        print(f"\n💡 주요 인사이트:")
        print("-" * 30)
        print(f"• {insights['overall_trend']}")
        print(f"• {insights['market_concentration_trend']}")
        for mover in insights['key_movers']:
            print(f"• {mover}")
        print(f"• {insights['data_quality_assessment']}")
        
        # 결과 저장 여부 확인
        save_choice = input("\n결과를 파일로 저장하시겠습니까? (y/N): ").strip().lower()
        if save_choice == 'y':
            output_file = analyzer.save_analysis_report(result)
            print(f"✅ 저장 완료: {output_file}")
            
    except Exception as e:
        logger.error(f"분석 실패: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()