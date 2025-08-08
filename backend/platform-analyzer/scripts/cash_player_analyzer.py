#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cash Player Focused Analyzer
캐시 플레이어 중심 분석 시스템 - 캐시 카우 모델
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from multi_period_analyzer import MultiPeriodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CashPlayerAnalyzer:
    """
    캐시 플레이어 중심 분석 엔진
    - 캐시 카우 모델: 캐시 플레이어가 실제 수익원
    - 시장 점유율 변화가 핵심 트렌드 지표
    """
    
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.base_analyzer = MultiPeriodAnalyzer(db_path)
        
        # 캐시 카우 모델 임계값
        self.thresholds = {
            'cash_ratio': {  # 캐시 플레이어 비율
                'excellent': 0.6,   # 60% 이상
                'good': 0.5,        # 50% 이상
                'normal': 0.4,      # 40% 이상
                'warning': 0.3      # 30% 이상
            },
            'market_share_change': {  # 시장 점유율 변화
                'surge': 2.0,       # +2%p 이상 급증
                'growth': 0.5,      # +0.5%p 이상 성장
                'stable': -0.5,     # -0.5%p ~ +0.5%p 안정
                'decline': -2.0     # -2%p 이상 급락
            },
            'cash_growth': {  # 캐시 플레이어 성장률
                'explosive': 15,    # 15% 이상
                'strong': 10,       # 10% 이상
                'moderate': 5,      # 5% 이상
                'weak': 0          # 0% 이상
            }
        }
    
    def analyze_cash_focused_daily(self, target_date: str = None) -> Dict:
        """캐시 플레이어 중심 일일 분석"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"💰 캐시 플레이어 중심 일일 분석: {target_date}")
        
        # 기본 데이터 수집
        base_result = self.base_analyzer.daily_comparison_analysis(target_date)
        
        # 캐시 플레이어 중심 재분석
        cash_analysis = self._analyze_cash_metrics(base_result)
        
        # 시장 점유율 분석
        market_share_analysis = self._analyze_market_share(base_result)
        
        # 캐시 카우 스코어 계산
        cash_cow_score = self._calculate_cash_cow_score(cash_analysis, market_share_analysis)
        
        return {
            'analysis_type': 'cash_focused_daily',
            'period': base_result['period'],
            'base_data': base_result,
            'cash_analysis': cash_analysis,
            'market_share_analysis': market_share_analysis,
            'cash_cow_score': cash_cow_score,
            'insights': self._generate_cash_insights(cash_analysis, market_share_analysis, cash_cow_score),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_cash_metrics(self, base_result: Dict) -> Dict:
        """캐시 플레이어 핵심 지표 분석"""
        changes = base_result['changes']
        yesterday = base_result['yesterday']['summary']
        today = base_result['today']['summary']
        
        # 캐시 플레이어 비율 계산
        yesterday_cash_ratio = (
            yesterday.get('total_cash_players', 0) / yesterday.get('total_players', 1)
            if yesterday.get('total_players', 0) > 0 else 0
        )
        
        today_cash_ratio = (
            today.get('total_cash_players', 0) / today.get('total_players', 1)
            if today.get('total_players', 0) > 0 else 0
        )
        
        cash_ratio_change = today_cash_ratio - yesterday_cash_ratio
        
        # 캐시 플레이어 성장률
        cash_growth = changes.get('total_cash_players', {}).get('change_pct', 0)
        
        # 총 플레이어 대비 캐시 플레이어 성장 배수
        total_growth = changes.get('total_players', {}).get('change_pct', 0)
        cash_vs_total_multiplier = (
            cash_growth / total_growth if total_growth != 0 else 
            float('inf') if cash_growth > 0 else 0
        )
        
        return {
            'cash_players': {
                'yesterday': yesterday.get('total_cash_players', 0),
                'today': today.get('total_cash_players', 0),
                'change': changes.get('total_cash_players', {}).get('change', 0),
                'change_pct': cash_growth
            },
            'cash_ratio': {
                'yesterday': yesterday_cash_ratio * 100,
                'today': today_cash_ratio * 100,
                'change': cash_ratio_change * 100,
                'quality': self._evaluate_cash_ratio(today_cash_ratio)
            },
            'cash_vs_total': {
                'multiplier': cash_vs_total_multiplier,
                'outperforming': cash_growth > total_growth,
                'interpretation': self._interpret_cash_performance(cash_vs_total_multiplier)
            },
            'cash_growth_grade': self._grade_cash_growth(cash_growth)
        }
    
    def _analyze_market_share(self, base_result: Dict) -> Dict:
        """시장 점유율 변화 분석"""
        site_comparison = base_result.get('site_comparison', {})
        
        # 캐시 플레이어 기준 시장 점유율 계산
        yesterday_data = base_result.get('yesterday_data', [])
        today_data = base_result.get('today_data', [])
        
        # 상위 사이트별 점유율 변화
        market_shares = {}
        
        # 전일 총 캐시 플레이어
        yesterday_total_cash = sum(
            d.get('cash_players', 0) for d in yesterday_data
        ) or 1
        
        # 오늘 총 캐시 플레이어
        today_total_cash = sum(
            d.get('cash_players', 0) for d in today_data
        ) or 1
        
        # 사이트별 점유율 계산
        site_shares = []
        
        for site in site_comparison.get('all_changes', [])[:10]:  # Top 10
            site_name = site['site_name']
            
            # 전일 점유율
            yesterday_cash = next(
                (d['cash_players'] for d in yesterday_data if d.get('site_name') == site_name),
                0
            )
            yesterday_share = (yesterday_cash / yesterday_total_cash) * 100
            
            # 오늘 점유율
            today_cash = next(
                (d['cash_players'] for d in today_data if d.get('site_name') == site_name),
                0
            )
            today_share = (today_cash / today_total_cash) * 100
            
            share_change = today_share - yesterday_share
            
            site_shares.append({
                'site_name': site_name,
                'yesterday_share': yesterday_share,
                'today_share': today_share,
                'share_change': share_change,
                'trend': self._classify_share_trend(share_change)
            })
        
        # 점유율 변화 기준 정렬
        site_shares.sort(key=lambda x: abs(x['share_change']), reverse=True)
        
        # 상위 3개 사이트 집중도 (캐시 플레이어 기준)
        top3_concentration = sum(s['today_share'] for s in site_shares[:3])
        
        return {
            'total_cash_players': {
                'yesterday': yesterday_total_cash,
                'today': today_total_cash
            },
            'site_shares': site_shares[:5],  # Top 5만
            'top3_concentration': top3_concentration,
            'market_volatility': self._calculate_market_volatility(site_shares),
            'dominant_player': site_shares[0] if site_shares else None,
            'share_movements': {
                'gainers': [s for s in site_shares if s['share_change'] > 0.5][:3],
                'losers': [s for s in site_shares if s['share_change'] < -0.5][:3]
            }
        }
    
    def _calculate_cash_cow_score(self, cash_analysis: Dict, market_share: Dict) -> Dict:
        """캐시 카우 스코어 계산 (100점 만점)"""
        score_components = {}
        
        # 1. 캐시 플레이어 성장률 (30점)
        cash_growth = cash_analysis['cash_players']['change_pct']
        if cash_growth >= 15:
            score_components['cash_growth'] = 30
        elif cash_growth >= 10:
            score_components['cash_growth'] = 25
        elif cash_growth >= 5:
            score_components['cash_growth'] = 20
        elif cash_growth >= 0:
            score_components['cash_growth'] = 15
        else:
            score_components['cash_growth'] = max(0, 15 + cash_growth)
        
        # 2. 캐시 비율 품질 (25점)
        cash_ratio = cash_analysis['cash_ratio']['today']
        if cash_ratio >= 60:
            score_components['cash_ratio'] = 25
        elif cash_ratio >= 50:
            score_components['cash_ratio'] = 20
        elif cash_ratio >= 40:
            score_components['cash_ratio'] = 15
        elif cash_ratio >= 30:
            score_components['cash_ratio'] = 10
        else:
            score_components['cash_ratio'] = 5
        
        # 3. 시장 점유율 변동성 (25점)
        volatility = market_share.get('market_volatility', 0)
        if volatility < 1:  # 낮은 변동성이 좋음 (안정적)
            score_components['stability'] = 25
        elif volatility < 2:
            score_components['stability'] = 20
        elif volatility < 3:
            score_components['stability'] = 15
        else:
            score_components['stability'] = 10
        
        # 4. 캐시 vs 총 플레이어 성과 (20점)
        multiplier = cash_analysis['cash_vs_total']['multiplier']
        if multiplier > 1.5:
            score_components['cash_performance'] = 20
        elif multiplier > 1.0:
            score_components['cash_performance'] = 15
        elif multiplier > 0.5:
            score_components['cash_performance'] = 10
        else:
            score_components['cash_performance'] = 5
        
        total_score = sum(score_components.values())
        
        # 등급 판정
        if total_score >= 85:
            grade = 'S'
            interpretation = '탁월한 캐시 카우 성과'
        elif total_score >= 70:
            grade = 'A'
            interpretation = '우수한 캐시 카우 성과'
        elif total_score >= 55:
            grade = 'B'
            interpretation = '양호한 캐시 카우 성과'
        elif total_score >= 40:
            grade = 'C'
            interpretation = '보통 수준의 성과'
        else:
            grade = 'D'
            interpretation = '개선이 필요한 성과'
        
        return {
            'total_score': total_score,
            'grade': grade,
            'interpretation': interpretation,
            'components': score_components,
            'strengths': self._identify_strengths(score_components),
            'weaknesses': self._identify_weaknesses(score_components)
        }
    
    def _generate_cash_insights(self, cash_analysis: Dict, market_share: Dict, score: Dict) -> Dict:
        """캐시 플레이어 중심 인사이트 생성"""
        insights = {
            'primary': [],
            'market_dynamics': [],
            'strategic': [],
            'warnings': []
        }
        
        # 1. 핵심 인사이트
        cash_growth = cash_analysis['cash_players']['change_pct']
        if cash_growth > 10:
            insights['primary'].append(f"💰 캐시 플레이어가 {cash_growth:.1f}% 급증하여 수익성이 크게 개선되고 있습니다")
        elif cash_growth > 5:
            insights['primary'].append(f"💵 캐시 플레이어가 {cash_growth:.1f}% 증가하여 안정적인 성장세입니다")
        elif cash_growth > 0:
            insights['primary'].append(f"💴 캐시 플레이어가 {cash_growth:.1f}% 소폭 증가했습니다")
        else:
            insights['primary'].append(f"⚠️ 캐시 플레이어가 {abs(cash_growth):.1f}% 감소하여 주의가 필요합니다")
        
        # 2. 캐시 비율 인사이트
        cash_ratio = cash_analysis['cash_ratio']['today']
        ratio_change = cash_analysis['cash_ratio']['change']
        
        if cash_ratio > 60:
            insights['primary'].append(f"🎯 캐시 비율 {cash_ratio:.1f}%로 매우 건전한 수익 구조입니다")
        elif ratio_change > 5:
            insights['primary'].append(f"📈 캐시 비율이 {ratio_change:.1f}%p 상승하여 수익성이 개선되고 있습니다")
        
        # 3. 시장 점유율 인사이트
        if market_share.get('dominant_player'):
            dominant = market_share['dominant_player']
            insights['market_dynamics'].append(
                f"👑 {dominant['site_name']}이 캐시 시장 {dominant['today_share']:.1f}%를 점유하고 있습니다"
            )
        
        # 점유율 급변 사이트
        for gainer in market_share['share_movements']['gainers'][:2]:
            insights['market_dynamics'].append(
                f"🚀 {gainer['site_name']}: 점유율 +{gainer['share_change']:.2f}%p 급증"
            )
        
        for loser in market_share['share_movements']['losers'][:2]:
            insights['warnings'].append(
                f"📉 {loser['site_name']}: 점유율 {loser['share_change']:.2f}%p 급락"
            )
        
        # 4. 전략적 인사이트
        if cash_analysis['cash_vs_total']['outperforming']:
            multiplier = cash_analysis['cash_vs_total']['multiplier']
            insights['strategic'].append(
                f"💎 캐시 게임이 전체 대비 {multiplier:.1f}배 빠르게 성장 중입니다"
            )
        
        # 5. 캐시 카우 스코어 기반 인사이트
        if score['grade'] in ['S', 'A']:
            insights['strategic'].append(f"🏆 {score['interpretation']} (Score: {score['total_score']}/100)")
        elif score['grade'] in ['D']:
            insights['warnings'].append(f"⚠️ {score['interpretation']} - 즉시 개선 필요")
        
        return insights
    
    def _evaluate_cash_ratio(self, ratio: float) -> str:
        """캐시 비율 평가"""
        if ratio >= self.thresholds['cash_ratio']['excellent']:
            return 'excellent'
        elif ratio >= self.thresholds['cash_ratio']['good']:
            return 'good'
        elif ratio >= self.thresholds['cash_ratio']['normal']:
            return 'normal'
        elif ratio >= self.thresholds['cash_ratio']['warning']:
            return 'warning'
        else:
            return 'critical'
    
    def _grade_cash_growth(self, growth: float) -> str:
        """캐시 성장률 등급"""
        if growth >= self.thresholds['cash_growth']['explosive']:
            return '🔥 폭발적'
        elif growth >= self.thresholds['cash_growth']['strong']:
            return '💪 강력'
        elif growth >= self.thresholds['cash_growth']['moderate']:
            return '📈 적당'
        elif growth >= self.thresholds['cash_growth']['weak']:
            return '➡️ 미약'
        else:
            return '📉 감소'
    
    def _classify_share_trend(self, change: float) -> str:
        """시장 점유율 변화 분류"""
        if change >= self.thresholds['market_share_change']['surge']:
            return '🚀 급증'
        elif change >= self.thresholds['market_share_change']['growth']:
            return '📈 성장'
        elif change >= self.thresholds['market_share_change']['stable']:
            return '➡️ 안정'
        elif change >= self.thresholds['market_share_change']['decline']:
            return '📉 하락'
        else:
            return '⬇️ 급락'
    
    def _interpret_cash_performance(self, multiplier: float) -> str:
        """캐시 vs 총 플레이어 성과 해석"""
        if multiplier > 2:
            return '캐시 게임 집중도 매우 높음'
        elif multiplier > 1.5:
            return '캐시 게임 선호도 상승'
        elif multiplier > 1:
            return '캐시 게임 비중 증가'
        elif multiplier > 0.5:
            return '균형적 성장'
        else:
            return '토너먼트 비중 증가'
    
    def _calculate_market_volatility(self, site_shares: List[Dict]) -> float:
        """시장 변동성 계산"""
        if not site_shares:
            return 0
        
        changes = [abs(s['share_change']) for s in site_shares]
        return np.mean(changes) if changes else 0
    
    def _identify_strengths(self, components: Dict) -> List[str]:
        """강점 식별"""
        strengths = []
        
        if components.get('cash_growth', 0) >= 25:
            strengths.append('캐시 플레이어 고성장')
        if components.get('cash_ratio', 0) >= 20:
            strengths.append('건전한 캐시 비율')
        if components.get('stability', 0) >= 20:
            strengths.append('안정적 시장 구조')
        if components.get('cash_performance', 0) >= 15:
            strengths.append('캐시 게임 우수 성과')
        
        return strengths
    
    def _identify_weaknesses(self, components: Dict) -> List[str]:
        """약점 식별"""
        weaknesses = []
        
        if components.get('cash_growth', 0) < 15:
            weaknesses.append('캐시 성장률 부진')
        if components.get('cash_ratio', 0) < 15:
            weaknesses.append('낮은 캐시 비율')
        if components.get('stability', 0) < 15:
            weaknesses.append('높은 시장 변동성')
        if components.get('cash_performance', 0) < 10:
            weaknesses.append('캐시 게임 성과 미흡')
        
        return weaknesses
    
    def generate_cash_cow_report(self, analysis_result: Dict) -> str:
        """캐시 카우 리포트 생성"""
        cash = analysis_result['cash_analysis']
        market = analysis_result['market_share_analysis']
        score = analysis_result['cash_cow_score']
        insights = analysis_result['insights']
        
        report = f"""
================================================================================
💰 캐시 카우 모델 분석 리포트
================================================================================
📅 분석 기간: {analysis_result['period']}
⏰ 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 캐시 카우 스코어: {score['total_score']}/100 (등급: {score['grade']})
{score['interpretation']}

================================================================================
1️⃣ 캐시 플레이어 핵심 지표
================================================================================
• 캐시 플레이어 수: {cash['cash_players']['yesterday']:,} → {cash['cash_players']['today']:,}
• 변화: {cash['cash_players']['change']:+,}명 ({cash['cash_players']['change_pct']:+.1f}%)
• 성장 등급: {cash['cash_growth_grade']}

• 캐시 비율: {cash['cash_ratio']['yesterday']:.1f}% → {cash['cash_ratio']['today']:.1f}%
• 비율 변화: {cash['cash_ratio']['change']:+.1f}%p
• 품질 평가: {cash['cash_ratio']['quality']}

• 캐시 vs 총 플레이어: {cash['cash_vs_total']['multiplier']:.1f}배
• 성과: {cash['cash_vs_total']['interpretation']}

================================================================================
2️⃣ 시장 점유율 분석 (캐시 플레이어 기준)
================================================================================
🏆 Top 5 점유율 변화
"""
        
        for i, site in enumerate(market['site_shares'][:5], 1):
            report += f"""
{i}. {site['site_name']}
   점유율: {site['yesterday_share']:.2f}% → {site['today_share']:.2f}%
   변화: {site['share_change']:+.2f}%p {site['trend']}
"""
        
        report += f"""
• 상위 3개 집중도: {market['top3_concentration']:.1f}%
• 시장 변동성: {market['market_volatility']:.2f}

================================================================================
3️⃣ 핵심 인사이트
================================================================================
"""
        
        for insight in insights['primary']:
            report += f"• {insight}\n"
        
        if insights['market_dynamics']:
            report += "\n📊 시장 역학:\n"
            for insight in insights['market_dynamics']:
                report += f"• {insight}\n"
        
        if insights['strategic']:
            report += "\n💡 전략적 시사점:\n"
            for insight in insights['strategic']:
                report += f"• {insight}\n"
        
        if insights['warnings']:
            report += "\n⚠️ 주의 사항:\n"
            for warning in insights['warnings']:
                report += f"• {warning}\n"
        
        report += f"""
================================================================================
4️⃣ 스코어 상세
================================================================================
• 캐시 성장률: {score['components']['cash_growth']}/30점
• 캐시 비율: {score['components']['cash_ratio']}/25점
• 시장 안정성: {score['components']['stability']}/25점
• 캐시 성과: {score['components']['cash_performance']}/20점

강점: {', '.join(score['strengths']) if score['strengths'] else '없음'}
약점: {', '.join(score['weaknesses']) if score['weaknesses'] else '없음'}
================================================================================
"""
        
        return report

def main():
    print("💰 캐시 카우 모델 분석 시스템")
    print("=" * 60)
    print("핵심: 캐시 플레이어 수와 시장 점유율 변화에 집중")
    print("=" * 60)
    
    analyzer = CashPlayerAnalyzer()
    
    try:
        # 캐시 중심 분석 실행
        print("\n📊 캐시 플레이어 중심 분석 실행 중...")
        result = analyzer.analyze_cash_focused_daily()
        
        # 리포트 생성
        report = analyzer.generate_cash_cow_report(result)
        print(report)
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"cash_cow_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 분석 결과 저장: {output_file}")
        
    except Exception as e:
        logger.error(f"분석 실행 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()