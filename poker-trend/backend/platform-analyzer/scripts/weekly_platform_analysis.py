#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간 온라인 포커 플랫폼 심층 분석
주간 트렌드와 패턴을 심층적으로 분석

기능:
- 주간 플레이어 이동 패턴 분석
- 요일별/시간대별 트래픽 분석
- 플랫폼 간 상관관계 분석
- 주간 승자와 패자 식별
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from collections import defaultdict

# 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from online_platform_trend_analyzer import OnlinePlatformTrendAnalyzer

logger = logging.getLogger(__name__)

class WeeklyPlatformAnalyzer(OnlinePlatformTrendAnalyzer):
    """주간 플랫폼 분석기"""
    
    def __init__(self):
        super().__init__()
        self.analysis_period_days = 7
        self.comparison_period_days = 14  # 2주 데이터로 주간 비교
    
    def analyze_weekly_patterns(self, platform_data: Dict) -> Dict:
        """
        주간 패턴 분석
        
        Args:
            platform_data: 플랫폼 데이터
            
        Returns:
            주간 패턴 분석 결과
        """
        weekly_patterns = {}
        
        for platform_name, data in platform_data.items():
            historical = data.get('historical_data', [])
            
            if len(historical) < 7:
                continue
            
            # 요일별 평균 계산
            daily_averages = defaultdict(list)
            
            for record in historical:
                if 'timestamp' in record and 'cash_players' in record:
                    timestamp = record['timestamp']
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    
                    day_name = timestamp.strftime('%A')
                    daily_averages[day_name].append(record['cash_players'])
            
            # 요일별 평균과 피크 시간 계산
            day_stats = {}
            for day, values in daily_averages.items():
                if values:
                    day_stats[day] = {
                        'avg': np.mean(values),
                        'max': max(values),
                        'min': min(values),
                        'volatility': np.std(values)
                    }
            
            # 최고/최저 요일 식별
            if day_stats:
                best_day = max(day_stats.items(), key=lambda x: x[1]['avg'])
                worst_day = min(day_stats.items(), key=lambda x: x[1]['avg'])
                
                weekly_patterns[platform_name] = {
                    'daily_stats': day_stats,
                    'best_day': best_day[0],
                    'worst_day': worst_day[0],
                    'weekly_volatility': self._calculate_weekly_volatility(historical)
                }
        
        return weekly_patterns
    
    def _calculate_weekly_volatility(self, historical_data: List) -> float:
        """주간 변동성 계산"""
        if len(historical_data) < 2:
            return 0.0
        
        player_counts = [d.get('cash_players', 0) for d in historical_data]
        if not player_counts:
            return 0.0
        
        return float(np.std(player_counts) / np.mean(player_counts) * 100)
    
    def identify_weekly_movers(self, trends: Dict) -> Dict:
        """
        주간 상승/하락 플랫폼 식별
        
        Args:
            trends: 트렌드 데이터
            
        Returns:
            주간 변동 플랫폼
        """
        movers = {
            'top_gainers': [],
            'top_losers': [],
            'most_stable': [],
            'most_volatile': []
        }
        
        # 성장률 기준 정렬
        sorted_by_growth = sorted(
            trends.items(), 
            key=lambda x: x[1].get('growth_rate', 0), 
            reverse=True
        )
        
        # 상위 상승 플랫폼
        for platform, trend in sorted_by_growth[:5]:
            if trend['growth_rate'] > 0:
                movers['top_gainers'].append({
                    'platform': platform,
                    'growth': trend['growth_rate'],
                    'current_players': trend['current_players']
                })
        
        # 상위 하락 플랫폼
        for platform, trend in sorted_by_growth[-5:]:
            if trend['growth_rate'] < 0:
                movers['top_losers'].append({
                    'platform': platform,
                    'decline': abs(trend['growth_rate']),
                    'current_players': trend['current_players']
                })
        
        # 변동성 기준 정렬
        sorted_by_volatility = sorted(
            trends.items(),
            key=lambda x: x[1].get('volatility', 0)
        )
        
        # 가장 안정적인 플랫폼
        for platform, trend in sorted_by_volatility[:3]:
            if trend['volatility'] < 5:
                movers['most_stable'].append({
                    'platform': platform,
                    'volatility': trend['volatility'],
                    'players': trend['current_players']
                })
        
        # 가장 변동성 높은 플랫폼
        for platform, trend in sorted_by_volatility[-3:]:
            if trend['volatility'] > 10:
                movers['most_volatile'].append({
                    'platform': platform,
                    'volatility': trend['volatility'],
                    'players': trend['current_players']
                })
        
        return movers
    
    def analyze_platform_correlations(self, platform_data: Dict) -> Dict:
        """
        플랫폼 간 상관관계 분석
        
        Args:
            platform_data: 플랫폼 데이터
            
        Returns:
            상관관계 분석 결과
        """
        # 데이터프레임 준비
        df_data = {}
        
        for platform_name, data in platform_data.items():
            historical = data.get('historical_data', [])
            if len(historical) >= 7:
                player_counts = [d.get('cash_players', 0) for d in historical[-7:]]
                df_data[platform_name] = player_counts
        
        if len(df_data) < 2:
            return {}
        
        # 상관관계 계산
        df = pd.DataFrame(df_data)
        correlation_matrix = df.corr()
        
        # 강한 상관관계 찾기
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                platform1 = correlation_matrix.columns[i]
                platform2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                if abs(corr_value) > 0.7:  # 강한 상관관계
                    strong_correlations.append({
                        'platform1': platform1,
                        'platform2': platform2,
                        'correlation': round(corr_value, 3),
                        'type': 'positive' if corr_value > 0 else 'negative'
                    })
        
        return {
            'strong_correlations': strong_correlations,
            'correlation_summary': self._summarize_correlations(correlation_matrix)
        }
    
    def _summarize_correlations(self, correlation_matrix: pd.DataFrame) -> Dict:
        """상관관계 요약"""
        summary = {
            'highly_correlated_groups': [],
            'independent_platforms': []
        }
        
        # 평균 상관계수가 낮은 플랫폼 (독립적)
        avg_correlations = correlation_matrix.mean()
        
        for platform in correlation_matrix.columns:
            avg_corr = avg_correlations[platform]
            if avg_corr < 0.3:
                summary['independent_platforms'].append(platform)
        
        return summary
    
    def generate_weekly_insights(self, analysis_results: Dict) -> str:
        """
        주간 AI 인사이트 생성
        
        Args:
            analysis_results: 분석 결과
            
        Returns:
            주간 인사이트
        """
        if not self.gemini_model:
            return self._generate_manual_insights(analysis_results)
        
        try:
            prompt = f"""
            온라인 포커 플랫폼의 주간 심층 분석 결과를 바탕으로 전문적인 인사이트를 제공해주세요.
            
            [주간 변동 플랫폼]
            {json.dumps(analysis_results.get('weekly_movers', {}), indent=2, ensure_ascii=False)}
            
            [요일별 패턴]
            {json.dumps(analysis_results.get('weekly_patterns', {})[:5], indent=2, ensure_ascii=False)}
            
            [플랫폼 간 상관관계]
            {json.dumps(analysis_results.get('correlations', {}), indent=2, ensure_ascii=False)}
            
            다음 항목들을 포함하여 분석해주세요:
            1. 이번 주 가장 주목할 만한 트렌드 3가지
            2. 플레이어들이 이동하는 패턴과 그 이유
            3. 요일별 트래픽 패턴의 의미
            4. 다음 주 예상되는 변화
            5. 투자자/운영자 관점에서의 제언
            
            한국어로 전문적이면서도 이해하기 쉽게 작성해주세요.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI 인사이트 생성 실패: {e}")
            return self._generate_manual_insights(analysis_results)
    
    def _generate_manual_insights(self, analysis_results: Dict) -> str:
        """수동 인사이트 생성 (AI 사용 불가 시)"""
        movers = analysis_results.get('weekly_movers', {})
        patterns = analysis_results.get('weekly_patterns', {})
        
        insights = "📊 **주간 분석 요약**\n\n"
        
        # 상승 플랫폼
        if movers.get('top_gainers'):
            insights += "**📈 주간 상승 플랫폼:**\n"
            for gainer in movers['top_gainers'][:3]:
                insights += f"• {gainer['platform']}: +{gainer['growth']:.1f}%\n"
        
        # 하락 플랫폼
        if movers.get('top_losers'):
            insights += "\n**📉 주간 하락 플랫폼:**\n"
            for loser in movers['top_losers'][:3]:
                insights += f"• {loser['platform']}: -{loser['decline']:.1f}%\n"
        
        # 안정적 플랫폼
        if movers.get('most_stable'):
            insights += "\n**⚖️ 가장 안정적인 플랫폼:**\n"
            for stable in movers['most_stable']:
                insights += f"• {stable['platform']} (변동성: {stable['volatility']:.1f}%)\n"
        
        return insights
    
    def run_weekly_analysis(self):
        """주간 분석 실행"""
        logger.info("📅 주간 온라인 포커 플랫폼 분석 시작")
        
        try:
            # 기본 분석 실행
            platform_data = self.fetch_platform_data()
            trends = self.calculate_trends(platform_data)
            market_share = self.analyze_market_share(trends)
            
            # 주간 특화 분석
            weekly_patterns = self.analyze_weekly_patterns(platform_data)
            weekly_movers = self.identify_weekly_movers(trends)
            correlations = self.analyze_platform_correlations(platform_data)
            
            # 결과 종합
            weekly_results = {
                'analysis_type': 'weekly',
                'period': '7_days',
                'timestamp': datetime.now().isoformat(),
                'basic_trends': trends,
                'market_share': market_share,
                'weekly_patterns': weekly_patterns,
                'weekly_movers': weekly_movers,
                'correlations': correlations
            }
            
            # AI 인사이트 생성
            weekly_insights = self.generate_weekly_insights(weekly_results)
            weekly_results['ai_insights'] = weekly_insights
            
            # 결과 저장
            self.save_weekly_results(weekly_results)
            
            # Slack 리포트 전송
            slack_report = self.format_weekly_slack_report(weekly_results)
            self.send_to_slack(slack_report)
            
            logger.info("✅ 주간 분석 완료")
            return weekly_results
            
        except Exception as e:
            logger.error(f"❌ 주간 분석 실패: {e}")
            raise
    
    def save_weekly_results(self, results: Dict):
        """주간 분석 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/weekly_platform_analysis_{timestamp}.json"
        
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📁 주간 분석 결과 저장: {filename}")
    
    def format_weekly_slack_report(self, results: Dict) -> str:
        """주간 Slack 리포트 포맷"""
        report = f"""
📅 **온라인 포커 플랫폼 주간 분석 리포트**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 분석 기간: 최근 7일
⏰ 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')} KST

"""
        
        # 주간 변동 플랫폼
        movers = results.get('weekly_movers', {})
        
        if movers.get('top_gainers'):
            report += "**🚀 주간 TOP 상승 플랫폼**\n"
            for i, gainer in enumerate(movers['top_gainers'][:3], 1):
                report += f"{i}. {gainer['platform']}: +{gainer['growth']:.1f}% 📈\n"
            report += "\n"
        
        if movers.get('top_losers'):
            report += "**📉 주간 TOP 하락 플랫폼**\n"
            for i, loser in enumerate(movers['top_losers'][:3], 1):
                report += f"{i}. {loser['platform']}: -{loser['decline']:.1f}% 🔻\n"
            report += "\n"
        
        # AI 인사이트
        if results.get('ai_insights'):
            report += f"**🤖 AI 주간 분석**\n{results['ai_insights'][:1000]}\n\n"
        
        report += "────────────────────────────\n"
        report += "📈 상세 분석: https://garimto81.github.io/poker-online-analyze\n"
        
        return report


def main():
    """메인 실행 함수"""
    analyzer = WeeklyPlatformAnalyzer()
    analyzer.run_weekly_analysis()


if __name__ == "__main__":
    main()