#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Competitive Analysis Reporter
GGNetwork 독점 상황에서 2-3위 경쟁 분석 중심 리포터
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitiveAnalysisReporter:
    """
    경쟁 구도 분석 리포터
    - GGNetwork는 독점 1위로 별도 추적
    - 2위, 3위 사이트 상세 분석
    - 실질 경쟁 구도 파악
    """
    
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        
    def analyze_competitive_landscape(self, target_date: str = None) -> Dict:
        """경쟁 구도 종합 분석"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        yesterday = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        
        logger.info(f"[타겟] 경쟁 구도 분석: {yesterday} vs {target_date}")
        
        # 데이터 수집
        online_analysis = self._analyze_online_competition(yesterday, target_date)
        cash_analysis = self._analyze_cash_competition(yesterday, target_date)
        ggnetwork_trend = self._analyze_ggnetwork_trend(yesterday, target_date)
        challenger_analysis = self._analyze_challengers(yesterday, target_date)
        market_dynamics = self._analyze_market_dynamics(online_analysis, cash_analysis)
        
        return {
            'analysis_type': 'competitive_landscape',
            'period': f'{yesterday} vs {target_date}',
            'ggnetwork_dominance': ggnetwork_trend,
            'online_competition': online_analysis,
            'cash_competition': cash_analysis,
            'challenger_analysis': challenger_analysis,
            'market_dynamics': market_dynamics,
            'insights': self._generate_competitive_insights(
                ggnetwork_trend, online_analysis, cash_analysis, challenger_analysis
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_online_competition(self, yesterday: str, today: str) -> Dict:
        """온라인 플레이어 경쟁 분석 (2-3위 중심)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # TOP 5 조회 (GGNetwork 포함, PokerStars 오염 데이터 제외)
        query = """
        SELECT site_name, players_online, cash_players
        FROM daily_data
        WHERE date = ? AND site_name NOT LIKE '%PokerStars%'
        ORDER BY players_online DESC
        LIMIT 5
        """
        
        cursor.execute(query, (yesterday,))
        yesterday_top5 = cursor.fetchall()
        
        cursor.execute(query, (today,))
        today_top5 = cursor.fetchall()
        
        # 디버깅: 실제 조회된 데이터 출력
        logger.info(f"DEBUG: DB Path: {self.db_path}")
        logger.info(f"DEBUG: Today date: {today}, Yesterday date: {yesterday}")
        logger.info(f"DEBUG: Today TOP 5 data: {today_top5}")
        logger.info(f"DEBUG: Yesterday TOP 5 data: {yesterday_top5}")
        
        # 추가 디버깅: 해당 날짜의 모든 데이터 확인
        cursor.execute("SELECT DISTINCT date FROM daily_data ORDER BY date DESC")
        all_dates = cursor.fetchall()
        logger.info(f"DEBUG: All dates in DB: {all_dates}")
        
        conn.close()
        
        # 2-3위 상세 분석
        analysis = {
            'top5_yesterday': [],
            'top5_today': [],
            'second_place_battle': {},
            'third_place_battle': {},
            'gap_analysis': {}
        }
        
        # TOP 5 데이터 정리
        for i, (site, players, cash) in enumerate(today_top5):
            rank = i + 1
            
            # 어제 데이터 찾기
            yesterday_data = next(
                ((idx+1, p, c) for idx, (s, p, c) in enumerate(yesterday_top5) if s == site),
                (99, 0, 0)
            )
            yesterday_rank, yesterday_players, yesterday_cash = yesterday_data
            
            change = players - yesterday_players
            change_pct = (change / yesterday_players * 100) if yesterday_players > 0 else 0
            rank_change = yesterday_rank - rank
            
            site_data = {
                'rank': rank,
                'site_name': site,
                'players': players,
                'yesterday_players': yesterday_players,
                'change': change,
                'change_pct': change_pct,
                'rank_change': rank_change,
                'is_ggnetwork': 'GG' in site.upper()
            }
            
            analysis['top5_today'].append(site_data)
            
            # 2위 분석
            if rank == 2:
                analysis['second_place_battle'] = {
                    'current_holder': site,
                    'players': players,
                    'change': change,
                    'change_pct': change_pct,
                    'gap_to_first': today_top5[0][1] - players if today_top5 else 0,
                    'gap_to_third': players - today_top5[2][1] if len(today_top5) > 2 else 0,
                    'stability': 'stable' if abs(rank_change) <= 1 else 'volatile'
                }
            
            # 3위 분석
            elif rank == 3:
                analysis['third_place_battle'] = {
                    'current_holder': site,
                    'players': players,
                    'change': change,
                    'change_pct': change_pct,
                    'gap_to_second': today_top5[1][1] - players if len(today_top5) > 1 else 0,
                    'gap_to_fourth': players - today_top5[3][1] if len(today_top5) > 3 else 0,
                    'threat_level': self._assess_threat_level(change_pct, rank_change)
                }
        
        # 격차 분석
        if len(today_top5) >= 3:
            first_share = today_top5[0][1] / sum(t[1] for t in today_top5) * 100
            second_share = today_top5[1][1] / sum(t[1] for t in today_top5) * 100
            third_share = today_top5[2][1] / sum(t[1] for t in today_top5) * 100
            
            analysis['gap_analysis'] = {
                'first_dominance': first_share,
                'second_third_combined': second_share + third_share,
                'competition_intensity': self._calculate_competition_intensity(
                    today_top5[1][1], today_top5[2][1]
                )
            }
        
        return analysis
    
    def _analyze_cash_competition(self, yesterday: str, today: str) -> Dict:
        """캐시 플레이어 경쟁 분석 (2-3위 중심)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 캐시 TOP 5 (PokerStars 오염 데이터 제외)
        query = """
        SELECT site_name, cash_players, players_online
        FROM daily_data
        WHERE date = ? AND site_name NOT LIKE '%PokerStars%'
        ORDER BY cash_players DESC
        LIMIT 5
        """
        
        cursor.execute(query, (yesterday,))
        yesterday_top5 = cursor.fetchall()
        
        cursor.execute(query, (today,))
        today_top5 = cursor.fetchall()
        
        conn.close()
        
        analysis = {
            'top5_today': [],
            'second_place_battle': {},
            'third_place_battle': {},
            'cash_concentration': {}
        }
        
        # TOP 5 분석
        for i, (site, cash, online) in enumerate(today_top5):
            rank = i + 1
            
            yesterday_data = next(
                ((idx+1, c, o) for idx, (s, c, o) in enumerate(yesterday_top5) if s == site),
                (99, 0, 0)
            )
            yesterday_rank, yesterday_cash, yesterday_online = yesterday_data
            
            change = cash - yesterday_cash
            change_pct = (change / yesterday_cash * 100) if yesterday_cash > 0 else 0
            rank_change = yesterday_rank - rank
            
            # 캐시 비율
            cash_ratio = (cash / online * 100) if online > 0 else 0
            
            site_data = {
                'rank': rank,
                'site_name': site,
                'cash_players': cash,
                'yesterday_cash': yesterday_cash,
                'change': change,
                'change_pct': change_pct,
                'rank_change': rank_change,
                'cash_ratio': cash_ratio,
                'is_ggnetwork': 'GG' in site.upper()
            }
            
            analysis['top5_today'].append(site_data)
            
            # 2위 분석
            if rank == 2:
                analysis['second_place_battle'] = {
                    'current_holder': site,
                    'cash_players': cash,
                    'change': change,
                    'change_pct': change_pct,
                    'cash_ratio': cash_ratio,
                    'gap_to_first': today_top5[0][1] - cash if today_top5 else 0,
                    'revenue_potential': self._assess_revenue_potential(cash, cash_ratio)
                }
            
            # 3위 분석
            elif rank == 3:
                analysis['third_place_battle'] = {
                    'current_holder': site,
                    'cash_players': cash,
                    'change': change,
                    'change_pct': change_pct,
                    'cash_ratio': cash_ratio,
                    'gap_to_second': today_top5[1][1] - cash if len(today_top5) > 1 else 0,
                    'growth_momentum': self._assess_growth_momentum(change_pct, rank_change)
                }
        
        # 캐시 집중도
        if len(today_top5) >= 3:
            total_cash = sum(t[1] for t in today_top5)
            analysis['cash_concentration'] = {
                'ggnetwork_share': (today_top5[0][1] / total_cash * 100) if total_cash > 0 else 0,
                'second_third_share': ((today_top5[1][1] + today_top5[2][1]) / total_cash * 100) if total_cash > 0 else 0,
                'competitive_landscape': self._classify_cash_landscape(today_top5)
            }
        
        return analysis
    
    def _analyze_ggnetwork_trend(self, yesterday: str, today: str) -> Dict:
        """GGNetwork 트렌드 별도 추적"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # GGNetwork 데이터
        query = """
        SELECT players_online, cash_players
        FROM daily_data
        WHERE date = ? AND site_name LIKE '%GG%'
        """
        
        cursor.execute(query, (yesterday,))
        yesterday_gg = cursor.fetchone()
        
        cursor.execute(query, (today,))
        today_gg = cursor.fetchone()
        
        # 주간 트렌드
        week_ago = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
        
        query_weekly = """
        SELECT date, players_online, cash_players
        FROM daily_data
        WHERE site_name LIKE '%GG%' AND date >= ? AND date <= ?
        ORDER BY date
        """
        
        cursor.execute(query_weekly, (week_ago, today))
        weekly_data = cursor.fetchall()
        
        conn.close()
        
        if not today_gg or not yesterday_gg:
            return {'status': 'no_data'}
        
        # 일일 변화
        online_change = today_gg[0] - yesterday_gg[0]
        online_change_pct = (online_change / yesterday_gg[0] * 100) if yesterday_gg[0] > 0 else 0
        
        cash_change = today_gg[1] - yesterday_gg[1]
        cash_change_pct = (cash_change / yesterday_gg[1] * 100) if yesterday_gg[1] > 0 else 0
        
        # 주간 트렌드
        weekly_trend = 'stable'
        if len(weekly_data) >= 3:
            online_values = [d[1] for d in weekly_data]
            if len(online_values) > 1:
                trend_slope = np.polyfit(range(len(online_values)), online_values, 1)[0]
                if trend_slope > 1000:
                    weekly_trend = 'growing'
                elif trend_slope < -1000:
                    weekly_trend = 'declining'
        
        # 시장 지배력
        conn2 = sqlite3.connect(self.db_path)
        cursor2 = conn2.cursor()
        cursor2.execute("""
            SELECT SUM(players_online), SUM(cash_players)
            FROM daily_data
            WHERE date = ?
        """, (today,))
        market_total = cursor2.fetchone()
        conn2.close()
        
        online_dominance = (today_gg[0] / market_total[0] * 100) if market_total[0] > 0 else 0
        cash_dominance = (today_gg[1] / market_total[1] * 100) if market_total[1] > 0 else 0
        
        return {
            'status': 'dominant',
            'online_players': {
                'current': today_gg[0],
                'yesterday': yesterday_gg[0],
                'change': online_change,
                'change_pct': online_change_pct
            },
            'cash_players': {
                'current': today_gg[1],
                'yesterday': yesterday_gg[1],
                'change': cash_change,
                'change_pct': cash_change_pct
            },
            'market_dominance': {
                'online_share': online_dominance,
                'cash_share': cash_dominance
            },
            'weekly_trend': weekly_trend,
            'dominance_level': self._classify_dominance(online_dominance)
        }
    
    def _analyze_challengers(self, yesterday: str, today: str) -> Dict:
        """도전자 분석 (2-4위 사이트들)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 2-4위 사이트 데이터
        query = """
        SELECT site_name, players_online, cash_players
        FROM daily_data
        WHERE date = ?
        ORDER BY players_online DESC
        LIMIT 4 OFFSET 1
        """
        
        cursor.execute(query, (today,))
        challengers = cursor.fetchall()
        
        cursor.execute(query, (yesterday,))
        yesterday_challengers = cursor.fetchall()
        
        conn.close()
        
        challenger_profiles = []
        
        for site, online, cash in challengers:
            # 어제 데이터
            yesterday_data = next(
                ((o, c) for s, o, c in yesterday_challengers if s == site),
                (0, 0)
            )
            
            online_growth = ((online - yesterday_data[0]) / yesterday_data[0] * 100) if yesterday_data[0] > 0 else 0
            cash_growth = ((cash - yesterday_data[1]) / yesterday_data[1] * 100) if yesterday_data[1] > 0 else 0
            
            profile = {
                'site_name': site,
                'online_players': online,
                'cash_players': cash,
                'online_growth': online_growth,
                'cash_growth': cash_growth,
                'cash_ratio': (cash / online * 100) if online > 0 else 0,
                'competitive_position': self._assess_competitive_position(site, online, cash),
                'growth_potential': self._assess_growth_potential(online_growth, cash_growth)
            }
            
            challenger_profiles.append(profile)
        
        # 가장 위협적인 도전자
        most_threatening = max(challenger_profiles, key=lambda x: x['online_players']) if challenger_profiles else None
        fastest_growing = max(challenger_profiles, key=lambda x: x['online_growth']) if challenger_profiles else None
        
        return {
            'challengers': challenger_profiles,
            'most_threatening': most_threatening,
            'fastest_growing': fastest_growing,
            'competition_intensity': self._calculate_challenger_competition(challenger_profiles)
        }
    
    def _analyze_market_dynamics(self, online: Dict, cash: Dict) -> Dict:
        """시장 역학 분석"""
        dynamics = {
            'market_structure': '',
            'competition_level': '',
            'key_battlegrounds': [],
            'strategic_implications': []
        }
        
        # 시장 구조 분류
        if online.get('gap_analysis', {}).get('first_dominance', 0) > 70:
            dynamics['market_structure'] = 'monopolistic'
            dynamics['strategic_implications'].append('GGNetwork의 독점적 지위 공고화')
        elif online.get('gap_analysis', {}).get('first_dominance', 0) > 50:
            dynamics['market_structure'] = 'dominant_leader'
            dynamics['strategic_implications'].append('1위 독주 체제 지속')
        else:
            dynamics['market_structure'] = 'competitive'
            dynamics['strategic_implications'].append('경쟁적 시장 구조')
        
        # 경쟁 수준
        if online.get('gap_analysis', {}).get('competition_intensity', '') == 'high':
            dynamics['competition_level'] = 'intense'
            dynamics['key_battlegrounds'].append('2-3위 순위 경쟁 치열')
        else:
            dynamics['competition_level'] = 'moderate'
        
        # 주요 전장
        if online.get('second_place_battle', {}).get('stability') == 'volatile':
            dynamics['key_battlegrounds'].append('2위 자리 불안정')
        
        if cash.get('cash_concentration', {}).get('second_third_share', 0) > 20:
            dynamics['key_battlegrounds'].append('캐시 게임 2-3위 경쟁 활발')
        
        return dynamics
    
    def _generate_competitive_insights(self, ggnetwork: Dict, online: Dict, 
                                      cash: Dict, challengers: Dict) -> List[str]:
        """경쟁 구도 인사이트 생성"""
        insights = []
        
        # GGNetwork 트렌드
        if ggnetwork.get('status') == 'dominant':
            gg_online = ggnetwork['online_players']
            insights.append(
                f"[왕관] GGNetwork 독점 지속: 온라인 {gg_online['current']:,}명 ({gg_online['change_pct']:+.1f}%)"
            )
            
            if ggnetwork['weekly_trend'] == 'growing':
                insights.append("[성장] GGNetwork 주간 성장세 지속")
            elif ggnetwork['weekly_trend'] == 'declining':
                insights.append("[하락] GGNetwork 주간 하락세 전환")
        
        # 2위 경쟁
        if online.get('second_place_battle'):
            second = online['second_place_battle']
            insights.append(
                f"[2위] 온라인 2위: {second['current_holder']} ({second['players']:,}명, {second['change_pct']:+.1f}%)"
            )
            
            if second['gap_to_third'] < 1000:
                insights.append(f"[격전] 2-3위 격차 {second['gap_to_third']:,}명으로 경쟁 치열")
        
        # 3위 경쟁
        if online.get('third_place_battle'):
            third = online['third_place_battle']
            if third['threat_level'] == 'high':
                insights.append(f"[화염] {third['current_holder']} 3위 수성 위협")
        
        # 캐시 게임 경쟁
        if cash.get('second_place_battle'):
            cash_second = cash['second_place_battle']
            insights.append(
                f"[캐시] 캐시 2위: {cash_second['current_holder']} ({cash_second['cash_players']:,}명)"
            )
            
            if cash_second['revenue_potential'] == 'high':
                insights.append(f"[다이아] {cash_second['current_holder']} 높은 수익성 (캐시비율 {cash_second['cash_ratio']:.1f}%)")
        
        # 도전자 분석
        if challengers.get('fastest_growing'):
            fastest = challengers['fastest_growing']
            if fastest['online_growth'] > 10:
                insights.append(
                    f"[로켓] {fastest['site_name']} 급성장 중 (+{fastest['online_growth']:.1f}%)"
                )
        
        # 시장 구조
        if online.get('gap_analysis'):
            gap = online['gap_analysis']
            if gap['second_third_combined'] < 20:
                insights.append("[경고] 2-3위 합쳐도 시장 점유율 20% 미만")
        
        return insights
    
    # 헬퍼 메서드들
    def _assess_threat_level(self, change_pct: float, rank_change: int) -> str:
        if change_pct > 10 or rank_change > 0:
            return 'high'
        elif change_pct > 0:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_competition_intensity(self, second: int, third: int) -> str:
        gap = second - third
        ratio = gap / second if second > 0 else 0
        
        if ratio < 0.1:
            return 'high'
        elif ratio < 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_revenue_potential(self, cash: int, ratio: float) -> str:
        if cash > 1000 and ratio > 40:
            return 'high'
        elif cash > 500 or ratio > 30:
            return 'medium'
        else:
            return 'low'
    
    def _assess_growth_momentum(self, change_pct: float, rank_change: int) -> str:
        if change_pct > 10 and rank_change >= 0:
            return 'strong'
        elif change_pct > 0:
            return 'moderate'
        else:
            return 'weak'
    
    def _classify_cash_landscape(self, top5: List) -> str:
        if len(top5) < 3:
            return 'insufficient_data'
        
        first_share = top5[0][1]
        second_third = top5[1][1] + top5[2][1]
        
        if first_share > second_third * 3:
            return 'monopoly'
        elif first_share > second_third * 2:
            return 'dominant'
        else:
            return 'competitive'
    
    def _classify_dominance(self, share: float) -> str:
        if share > 70:
            return 'absolute'
        elif share > 50:
            return 'strong'
        elif share > 30:
            return 'moderate'
        else:
            return 'weak'
    
    def _assess_competitive_position(self, site: str, online: int, cash: int) -> str:
        # 사이트별 특성 평가
        if 'PokerStars' in site:
            return 'established_brand'
        elif 'WPT' in site:
            return 'tournament_focused'
        elif 'iPoker' in site:
            return 'network_based'
        else:
            return 'niche_player'
    
    def _assess_growth_potential(self, online_growth: float, cash_growth: float) -> str:
        avg_growth = (online_growth + cash_growth) / 2
        
        if avg_growth > 15:
            return 'very_high'
        elif avg_growth > 5:
            return 'high'
        elif avg_growth > 0:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_challenger_competition(self, profiles: List[Dict]) -> str:
        if not profiles:
            return 'none'
        
        # 성장률 표준편차로 경쟁 강도 측정
        growth_rates = [p['online_growth'] for p in profiles]
        if len(growth_rates) > 1:
            std_dev = np.std(growth_rates)
            if std_dev > 10:
                return 'very_high'
            elif std_dev > 5:
                return 'high'
            else:
                return 'moderate'
        
        return 'low'


def main():
    print("Competitive Analysis System")
    print("=" * 60)
    print("2nd-3rd Place Competition Analysis (GGNetwork Dominant)")
    print("=" * 60)
    
    analyzer = CompetitiveAnalysisReporter()
    
    try:
        result = analyzer.analyze_competitive_landscape()
        
        # GGNetwork 현황
        print("\n[GGNetwork Dominance]")
        print("-" * 40)
        gg = result['ggnetwork_dominance']
        if gg.get('status') == 'dominant':
            print(f"Online: {gg['online_players']['current']:,} ({gg['online_players']['change_pct']:+.1f}%)")
            print(f"Cash: {gg['cash_players']['current']:,} ({gg['cash_players']['change_pct']:+.1f}%)")
            print(f"Market Share: Online {gg['market_dominance']['online_share']:.1f}% | Cash {gg['market_dominance']['cash_share']:.1f}%")
            print(f"Weekly Trend: {gg['weekly_trend']}")
        
        # 온라인 2-3위 경쟁
        print("\n[Online Players - 2nd & 3rd Competition]")
        print("-" * 40)
        online = result['online_competition']
        if online.get('second_place_battle'):
            second = online['second_place_battle']
            print(f"2nd: {second['current_holder']}")
            print(f"  Players: {second['players']:,} ({second['change_pct']:+.1f}%)")
            print(f"  Gap to 3rd: {second['gap_to_third']:,}")
            print(f"  Stability: {second['stability']}")
        
        if online.get('third_place_battle'):
            third = online['third_place_battle']
            print(f"3rd: {third['current_holder']}")
            print(f"  Players: {third['players']:,} ({third['change_pct']:+.1f}%)")
            print(f"  Gap to 2nd: {third['gap_to_second']:,}")
        
        # 캐시 2-3위 경쟁
        print("\n[Cash Players - 2nd & 3rd Competition]")
        print("-" * 40)
        cash = result['cash_competition']
        if cash.get('second_place_battle'):
            second = cash['second_place_battle']
            print(f"2nd: {second['current_holder']}")
            print(f"  Cash: {second['cash_players']:,} ({second['change_pct']:+.1f}%)")
            print(f"  Cash Ratio: {second['cash_ratio']:.1f}%")
            print(f"  Revenue Potential: {second['revenue_potential']}")
        
        if cash.get('third_place_battle'):
            third = cash['third_place_battle']
            print(f"3rd: {third['current_holder']}")
            print(f"  Cash: {third['cash_players']:,} ({third['change_pct']:+.1f}%)")
            print(f"  Growth Momentum: {third['growth_momentum']}")
        
        # 도전자 분석
        print("\n[Key Challengers]")
        print("-" * 40)
        challengers = result['challenger_analysis']
        if challengers.get('fastest_growing'):
            fastest = challengers['fastest_growing']
            print(f"Fastest Growing: {fastest['site_name']} (+{fastest['online_growth']:.1f}%)")
        
        # 인사이트
        print("\n[Key Insights]")
        print("-" * 40)
        for insight in result['insights'][:10]:
            print(f"- {insight}")
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"competitive_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\nAnalysis saved: {output_file}")
        
    except Exception as e:
        logger.error(f"분석 중 오류: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()