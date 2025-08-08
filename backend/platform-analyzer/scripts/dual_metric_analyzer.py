#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual Metric Analyzer
총 온라인 플레이어 & 캐시 플레이어 통합 분석 시스템
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

class DualMetricAnalyzer:
    """
    이중 지표 분석 엔진
    - 총 온라인 플레이어: 시장 규모와 성장성
    - 캐시 플레이어: 수익성과 실질 가치 (캐시 카우)
    - 시장 점유율: 경쟁 포지션과 트렌드
    """
    
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.base_analyzer = MultiPeriodAnalyzer(db_path)
        
        # 이중 지표 임계값
        self.thresholds = {
            'growth': {  # 성장률 기준
                'explosive': 15,    # 폭발적
                'strong': 10,       # 강력
                'good': 5,          # 양호
                'stable': 0,        # 안정
                'decline': -5       # 감소
            },
            'cash_ratio': {  # 캐시 비율 (캐시/총)
                'excellent': 0.55,  # 55% 이상 - 매우 건전
                'good': 0.45,       # 45% 이상 - 건전
                'normal': 0.35,     # 35% 이상 - 보통
                'low': 0.25         # 25% 이상 - 낮음
            },
            'market_share': {  # 점유율 변화
                'dominant_change': 3.0,   # 지배적 변화
                'significant': 1.5,       # 중요 변화
                'moderate': 0.5,          # 보통 변화
                'minimal': 0.1            # 미미한 변화
            }
        }
    
    def analyze_dual_metrics_daily(self, target_date: str = None) -> Dict:
        """총 온라인 & 캐시 플레이어 통합 일일 분석"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"🎯 이중 지표 일일 분석: {target_date}")
        
        # 기본 데이터 수집
        base_result = self.base_analyzer.daily_comparison_analysis(target_date)
        
        # 총 온라인 플레이어 분석
        online_analysis = self._analyze_online_players(base_result)
        
        # 캐시 플레이어 분석
        cash_analysis = self._analyze_cash_players(base_result)
        
        # 이중 지표 상관 분석
        correlation_analysis = self._analyze_correlation(online_analysis, cash_analysis)
        
        # 시장 점유율 분석 (두 지표 모두)
        market_share = self._analyze_dual_market_share(base_result)
        
        # 종합 평가
        comprehensive_score = self._calculate_comprehensive_score(
            online_analysis, cash_analysis, correlation_analysis, market_share
        )
        
        return {
            'analysis_type': 'dual_metrics_daily',
            'period': base_result['period'],
            'online_players': online_analysis,
            'cash_players': cash_analysis,
            'correlation': correlation_analysis,
            'market_share': market_share,
            'comprehensive_score': comprehensive_score,
            'insights': self._generate_dual_insights(
                online_analysis, cash_analysis, correlation_analysis, market_share, comprehensive_score
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_online_players(self, base_result: Dict) -> Dict:
        """총 온라인 플레이어 분석"""
        changes = base_result['changes']
        yesterday = base_result['yesterday']['summary']
        today = base_result['today']['summary']
        
        online_change = changes.get('total_players', {})
        avg_change = changes.get('avg_players', {})
        
        # 성장률 등급 판정
        growth_grade = self._grade_growth(online_change.get('change_pct', 0))
        
        # 시장 규모 평가
        market_size = today.get('total_players', 0)
        size_category = self._categorize_market_size(market_size)
        
        return {
            'metrics': {
                'total': {
                    'yesterday': yesterday.get('total_players', 0),
                    'today': today.get('total_players', 0),
                    'change': online_change.get('change', 0),
                    'change_pct': online_change.get('change_pct', 0)
                },
                'average': {
                    'yesterday': yesterday.get('avg_players', 0),
                    'today': today.get('avg_players', 0),
                    'change': avg_change.get('change', 0),
                    'change_pct': avg_change.get('change_pct', 0)
                }
            },
            'growth_grade': growth_grade,
            'market_size': size_category,
            'trend': self._determine_trend(online_change.get('change_pct', 0))
        }
    
    def _analyze_cash_players(self, base_result: Dict) -> Dict:
        """캐시 플레이어 분석"""
        changes = base_result['changes']
        yesterday = base_result['yesterday']['summary']
        today = base_result['today']['summary']
        
        cash_change = changes.get('total_cash_players', {})
        cash_avg_change = changes.get('avg_cash_players', {})
        
        # 캐시 비율 계산
        yesterday_ratio = (
            yesterday.get('total_cash_players', 0) / yesterday.get('total_players', 1)
            if yesterday.get('total_players', 0) > 0 else 0
        )
        today_ratio = (
            today.get('total_cash_players', 0) / today.get('total_players', 1)
            if today.get('total_players', 0) > 0 else 0
        )
        
        # 캐시 비율 품질 평가
        ratio_quality = self._evaluate_cash_ratio(today_ratio)
        
        return {
            'metrics': {
                'total': {
                    'yesterday': yesterday.get('total_cash_players', 0),
                    'today': today.get('total_cash_players', 0),
                    'change': cash_change.get('change', 0),
                    'change_pct': cash_change.get('change_pct', 0)
                },
                'average': {
                    'yesterday': yesterday.get('avg_cash_players', 0),
                    'today': today.get('avg_cash_players', 0),
                    'change': cash_avg_change.get('change', 0),
                    'change_pct': cash_avg_change.get('change_pct', 0)
                }
            },
            'cash_ratio': {
                'yesterday': yesterday_ratio * 100,
                'today': today_ratio * 100,
                'change': (today_ratio - yesterday_ratio) * 100,
                'quality': ratio_quality
            },
            'growth_grade': self._grade_growth(cash_change.get('change_pct', 0)),
            'revenue_potential': self._assess_revenue_potential(today_ratio, cash_change.get('change_pct', 0))
        }
    
    def _analyze_correlation(self, online: Dict, cash: Dict) -> Dict:
        """온라인 vs 캐시 상관관계 분석"""
        online_growth = online['metrics']['total']['change_pct']
        cash_growth = cash['metrics']['total']['change_pct']
        
        # 성장률 배수
        if online_growth != 0:
            growth_multiplier = cash_growth / online_growth
        else:
            growth_multiplier = float('inf') if cash_growth > 0 else 0
        
        # 상관관계 패턴 분석
        if cash_growth > online_growth + 5:
            pattern = 'cash_dominant'
            interpretation = '캐시 게임 강세 (수익성 개선)'
        elif cash_growth > online_growth:
            pattern = 'cash_leading'
            interpretation = '캐시 게임 선호 증가'
        elif abs(cash_growth - online_growth) < 2:
            pattern = 'balanced'
            interpretation = '균형적 성장'
        elif online_growth > cash_growth + 5:
            pattern = 'tournament_dominant'
            interpretation = '토너먼트 강세 (신규 유저 유입)'
        else:
            pattern = 'tournament_leading'
            interpretation = '토너먼트 선호 증가'
        
        # 건전성 지수 (캐시 비율 × 성장 균형)
        health_index = self._calculate_health_index(
            cash['cash_ratio']['today'],
            growth_multiplier
        )
        
        return {
            'growth_multiplier': growth_multiplier,
            'pattern': pattern,
            'interpretation': interpretation,
            'health_index': health_index,
            'sync_level': self._evaluate_sync(online_growth, cash_growth)
        }
    
    def _analyze_dual_market_share(self, base_result: Dict) -> Dict:
        """이중 지표 기반 시장 점유율 분석"""
        site_comparison = base_result.get('site_comparison', {})
        
        # 데이터 추출
        yesterday_data = base_result.get('yesterday_data', [])
        today_data = base_result.get('today_data', [])
        
        # 총 합계 계산
        yesterday_total_online = sum(d.get('players_online', 0) for d in yesterday_data) or 1
        today_total_online = sum(d.get('players_online', 0) for d in today_data) or 1
        yesterday_total_cash = sum(d.get('cash_players', 0) for d in yesterday_data) or 1
        today_total_cash = sum(d.get('cash_players', 0) for d in today_data) or 1
        
        # 사이트별 이중 점유율 계산
        dual_shares = []
        
        for site in site_comparison.get('all_changes', [])[:10]:
            site_name = site['site_name']
            
            # 온라인 점유율
            yesterday_online = next(
                (d['players_online'] for d in yesterday_data if d.get('site_name') == site_name), 0
            )
            today_online = next(
                (d['players_online'] for d in today_data if d.get('site_name') == site_name), 0
            )
            
            yesterday_online_share = (yesterday_online / yesterday_total_online) * 100
            today_online_share = (today_online / today_total_online) * 100
            online_share_change = today_online_share - yesterday_online_share
            
            # 캐시 점유율
            yesterday_cash = next(
                (d['cash_players'] for d in yesterday_data if d.get('site_name') == site_name), 0
            )
            today_cash = next(
                (d['cash_players'] for d in today_data if d.get('site_name') == site_name), 0
            )
            
            yesterday_cash_share = (yesterday_cash / yesterday_total_cash) * 100
            today_cash_share = (today_cash / today_total_cash) * 100
            cash_share_change = today_cash_share - yesterday_cash_share
            
            # 종합 점유율 점수 (온라인 40% + 캐시 60% 가중치)
            composite_share = (today_online_share * 0.4) + (today_cash_share * 0.6)
            composite_change = (online_share_change * 0.4) + (cash_share_change * 0.6)
            
            dual_shares.append({
                'site_name': site_name,
                'online_share': {
                    'yesterday': yesterday_online_share,
                    'today': today_online_share,
                    'change': online_share_change
                },
                'cash_share': {
                    'yesterday': yesterday_cash_share,
                    'today': today_cash_share,
                    'change': cash_share_change
                },
                'composite_share': composite_share,
                'composite_change': composite_change,
                'trend': self._classify_share_trend(composite_change)
            })
        
        # 종합 점유율 변화 기준 정렬
        dual_shares.sort(key=lambda x: abs(x['composite_change']), reverse=True)
        
        # 상위 3개 집중도 (이중 지표)
        top3_online = sum(s['online_share']['today'] for s in dual_shares[:3])
        top3_cash = sum(s['cash_share']['today'] for s in dual_shares[:3])
        
        return {
            'dual_shares': dual_shares[:5],
            'top3_concentration': {
                'online': top3_online,
                'cash': top3_cash,
                'composite': (top3_online * 0.4) + (top3_cash * 0.6)
            },
            'market_leaders': {
                'online': max(dual_shares, key=lambda x: x['online_share']['today']) if dual_shares else None,
                'cash': max(dual_shares, key=lambda x: x['cash_share']['today']) if dual_shares else None,
                'composite': dual_shares[0] if dual_shares else None
            },
            'movers': {
                'online_gainers': sorted([s for s in dual_shares if s['online_share']['change'] > 0.5], 
                                        key=lambda x: x['online_share']['change'], reverse=True)[:3],
                'cash_gainers': sorted([s for s in dual_shares if s['cash_share']['change'] > 0.5],
                                      key=lambda x: x['cash_share']['change'], reverse=True)[:3],
                'online_losers': sorted([s for s in dual_shares if s['online_share']['change'] < -0.5],
                                       key=lambda x: x['online_share']['change'])[:3],
                'cash_losers': sorted([s for s in dual_shares if s['cash_share']['change'] < -0.5],
                                     key=lambda x: x['cash_share']['change'])[:3]
            }
        }
    
    def _calculate_comprehensive_score(self, online: Dict, cash: Dict, 
                                      correlation: Dict, market_share: Dict) -> Dict:
        """종합 평가 스코어 (200점 만점 - 온라인 100점 + 캐시 100점)"""
        scores = {}
        
        # 1. 온라인 플레이어 부문 (100점)
        online_growth = online['metrics']['total']['change_pct']
        if online_growth >= 15:
            scores['online_growth'] = 40
        elif online_growth >= 10:
            scores['online_growth'] = 35
        elif online_growth >= 5:
            scores['online_growth'] = 30
        elif online_growth >= 0:
            scores['online_growth'] = 25
        else:
            scores['online_growth'] = max(0, 25 + online_growth * 2)
        
        # 시장 규모 보너스
        if online['market_size'] == 'massive':
            scores['market_size'] = 10
        elif online['market_size'] == 'large':
            scores['market_size'] = 8
        elif online['market_size'] == 'medium':
            scores['market_size'] = 6
        else:
            scores['market_size'] = 4
        
        # 2. 캐시 플레이어 부문 (100점)
        cash_growth = cash['metrics']['total']['change_pct']
        if cash_growth >= 15:
            scores['cash_growth'] = 40
        elif cash_growth >= 10:
            scores['cash_growth'] = 35
        elif cash_growth >= 5:
            scores['cash_growth'] = 30
        elif cash_growth >= 0:
            scores['cash_growth'] = 25
        else:
            scores['cash_growth'] = max(0, 25 + cash_growth * 2)
        
        # 캐시 비율 품질
        cash_ratio = cash['cash_ratio']['today']
        if cash_ratio >= 55:
            scores['cash_ratio'] = 10
        elif cash_ratio >= 45:
            scores['cash_ratio'] = 8
        elif cash_ratio >= 35:
            scores['cash_ratio'] = 6
        else:
            scores['cash_ratio'] = 4
        
        # 3. 상관관계 보너스 (각 부문 25점씩)
        if correlation['pattern'] in ['balanced', 'cash_leading']:
            scores['online_correlation'] = 25
            scores['cash_correlation'] = 25
        elif correlation['pattern'] == 'cash_dominant':
            scores['online_correlation'] = 20
            scores['cash_correlation'] = 30
        elif correlation['pattern'] == 'tournament_dominant':
            scores['online_correlation'] = 30
            scores['cash_correlation'] = 20
        else:
            scores['online_correlation'] = 22
            scores['cash_correlation'] = 22
        
        # 4. 시장 점유율 안정성 (각 부문 25점씩)
        concentration = market_share['top3_concentration']['composite']
        if 40 <= concentration <= 60:  # 적정 집중도
            scores['online_market'] = 25
            scores['cash_market'] = 25
        elif concentration < 40:  # 너무 분산
            scores['online_market'] = 20
            scores['cash_market'] = 20
        else:  # 너무 집중
            scores['online_market'] = 15
            scores['cash_market'] = 15
        
        # 부문별 점수 계산
        online_score = (scores.get('online_growth', 0) + scores.get('market_size', 0) +
                       scores.get('online_correlation', 0) + scores.get('online_market', 0))
        
        cash_score = (scores.get('cash_growth', 0) + scores.get('cash_ratio', 0) +
                     scores.get('cash_correlation', 0) + scores.get('cash_market', 0))
        
        total_score = online_score + cash_score
        
        # 등급 판정
        if total_score >= 170:
            grade = 'S'
            interpretation = '탁월한 종합 성과'
        elif total_score >= 140:
            grade = 'A'
            interpretation = '우수한 종합 성과'
        elif total_score >= 110:
            grade = 'B'
            interpretation = '양호한 종합 성과'
        elif total_score >= 80:
            grade = 'C'
            interpretation = '보통 수준의 성과'
        else:
            grade = 'D'
            interpretation = '개선이 필요한 성과'
        
        return {
            'total_score': total_score,
            'online_score': online_score,
            'cash_score': cash_score,
            'grade': grade,
            'interpretation': interpretation,
            'score_details': scores,
            'balance_ratio': cash_score / online_score if online_score > 0 else 0
        }
    
    def _generate_dual_insights(self, online: Dict, cash: Dict, correlation: Dict,
                               market_share: Dict, score: Dict) -> Dict:
        """이중 지표 기반 인사이트 생성"""
        insights = {
            'online_insights': [],
            'cash_insights': [],
            'correlation_insights': [],
            'market_insights': [],
            'strategic_insights': []
        }
        
        # 1. 온라인 플레이어 인사이트
        online_growth = online['metrics']['total']['change_pct']
        if online_growth > 10:
            insights['online_insights'].append(
                f"🚀 총 온라인 플레이어가 {online_growth:.1f}% 급증, 시장 확장세"
            )
        elif online_growth > 5:
            insights['online_insights'].append(
                f"📈 총 온라인 플레이어 {online_growth:.1f}% 증가, 안정적 성장"
            )
        elif online_growth > 0:
            insights['online_insights'].append(
                f"➡️ 총 온라인 플레이어 {online_growth:.1f}% 소폭 증가"
            )
        else:
            insights['online_insights'].append(
                f"📉 총 온라인 플레이어 {abs(online_growth):.1f}% 감소, 시장 위축"
            )
        
        # 2. 캐시 플레이어 인사이트
        cash_growth = cash['metrics']['total']['change_pct']
        cash_ratio = cash['cash_ratio']['today']
        
        if cash_growth > 10:
            insights['cash_insights'].append(
                f"💰 캐시 플레이어 {cash_growth:.1f}% 급증, 수익성 크게 개선"
            )
        elif cash_growth > 5:
            insights['cash_insights'].append(
                f"💵 캐시 플레이어 {cash_growth:.1f}% 증가, 수익 기반 강화"
            )
        
        if cash_ratio > 50:
            insights['cash_insights'].append(
                f"🎯 캐시 비율 {cash_ratio:.1f}%로 매우 건전한 수익 구조"
            )
        elif cash['cash_ratio']['change'] > 3:
            insights['cash_insights'].append(
                f"📈 캐시 비율 {cash['cash_ratio']['change']:.1f}%p 상승, 수익성 개선"
            )
        
        # 3. 상관관계 인사이트
        insights['correlation_insights'].append(
            f"🔄 {correlation['interpretation']}"
        )
        
        if correlation['growth_multiplier'] > 1.5:
            insights['correlation_insights'].append(
                f"💎 캐시 게임이 전체 대비 {correlation['growth_multiplier']:.1f}배 빠른 성장"
            )
        
        # 4. 시장 점유율 인사이트
        if market_share['market_leaders']['composite']:
            leader = market_share['market_leaders']['composite']
            insights['market_insights'].append(
                f"👑 {leader['site_name']}이 종합 점유율 {leader['composite_share']:.1f}% 차지"
            )
        
        # 급변 사이트
        if market_share['movers']['cash_gainers']:
            top_gainer = market_share['movers']['cash_gainers'][0]
            insights['market_insights'].append(
                f"🚀 {top_gainer['site_name']}: 캐시 점유율 +{top_gainer['cash_share']['change']:.1f}%p"
            )
        
        # 5. 전략적 인사이트
        balance_ratio = score['balance_ratio']
        if 0.8 <= balance_ratio <= 1.2:
            insights['strategic_insights'].append(
                "⚖️ 온라인과 캐시 성과가 균형적으로 발전 중"
            )
        elif balance_ratio > 1.2:
            insights['strategic_insights'].append(
                "💰 캐시 게임 중심의 성장 전략이 효과적"
            )
        else:
            insights['strategic_insights'].append(
                "🎮 신규 유저 유입 중심의 성장 전략 실행 중"
            )
        
        # 종합 평가
        insights['strategic_insights'].append(
            f"🏆 {score['interpretation']} (종합점수: {score['total_score']}/200)"
        )
        
        return insights
    
    # 헬퍼 메서드들
    def _grade_growth(self, growth_pct: float) -> str:
        if growth_pct >= self.thresholds['growth']['explosive']:
            return '🔥 폭발적'
        elif growth_pct >= self.thresholds['growth']['strong']:
            return '💪 강력'
        elif growth_pct >= self.thresholds['growth']['good']:
            return '📈 양호'
        elif growth_pct >= self.thresholds['growth']['stable']:
            return '➡️ 안정'
        else:
            return '📉 감소'
    
    def _categorize_market_size(self, total_players: int) -> str:
        if total_players >= 500000:
            return 'massive'
        elif total_players >= 200000:
            return 'large'
        elif total_players >= 100000:
            return 'medium'
        else:
            return 'small'
    
    def _determine_trend(self, change_pct: float) -> str:
        if change_pct > 10:
            return 'strong_uptrend'
        elif change_pct > 3:
            return 'uptrend'
        elif change_pct > -3:
            return 'sideways'
        elif change_pct > -10:
            return 'downtrend'
        else:
            return 'strong_downtrend'
    
    def _evaluate_cash_ratio(self, ratio: float) -> str:
        if ratio >= self.thresholds['cash_ratio']['excellent']:
            return 'excellent'
        elif ratio >= self.thresholds['cash_ratio']['good']:
            return 'good'
        elif ratio >= self.thresholds['cash_ratio']['normal']:
            return 'normal'
        elif ratio >= self.thresholds['cash_ratio']['low']:
            return 'low'
        else:
            return 'critical'
    
    def _assess_revenue_potential(self, cash_ratio: float, growth: float) -> str:
        score = (cash_ratio * 100) + (growth * 2)
        
        if score >= 80:
            return '매우 높음'
        elif score >= 60:
            return '높음'
        elif score >= 40:
            return '보통'
        elif score >= 20:
            return '낮음'
        else:
            return '매우 낮음'
    
    def _calculate_health_index(self, cash_ratio: float, multiplier: float) -> float:
        # 캐시 비율(50%)과 성장 균형(50%)을 고려한 건전성
        ratio_score = min(cash_ratio / 50 * 50, 50)  # 최대 50점
        balance_score = 50 - abs(1 - multiplier) * 25  # 균형에 가까울수록 높음
        return max(0, min(100, ratio_score + balance_score))
    
    def _evaluate_sync(self, online_growth: float, cash_growth: float) -> str:
        diff = abs(online_growth - cash_growth)
        
        if diff < 2:
            return '매우 동조'
        elif diff < 5:
            return '동조'
        elif diff < 10:
            return '부분 동조'
        else:
            return '비동조'
    
    def _classify_share_trend(self, change: float) -> str:
        abs_change = abs(change)
        
        if abs_change >= self.thresholds['market_share']['dominant_change']:
            return '🚀 지배적' if change > 0 else '⬇️ 급락'
        elif abs_change >= self.thresholds['market_share']['significant']:
            return '📈 중요' if change > 0 else '📉 하락'
        elif abs_change >= self.thresholds['market_share']['moderate']:
            return '↗️ 상승' if change > 0 else '↘️ 감소'
        elif abs_change >= self.thresholds['market_share']['minimal']:
            return '→ 유지' if change > 0 else '← 미세감소'
        else:
            return '━ 불변'

def main():
    print("🎯 이중 지표 분석 시스템")
    print("=" * 60)
    print("총 온라인 플레이어 & 캐시 플레이어 통합 분석")
    print("=" * 60)
    
    analyzer = DualMetricAnalyzer()
    
    try:
        # 이중 지표 분석 실행
        print("\n📊 이중 지표 일일 분석 실행 중...")
        result = analyzer.analyze_dual_metrics_daily()
        
        # 결과 출력
        print("\n" + "=" * 80)
        print("🎯 이중 지표 분석 결과")
        print("=" * 80)
        
        # 종합 점수
        score = result['comprehensive_score']
        print(f"\n🏆 종합 평가: {score['grade']}등급 - {score['interpretation']}")
        print(f"   총점: {score['total_score']}/200")
        print(f"   온라인 부문: {score['online_score']}/100")
        print(f"   캐시 부문: {score['cash_score']}/100")
        
        # 온라인 플레이어
        online = result['online_players']
        print(f"\n📊 총 온라인 플레이어")
        print(f"   {online['metrics']['total']['yesterday']:,} → {online['metrics']['total']['today']:,}")
        print(f"   변화: {online['metrics']['total']['change']:+,}명 ({online['metrics']['total']['change_pct']:+.1f}%)")
        print(f"   등급: {online['growth_grade']}")
        
        # 캐시 플레이어
        cash = result['cash_players']
        print(f"\n💰 캐시 플레이어")
        print(f"   {cash['metrics']['total']['yesterday']:,} → {cash['metrics']['total']['today']:,}")
        print(f"   변화: {cash['metrics']['total']['change']:+,}명 ({cash['metrics']['total']['change_pct']:+.1f}%)")
        print(f"   캐시 비율: {cash['cash_ratio']['today']:.1f}% ({cash['cash_ratio']['quality']})")
        
        # 상관관계
        correlation = result['correlation']
        print(f"\n🔄 상관관계")
        print(f"   패턴: {correlation['interpretation']}")
        print(f"   성장 배수: {correlation['growth_multiplier']:.1f}배")
        print(f"   건전성 지수: {correlation['health_index']:.1f}/100")
        
        # 인사이트
        insights = result['insights']
        print(f"\n💡 주요 인사이트")
        
        for category, items in insights.items():
            if items:
                print(f"\n{category.replace('_', ' ').title()}:")
                for insight in items[:2]:
                    print(f"  • {insight}")
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"dual_metric_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 분석 결과 저장: {output_file}")
        
    except Exception as e:
        logger.error(f"분석 실행 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()