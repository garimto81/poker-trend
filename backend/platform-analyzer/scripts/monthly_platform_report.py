#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
월간 온라인 포커 플랫폼 종합 분석
30일간의 데이터를 기반으로 한 심층 트렌드 분석

기능:
- 월간 성장/하락 트렌드 분석
- 장기 패턴 식별
- 시장 구조 변화 분석
- 월간 종합 리포트 생성
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict

# 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from online_platform_trend_analyzer import OnlinePlatformTrendAnalyzer

logger = logging.getLogger(__name__)

class MonthlyPlatformAnalyzer(OnlinePlatformTrendAnalyzer):
    """월간 플랫폼 분석기"""
    
    def __init__(self, test_mode: bool = False):
        super().__init__(test_mode=test_mode)
        self.analysis_type = 'monthly'
        self.analysis_period_days = 30
    
    def analyze_monthly_trends(self, platform_data: Dict) -> Dict:
        """
        월간 트렌드 심층 분석
        
        Args:
            platform_data: 플랫폼 데이터
            
        Returns:
            월간 트렌드 분석 결과
        """
        monthly_analysis = {
            'growth_leaders': [],      # 성장 리더
            'declining_platforms': [],  # 하락 플랫폼
            'stable_performers': [],    # 안정적 플랫폼
            'new_entrants': [],        # 신규 진입 플랫폼
            'market_shifts': {}        # 시장 변화
        }
        
        for platform_name, data in platform_data.items():
            historical = data.get('historical_data', [])
            
            if len(historical) < 20:  # 최소 20일 데이터 필요
                continue
            
            # 30일 데이터를 주별로 분할
            weekly_averages = self._calculate_weekly_averages(historical)
            
            # 성장 트렌드 계산
            if len(weekly_averages) >= 4:
                first_week_avg = weekly_averages[0]
                last_week_avg = weekly_averages[-1]
                
                if first_week_avg > 0:
                    monthly_growth = ((last_week_avg - first_week_avg) / first_week_avg) * 100
                    
                    platform_info = {
                        'platform': platform_name,
                        'monthly_growth': monthly_growth,
                        'current_players': data.get('current_data', {}).get('cash_players', 0),
                        'weekly_trend': self._determine_weekly_trend(weekly_averages)
                    }
                    
                    # 카테고리 분류
                    if monthly_growth >= 30:
                        monthly_analysis['growth_leaders'].append(platform_info)
                    elif monthly_growth <= -20:
                        monthly_analysis['declining_platforms'].append(platform_info)
                    elif abs(monthly_growth) <= 5:
                        monthly_analysis['stable_performers'].append(platform_info)
        
        # 정렬
        monthly_analysis['growth_leaders'].sort(key=lambda x: x['monthly_growth'], reverse=True)
        monthly_analysis['declining_platforms'].sort(key=lambda x: x['monthly_growth'])
        monthly_analysis['stable_performers'].sort(key=lambda x: x['current_players'], reverse=True)
        
        return monthly_analysis
    
    def _calculate_weekly_averages(self, historical_data: List) -> List[float]:
        """주별 평균 계산"""
        weekly_averages = []
        week_data = []
        
        for i, record in enumerate(historical_data):
            week_data.append(record.get('cash_players', 0))
            
            # 7일마다 평균 계산
            if (i + 1) % 7 == 0 or i == len(historical_data) - 1:
                if week_data:
                    weekly_averages.append(np.mean(week_data))
                    week_data = []
        
        return weekly_averages
    
    def _determine_weekly_trend(self, weekly_averages: List[float]) -> str:
        """주별 트렌드 방향 결정"""
        if len(weekly_averages) < 2:
            return 'insufficient_data'
        
        # 선형 회귀로 트렌드 방향 계산
        x = np.arange(len(weekly_averages))
        y = np.array(weekly_averages)
        
        # 기울기 계산
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 10:
            return 'strong_upward'
        elif slope > 0:
            return 'upward'
        elif slope < -10:
            return 'strong_downward'
        elif slope < 0:
            return 'downward'
        else:
            return 'flat'
    
    def analyze_market_concentration(self, market_share: Dict) -> Dict:
        """
        시장 집중도 분석 (HHI 지수 등)
        
        Args:
            market_share: 시장 점유율 데이터
            
        Returns:
            시장 집중도 분석 결과
        """
        shares = [p['share_percentage'] for p in market_share['platform_shares'].values()]
        
        # HHI (Herfindahl-Hirschman Index) 계산
        hhi = sum(s**2 for s in shares)
        
        # 상위 3개, 5개, 10개 플랫폼 점유율
        sorted_shares = sorted(shares, reverse=True)
        top3_share = sum(sorted_shares[:3])
        top5_share = sum(sorted_shares[:5])
        top10_share = sum(sorted_shares[:10])
        
        # 시장 집중도 평가
        if hhi > 2500:
            concentration_level = 'highly_concentrated'
            description = '높은 집중도 (소수 플랫폼 지배)'
        elif hhi > 1500:
            concentration_level = 'moderately_concentrated'
            description = '중간 집중도 (적당한 경쟁)'
        else:
            concentration_level = 'low_concentration'
            description = '낮은 집중도 (활발한 경쟁)'
        
        return {
            'hhi_index': round(hhi, 2),
            'concentration_level': concentration_level,
            'description': description,
            'top3_share': round(top3_share, 1),
            'top5_share': round(top5_share, 1),
            'top10_share': round(top10_share, 1),
            'platform_count': len(shares)
        }
    
    def generate_monthly_insights(self, analysis_results: Dict) -> str:
        """
        월간 AI 인사이트 생성
        
        Args:
            analysis_results: 분석 결과
            
        Returns:
            월간 인사이트
        """
        if not self.gemini_model:
            return self._generate_manual_monthly_insights(analysis_results)
        
        try:
            issue_detection = analysis_results.get('issue_detection', {})
            
            # 이슈가 없으면 간단한 월간 요약
            if not issue_detection.get('has_issue'):
                prompt = f"""
                온라인 포커 플랫폼 월간 데이터 요약:
                - 분석 기간: 30일
                - 시장 변동성: {issue_detection.get('market_volatility', 0):.1f}%
                - 시장 집중도: {analysis_results.get('market_concentration', {}).get('description', '')}
                
                특별한 이슈가 없는 상황입니다. 한두 문장으로 간단히 월간 시장 상황을 요약해주세요.
                "월간 온라인 포커 시장은 안정적으로 유지되었습니다" 정도로 간단히 답변해주세요.
                """
            else:
                # 이슈가 있을 때 상세 분석
                prompt = f"""
                온라인 포커 플랫폼 30일간 종합 분석:
                
                [월간 트렌드]
                {json.dumps(analysis_results.get('monthly_trends', {}), indent=2, ensure_ascii=False)}
                
                [시장 집중도]
                {json.dumps(analysis_results.get('market_concentration', {}), indent=2, ensure_ascii=False)}
                
                [주요 이슈]
                {json.dumps(issue_detection, indent=2, ensure_ascii=False)}
                
                다음 내용으로 월간 종합 분석을 작성해주세요:
                1. 이번 달 가장 중요한 변화 3가지
                2. 시장 구조의 변화 (집중화/분산화)
                3. 성장 플랫폼과 하락 플랫폼의 특징
                4. 다음 달 예상 트렌드
                5. 투자자/운영자를 위한 전략적 제언
                
                한국어로 전문적이고 통찰력 있게 작성해주세요.
                """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"월간 AI 인사이트 생성 실패: {e}")
            return self._generate_manual_monthly_insights(analysis_results)
    
    def _generate_manual_monthly_insights(self, analysis_results: Dict) -> str:
        """수동 월간 인사이트 생성"""
        monthly_trends = analysis_results.get('monthly_trends', {})
        market_conc = analysis_results.get('market_concentration', {})
        
        insights = "📊 **월간 분석 요약**\n\n"
        
        # 성장 리더
        if monthly_trends.get('growth_leaders'):
            insights += "**🚀 월간 성장 리더:**\n"
            for leader in monthly_trends['growth_leaders'][:3]:
                insights += f"• {leader['platform']}: +{leader['monthly_growth']:.1f}%\n"
        
        # 시장 집중도
        if market_conc:
            insights += f"\n**📈 시장 구조:**\n"
            insights += f"• HHI 지수: {market_conc['hhi_index']}\n"
            insights += f"• {market_conc['description']}\n"
            insights += f"• TOP 5 점유율: {market_conc['top5_share']:.1f}%\n"
        
        return insights
    
    def run_monthly_analysis(self):
        """월간 분석 실행"""
        logger.info("📊 월간 온라인 포커 플랫폼 분석 시작")
        
        try:
            # 기본 분석 실행
            platform_data = self.fetch_platform_data()
            trends = self.calculate_trends(platform_data)
            market_share = self.analyze_market_share(trends)
            issue_detection = self.detect_market_issues(trends, market_share)
            
            # 월간 특화 분석
            monthly_trends = self.analyze_monthly_trends(platform_data)
            market_concentration = self.analyze_market_concentration(market_share)
            
            # 데이터 출력
            self.print_monthly_summary(trends, market_share, issue_detection, 
                                      monthly_trends, market_concentration)
            
            # 결과 종합
            monthly_results = {
                'analysis_type': 'monthly',
                'period': '30_days',
                'timestamp': datetime.now().isoformat(),
                'basic_trends': trends,
                'market_share': market_share,
                'issue_detection': issue_detection,
                'monthly_trends': monthly_trends,
                'market_concentration': market_concentration
            }
            
            # AI 인사이트 생성
            monthly_insights = self.generate_monthly_insights(monthly_results)
            monthly_results['ai_insights'] = monthly_insights
            
            # 결과 저장
            self.save_monthly_results(monthly_results)
            
            # Slack 리포트 전송
            if not self.test_mode:
                slack_report = self.format_monthly_slack_report(monthly_results)
                self.send_to_slack(slack_report)
                logger.info("✅ 월간 Slack 리포트 전송 완료")
            
            logger.info("✅ 월간 분석 완료")
            return monthly_results
            
        except Exception as e:
            logger.error(f"❌ 월간 분석 실패: {e}")
            raise
    
    def print_monthly_summary(self, trends: Dict, market_share: Dict, 
                             issue_detection: Dict, monthly_trends: Dict, 
                             market_concentration: Dict):
        """월간 분석 결과 출력"""
        print("\n" + "="*70)
        print("📊 온라인 포커 플랫폼 월간 종합 분석")
        print("="*70)
        
        # 기본 정보
        super().print_analysis_summary(trends, market_share, issue_detection)
        
        # 월간 특화 정보
        print("\n[월간 트렌드 분석]")
        
        if monthly_trends.get('growth_leaders'):
            print("\n🚀 성장 리더 (30일 기준):")
            for i, leader in enumerate(monthly_trends['growth_leaders'][:3], 1):
                print(f"  {i}. {leader['platform']}: +{leader['monthly_growth']:.1f}%")
        
        if monthly_trends.get('declining_platforms'):
            print("\n📉 하락 플랫폼:")
            for i, declining in enumerate(monthly_trends['declining_platforms'][:3], 1):
                print(f"  {i}. {declining['platform']}: {declining['monthly_growth']:.1f}%")
        
        print(f"\n[시장 집중도 분석]")
        print(f"• HHI 지수: {market_concentration['hhi_index']}")
        print(f"• 평가: {market_concentration['description']}")
        print(f"• TOP 3 점유율: {market_concentration['top3_share']:.1f}%")
        print(f"• TOP 5 점유율: {market_concentration['top5_share']:.1f}%")
        print(f"• TOP 10 점유율: {market_concentration['top10_share']:.1f}%")
        
        print("\n" + "="*70 + "\n")
    
    def save_monthly_results(self, results: Dict):
        """월간 분석 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/monthly_platform_analysis_{timestamp}.json"
        
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📁 월간 분석 결과 저장: {filename}")
    
    def format_monthly_slack_report(self, results: Dict) -> str:
        """월간 Slack 리포트 포맷"""
        issue_detection = results['issue_detection']
        monthly_trends = results['monthly_trends']
        market_conc = results['market_concentration']
        
        # 이슈가 없는 경우
        if not issue_detection['has_issue']:
            return f"""
📊 **온라인 포커 플랫폼 월간 리포트**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y년 %m월')} 종합 분석

✅ **월간 평가**: 안정적 운영

**시장 현황**
• 시장 집중도: {market_conc['description']}
• TOP 5 점유율: {market_conc['top5_share']:.1f}%
• 월간 변동성: {issue_detection['market_volatility']:.1f}%

💡 {results['ai_insights']}
"""
        
        # 이슈가 있는 경우 - 상세 리포트
        report = f"""
📊 **온라인 포커 플랫폼 월간 종합 리포트**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y년 %m월')} 분석

⚠️ **월간 주요 이슈**
{issue_detection['issue_summary']}

**🚀 월간 성장 TOP 3**
"""
        
        for i, leader in enumerate(monthly_trends.get('growth_leaders', [])[:3], 1):
            report += f"{i}. {leader['platform']}: +{leader['monthly_growth']:.1f}%\n"
        
        report += f"\n**📊 시장 구조**\n"
        report += f"• {market_conc['description']}\n"
        report += f"• HHI: {market_conc['hhi_index']} | TOP5: {market_conc['top5_share']:.1f}%\n"
        
        report += f"\n**🤖 AI 월간 분석**\n{results['ai_insights'][:600]}\n"
        report += f"\n📈 상세: https://garimto81.github.io/poker-online-analyze"
        
        return report


def main():
    """메인 실행 함수"""
    import sys
    test_mode = '--test' in sys.argv
    
    analyzer = MonthlyPlatformAnalyzer(test_mode=test_mode)
    
    if test_mode:
        print("🧪 테스트 모드로 실행 중")
    
    analyzer.run_monthly_analysis()


if __name__ == "__main__":
    main()