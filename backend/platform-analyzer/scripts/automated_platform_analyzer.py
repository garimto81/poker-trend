#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동화된 플랫폼 분석기
- GitHub Actions에서 자동 실행 가능
- REPORT_TYPE에 따른 동적 분석
- 실제 데이터 수집 (모킹된 데이터로 시작)
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

# 현실적인 플랫폼 데이터 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from realistic_platform_data import RealisticPlatformData

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedPlatformAnalyzer:
    """자동화된 플랫폼 분석기"""
    
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.report_type = os.getenv('REPORT_TYPE', 'daily')
        self.data_start = os.getenv('DATA_PERIOD_START', '')
        self.data_end = os.getenv('DATA_PERIOD_END', '')
        
        # 데이터베이스 초기화
        self._ensure_database_schema()
        
        logger.info(f"플랫폼 분석기 초기화 - 리포트 타입: {self.report_type}")
        logger.info(f"데이터 기간: {self.data_start} ~ {self.data_end}")
    
    def _ensure_database_schema(self):
        """데이터베이스 스키마 확인 및 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 플랫폼 데이터 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS platform_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                platform_name TEXT NOT NULL,
                online_players INTEGER DEFAULT 0,
                cash_players INTEGER DEFAULT 0,
                tournament_players INTEGER DEFAULT 0,
                peak_24h INTEGER DEFAULT 0,
                seven_day_avg INTEGER DEFAULT 0,
                market_share REAL DEFAULT 0,
                growth_rate REAL DEFAULT 0,
                data_source TEXT DEFAULT 'simulated',
                created_at TEXT NOT NULL,
                UNIQUE(date, platform_name)
            )
        """)
        
        # 경쟁 분석 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competition_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                report_type TEXT NOT NULL,
                leader_platform TEXT,
                leader_share REAL,
                second_platform TEXT,
                second_share REAL,
                third_platform TEXT,
                third_share REAL,
                market_concentration REAL,
                competition_intensity TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(analysis_date, report_type)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_platform_data(self) -> List[Dict]:
        """플랫폼 데이터 수집 (현실적인 데이터 사용)"""
        logger.info("플랫폼 데이터 수집 시작...")
        
        # 날짜 설정
        current_date = self.data_end if self.data_end else datetime.now().strftime('%Y-%m-%d')
        
        # 리포트 타입에 따른 데이터 수집
        if self.report_type == 'daily':
            collected_data = RealisticPlatformData.get_daily_data(current_date)
        elif self.report_type == 'weekly':
            collected_data = RealisticPlatformData.get_weekly_data(current_date)
        else:  # monthly
            collected_data = RealisticPlatformData.get_monthly_data(current_date)
        
        # 데이터베이스 저장용 필드 추가
        for platform in collected_data:
            platform['date'] = current_date
        
        logger.info(f"플랫폼 데이터 수집 완료: {len(collected_data)}개 플랫폼")
        logger.info(f"리더: {collected_data[0]['platform_name']} ({collected_data[0]['market_share']}%)")
        
        return collected_data
    
    def save_platform_data(self, data: List[Dict]) -> int:
        """수집된 데이터를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for platform in data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO platform_data 
                    (date, platform_name, online_players, cash_players, tournament_players,
                     peak_24h, seven_day_avg, market_share, growth_rate, data_source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    platform['date'],
                    platform['platform_name'],
                    platform['online_players'],
                    platform['cash_players'],
                    platform['tournament_players'],
                    platform['peak_24h'],
                    platform['seven_day_avg'],
                    platform['market_share'],
                    platform['growth_rate'],
                    'simulated',  # 실제 데이터 소스로 변경 예정
                    datetime.now().isoformat()
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"데이터 저장 실패 ({platform['platform_name']}): {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"데이터베이스 저장 완료: {saved_count}개 플랫폼")
        return saved_count
    
    def analyze_competition(self, data: List[Dict]) -> Dict:
        """경쟁 구도 분석"""
        if not data:
            return {}
        
        # TOP 3 플랫폼
        top3 = data[:3]
        
        # 시장 집중도 (HHI - Herfindahl-Hirschman Index)
        hhi = sum(p['market_share'] ** 2 for p in data)
        
        # 경쟁 강도 판단
        if hhi > 5000:
            competition_intensity = "독점적"
        elif hhi > 2500:
            competition_intensity = "집중적"
        elif hhi > 1500:
            competition_intensity = "보통"
        else:
            competition_intensity = "경쟁적"
        
        # 2-3위 격차 분석
        gap_2_3 = top3[1]['online_players'] - top3[2]['online_players'] if len(top3) >= 3 else 0
        gap_percentage = (gap_2_3 / top3[2]['online_players'] * 100) if len(top3) >= 3 and top3[2]['online_players'] > 0 else 0
        
        analysis = {
            'report_type': self.report_type,
            'analysis_date': data[0]['date'] if data else datetime.now().strftime('%Y-%m-%d'),
            'leader': {
                'name': top3[0]['platform_name'],
                'share': top3[0]['market_share'],
                'players': top3[0]['online_players'],
                'growth': top3[0]['growth_rate']
            },
            'second': {
                'name': top3[1]['platform_name'] if len(top3) > 1 else 'N/A',
                'share': top3[1]['market_share'] if len(top3) > 1 else 0,
                'players': top3[1]['online_players'] if len(top3) > 1 else 0,
                'growth': top3[1]['growth_rate'] if len(top3) > 1 else 0
            },
            'third': {
                'name': top3[2]['platform_name'] if len(top3) > 2 else 'N/A',
                'share': top3[2]['market_share'] if len(top3) > 2 else 0,
                'players': top3[2]['online_players'] if len(top3) > 2 else 0,
                'growth': top3[2]['growth_rate'] if len(top3) > 2 else 0
            },
            'market_concentration': round(hhi, 2),
            'competition_intensity': competition_intensity,
            'gap_2_3': gap_2_3,
            'gap_2_3_percentage': round(gap_percentage, 1),
            'total_market_size': sum(p['online_players'] for p in data)
        }
        
        # 경쟁 분석 저장
        self._save_competition_analysis(analysis)
        
        return analysis
    
    def _save_competition_analysis(self, analysis: Dict):
        """경쟁 분석 결과 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO competition_analysis
                (analysis_date, report_type, leader_platform, leader_share,
                 second_platform, second_share, third_platform, third_share,
                 market_concentration, competition_intensity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis['analysis_date'],
                analysis['report_type'],
                analysis['leader']['name'],
                analysis['leader']['share'],
                analysis['second']['name'],
                analysis['second']['share'],
                analysis['third']['name'],
                analysis['third']['share'],
                analysis['market_concentration'],
                analysis['competition_intensity'],
                datetime.now().isoformat()
            ))
            conn.commit()
            logger.info("경쟁 분석 결과 저장 완료")
        except Exception as e:
            logger.error(f"경쟁 분석 저장 실패: {e}")
        finally:
            conn.close()
    
    def generate_insights(self, data: List[Dict], competition: Dict) -> List[str]:
        """핵심 인사이트 생성"""
        insights = []
        
        # 1. 시장 지배력 인사이트
        leader = competition['leader']
        if leader['share'] > 40:
            insights.append(f"[DOMINANCE] {leader['name']} dominates with {leader['share']:.1f}% market share")
        
        # 2. 성장률 인사이트
        fastest_growing = max(data, key=lambda x: x['growth_rate'])
        if fastest_growing['growth_rate'] > 5:
            insights.append(f"[GROWTH] {fastest_growing['platform_name']} growing fastest at {fastest_growing['growth_rate']:.1f}%")
        
        # 3. 캐시 게임 인사이트
        cash_leader = max(data, key=lambda x: x['cash_players'])
        cash_ratio = (cash_leader['cash_players'] / cash_leader['online_players']) * 100
        insights.append(f"[CASH] {cash_leader['platform_name']} leads cash games with {cash_leader['cash_players']:,} players ({cash_ratio:.1f}%)")
        
        # 4. 경쟁 구도 인사이트
        if competition['gap_2_3_percentage'] > 20:
            insights.append(f"[COMPETITION] 2nd-3rd gap at {competition['gap_2_3_percentage']:.1f}% - stable 2nd position")
        else:
            insights.append(f"[COMPETITION] 2nd-3rd gap at {competition['gap_2_3_percentage']:.1f}% - intense competition")
        
        # 5. 시장 집중도 인사이트
        if competition['market_concentration'] > 5000:
            insights.append(f"[CONCENTRATION] HHI {competition['market_concentration']:.0f} - highly concentrated market")
        
        # 6. 리포트 타입별 특별 인사이트
        if self.report_type == 'monthly':
            # 월간 트렌드
            avg_growth = sum(p['growth_rate'] for p in data[:5]) / 5
            if avg_growth > 0:
                insights.append(f"[TREND] TOP 5 avg growth {avg_growth:.1f}% - market expanding")
            else:
                insights.append(f"[TREND] TOP 5 avg growth {avg_growth:.1f}% - market stagnating")
        elif self.report_type == 'weekly':
            # 주간 변동성
            insights.append(f"[WEEKLY] Market size: {competition['total_market_size']:,} players online")
        else:  # daily
            # 일간 피크 타임
            peak_platform = max(data, key=lambda x: x['peak_24h'])
            insights.append(f"[PEAK] {peak_platform['platform_name']} 24h peak: {peak_platform['peak_24h']:,} players")
        
        return insights
    
    def generate_report(self) -> Dict:
        """최종 리포트 생성"""
        # 1. 데이터 수집
        platform_data = self.collect_platform_data()
        
        # 2. 데이터 저장
        self.save_platform_data(platform_data)
        
        # 3. 경쟁 분석
        competition_analysis = self.analyze_competition(platform_data)
        
        # 4. 인사이트 생성
        insights = self.generate_insights(platform_data, competition_analysis)
        
        # 5. 리포트 구성
        report = {
            'report_type': self.report_type,
            'data_period': {
                'start': self.data_start,
                'end': self.data_end
            },
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_platforms': len(platform_data),
                'total_online_players': sum(p['online_players'] for p in platform_data),
                'total_cash_players': sum(p['cash_players'] for p in platform_data),
                'market_leader': competition_analysis['leader']['name'],
                'market_leader_share': competition_analysis['leader']['share']
            },
            'top_platforms': platform_data[:10],
            'competition_analysis': competition_analysis,
            'insights': insights
        }
        
        # 6. JSON 파일로 저장
        report_file = f"platform_report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"리포트 생성 완료: {report_file}")
        
        return report

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("Automated Platform Analysis System")
    print("=" * 80)
    
    analyzer = AutomatedPlatformAnalyzer()
    
    # 리포트 생성
    report = analyzer.generate_report()
    
    # 결과 출력
    print(f"\n[COMPLETE] {report['report_type'].upper()} Platform Analysis")
    print(f"Period: {report['data_period']['start']} ~ {report['data_period']['end']}")
    print(f"Analyzed Platforms: {report['summary']['total_platforms']}")
    print(f"Total Online Players: {report['summary']['total_online_players']:,}")
    print(f"Market Leader: {report['summary']['market_leader']} ({report['summary']['market_leader_share']:.1f}%)")
    
    print("\nTOP 5 Platforms:")
    for i, platform in enumerate(report['top_platforms'][:5], 1):
        print(f"{i}. {platform['platform_name']:<15} - {platform['online_players']:>7,} players ({platform['market_share']:>5.1f}%) [{platform['growth_rate']:+.1f}%]")
    
    print("\nKey Insights:")
    for insight in report['insights']:
        print(f"  {insight}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())