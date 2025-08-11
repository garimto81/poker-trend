#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 실제 데이터 기반 플랫폼 분석기
- 7/30부터의 데이터 사용
- PokerStars US/Ontario 제외 (오염된 데이터)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

class FirebasePlatformAnalyzer:
    """Firebase 실제 데이터 기반 플랫폼 분석"""
    
    # 제외할 사이트 목록 (데이터 오염)
    EXCLUDED_SITES = [
        'PokerStars US',
        'PokerStars Ontario'
    ]
    
    def __init__(self):
        self.report_type = os.getenv('REPORT_TYPE', 'daily').lower()
        self.firebase_project_id = "poker-online-analyze"
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        self.db_path = 'platform_history.db'
        self.init_database()
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT NOT NULL,
                date TEXT NOT NULL,
                online_players INTEGER,
                cash_players INTEGER,
                tournament_players INTEGER,
                peak_24h INTEGER,
                seven_day_avg INTEGER,
                collected_at TIMESTAMP,
                UNIQUE(platform_name, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def fetch_firebase_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Firebase에서 기간별 데이터 수집"""
        print(f"Firebase 데이터 수집: {start_date} ~ {end_date}")
        
        sites_url = f"{self.base_url}/sites"
        aggregated_data = {}
        
        try:
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
                return []
            
            data = response.json()
            documents = data.get('documents', [])
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                
                site_name = self.extract_value(fields.get('name', {}), doc_name)
                
                # 제외 사이트 체크
                if site_name in self.EXCLUDED_SITES:
                    print(f"[SKIP] {site_name} - 오염된 데이터로 제외")
                    continue
                
                # 트래픽 로그 가져오기 (전체 기간)
                traffic_url = f"{self.base_url}/sites/{doc_name}/traffic_logs?pageSize=100&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        for traffic_doc in traffic_docs:
                            traffic_fields = traffic_doc.get('fields', {})
                            collected_at = self.extract_value(traffic_fields.get('collected_at', {}), '')
                            
                            if collected_at:
                                # 날짜 파싱
                                date_str = collected_at.split('T')[0]
                                
                                # 기간 필터링
                                if start_date <= date_str <= end_date:
                                    if site_name not in aggregated_data:
                                        aggregated_data[site_name] = {}
                                    
                                    if date_str not in aggregated_data[site_name]:
                                        aggregated_data[site_name][date_str] = []
                                    
                                    log_data = {
                                        'collected_at': collected_at,
                                        'online_players': self.extract_value(traffic_fields.get('players_online', {}), 0),
                                        'cash_players': self.extract_value(traffic_fields.get('cash_players', {}), 0),
                                        'peak_24h': self.extract_value(traffic_fields.get('peak_24h', {}), 0),
                                        'seven_day_avg': self.extract_value(traffic_fields.get('seven_day_avg', {}), 0),
                                    }
                                    
                                    aggregated_data[site_name][date_str].append(log_data)
                                    
                except Exception as e:
                    pass
            
            # 데이터 정리 및 평균 계산
            result_data = []
            for platform, dates in aggregated_data.items():
                for date, logs in dates.items():
                    if logs:
                        # 일별 평균 계산
                        avg_data = {
                            'platform_name': platform,
                            'date': date,
                            'online_players': sum(log['online_players'] for log in logs) // len(logs),
                            'cash_players': sum(log['cash_players'] for log in logs) // len(logs),
                            'tournament_players': 0,  # Firebase에 없는 데이터
                            'peak_24h': max(log['peak_24h'] for log in logs),
                            'seven_day_avg': sum(log['seven_day_avg'] for log in logs) // len(logs),
                            'collected_at': logs[0]['collected_at']
                        }
                        
                        # 토너먼트 플레이어 추정 (온라인 - 캐시의 약 40%)
                        cash = avg_data['cash_players']
                        online = avg_data['online_players']
                        if online > cash:
                            avg_data['tournament_players'] = int((online - cash) * 0.4)
                        
                        result_data.append(avg_data)
                        
                        # DB에 저장
                        self.save_to_database(avg_data)
            
            print(f"[SUCCESS] {len(result_data)}개 데이터 포인트 수집")
            return result_data
            
        except Exception as e:
            print(f"[ERROR] Firebase 데이터 수집 오류: {e}")
            return []
    
    def extract_value(self, field_data: Dict, default_value=''):
        """Firebase 필드에서 값 추출"""
        if not field_data:
            return default_value
        
        if 'stringValue' in field_data:
            return field_data['stringValue']
        elif 'integerValue' in field_data:
            return int(field_data['integerValue'])
        elif 'doubleValue' in field_data:
            return float(field_data['doubleValue'])
        elif 'timestampValue' in field_data:
            return field_data['timestampValue']
        elif 'booleanValue' in field_data:
            return field_data['booleanValue']
        else:
            return default_value
    
    def save_to_database(self, data: Dict):
        """데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO platform_data 
            (platform_name, date, online_players, cash_players, tournament_players, 
             peak_24h, seven_day_avg, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['platform_name'],
            data['date'],
            data['online_players'],
            data['cash_players'],
            data['tournament_players'],
            data['peak_24h'],
            data['seven_day_avg'],
            data.get('collected_at', datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
    
    def get_date_range(self) -> tuple:
        """보고서 타입에 따른 날짜 범위 계산"""
        # 기준일: 8/10 (최신 데이터가 있는 날짜)
        base_date = datetime(2025, 8, 10)
        
        if self.report_type == 'daily':
            # 일간: 8/10 하루
            start_date = base_date
            end_date = base_date
        elif self.report_type == 'weekly':
            # 주간: 8/4 ~ 8/10 (7일)
            end_date = base_date
            start_date = base_date - timedelta(days=6)
        else:  # monthly
            # 월간: 7/30 ~ 8/10 (데이터 시작일부터)
            start_date = datetime(2025, 7, 30)
            end_date = base_date
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def aggregate_period_data(self, data: List[Dict]) -> List[Dict]:
        """기간별 데이터 집계"""
        platform_aggregates = {}
        
        for entry in data:
            platform = entry['platform_name']
            
            if platform not in platform_aggregates:
                platform_aggregates[platform] = {
                    'platform_name': platform,
                    'online_players_sum': 0,
                    'cash_players_sum': 0,
                    'tournament_players_sum': 0,
                    'peak_24h_max': 0,
                    'seven_day_avg_sum': 0,
                    'count': 0,
                    'dates': []
                }
            
            agg = platform_aggregates[platform]
            agg['online_players_sum'] += entry['online_players']
            agg['cash_players_sum'] += entry['cash_players']
            agg['tournament_players_sum'] += entry['tournament_players']
            agg['peak_24h_max'] = max(agg['peak_24h_max'], entry['peak_24h'])
            agg['seven_day_avg_sum'] += entry['seven_day_avg']
            agg['count'] += 1
            agg['dates'].append(entry['date'])
        
        # 평균 계산 및 최종 데이터 생성
        result = []
        for platform, agg in platform_aggregates.items():
            if agg['count'] > 0:
                result.append({
                    'platform_name': platform,
                    'online_players': agg['online_players_sum'] // agg['count'],
                    'cash_players': agg['cash_players_sum'] // agg['count'],
                    'tournament_players': agg['tournament_players_sum'] // agg['count'],
                    'peak_24h': agg['peak_24h_max'],
                    'seven_day_avg': agg['seven_day_avg_sum'] // agg['count'],
                    'data_points': agg['count'],
                    'date_range': f"{min(agg['dates'])} ~ {max(agg['dates'])}"
                })
        
        # 온라인 플레이어 기준 정렬
        result.sort(key=lambda x: x['online_players'], reverse=True)
        
        return result
    
    def calculate_market_share(self, platforms: List[Dict]) -> List[Dict]:
        """시장 점유율 계산"""
        total_online = sum(p['online_players'] for p in platforms)
        
        for platform in platforms:
            if total_online > 0:
                platform['market_share'] = round(
                    (platform['online_players'] / total_online) * 100, 2
                )
            else:
                platform['market_share'] = 0
        
        return platforms
    
    def generate_report(self) -> Dict:
        """리포트 생성"""
        start_date, end_date = self.get_date_range()
        
        # Firebase에서 데이터 수집
        raw_data = self.fetch_firebase_data(start_date, end_date)
        
        if not raw_data:
            print("[WARNING] Firebase 데이터가 없습니다.")
            return None
        
        # 기간별 집계
        if self.report_type == 'daily':
            # 일간은 그대로 사용하되 온라인 플레이어 기준 정렬
            platforms = sorted(raw_data, key=lambda x: x['online_players'], reverse=True)
        else:
            # 주간/월간은 평균 계산
            platforms = self.aggregate_period_data(raw_data)
        
        # 시장 점유율 계산
        platforms = self.calculate_market_share(platforms)
        
        # 상위 10개만 선택
        top_platforms = platforms[:10]
        
        # 통계 계산
        total_online = sum(p['online_players'] for p in platforms)
        total_cash = sum(p['cash_players'] for p in platforms)
        
        # 경쟁 분석
        competition_analysis = self.analyze_competition(top_platforms)
        
        # 인사이트 생성
        insights = self.generate_insights(top_platforms, competition_analysis)
        
        report = {
            'report_type': self.report_type,
            'data_period': {
                'start': start_date,
                'end': end_date
            },
            'generated_at': datetime.now().isoformat(),
            'data_source': 'Firebase (PokerStars US/Ontario excluded)',
            'summary': {
                'total_platforms': len(platforms),
                'total_online_players': total_online,
                'total_cash_players': total_cash,
                'market_leader': top_platforms[0]['platform_name'] if top_platforms else 'N/A',
                'market_leader_share': top_platforms[0]['market_share'] if top_platforms else 0
            },
            'top_platforms': top_platforms,
            'competition_analysis': competition_analysis,
            'insights': insights
        }
        
        # JSON 파일로 저장
        filename = f"firebase_platform_report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVED] {filename}")
        
        return report
    
    def analyze_competition(self, platforms: List[Dict]) -> Dict:
        """경쟁 분석"""
        if len(platforms) < 3:
            return {}
        
        # HHI (Herfindahl-Hirschman Index) 계산
        hhi = sum(p['market_share'] ** 2 for p in platforms)
        
        # 경쟁 강도 판단
        if hhi > 2500:
            intensity = "매우 집중"
        elif hhi > 1500:
            intensity = "보통"
        else:
            intensity = "경쟁 치열"
        
        return {
            'report_type': self.report_type,
            'analysis_date': platforms[0].get('date_range', platforms[0].get('date', '')),
            'leader': {
                'name': platforms[0]['platform_name'],
                'share': platforms[0]['market_share'],
                'players': platforms[0]['online_players']
            },
            'second': {
                'name': platforms[1]['platform_name'],
                'share': platforms[1]['market_share'],
                'players': platforms[1]['online_players']
            } if len(platforms) > 1 else None,
            'third': {
                'name': platforms[2]['platform_name'],
                'share': platforms[2]['market_share'],
                'players': platforms[2]['online_players']
            } if len(platforms) > 2 else None,
            'market_concentration': round(hhi, 2),
            'competition_intensity': intensity,
            'total_market_size': sum(p['online_players'] for p in platforms)
        }
    
    def generate_insights(self, platforms: List[Dict], competition: Dict) -> List[str]:
        """인사이트 생성"""
        insights = []
        
        if platforms:
            # 1위 플랫폼 분석
            leader = platforms[0]
            insights.append(
                f"[LEADER] {leader['platform_name']} leads with {leader['market_share']}% market share"
            )
            
            # 캐시 게임 리더
            cash_leader = max(platforms, key=lambda x: x['cash_players'])
            insights.append(
                f"[CASH] {cash_leader['platform_name']} dominates cash games: {cash_leader['cash_players']:,} players"
            )
            
            # 데이터 소스 정보
            insights.append(
                f"[DATA] Based on Firebase data from {self.get_date_range()[0]} (excluding contaminated sites)"
            )
            
            # 보고서 타입별 추가 인사이트
            if self.report_type == 'daily':
                if leader.get('peak_24h', 0) > 0:
                    insights.append(
                        f"[PEAK] {leader['platform_name']} 24h peak: {leader['peak_24h']:,} players"
                    )
            elif self.report_type == 'weekly':
                total_market = competition.get('total_market_size', 0)
                insights.append(
                    f"[WEEKLY] Average market size: {total_market:,} players online"
                )
            else:  # monthly
                insights.append(
                    f"[MONTHLY] Full month analysis from Firebase historical data"
                )
        
        return insights

def main():
    """메인 실행 함수"""
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if report:
        print("\n" + "="*80)
        print(f"Firebase Platform Analysis Report - {report['report_type'].upper()}")
        print("="*80)
        print(f"Period: {report['data_period']['start']} ~ {report['data_period']['end']}")
        print(f"Total Platforms: {report['summary']['total_platforms']}")
        print(f"Total Online: {report['summary']['total_online_players']:,}")
        print(f"Market Leader: {report['summary']['market_leader']} ({report['summary']['market_leader_share']}%)")
        print("\nTop 5 Platforms:")
        for i, platform in enumerate(report['top_platforms'][:5], 1):
            print(f"{i}. {platform['platform_name']:<20} {platform['online_players']:>8,} ({platform['market_share']:>5.1f}%)")
    else:
        print("[ERROR] 리포트 생성 실패")
    
    return report

if __name__ == "__main__":
    main()