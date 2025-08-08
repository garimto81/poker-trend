#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Period Poker Data Analyzer
일일/주간/월간 비교 분석 시스템
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_data_collector import DailyDataCollector

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiPeriodAnalyzer:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.collector = DailyDataCollector(db_path)
        
    def get_date_range_data(self, start_date: str, end_date: str) -> List[Dict]:
        """특정 기간의 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, site_name, players_online, cash_players, 
                       peak_24h, seven_day_avg, data_quality
                FROM daily_data 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, players_online DESC
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            
            return [{
                'date': row[0],
                'site_name': row[1], 
                'players_online': row[2],
                'cash_players': row[3],
                'peak_24h': row[4],
                'seven_day_avg': row[5],
                'data_quality': row[6]
            } for row in results]
    
    def calculate_period_summary(self, data: List[Dict]) -> Dict:
        """기간별 요약 통계 계산"""
        if not data:
            return {
                'total_records': 0,
                'total_players': 0,
                'total_cash_players': 0,
                'avg_players': 0,
                'avg_cash_players': 0,
                'unique_sites': 0,
                'unique_dates': 0,
                'top_sites': [],
                'market_concentration': 0
            }
        
        # 기본 통계
        total_players = sum(row['players_online'] for row in data)
        total_cash = sum(row['cash_players'] for row in data)
        unique_sites = len(set(row['site_name'] for row in data))
        unique_dates = len(set(row['date'] for row in data))
        
        # 사이트별 평균 계산
        site_stats = {}
        for row in data:
            site = row['site_name']
            if site not in site_stats:
                site_stats[site] = []
            site_stats[site].append(row['players_online'])
        
        site_averages = {
            site: sum(values) / len(values) 
            for site, values in site_stats.items()
        }
        
        # 상위 10개 사이트
        top_sites = sorted(site_averages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 시장 집중도 (상위 3개 사이트 점유율)
        if top_sites:
            top3_total = sum(avg for _, avg in top_sites[:3])
            total_avg = sum(avg for _, avg in site_averages.items())
            market_concentration = (top3_total / total_avg * 100) if total_avg > 0 else 0
        else:
            market_concentration = 0
        
        return {
            'total_records': len(data),
            'total_players': total_players,
            'total_cash_players': total_cash,
            'avg_players': total_players / len(data) if data else 0,
            'avg_cash_players': total_cash / len(data) if data else 0,
            'unique_sites': unique_sites,
            'unique_dates': unique_dates,
            'top_sites': top_sites,
            'market_concentration': market_concentration
        }
    
    def daily_comparison_analysis(self, target_date: str = None) -> Dict:
        """일일 비교 분석 (전일 vs 오늘)"""
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        today = datetime.strptime(target_date, '%Y-%m-%d')
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        logger.info(f"일일 분석: {yesterday} vs {today_str}")
        
        # 데이터 조회
        yesterday_data = self.get_date_range_data(yesterday, yesterday)
        today_data = self.get_date_range_data(today_str, today_str)
        
        # 요약 통계
        yesterday_summary = self.calculate_period_summary(yesterday_data)
        today_summary = self.calculate_period_summary(today_data)
        
        # 변화율 계산
        changes = self._calculate_changes(yesterday_summary, today_summary)
        
        # 사이트별 세부 비교
        site_comparison = self._compare_sites_between_periods(yesterday_data, today_data)
        
        return {
            'analysis_type': 'daily',
            'period': f"{yesterday} vs {today_str}",
            'yesterday': {
                'date': yesterday,
                'summary': yesterday_summary,
                'data_count': len(yesterday_data)
            },
            'today': {
                'date': today_str,
                'summary': today_summary,
                'data_count': len(today_data)
            },
            'changes': changes,
            'site_comparison': site_comparison,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def weekly_comparison_analysis(self, target_week_start: str = None) -> Dict:
        """주간 비교 분석 (지난주 vs 이번주)"""
        if not target_week_start:
            today = datetime.now()
            # 이번주 월요일 찾기
            days_since_monday = today.weekday()
            this_monday = today - timedelta(days=days_since_monday)
            target_week_start = this_monday.strftime('%Y-%m-%d')
        
        this_week_start = datetime.strptime(target_week_start, '%Y-%m-%d')
        this_week_end = (this_week_start + timedelta(days=6)).strftime('%Y-%m-%d')
        
        last_week_start = (this_week_start - timedelta(days=7)).strftime('%Y-%m-%d')
        last_week_end = (this_week_start - timedelta(days=1)).strftime('%Y-%m-%d')
        
        logger.info(f"주간 분석: {last_week_start}~{last_week_end} vs {target_week_start}~{this_week_end}")
        
        # 데이터 조회
        last_week_data = self.get_date_range_data(last_week_start, last_week_end)
        this_week_data = self.get_date_range_data(target_week_start, this_week_end)
        
        # 요약 통계
        last_week_summary = self.calculate_period_summary(last_week_data)
        this_week_summary = self.calculate_period_summary(this_week_data)
        
        # 변화율 계산
        changes = self._calculate_changes(last_week_summary, this_week_summary)
        
        # 사이트별 세부 비교
        site_comparison = self._compare_sites_between_periods(last_week_data, this_week_data)
        
        return {
            'analysis_type': 'weekly',
            'period': f"{last_week_start}~{last_week_end} vs {target_week_start}~{this_week_end}",
            'last_week': {
                'period': f"{last_week_start}~{last_week_end}",
                'summary': last_week_summary,
                'data_count': len(last_week_data)
            },
            'this_week': {
                'period': f"{target_week_start}~{this_week_end}",
                'summary': this_week_summary,
                'data_count': len(this_week_data)
            },
            'changes': changes,
            'site_comparison': site_comparison,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def monthly_comparison_analysis(self, target_month: str = None) -> Dict:
        """월간 비교 분석 (지난달 vs 이번달)"""
        if not target_month:
            target_month = datetime.now().strftime('%Y-%m')
        
        # 이번달과 지난달 계산
        this_month = datetime.strptime(target_month + '-01', '%Y-%m-%d')
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # 지난달 전체 기간
        last_month_start = last_month.strftime('%Y-%m-%d')
        last_month_end = (this_month - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 이번달 현재까지
        this_month_start = this_month.strftime('%Y-%m-%d')
        this_month_end = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"월간 분석: {last_month_start}~{last_month_end} vs {this_month_start}~{this_month_end}")
        
        # 데이터 조회
        last_month_data = self.get_date_range_data(last_month_start, last_month_end)
        this_month_data = self.get_date_range_data(this_month_start, this_month_end)
        
        # 요약 통계
        last_month_summary = self.calculate_period_summary(last_month_data)
        this_month_summary = self.calculate_period_summary(this_month_data)
        
        # 변화율 계산
        changes = self._calculate_changes(last_month_summary, this_month_summary)
        
        # 사이트별 세부 비교
        site_comparison = self._compare_sites_between_periods(last_month_data, this_month_data)
        
        return {
            'analysis_type': 'monthly',
            'period': f"{last_month.strftime('%Y-%m')} vs {target_month}",
            'last_month': {
                'period': f"{last_month_start}~{last_month_end}",
                'summary': last_month_summary,
                'data_count': len(last_month_data)
            },
            'this_month': {
                'period': f"{this_month_start}~{this_month_end}",
                'summary': this_month_summary,
                'data_count': len(this_month_data)
            },
            'changes': changes,
            'site_comparison': site_comparison,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_changes(self, old_summary: Dict, new_summary: Dict) -> Dict:
        """두 기간 간 변화율 계산"""
        changes = {}
        
        metrics = ['total_players', 'total_cash_players', 'avg_players', 'avg_cash_players', 
                  'unique_sites', 'market_concentration']
        
        for metric in metrics:
            old_value = old_summary.get(metric, 0)
            new_value = new_summary.get(metric, 0)
            
            if old_value > 0:
                change_pct = ((new_value - old_value) / old_value) * 100
                changes[metric] = {
                    'old': old_value,
                    'new': new_value,
                    'change': new_value - old_value,
                    'change_pct': round(change_pct, 2)
                }
            else:
                changes[metric] = {
                    'old': old_value,
                    'new': new_value,
                    'change': new_value - old_value,
                    'change_pct': 0 if new_value == 0 else 100
                }
        
        return changes
    
    def _compare_sites_between_periods(self, old_data: List[Dict], new_data: List[Dict]) -> Dict:
        """사이트별 기간 간 비교"""
        # 사이트별 평균 플레이어 수 계산
        old_sites = self._calculate_site_averages(old_data)
        new_sites = self._calculate_site_averages(new_data)
        
        # 공통 사이트 찾기
        common_sites = set(old_sites.keys()) & set(new_sites.keys())
        
        site_changes = []
        for site in common_sites:
            old_avg = old_sites[site]
            new_avg = new_sites[site]
            
            change = new_avg - old_avg
            change_pct = (change / old_avg * 100) if old_avg > 0 else 0
            
            site_changes.append({
                'site_name': site,
                'old_avg': round(old_avg, 1),
                'new_avg': round(new_avg, 1),
                'change': round(change, 1),
                'change_pct': round(change_pct, 2)
            })
        
        # 변화율로 정렬
        site_changes.sort(key=lambda x: x['change_pct'], reverse=True)
        
        return {
            'top_gainers': site_changes[:5],
            'top_losers': site_changes[-5:],
            'all_changes': site_changes
        }
    
    def _calculate_site_averages(self, data: List[Dict]) -> Dict[str, float]:
        """사이트별 평균 플레이어 수 계산"""
        site_data = {}
        for row in data:
            site = row['site_name']
            if site not in site_data:
                site_data[site] = []
            site_data[site].append(row['players_online'])
        
        return {
            site: sum(values) / len(values) 
            for site, values in site_data.items()
        }
    
    def generate_comprehensive_report(self, analysis_type: str = 'all') -> Dict:
        """종합 리포트 생성"""
        logger.info(f"종합 리포트 생성: {analysis_type}")
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type
        }
        
        if analysis_type in ['all', 'daily']:
            report['daily_analysis'] = self.daily_comparison_analysis()
        
        if analysis_type in ['all', 'weekly']:
            report['weekly_analysis'] = self.weekly_comparison_analysis()
        
        if analysis_type in ['all', 'monthly']:
            report['monthly_analysis'] = self.monthly_comparison_analysis()
        
        # 전체 데이터베이스 상태
        report['database_status'] = self._get_database_status()
        
        return report
    
    def _get_database_status(self) -> Dict:
        """데이터베이스 전체 상태 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 전체 통계
            cursor.execute("SELECT COUNT(*) FROM daily_data")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT site_name) FROM daily_data")
            total_sites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT date) FROM daily_data")
            total_dates = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(date), MAX(date) FROM daily_data")
            date_range = cursor.fetchone()
            
            # 데이터 품질 분포
            cursor.execute("""
                SELECT data_quality, COUNT(*) 
                FROM daily_data 
                GROUP BY data_quality
            """)
            quality_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_records': total_records,
                'total_sites': total_sites,
                'total_dates': total_dates,
                'date_range': {
                    'start': date_range[0],
                    'end': date_range[1]
                },
                'quality_distribution': quality_distribution
            }

def main():
    analyzer = MultiPeriodAnalyzer()
    
    print("=" * 80)
    print("🏆 다기간 포커 데이터 비교 분석 시스템")
    print("=" * 80)
    
    print("\n분석 유형을 선택하세요:")
    print("1. 일일 분석 (전일 vs 오늘)")
    print("2. 주간 분석 (지난주 vs 이번주)")
    print("3. 월간 분석 (지난달 vs 이번달)")
    print("4. 종합 분석 (모든 기간)")
    print("5. 데이터베이스 상태 확인")
    
    try:
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == '1':
            print("\n📅 일일 비교 분석 실행 중...")
            result = analyzer.daily_comparison_analysis()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif choice == '2':
            print("\n📊 주간 비교 분석 실행 중...")
            result = analyzer.weekly_comparison_analysis()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif choice == '3':
            print("\n📈 월간 비교 분석 실행 중...")
            result = analyzer.monthly_comparison_analysis()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif choice == '4':
            print("\n🎯 종합 분석 실행 중...")
            result = analyzer.generate_comprehensive_report()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif choice == '5':
            print("\n🗃️ 데이터베이스 상태 확인 중...")
            status = analyzer._get_database_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()