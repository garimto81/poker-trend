#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History-based Poker Platform Analyzer
자체 수집한 히스토리 데이터를 기반으로 정확한 트렌드 분석
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_data_collector import DailyDataCollector
from analyze_live_data import LivePokerDataAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoryBasedAnalyzer:
    def __init__(self, db_path: str = "poker_history.db"):
        self.db_path = db_path
        self.collector = DailyDataCollector(db_path)
        self.live_analyzer = LivePokerDataAnalyzer()
    
    def analyze_with_history(self, analysis_type: str = 'daily') -> Dict:
        """Perform trend analysis using historical data"""
        logger.info(f"📊 히스토리 기반 {analysis_type} 분석 시작")
        
        # Get current data
        current_data = self.live_analyzer.crawl_pokerscout_data()
        if not current_data:
            logger.error("❌ 현재 데이터 수집 실패")
            return {}
        
        # Validate current data
        validated_current = self.collector._validate_and_clean_data(current_data)
        
        # Calculate growth rates based on analysis type
        if analysis_type == 'daily':
            growth_data = self.collector.calculate_growth_from_history(validated_current, days_back=1)
        elif analysis_type == 'weekly':
            growth_data = self.collector.calculate_growth_from_history(validated_current, days_back=7)
        elif analysis_type == 'monthly':
            growth_data = self.collector.calculate_growth_from_history(validated_current, days_back=30)
        else:
            growth_data = self.collector.calculate_growth_from_history(validated_current, days_back=7)
        
        # Analyze results
        analysis_result = self._analyze_growth_patterns(growth_data, analysis_type)
        
        # Store analysis results
        self._store_analysis_results(analysis_type, analysis_result, growth_data)
        
        return analysis_result
    
    def _analyze_growth_patterns(self, growth_data: List[Dict], analysis_type: str) -> Dict:
        """Analyze growth patterns and identify significant changes"""
        logger.info("🔍 성장 패턴 분석")
        
        # Separate data by growth type
        calculated_growth = [g for g in growth_data if g['growth_type'] == 'calculated']
        fallback_growth = [g for g in growth_data if g['growth_type'] == 'fallback']
        
        # Calculate thresholds based on analysis type
        thresholds = {
            'daily': {'minor': 5, 'major': 15, 'extreme': 50},
            'weekly': {'minor': 10, 'major': 25, 'extreme': 100},
            'monthly': {'minor': 20, 'major': 50, 'extreme': 200}
        }
        
        threshold = thresholds.get(analysis_type, thresholds['weekly'])
        
        # Categorize platforms by growth
        significant_changes = []
        growing_platforms = []
        declining_platforms = []
        stable_platforms = []
        
        total_online = 0
        total_historical = 0
        reliable_comparisons = 0
        
        for growth in calculated_growth:
            site_name = growth['site_name']
            current = growth['current_online']
            growth_rate = growth['growth_rate']
            
            total_online += current
            total_historical += growth['historical_online']
            reliable_comparisons += 1
            
            # Categorize by growth rate
            if abs(growth_rate) >= threshold['major']:
                significant_changes.append({
                    'platform': site_name,
                    'current': current,
                    'historical': growth['historical_online'],
                    'growth_rate': growth_rate,
                    'severity': 'extreme' if abs(growth_rate) >= threshold['extreme'] else 'major',
                    'direction': 'up' if growth_rate > 0 else 'down'
                })
            
            if growth_rate > threshold['minor']:
                growing_platforms.append((site_name, growth_rate, current))
            elif growth_rate < -threshold['minor']:
                declining_platforms.append((site_name, growth_rate, current))
            else:
                stable_platforms.append((site_name, growth_rate, current))
        
        # Sort by absolute growth rate
        significant_changes.sort(key=lambda x: abs(x['growth_rate']), reverse=True)
        growing_platforms.sort(key=lambda x: x[1], reverse=True)
        declining_platforms.sort(key=lambda x: x[1])
        
        # Determine alert level
        alert_level = 'none'
        extreme_changes = len([c for c in significant_changes if c['severity'] == 'extreme'])
        major_changes = len([c for c in significant_changes if c['severity'] == 'major'])
        
        if extreme_changes >= 3 or major_changes >= 5:
            alert_level = 'high'
        elif extreme_changes >= 1 or major_changes >= 3:
            alert_level = 'medium'
        elif major_changes >= 1:
            alert_level = 'low'
        
        # Calculate market metrics
        market_growth = 0
        if total_historical > 0:
            market_growth = ((total_online - total_historical) / total_historical) * 100
        
        # Generate summary
        summary_text = self._generate_summary(
            analysis_type, significant_changes, growing_platforms, 
            declining_platforms, market_growth, alert_level, reliable_comparisons
        )
        
        return {
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'alert_level': alert_level,
            'summary_text': summary_text,
            'market_metrics': {
                'total_online': total_online,
                'total_historical': total_historical,
                'market_growth': market_growth,
                'platforms_analyzed': len(growth_data),
                'reliable_comparisons': reliable_comparisons,
                'fallback_comparisons': len(fallback_growth)
            },
            'significant_changes': significant_changes[:10],  # Top 10
            'growing_platforms': growing_platforms[:10],
            'declining_platforms': declining_platforms[:10],
            'stable_platforms': len(stable_platforms),
            'thresholds_used': threshold
        }
    
    def _generate_summary(self, analysis_type: str, significant_changes: List[Dict], 
                         growing: List, declining: List, market_growth: float,
                         alert_level: str, reliable_comparisons: int) -> str:
        """Generate human-readable summary"""
        
        if alert_level == 'none':
            return f"온라인 포커 플랫폼 시장이 안정적입니다. {reliable_comparisons}개 플랫폼을 분석한 결과 큰 변화가 감지되지 않았습니다."
        
        summary_parts = []
        
        # Market overview
        if market_growth > 10:
            summary_parts.append(f"전체 시장이 {market_growth:+.1f}% 성장하여 상승세를 보이고 있습니다.")
        elif market_growth < -10:
            summary_parts.append(f"전체 시장이 {market_growth:+.1f}% 하락하여 하락세를 보이고 있습니다.")
        else:
            summary_parts.append(f"전체 시장이 {market_growth:+.1f}% 변동으로 안정적입니다.")
        
        # Significant changes
        if significant_changes:
            extreme_count = len([c for c in significant_changes if c['severity'] == 'extreme'])
            major_count = len([c for c in significant_changes if c['severity'] == 'major'])
            
            if extreme_count > 0:
                summary_parts.append(f"{extreme_count}개 플랫폼에서 극단적 변화가 감지되었습니다.")
            
            if major_count > 0:
                summary_parts.append(f"{major_count}개 플랫폼에서 주요 변화가 확인되었습니다.")
            
            # Top changer
            top_change = significant_changes[0]
            direction = "급증" if top_change['direction'] == 'up' else "급감"
            summary_parts.append(f"{top_change['platform']}에서 가장 큰 변화({direction} {abs(top_change['growth_rate']):.1f}%)를 보였습니다.")
        
        # Growing platforms
        if len(growing) >= 3:
            summary_parts.append(f"{len(growing)}개 플랫폼이 성장세를 보이고 있습니다.")
        
        # Declining platforms
        if len(declining) >= 3:
            summary_parts.append(f"{len(declining)}개 플랫폼이 하락세를 보이고 있습니다.")
        
        return " ".join(summary_parts)
    
    def _store_analysis_results(self, analysis_type: str, analysis_result: Dict, growth_data: List[Dict]):
        """Store analysis results in database"""
        logger.info("💾 분석 결과 저장")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analysis_results
                (date, analysis_type, total_online, total_cash, active_platforms,
                 market_leader, significant_changes, alert_level, summary_text, data_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime('%Y-%m-%d'),
                analysis_type,
                analysis_result['market_metrics']['total_online'],
                0,  # total_cash - will calculate if needed
                analysis_result['market_metrics']['platforms_analyzed'],
                analysis_result['significant_changes'][0]['platform'] if analysis_result['significant_changes'] else 'N/A',
                len(analysis_result['significant_changes']),
                analysis_result['alert_level'],
                analysis_result['summary_text'],
                json.dumps(growth_data, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
        
        logger.info("✅ 분석 결과 저장 완료")
    
    def get_trend_chart_data(self, site_name: str, days: int = 30) -> Dict:
        """Get trend chart data for a specific platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, players_online, cash_players, peak_24h
                FROM daily_data
                WHERE site_name = ?
                ORDER BY date DESC
                LIMIT ?
            """, (site_name, days))
            
            rows = cursor.fetchall()
            
            if not rows:
                return {}
            
            dates = [row[0] for row in reversed(rows)]
            online_players = [row[1] for row in reversed(rows)]
            cash_players = [row[2] for row in reversed(rows)]
            peaks = [row[3] for row in reversed(rows)]
            
            return {
                'site_name': site_name,
                'dates': dates,
                'online_players': online_players,
                'cash_players': cash_players,
                'peak_24h': peaks,
                'days': len(dates)
            }
    
    def show_comprehensive_analysis(self, analysis_type: str = 'weekly'):
        """Show comprehensive analysis with charts and insights"""
        print("=" * 100)
        print(f"📊 포커 플랫폼 히스토리 기반 {analysis_type.upper()} 분석")
        print("=" * 100)
        
        # Perform analysis
        result = self.analyze_with_history(analysis_type)
        
        if not result:
            print("❌ 분석 실패")
            return
        
        # Show summary
        print(f"\n🎯 분석 요약:")
        print(f"분석 유형: {result['analysis_type']}")
        print(f"경고 수준: {result['alert_level']}")
        print(f"분석 시각: {result['timestamp']}")
        print()
        print(f"📋 요약:")
        print(f"  {result['summary_text']}")
        
        # Show market metrics
        metrics = result['market_metrics']
        print(f"\n📈 시장 지표:")
        print(f"  현재 총 온라인 플레이어: {metrics['total_online']:,}명")
        print(f"  이전 총 온라인 플레이어: {metrics['total_historical']:,}명")
        print(f"  시장 성장률: {metrics['market_growth']:+.2f}%")
        print(f"  분석된 플랫폼: {metrics['platforms_analyzed']}개")
        print(f"  신뢰할 수 있는 비교: {metrics['reliable_comparisons']}개")
        print(f"  대체 데이터 사용: {metrics['fallback_comparisons']}개")
        
        # Show significant changes
        if result['significant_changes']:
            print(f"\n🚨 주요 변화 ({len(result['significant_changes'])}개):")
            print(f"{'플랫폼':<25} {'현재':<12} {'이전':<12} {'성장률':<12} {'방향':<8}")
            print("-" * 80)
            
            for change in result['significant_changes'][:10]:
                direction_icon = "🚀" if change['direction'] == 'up' else "📉"
                severity_icon = "⚠️" if change['severity'] == 'extreme' else "📊"
                
                print(f"{change['platform'][:24]:<25} {change['current']:<12,} {change['historical']:<12,} {change['growth_rate']:+10.1f}% {direction_icon}{severity_icon}")
        
        # Show growing platforms
        if result['growing_platforms']:
            print(f"\n📈 성장 플랫폼 ({len(result['growing_platforms'])}개):")
            for platform, growth, current in result['growing_platforms'][:5]:
                print(f"  🟢 {platform}: +{growth:.1f}% ({current:,}명)")
        
        # Show declining platforms
        if result['declining_platforms']:
            print(f"\n📉 하락 플랫폼 ({len(result['declining_platforms'])}개):")
            for platform, growth, current in result['declining_platforms'][:5]:
                print(f"  🔴 {platform}: {growth:.1f}% ({current:,}명)")
        
        # Show data quality info
        print(f"\n📊 데이터 품질:")
        print(f"  안정적 플랫폼: {result['stable_platforms']}개")
        print(f"  사용된 임계값: 소폭 {result['thresholds_used']['minor']}%, 주요 {result['thresholds_used']['major']}%, 극단 {result['thresholds_used']['extreme']}%")
        
        # Show collection summary
        summary = self.collector.get_collection_summary()
        print(f"\n💾 데이터 수집 현황:")
        print(f"  수집 기간: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
        print(f"  총 데이터 포인트: {summary['total_data_points']:,}개")
        print(f"  추적 플랫폼: {summary['unique_platforms']}개")
        
        print("\n" + "=" * 100)
        print(f"✅ {analysis_type.upper()} 히스토리 기반 분석 완료!")
        print("=" * 100)
        
        return result

def main():
    print("=" * 100)
    print("🏆 포커 플랫폼 히스토리 기반 분석기")
    print("=" * 100)
    
    analyzer = HistoryBasedAnalyzer()
    
    # Show menu
    print("\n분석 유형을 선택하세요:")
    print("1. 일일 분석 (1일 전 대비)")
    print("2. 주간 분석 (7일 전 대비)")
    print("3. 월간 분석 (30일 전 대비)")
    print("4. 모든 분석 실행")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == '1':
        analyzer.show_comprehensive_analysis('daily')
    elif choice == '2':
        analyzer.show_comprehensive_analysis('weekly')
    elif choice == '3':
        analyzer.show_comprehensive_analysis('monthly')
    elif choice == '4':
        print("\n🔄 모든 분석 실행...")
        analyzer.show_comprehensive_analysis('daily')
        print("\n" + "="*50)
        analyzer.show_comprehensive_analysis('weekly')
        print("\n" + "="*50)
        analyzer.show_comprehensive_analysis('monthly')
    else:
        print("잘못된 선택입니다. 기본값으로 주간 분석을 실행합니다.")
        analyzer.show_comprehensive_analysis('weekly')

if __name__ == "__main__":
    main()