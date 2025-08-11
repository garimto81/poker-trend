#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Dual Metric Analyzer with Top Sites
온라인/캐시 TOP 3 사이트 및 트렌드 분석 강화
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

class EnhancedDualMetricAnalyzer:
    """
    강화된 이중 지표 분석 엔진
    - 온라인 TOP 3 사이트
    - 캐시 TOP 3 사이트
    - 전날 대비 상세 변화량
    - 트렌드 분석
    """
    
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.base_analyzer = MultiPeriodAnalyzer(db_path)
        
    def analyze_enhanced_daily(self, target_date: str = None) -> Dict:
        """강화된 일일 분석"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"🎯 강화된 이중 지표 일일 분석: {target_date}")
        
        # 기본 데이터 수집
        base_result = self.base_analyzer.daily_comparison_analysis(target_date)
        
        # TOP 3 사이트 분석
        top_sites = self._analyze_top_sites(base_result)
        
        # 전날 대비 변화 분석
        daily_changes = self._analyze_daily_changes(base_result)
        
        # 트렌드 분석
        trend_analysis = self._analyze_trends(base_result)
        
        # 종합 스코어
        comprehensive_score = self._calculate_comprehensive_score(
            top_sites, daily_changes, trend_analysis
        )
        
        return {
            'analysis_type': 'enhanced_dual_metrics',
            'period': base_result['period'],
            'top_sites': top_sites,
            'daily_changes': daily_changes,
            'trend_analysis': trend_analysis,
            'comprehensive_score': comprehensive_score,
            'insights': self._generate_enhanced_insights(
                top_sites, daily_changes, trend_analysis
            ),
            'raw_data': {
                'yesterday': base_result.get('yesterday_data', []),
                'today': base_result.get('today_data', [])
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_top_sites(self, base_result: Dict) -> Dict:
        """TOP 3 사이트 분석"""
        # yesterday_data와 today_data 직접 조회
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        yesterday_date = base_result.get('yesterday', {}).get('date', '')
        today_date = base_result.get('today', {}).get('date', '')
        
        # 어제 데이터
        cursor.execute("""
            SELECT site_name, players_online, cash_players 
            FROM daily_data 
            WHERE date = ?
        """, (yesterday_date,))
        yesterday_data = [
            {'site_name': row[0], 'players_online': row[1], 'cash_players': row[2]}
            for row in cursor.fetchall()
        ]
        
        # 오늘 데이터
        cursor.execute("""
            SELECT site_name, players_online, cash_players 
            FROM daily_data 
            WHERE date = ?
        """, (today_date,))
        today_data = [
            {'site_name': row[0], 'players_online': row[1], 'cash_players': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # 온라인 플레이어 TOP 3
        online_top3_today = sorted(
            today_data, 
            key=lambda x: x.get('players_online', 0), 
            reverse=True
        )[:3]
        
        online_top3_yesterday = sorted(
            yesterday_data,
            key=lambda x: x.get('players_online', 0),
            reverse=True
        )[:3]
        
        # 캐시 플레이어 TOP 3
        cash_top3_today = sorted(
            today_data,
            key=lambda x: x.get('cash_players', 0),
            reverse=True
        )[:3]
        
        cash_top3_yesterday = sorted(
            yesterday_data,
            key=lambda x: x.get('cash_players', 0),
            reverse=True
        )[:3]
        
        # TOP 3 분석 결과
        online_top3_analysis = []
        for i, site in enumerate(online_top3_today):
            site_name = site.get('site_name', 'Unknown')
            today_players = site.get('players_online', 0)
            
            # 어제 데이터 찾기
            yesterday_site = next(
                (s for s in yesterday_data if s.get('site_name') == site_name),
                None
            )
            yesterday_players = yesterday_site.get('players_online', 0) if yesterday_site else 0
            
            change = today_players - yesterday_players
            change_pct = (change / yesterday_players * 100) if yesterday_players > 0 else 0
            
            # 순위 변동
            yesterday_rank = next(
                (idx + 1 for idx, s in enumerate(online_top3_yesterday) 
                 if s.get('site_name') == site_name),
                99
            )
            rank_change = yesterday_rank - (i + 1)
            
            online_top3_analysis.append({
                'rank': i + 1,
                'site_name': site_name,
                'players_today': today_players,
                'players_yesterday': yesterday_players,
                'change': change,
                'change_pct': change_pct,
                'rank_change': rank_change,
                'trend': self._get_trend(change_pct)
            })
        
        # 캐시 TOP 3 분석
        cash_top3_analysis = []
        for i, site in enumerate(cash_top3_today):
            site_name = site.get('site_name', 'Unknown')
            today_cash = site.get('cash_players', 0)
            
            yesterday_site = next(
                (s for s in yesterday_data if s.get('site_name') == site_name),
                None
            )
            yesterday_cash = yesterday_site.get('cash_players', 0) if yesterday_site else 0
            
            change = today_cash - yesterday_cash
            change_pct = (change / yesterday_cash * 100) if yesterday_cash > 0 else 0
            
            yesterday_rank = next(
                (idx + 1 for idx, s in enumerate(cash_top3_yesterday)
                 if s.get('site_name') == site_name),
                99
            )
            rank_change = yesterday_rank - (i + 1)
            
            cash_top3_analysis.append({
                'rank': i + 1,
                'site_name': site_name,
                'cash_today': today_cash,
                'cash_yesterday': yesterday_cash,
                'change': change,
                'change_pct': change_pct,
                'rank_change': rank_change,
                'trend': self._get_trend(change_pct)
            })
        
        return {
            'online_top3': online_top3_analysis,
            'cash_top3': cash_top3_analysis,
            'online_leader': online_top3_analysis[0] if online_top3_analysis else None,
            'cash_leader': cash_top3_analysis[0] if cash_top3_analysis else None
        }
    
    def _analyze_daily_changes(self, base_result: Dict) -> Dict:
        """전날 대비 상세 변화 분석"""
        changes = base_result.get('changes', {})
        yesterday = base_result.get('yesterday', {}).get('summary', {})
        today = base_result.get('today', {}).get('summary', {})
        
        # 전체 시장 변화
        market_changes = {
            'total_online': {
                'yesterday': yesterday.get('total_players', 0),
                'today': today.get('total_players', 0),
                'change': changes.get('total_players', {}).get('change', 0),
                'change_pct': changes.get('total_players', {}).get('change_pct', 0),
                'trend': self._get_trend(changes.get('total_players', {}).get('change_pct', 0))
            },
            'total_cash': {
                'yesterday': yesterday.get('total_cash_players', 0),
                'today': today.get('total_cash_players', 0),
                'change': changes.get('total_cash_players', {}).get('change', 0),
                'change_pct': changes.get('total_cash_players', {}).get('change_pct', 0),
                'trend': self._get_trend(changes.get('total_cash_players', {}).get('change_pct', 0))
            },
            'avg_online': {
                'yesterday': yesterday.get('avg_players', 0),
                'today': today.get('avg_players', 0),
                'change': changes.get('avg_players', {}).get('change', 0),
                'change_pct': changes.get('avg_players', {}).get('change_pct', 0)
            },
            'avg_cash': {
                'yesterday': yesterday.get('avg_cash_players', 0),
                'today': today.get('avg_cash_players', 0),
                'change': changes.get('avg_cash_players', {}).get('change', 0),
                'change_pct': changes.get('avg_cash_players', {}).get('change_pct', 0)
            }
        }
        
        # 캐시 비율 변화
        yesterday_cash_ratio = (
            yesterday.get('total_cash_players', 0) / yesterday.get('total_players', 1)
            if yesterday.get('total_players', 0) > 0 else 0
        )
        today_cash_ratio = (
            today.get('total_cash_players', 0) / today.get('total_players', 1)
            if today.get('total_players', 0) > 0 else 0
        )
        
        cash_ratio_change = {
            'yesterday': yesterday_cash_ratio * 100,
            'today': today_cash_ratio * 100,
            'change': (today_cash_ratio - yesterday_cash_ratio) * 100,
            'trend': 'improving' if today_cash_ratio > yesterday_cash_ratio else 'declining'
        }
        
        # 최대 변동 사이트
        site_changes = base_result.get('site_comparison', {})
        top_gainers = site_changes.get('top_gainers', [])[:5]
        top_losers = site_changes.get('top_losers', [])[:5]
        
        return {
            'market_changes': market_changes,
            'cash_ratio': cash_ratio_change,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'active_sites': {
                'yesterday': yesterday.get('unique_sites', 0),
                'today': today.get('unique_sites', 0),
                'change': changes.get('unique_sites', {}).get('change', 0)
            }
        }
    
    def _analyze_trends(self, base_result: Dict) -> Dict:
        """트렌드 분석"""
        # 최근 7일 데이터 조회
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        query = """
        SELECT 
            date,
            SUM(players_online) as total_online,
            SUM(cash_players) as total_cash,
            AVG(players_online) as avg_online,
            AVG(cash_players) as avg_cash,
            COUNT(DISTINCT site_name) as active_sites
        FROM daily_data
        WHERE date >= ? AND date <= ?
        GROUP BY date
        ORDER BY date
        """
        
        cursor.execute(query, (week_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')))
        weekly_data = cursor.fetchall()
        
        conn.close()
        
        if len(weekly_data) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'weekly_growth': None,
                'volatility': None,
                'momentum': 'neutral'
            }
        
        # 트렌드 계산
        online_values = [row[1] for row in weekly_data if row[1]]
        cash_values = [row[2] for row in weekly_data if row[2]]
        
        # 선형 회귀를 통한 트렌드 방향
        if len(online_values) >= 2:
            x = np.arange(len(online_values))
            online_trend = np.polyfit(x, online_values, 1)[0]
            cash_trend = np.polyfit(x, cash_values, 1)[0] if len(cash_values) >= 2 else 0
        else:
            online_trend = 0
            cash_trend = 0
        
        # 주간 성장률
        if weekly_data:
            first_week = weekly_data[0]
            last_week = weekly_data[-1]
            
            weekly_online_growth = (
                ((last_week[1] - first_week[1]) / first_week[1] * 100)
                if first_week[1] > 0 else 0
            )
            weekly_cash_growth = (
                ((last_week[2] - first_week[2]) / first_week[2] * 100)
                if first_week[2] > 0 else 0
            )
        else:
            weekly_online_growth = 0
            weekly_cash_growth = 0
        
        # 변동성 계산
        if len(online_values) > 1:
            online_volatility = np.std(online_values) / np.mean(online_values) * 100
            cash_volatility = np.std(cash_values) / np.mean(cash_values) * 100 if cash_values else 0
        else:
            online_volatility = 0
            cash_volatility = 0
        
        # 모멘텀 판단
        momentum = self._calculate_momentum(online_trend, cash_trend, online_volatility)
        
        # 트렌드 방향 결정
        if online_trend > 0 and cash_trend > 0:
            trend_direction = 'uptrend'
        elif online_trend < 0 and cash_trend < 0:
            trend_direction = 'downtrend'
        else:
            trend_direction = 'mixed'
        
        return {
            'trend_direction': trend_direction,
            'weekly_growth': {
                'online': weekly_online_growth,
                'cash': weekly_cash_growth
            },
            'volatility': {
                'online': online_volatility,
                'cash': cash_volatility
            },
            'momentum': momentum,
            'trend_strength': {
                'online': abs(online_trend),
                'cash': abs(cash_trend)
            },
            'data_points': len(weekly_data)
        }
    
    def _calculate_comprehensive_score(self, top_sites: Dict, 
                                      daily_changes: Dict, 
                                      trend_analysis: Dict) -> Dict:
        """종합 스코어 계산"""
        score = 0
        max_score = 100
        
        # TOP 3 성과 (30점)
        if top_sites['online_top3']:
            online_leader = top_sites['online_top3'][0]
            if online_leader['change_pct'] > 10:
                score += 15
            elif online_leader['change_pct'] > 0:
                score += 10
            else:
                score += 5
        
        if top_sites['cash_top3']:
            cash_leader = top_sites['cash_top3'][0]
            if cash_leader['change_pct'] > 10:
                score += 15
            elif cash_leader['change_pct'] > 0:
                score += 10
            else:
                score += 5
        
        # 시장 변화 (30점)
        market_online_change = daily_changes['market_changes']['total_online']['change_pct']
        market_cash_change = daily_changes['market_changes']['total_cash']['change_pct']
        
        if market_online_change > 5:
            score += 15
        elif market_online_change > 0:
            score += 10
        else:
            score += 5
        
        if market_cash_change > 5:
            score += 15
        elif market_cash_change > 0:
            score += 10
        else:
            score += 5
        
        # 트렌드 (20점)
        if trend_analysis['trend_direction'] == 'uptrend':
            score += 20
        elif trend_analysis['trend_direction'] == 'mixed':
            score += 10
        else:
            score += 5
        
        # 캐시 비율 (20점)
        cash_ratio = daily_changes['cash_ratio']['today']
        if cash_ratio > 50:
            score += 20
        elif cash_ratio > 40:
            score += 15
        elif cash_ratio > 30:
            score += 10
        else:
            score += 5
        
        # 등급 결정
        if score >= 85:
            grade = 'S'
            interpretation = '탁월한 시장 성과'
        elif score >= 70:
            grade = 'A'
            interpretation = '우수한 시장 성과'
        elif score >= 55:
            grade = 'B'
            interpretation = '양호한 시장 성과'
        elif score >= 40:
            grade = 'C'
            interpretation = '보통 수준'
        else:
            grade = 'D'
            interpretation = '개선 필요'
        
        return {
            'score': score,
            'max_score': max_score,
            'grade': grade,
            'interpretation': interpretation
        }
    
    def _generate_enhanced_insights(self, top_sites: Dict, 
                                   daily_changes: Dict, 
                                   trend_analysis: Dict) -> List[str]:
        """강화된 인사이트 생성"""
        insights = []
        
        # TOP 3 인사이트
        if top_sites['online_leader']:
            leader = top_sites['online_leader']
            insights.append(
                f"🥇 온라인 1위: {leader['site_name']} ({leader['players_today']:,}명, {leader['change_pct']:+.1f}%)"
            )
        
        if top_sites['cash_leader']:
            leader = top_sites['cash_leader']
            insights.append(
                f"💰 캐시 1위: {leader['site_name']} ({leader['cash_today']:,}명, {leader['change_pct']:+.1f}%)"
            )
        
        # 시장 변화 인사이트
        market = daily_changes['market_changes']
        if abs(market['total_online']['change_pct']) > 5:
            emoji = '📈' if market['total_online']['change_pct'] > 0 else '📉'
            insights.append(
                f"{emoji} 전체 온라인: {market['total_online']['change_pct']:+.1f}% ({market['total_online']['change']:+,}명)"
            )
        
        if abs(market['total_cash']['change_pct']) > 5:
            emoji = '💹' if market['total_cash']['change_pct'] > 0 else '💔'
            insights.append(
                f"{emoji} 전체 캐시: {market['total_cash']['change_pct']:+.1f}% ({market['total_cash']['change']:+,}명)"
            )
        
        # 트렌드 인사이트
        if trend_analysis['trend_direction'] == 'uptrend':
            insights.append("📊 주간 트렌드: 상승세 지속")
        elif trend_analysis['trend_direction'] == 'downtrend':
            insights.append("📊 주간 트렌드: 하락세 지속")
        else:
            insights.append("📊 주간 트렌드: 혼조세")
        
        # 순위 변동 인사이트
        for site in top_sites['online_top3']:
            if site['rank_change'] > 0:
                insights.append(f"⬆️ {site['site_name']}: 온라인 순위 {site['rank_change']}계단 상승")
            elif site['rank_change'] < 0:
                insights.append(f"⬇️ {site['site_name']}: 온라인 순위 {abs(site['rank_change'])}계단 하락")
        
        # 캐시 비율 인사이트
        cash_ratio = daily_changes['cash_ratio']
        if cash_ratio['change'] > 1:
            insights.append(f"💵 캐시 비율 {cash_ratio['change']:+.1f}%p 상승 ({cash_ratio['today']:.1f}%)")
        elif cash_ratio['change'] < -1:
            insights.append(f"💸 캐시 비율 {abs(cash_ratio['change']):.1f}%p 하락 ({cash_ratio['today']:.1f}%)")
        
        return insights
    
    def _get_trend(self, change_pct: float) -> str:
        """트렌드 판단"""
        if change_pct >= 10:
            return '🚀 급상승'
        elif change_pct >= 5:
            return '📈 상승'
        elif change_pct >= -5:
            return '➡️ 보합'
        elif change_pct >= -10:
            return '📉 하락'
        else:
            return '⬇️ 급락'
    
    def _calculate_momentum(self, online_trend: float, cash_trend: float, volatility: float) -> str:
        """모멘텀 계산"""
        combined_trend = (online_trend + cash_trend) / 2
        
        if combined_trend > 0 and volatility < 20:
            return 'strong_bullish'
        elif combined_trend > 0:
            return 'bullish'
        elif combined_trend < 0 and volatility < 20:
            return 'strong_bearish'
        elif combined_trend < 0:
            return 'bearish'
        else:
            return 'neutral'

def main():
    print("🎯 강화된 이중 지표 분석 시스템")
    print("=" * 60)
    
    analyzer = EnhancedDualMetricAnalyzer()
    
    try:
        # 분석 실행
        print("\n📊 강화된 분석 실행 중...")
        result = analyzer.analyze_enhanced_daily()
        
        # 결과 출력
        print("\n" + "=" * 80)
        print("📊 강화된 분석 결과")
        print("=" * 80)
        
        # TOP 3 온라인
        print("\n🌐 온라인 플레이어 TOP 3")
        print("-" * 40)
        for site in result['top_sites']['online_top3']:
            print(f"{site['rank']}. {site['site_name']}")
            print(f"   오늘: {site['players_today']:,}명")
            print(f"   어제: {site['players_yesterday']:,}명")
            print(f"   변화: {site['change']:+,}명 ({site['change_pct']:+.1f}%)")
            print(f"   트렌드: {site['trend']}")
            if site['rank_change'] != 0:
                print(f"   순위변동: {site['rank_change']:+d}")
            print()
        
        # TOP 3 캐시
        print("\n💰 캐시 플레이어 TOP 3")
        print("-" * 40)
        for site in result['top_sites']['cash_top3']:
            print(f"{site['rank']}. {site['site_name']}")
            print(f"   오늘: {site['cash_today']:,}명")
            print(f"   어제: {site['cash_yesterday']:,}명")
            print(f"   변화: {site['change']:+,}명 ({site['change_pct']:+.1f}%)")
            print(f"   트렌드: {site['trend']}")
            if site['rank_change'] != 0:
                print(f"   순위변동: {site['rank_change']:+d}")
            print()
        
        # 전날 대비 변화
        print("\n📈 전날 대비 시장 변화")
        print("-" * 40)
        market = result['daily_changes']['market_changes']
        print(f"총 온라인: {market['total_online']['yesterday']:,} → {market['total_online']['today']:,}")
        print(f"   변화: {market['total_online']['change']:+,}명 ({market['total_online']['change_pct']:+.1f}%)")
        print(f"총 캐시: {market['total_cash']['yesterday']:,} → {market['total_cash']['today']:,}")
        print(f"   변화: {market['total_cash']['change']:+,}명 ({market['total_cash']['change_pct']:+.1f}%)")
        
        # 트렌드 분석
        print("\n📊 트렌드 분석")
        print("-" * 40)
        trend = result['trend_analysis']
        print(f"트렌드 방향: {trend['trend_direction']}")
        if trend['weekly_growth']:
            print(f"주간 성장률:")
            print(f"   온라인: {trend['weekly_growth']['online']:.1f}%")
            print(f"   캐시: {trend['weekly_growth']['cash']:.1f}%")
        if trend['volatility']:
            print(f"변동성:")
            print(f"   온라인: {trend['volatility']['online']:.1f}%")
            print(f"   캐시: {trend['volatility']['cash']:.1f}%")
        print(f"모멘텀: {trend['momentum']}")
        
        # 종합 점수
        score = result['comprehensive_score']
        print(f"\n🏆 종합 평가: {score['score']}/{score['max_score']}점 ({score['grade']}등급)")
        print(f"   {score['interpretation']}")
        
        # 주요 인사이트
        print("\n💡 주요 인사이트")
        print("-" * 40)
        for insight in result['insights'][:10]:
            print(f"• {insight}")
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"enhanced_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 분석 결과 저장: {output_file}")
        
    except Exception as e:
        logger.error(f"분석 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()