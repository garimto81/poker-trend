#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Period Report Generator
일일/주간/월간 보고서 생성 및 포맷팅 시스템
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_comparison_analyzer import DailyComparisonAnalyzer
from weekly_comparison_analyzer import WeeklyComparisonAnalyzer
from monthly_comparison_analyzer import MonthlyComparisonAnalyzer

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, db_path: str = "poker_history.db"):
        self.daily_analyzer = DailyComparisonAnalyzer(db_path)
        self.weekly_analyzer = WeeklyComparisonAnalyzer(db_path)
        self.monthly_analyzer = MonthlyComparisonAnalyzer(db_path)
        
        self.templates = {
            'daily': self._get_daily_template(),
            'weekly': self._get_weekly_template(),
            'monthly': self._get_monthly_template()
        }
    
    def generate_daily_report(self, target_date: str = None, format_type: str = 'markdown') -> Dict:
        """일일 보고서 생성"""
        logger.info(f"일일 보고서 생성 시작: {target_date}")
        
        # 분석 실행
        result = self.daily_analyzer.run_daily_analysis(target_date)
        insights = self.daily_analyzer.get_trend_insights(result)
        
        # 보고서 포맷팅
        report = self._format_daily_report(result, insights, format_type)
        
        return {
            'type': 'daily',
            'data': result,
            'insights': insights,
            'formatted_report': report,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_weekly_report(self, target_week_start: str = None, format_type: str = 'markdown') -> Dict:
        """주간 보고서 생성"""
        logger.info(f"주간 보고서 생성 시작: {target_week_start}")
        
        # 분석 실행
        result = self.weekly_analyzer.run_weekly_analysis(target_week_start)
        trends = self.weekly_analyzer.get_weekly_trends(result)
        
        # 보고서 포맷팅
        report = self._format_weekly_report(result, trends, format_type)
        
        return {
            'type': 'weekly',
            'data': result,
            'trends': trends,
            'formatted_report': report,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_monthly_report(self, target_month: str = None, format_type: str = 'markdown') -> Dict:
        """월간 보고서 생성"""
        logger.info(f"월간 보고서 생성 시작: {target_month}")
        
        # 분석 실행
        result = self.monthly_analyzer.run_monthly_analysis(target_month)
        trends = self.monthly_analyzer.get_monthly_trends(result)
        
        # 보고서 포맷팅
        report = self._format_monthly_report(result, trends, format_type)
        
        return {
            'type': 'monthly',
            'data': result,
            'trends': trends,
            'formatted_report': report,
            'generated_at': datetime.now().isoformat()
        }
    
    def _format_daily_report(self, result: Dict, insights: Dict, format_type: str) -> str:
        """일일 보고서 포맷팅"""
        if format_type == 'markdown':
            return self._format_daily_markdown(result, insights)
        elif format_type == 'slack':
            return self._format_daily_slack(result, insights)
        elif format_type == 'plain':
            return self._format_daily_plain(result, insights)
        else:
            raise ValueError(f"지원하지 않는 포맷: {format_type}")
    
    def _format_weekly_report(self, result: Dict, trends: Dict, format_type: str) -> str:
        """주간 보고서 포맷팅"""
        if format_type == 'markdown':
            return self._format_weekly_markdown(result, trends)
        elif format_type == 'slack':
            return self._format_weekly_slack(result, trends)
        elif format_type == 'plain':
            return self._format_weekly_plain(result, trends)
        else:
            raise ValueError(f"지원하지 않는 포맷: {format_type}")
    
    def _format_monthly_report(self, result: Dict, trends: Dict, format_type: str) -> str:
        """월간 보고서 포맷팅"""
        if format_type == 'markdown':
            return self._format_monthly_markdown(result, trends)
        elif format_type == 'slack':
            return self._format_monthly_slack(result, trends)
        elif format_type == 'plain':
            return self._format_monthly_plain(result, trends)
        else:
            raise ValueError(f"지원하지 않는 포맷: {format_type}")
    
    def _format_daily_slack(self, result: Dict, insights: Dict) -> str:
        """일일 보고서 Slack 포맷"""
        changes = result['changes']
        yesterday = result['yesterday']
        today = result['today']
        
        # Slack 블록 구성
        report = f"""📅 *일일 포커 시장 분석 리포트*
        
*📊 기간:* {result['period']}
*⏰ 분석 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

*🎯 핵심 지표*
• 총 플레이어: {changes['total_players']['old']:,} → {changes['total_players']['new']:,} ({changes['total_players']['change_pct']:+.1f}%)
• 평균 플레이어: {changes['avg_players']['old']:,.0f} → {changes['avg_players']['new']:,.0f} ({changes['avg_players']['change_pct']:+.1f}%)
• 시장 집중도: {changes['market_concentration']['old']:.1f}% → {changes['market_concentration']['new']:.1f}% ({changes['market_concentration']['change']:+.1f}%p)

*💡 주요 인사이트*
• {insights['overall_trend']}
• {insights['market_concentration_trend']}"""

        if insights['key_movers']:
            report += "\n• " + "\n• ".join(insights['key_movers'])
        
        report += f"\n• {insights['data_quality_assessment']}"
        
        # 상위 변동 사이트
        site_comparison = result['site_comparison']
        if site_comparison['top_gainers']:
            top_gainer = site_comparison['top_gainers'][0]
            report += f"\n\n📈 *최대 증가*: {top_gainer['site_name']} (+{top_gainer['change_pct']:.1f}%)"
        
        if site_comparison['top_losers']:
            top_loser = site_comparison['top_losers'][-1]
            report += f"\n📉 *최대 감소*: {top_loser['site_name']} ({top_loser['change_pct']:.1f}%)"
        
        report += f"\n\n_데이터: 전일 {yesterday['data_count']}개, 오늘 {today['data_count']}개 레코드_"
        
        return report
    
    def _format_weekly_slack(self, result: Dict, trends: Dict) -> str:
        """주간 보고서 Slack 포맷"""
        changes = result['changes']
        last_week = result['last_week']
        this_week = result['this_week']
        
        report = f"""📊 *주간 포커 시장 분석 리포트*
        
*📅 기간:* {result['period']}
*⏰ 분석 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

*🏆 핵심 지표*
• 총 플레이어: {changes['total_players']['change']:+,}명 ({changes['total_players']['change_pct']:+.1f}%)
• 일평균: {changes['avg_players']['change']:+,.0f}명 ({changes['avg_players']['change_pct']:+.1f}%)
• 캐시 플레이어: {changes['total_cash_players']['change']:+,}명 ({changes['total_cash_players']['change_pct']:+.1f}%)
• 시장 집중도: {changes['market_concentration']['change']:+.1f}%p

*📈 주요 트렌드*
• 성장 동향: {trends['growth_trend']}
• 변동성: {trends['volatility_assessment']}
• 시장 역학: {trends['market_dynamics']}"""

        if trends['weekly_insights']:
            report += "\n\n*💎 주요 발견*"
            for insight in trends['weekly_insights']:
                report += f"\n• {insight}"
        
        # 주간 챔피언과 주의 대상
        site_comparison = result['site_comparison']
        if site_comparison['top_gainers']:
            champion = site_comparison['top_gainers'][0]
            report += f"\n\n🏆 *주간 챔피언*: {champion['site_name']} (+{champion['change_pct']:.1f}%)"
        
        if site_comparison['top_losers']:
            concern = site_comparison['top_losers'][-1]
            report += f"\n⚠️ *주의 대상*: {concern['site_name']} ({concern['change_pct']:.1f}%)"
        
        report += f"\n\n_{trends['data_completeness']}_"
        
        return report
    
    def _format_monthly_slack(self, result: Dict, trends: Dict) -> str:
        """월간 보고서 Slack 포맷"""
        changes = result['changes']
        
        report = f"""📈 *월간 포커 시장 분석 리포트*
        
*📅 기간:* {result['period']}
*⏰ 분석 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}

*🎯 핵심 성과*
• 월간 성장: {changes['total_players']['change_pct']:+.1f}% ({changes['total_players']['change']:+,}명)
• 일평균 변화: {changes['avg_players']['change_pct']:+.1f}% ({changes['avg_players']['change']:+,.0f}명)
• 캐시 게임: {changes['avg_cash_players']['change_pct']:+.1f}%
• 시장 구조: {changes['market_concentration']['change']:+.1f}%p

*🔍 전략적 인사이트*
• 성과: {trends['monthly_performance']}
• 시장 성숙도: {trends['market_maturity']}
• 경쟁 환경: {trends['competitive_landscape']}
• 계절 요인: {trends['seasonal_effects']}"""

        if trends['key_findings']:
            report += "\n\n*💡 핵심 발견*"
            for finding in trends['key_findings']:
                report += f"\n• {finding}"
        
        # 월간 MVP와 관심 대상
        site_comparison = result['site_comparison']
        if site_comparison['top_gainers']:
            mvp = site_comparison['top_gainers'][0]
            report += f"\n\n🌟 *월간 MVP*: {mvp['site_name']} (+{mvp['change_pct']:.1f}%)"
        
        if site_comparison['top_losers']:
            watch = site_comparison['top_losers'][-1]
            report += f"\n👀 *관심 대상*: {watch['site_name']} ({watch['change_pct']:.1f}%)"
        
        report += f"\n\n_{trends['data_reliability']}_"
        
        return report
    
    def _format_daily_markdown(self, result: Dict, insights: Dict) -> str:
        """일일 보고서 Markdown 포맷"""
        # 간단한 Markdown 구현 (필요시 확장)
        return self._format_daily_plain(result, insights)
    
    def _format_weekly_markdown(self, result: Dict, trends: Dict) -> str:
        """주간 보고서 Markdown 포맷"""
        return self._format_weekly_plain(result, trends)
    
    def _format_monthly_markdown(self, result: Dict, trends: Dict) -> str:
        """월간 보고서 Markdown 포맷"""
        return self._format_monthly_plain(result, trends)
    
    def _format_daily_plain(self, result: Dict, insights: Dict) -> str:
        """일일 보고서 Plain Text 포맷"""
        changes = result['changes']
        return f"""일일 포커 시장 분석 ({result['period']})

주요 지표:
- 총 플레이어: {changes['total_players']['change']:+,}명 ({changes['total_players']['change_pct']:+.1f}%)
- 평균 플레이어: {changes['avg_players']['change']:+,.0f}명 ({changes['avg_players']['change_pct']:+.1f}%)

인사이트: {insights['overall_trend']}"""
    
    def _format_weekly_plain(self, result: Dict, trends: Dict) -> str:
        """주간 보고서 Plain Text 포맷"""
        changes = result['changes']
        return f"""주간 포커 시장 분석 ({result['period']})

주요 지표:
- 총 플레이어: {changes['total_players']['change']:+,}명 ({changes['total_players']['change_pct']:+.1f}%)
- 일평균: {changes['avg_players']['change']:+,.0f}명 ({changes['avg_players']['change_pct']:+.1f}%)

트렌드: {trends['growth_trend']}"""
    
    def _format_monthly_plain(self, result: Dict, trends: Dict) -> str:
        """월간 보고서 Plain Text 포맷"""
        changes = result['changes']
        return f"""월간 포커 시장 분석 ({result['period']})

핵심 성과:
- 월간 성장: {changes['total_players']['change_pct']:+.1f}% ({changes['total_players']['change']:+,}명)
- 일평균 변화: {changes['avg_players']['change_pct']:+.1f}%

성과: {trends['monthly_performance']}"""
    
    def save_report(self, report_data: Dict, output_path: str = None) -> str:
        """보고서를 파일로 저장"""
        if not output_path:
            report_type = report_data['type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{report_type}_report_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"보고서가 저장되었습니다: {output_path}")
        return output_path
    
    def _get_daily_template(self) -> str:
        """일일 보고서 템플릿"""
        return """
📅 일일 포커 시장 분석 리포트
기간: {period}
분석 시간: {timestamp}

🎯 핵심 지표
- 총 플레이어 수: {total_change}
- 평균 플레이어 수: {avg_change}
- 시장 집중도: {concentration_change}

💡 주요 인사이트
- {overall_trend}
- {market_trend}
- {data_quality}

📈 상위 변동 사이트
{top_movers}
"""
    
    def _get_weekly_template(self) -> str:
        """주간 보고서 템플릿"""
        return """
📊 주간 포커 시장 분석 리포트
기간: {period}
분석 시간: {timestamp}

🏆 핵심 지표
- 주간 성장률: {growth_rate}
- 변동성: {volatility}
- 시장 역학: {market_dynamics}

📈 트렌드 분석
{trends}

🏆 주간 챔피언 & 주의 대상
{champions_and_concerns}
"""
    
    def _get_monthly_template(self) -> str:
        """월간 보고서 템플릿"""
        return """
📈 월간 포커 시장 분석 리포트
기간: {period}
분석 시간: {timestamp}

🎯 핵심 성과
- 월간 성장: {monthly_growth}
- 시장 성숙도: {market_maturity}
- 경쟁 환경: {competitive_landscape}

🔍 전략적 인사이트
{strategic_insights}

🌟 월간 MVP & 관심 대상
{mvp_and_watchlist}
"""

def main():
    generator = ReportGenerator()
    
    print("📊 기간별 포커 시장 보고서 생성 시스템")
    print("=" * 50)
    
    print("\n보고서 유형을 선택하세요:")
    print("1. 일일 보고서")
    print("2. 주간 보고서") 
    print("3. 월간 보고서")
    print("4. 모든 보고서 생성")
    
    try:
        choice = input("\n선택 (1-4): ").strip()
        
        # 포맷 선택
        print("\n출력 포맷을 선택하세요:")
        print("1. Slack 포맷")
        print("2. Markdown 포맷")
        print("3. Plain Text 포맷")
        
        format_choice = input("포맷 선택 (1-3): ").strip()
        format_map = {'1': 'slack', '2': 'markdown', '3': 'plain'}
        format_type = format_map.get(format_choice, 'slack')
        
        if choice == '1':
            print(f"\n📅 일일 보고서 생성 중 ({format_type} 포맷)...")
            report = generator.generate_daily_report(format_type=format_type)
            print("\n" + report['formatted_report'])
            
        elif choice == '2':
            print(f"\n📊 주간 보고서 생성 중 ({format_type} 포맷)...")
            report = generator.generate_weekly_report(format_type=format_type)
            print("\n" + report['formatted_report'])
            
        elif choice == '3':
            print(f"\n📈 월간 보고서 생성 중 ({format_type} 포맷)...")
            report = generator.generate_monthly_report(format_type=format_type)
            print("\n" + report['formatted_report'])
            
        elif choice == '4':
            print(f"\n🎯 모든 보고서 생성 중 ({format_type} 포맷)...")
            
            daily_report = generator.generate_daily_report(format_type=format_type)
            print("\n📅 일일 보고서:")
            print("-" * 50)
            print(daily_report['formatted_report'])
            
            weekly_report = generator.generate_weekly_report(format_type=format_type)
            print("\n📊 주간 보고서:")
            print("-" * 50)
            print(weekly_report['formatted_report'])
            
            monthly_report = generator.generate_monthly_report(format_type=format_type)
            print("\n📈 월간 보고서:")
            print("-" * 50)
            print(monthly_report['formatted_report'])
            
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        # 저장 여부 확인
        save_choice = input("\n보고서를 파일로 저장하시겠습니까? (y/N): ").strip().lower()
        if save_choice == 'y':
            if choice == '4':
                # 모든 보고서 저장
                generator.save_report(daily_report)
                generator.save_report(weekly_report)
                generator.save_report(monthly_report)
                print("✅ 모든 보고서가 저장되었습니다.")
            else:
                # 단일 보고서 저장
                if 'report' in locals():
                    generator.save_report(report)
                    print("✅ 보고서가 저장되었습니다.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"보고서 생성 실패: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()