#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현실적인 플랫폼 데이터 제공
실제 포커 사이트의 대략적인 통계 기반
"""

from datetime import datetime, timedelta
import random

class RealisticPlatformData:
    """실제에 가까운 플랫폼 데이터"""
    
    # 2024년 기준 실제 추정 데이터 (온라인 플레이어 기준)
    BASE_DATA = {
        "GGNetwork": {
            "base_online": 85000,
            "base_cash": 28000,
            "base_tournament": 15000,
            "avg_growth": 0.5,  # 일일 평균 성장률 %
            "volatility": 0.03,  # 일일 변동성
            "peak_ratio": 1.35,  # 피크 시간 배수
            "market_share": 0.30,
            "tier": 1
        },
        "PokerStars": {
            "base_online": 45000,
            "base_cash": 13000,
            "base_tournament": 10000,
            "avg_growth": -0.1,
            "volatility": 0.02,
            "peak_ratio": 1.3,
            "market_share": 0.16,
            "tier": 2
        },
        "iPoker": {
            "base_online": 38000,
            "base_cash": 11000,
            "base_tournament": 7000,
            "avg_growth": 0.05,
            "volatility": 0.02,
            "peak_ratio": 1.25,
            "market_share": 0.13,
            "tier": 2
        },
        "PartyPoker": {
            "base_online": 28000,
            "base_cash": 8000,
            "base_tournament": 5000,
            "avg_growth": -0.2,
            "volatility": 0.025,
            "peak_ratio": 1.28,
            "market_share": 0.10,
            "tier": 3
        },
        "888poker": {
            "base_online": 25000,
            "base_cash": 7000,
            "base_tournament": 4500,
            "avg_growth": -0.15,
            "volatility": 0.025,
            "peak_ratio": 1.25,
            "market_share": 0.09,
            "tier": 3
        },
        "Winamax": {
            "base_online": 22000,
            "base_cash": 6500,
            "base_tournament": 4000,
            "avg_growth": 0.1,
            "volatility": 0.03,
            "peak_ratio": 1.3,
            "market_share": 0.08,
            "tier": 3
        },
        "Winning Poker": {
            "base_online": 18000,
            "base_cash": 5000,
            "base_tournament": 3000,
            "avg_growth": -0.05,
            "volatility": 0.03,
            "peak_ratio": 1.22,
            "market_share": 0.06,
            "tier": 4
        },
        "Chico Poker": {
            "base_online": 15000,
            "base_cash": 4200,
            "base_tournament": 2500,
            "avg_growth": -0.1,
            "volatility": 0.035,
            "peak_ratio": 1.2,
            "market_share": 0.05,
            "tier": 4
        },
        "BetOnline": {
            "base_online": 12000,
            "base_cash": 3500,
            "base_tournament": 2000,
            "avg_growth": 0.05,
            "volatility": 0.04,
            "peak_ratio": 1.25,
            "market_share": 0.04,
            "tier": 4
        },
        "TigerGaming": {
            "base_online": 10000,
            "base_cash": 2800,
            "base_tournament": 1500,
            "avg_growth": -0.08,
            "volatility": 0.04,
            "peak_ratio": 1.18,
            "market_share": 0.03,
            "tier": 4
        }
    }
    
    @classmethod
    def get_daily_data(cls, date_str: str = None) -> list:
        """특정 날짜의 일일 데이터 생성"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 날짜 기반 시드 (같은 날짜는 항상 같은 데이터)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_number = (date_obj - datetime(2024, 1, 1)).days
        random.seed(day_number)
        
        data = []
        for platform_name, base_info in cls.BASE_DATA.items():
            # 시간에 따른 점진적 변화 적용
            days_passed = day_number
            growth_factor = 1 + (base_info['avg_growth'] * days_passed / 365)
            
            # 요일별 패턴 (주말에 더 많은 플레이어)
            weekday = date_obj.weekday()
            if weekday in [5, 6]:  # 토, 일
                weekday_factor = 1.15
            elif weekday == 4:  # 금요일
                weekday_factor = 1.10
            else:
                weekday_factor = 1.0
            
            # 계절별 패턴 (겨울에 더 많은 플레이어)
            month = date_obj.month
            if month in [12, 1, 2]:  # 겨울
                season_factor = 1.1
            elif month in [6, 7, 8]:  # 여름
                season_factor = 0.95
            else:
                season_factor = 1.0
            
            # 최종 온라인 플레이어 계산
            base = base_info['base_online']
            volatility = base_info['volatility']
            daily_variation = random.uniform(1 - volatility, 1 + volatility)
            
            online_players = int(
                base * growth_factor * weekday_factor * season_factor * daily_variation
            )
            
            # 캐시/토너먼트 플레이어 계산
            cash_ratio = base_info['base_cash'] / base_info['base_online']
            cash_players = int(online_players * cash_ratio * random.uniform(0.95, 1.05))
            
            tournament_ratio = base_info['base_tournament'] / base_info['base_online']
            tournament_players = int(online_players * tournament_ratio * random.uniform(0.9, 1.1))
            
            # 24시간 피크
            peak_24h = int(online_players * base_info['peak_ratio'] * random.uniform(0.95, 1.05))
            
            # 7일 평균 (과거 데이터 고려)
            seven_day_avg = int(online_players * random.uniform(0.98, 1.02))
            
            # 일일 성장률 (전날 대비)
            daily_growth = base_info['avg_growth'] + random.uniform(-2, 2)
            
            data.append({
                'platform_name': platform_name,
                'date': date_str,
                'online_players': online_players,
                'cash_players': cash_players,
                'tournament_players': tournament_players,
                'peak_24h': peak_24h,
                'seven_day_avg': seven_day_avg,
                'growth_rate': daily_growth,
                'tier': base_info['tier'],
                'market_share': 0  # 나중에 계산
            })
        
        # 시장 점유율 재계산
        total_online = sum(p['online_players'] for p in data)
        for platform in data:
            platform['market_share'] = round((platform['online_players'] / total_online) * 100, 2)
        
        # 온라인 플레이어 기준 정렬
        data.sort(key=lambda x: x['online_players'], reverse=True)
        
        # 랜덤 시드 리셋
        random.seed()
        
        return data
    
    @classmethod
    def get_weekly_data(cls, end_date_str: str = None) -> list:
        """주간 평균 데이터 생성"""
        if not end_date_str:
            end_date_str = datetime.now().strftime('%Y-%m-%d')
        
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 7일간의 데이터 수집
        weekly_data = {}
        for i in range(7):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily = cls.get_daily_data(date)
            
            for platform in daily:
                name = platform['platform_name']
                if name not in weekly_data:
                    weekly_data[name] = {
                        'online': [],
                        'cash': [],
                        'tournament': [],
                        'peak': []
                    }
                weekly_data[name]['online'].append(platform['online_players'])
                weekly_data[name]['cash'].append(platform['cash_players'])
                weekly_data[name]['tournament'].append(platform['tournament_players'])
                weekly_data[name]['peak'].append(platform['peak_24h'])
        
        # 평균 계산
        result = []
        for name, values in weekly_data.items():
            avg_online = int(sum(values['online']) / len(values['online']))
            avg_cash = int(sum(values['cash']) / len(values['cash']))
            avg_tournament = int(sum(values['tournament']) / len(values['tournament']))
            max_peak = max(values['peak'])
            
            # 주간 성장률 (첫날 대비 마지막날)
            growth = ((values['online'][-1] - values['online'][0]) / values['online'][0]) * 100
            
            result.append({
                'platform_name': name,
                'online_players': avg_online,
                'cash_players': avg_cash,
                'tournament_players': avg_tournament,
                'peak_24h': max_peak,
                'seven_day_avg': avg_online,
                'growth_rate': round(growth, 1),
                'tier': cls.BASE_DATA[name]['tier']
            })
        
        # 시장 점유율 계산
        total = sum(p['online_players'] for p in result)
        for platform in result:
            platform['market_share'] = round((platform['online_players'] / total) * 100, 2)
        
        result.sort(key=lambda x: x['online_players'], reverse=True)
        return result
    
    @classmethod
    def get_monthly_data(cls, end_date_str: str = None) -> list:
        """월간 평균 데이터 생성"""
        if not end_date_str:
            end_date_str = datetime.now().strftime('%Y-%m-%d')
        
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 30일간의 데이터 수집
        monthly_data = {}
        for i in range(30):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily = cls.get_daily_data(date)
            
            for platform in daily:
                name = platform['platform_name']
                if name not in monthly_data:
                    monthly_data[name] = {
                        'online': [],
                        'cash': [],
                        'tournament': [],
                        'peak': []
                    }
                monthly_data[name]['online'].append(platform['online_players'])
                monthly_data[name]['cash'].append(platform['cash_players'])
                monthly_data[name]['tournament'].append(platform['tournament_players'])
                monthly_data[name]['peak'].append(platform['peak_24h'])
        
        # 평균 계산
        result = []
        for name, values in monthly_data.items():
            avg_online = int(sum(values['online']) / len(values['online']))
            avg_cash = int(sum(values['cash']) / len(values['cash']))
            avg_tournament = int(sum(values['tournament']) / len(values['tournament']))
            max_peak = max(values['peak'])
            
            # 월간 성장률
            growth = ((values['online'][-1] - values['online'][0]) / values['online'][0]) * 100
            
            result.append({
                'platform_name': name,
                'online_players': avg_online,
                'cash_players': avg_cash,
                'tournament_players': avg_tournament,
                'peak_24h': max_peak,
                'seven_day_avg': int(sum(values['online'][-7:]) / 7),
                'growth_rate': round(growth, 1),
                'tier': cls.BASE_DATA[name]['tier']
            })
        
        # 시장 점유율 계산
        total = sum(p['online_players'] for p in result)
        for platform in result:
            platform['market_share'] = round((platform['online_players'] / total) * 100, 2)
        
        result.sort(key=lambda x: x['online_players'], reverse=True)
        return result


if __name__ == "__main__":
    # 테스트
    print("Daily Data Test:")
    daily = RealisticPlatformData.get_daily_data("2025-08-11")
    for p in daily[:5]:
        print(f"{p['platform_name']}: {p['online_players']:,} ({p['market_share']}%)")
    
    print("\nWeekly Data Test:")
    weekly = RealisticPlatformData.get_weekly_data("2025-08-11")
    for p in weekly[:5]:
        print(f"{p['platform_name']}: {p['online_players']:,} ({p['market_share']}%)")
    
    print("\nMonthly Data Test:")
    monthly = RealisticPlatformData.get_monthly_data("2025-08-11")
    for p in monthly[:5]:
        print(f"{p['platform_name']}: {p['online_players']:,} ({p['market_share']}%)")