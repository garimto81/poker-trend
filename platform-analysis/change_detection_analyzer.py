#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 수치 변화 감지 및 분석 시스템
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class PlatformChangeAnalyzer:
    """플랫폼 수치 변화 감지 및 분석기"""
    
    def __init__(self, report_type='weekly'):
        self.report_type = report_type
        self.firebase_project_id = "poker-online-analyze"
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        
        # 변화 감지 임계값 설정
        self.change_thresholds = {
            'weekly': {
                'major': 20,      # 20% 이상 주요 변화
                'moderate': 10,   # 10% 이상 보통 변화
                'minor': 5        # 5% 이상 경미한 변화
            },
            'monthly': {
                'major': 30,      # 30% 이상 주요 변화
                'moderate': 15,   # 15% 이상 보통 변화
                'minor': 8        # 8% 이상 경미한 변화
            }
        }
    
    def collect_time_series_data(self, start_date: str, end_date: str) -> Dict:
        """기간별 시계열 데이터 수집"""
        
        print(f"시계열 데이터 수집: {start_date} ~ {end_date}")
        
        sites_url = f"{self.base_url}/sites"
        time_series = {}
        
        try:
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Firebase 연결 실패")
                return {}
            
            data = response.json()
            documents = data.get('documents', [])
            
            excluded_sites = ['PokerStars US', 'PokerStars Ontario']
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                site_name = self.extract_value(fields.get('name', {}), doc_name)
                
                if site_name in excluded_sites:
                    continue
                
                # 해당 기간의 모든 트래픽 로그 수집
                traffic_url = f"{self.base_url}/sites/{doc_name}/traffic_logs?pageSize=100&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        site_data = []
                        
                        for traffic_doc in traffic_docs:
                            traffic_fields = traffic_doc.get('fields', {})
                            collected_at = self.extract_value(traffic_fields.get('collected_at', {}), '')
                            
                            if collected_at:
                                date_str = collected_at.split('T')[0]
                                
                                # 기간 내 데이터만
                                if start_date <= date_str <= end_date:
                                    site_data.append({
                                        'date': date_str,
                                        'online': self.extract_value(traffic_fields.get('players_online', {}), 0),
                                        'cash': self.extract_value(traffic_fields.get('cash_players', {}), 0),
                                        'peak_24h': self.extract_value(traffic_fields.get('peak_24h', {}), 0),
                                        'collected_at': collected_at
                                    })
                        
                        if site_data:
                            time_series[site_name] = sorted(site_data, key=lambda x: x['date'])
                            
                except Exception as e:
                    pass
            
            print(f"[SUCCESS] {len(time_series)}개 사이트 시계열 데이터 수집")
            return time_series
            
        except Exception as e:
            print(f"[ERROR] 데이터 수집 오류: {e}")
            return {}
    
    def detect_significant_changes(self, time_series: Dict) -> List[Dict]:
        """유의미한 변화 감지"""
        
        changes = []
        thresholds = self.change_thresholds[self.report_type]
        
        for platform, data_points in time_series.items():
            if len(data_points) < 2:
                continue
            
            # 첫날과 마지막날 비교
            first_day = data_points[0]
            last_day = data_points[-1]
            
            # 온라인 플레이어 변화
            if first_day['online'] > 0:
                online_change = ((last_day['online'] - first_day['online']) / first_day['online']) * 100
                
                if abs(online_change) >= thresholds['minor']:
                    
                    # 변화 심각도 분류
                    if abs(online_change) >= thresholds['major']:
                        severity = 'major'
                        severity_kr = '주요'
                    elif abs(online_change) >= thresholds['moderate']:
                        severity = 'moderate'
                        severity_kr = '보통'
                    else:
                        severity = 'minor'
                        severity_kr = '경미'
                    
                    # 변화 방향
                    direction = 'increase' if online_change > 0 else 'decrease'
                    direction_kr = '증가' if online_change > 0 else '감소'
                    
                    # 중간값들을 이용한 추가 분석
                    values = [dp['online'] for dp in data_points]
                    trend = self.analyze_trend(values)
                    volatility = statistics.stdev(values) if len(values) > 1 else 0
                    
                    change_info = {
                        'platform': platform,
                        'metric': 'online_players',
                        'start_value': first_day['online'],
                        'end_value': last_day['online'],
                        'change_percent': round(online_change, 1),
                        'change_absolute': last_day['online'] - first_day['online'],
                        'severity': severity,
                        'severity_kr': severity_kr,
                        'direction': direction,
                        'direction_kr': direction_kr,
                        'start_date': first_day['date'],
                        'end_date': last_day['date'],
                        'data_points': len(data_points),
                        'trend': trend,
                        'volatility': round(volatility, 0),
                        'analysis': self.generate_change_analysis(platform, online_change, trend, volatility)
                    }
                    
                    changes.append(change_info)
            
            # 캐시 플레이어 변화도 동일하게 분석
            if first_day['cash'] > 100:  # 최소 100명 이상일 때만 분석
                cash_change = ((last_day['cash'] - first_day['cash']) / first_day['cash']) * 100
                
                if abs(cash_change) >= thresholds['minor']:
                    
                    severity = 'major' if abs(cash_change) >= thresholds['major'] else ('moderate' if abs(cash_change) >= thresholds['moderate'] else 'minor')
                    direction = 'increase' if cash_change > 0 else 'decrease'
                    
                    cash_values = [dp['cash'] for dp in data_points]
                    cash_trend = self.analyze_trend(cash_values)
                    
                    change_info = {
                        'platform': platform,
                        'metric': 'cash_players',
                        'start_value': first_day['cash'],
                        'end_value': last_day['cash'],
                        'change_percent': round(cash_change, 1),
                        'change_absolute': last_day['cash'] - first_day['cash'],
                        'severity': severity,
                        'direction': direction,
                        'start_date': first_day['date'],
                        'end_date': last_day['date'],
                        'trend': cash_trend,
                        'analysis': self.generate_cash_change_analysis(platform, cash_change, cash_trend)
                    }
                    
                    changes.append(change_info)
        
        # 변화 크기 순으로 정렬
        changes.sort(key=lambda x: abs(x['change_percent']), reverse=True)
        
        return changes
    
    def analyze_trend(self, values: List[int]) -> str:
        """값들의 트렌드 분석"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # 선형 회귀를 단순화한 트렌드 분석
        increases = 0
        decreases = 0
        
        for i in range(1, len(values)):
            if values[i] > values[i-1]:
                increases += 1
            elif values[i] < values[i-1]:
                decreases += 1
        
        if increases > decreases * 1.5:
            return 'upward'
        elif decreases > increases * 1.5:
            return 'downward'
        else:
            return 'stable'
    
    def generate_change_analysis(self, platform: str, change_percent: float, trend: str, volatility: float) -> str:
        """변화에 대한 분석 생성"""
        
        analyses = []
        
        # 변화 크기 분석
        if abs(change_percent) > 50:
            analyses.append(f"극대 변화 ({abs(change_percent):.1f}%) - 시장 환경 변화 또는 데이터 이슈 가능성")
        elif abs(change_percent) > 30:
            analyses.append(f"대규모 변화 ({abs(change_percent):.1f}%) - 플랫폼 정책 변화나 마케팅 영향 추정")
        elif abs(change_percent) > 15:
            analyses.append(f"중간 규모 변화 ({abs(change_percent):.1f}%) - 운영 변화 또는 경쟁 상황 변화")
        else:
            analyses.append(f"일반적 변화 ({abs(change_percent):.1f}%) - 정상적 시장 변동 범위")
        
        # 트렌드 분석
        trend_analysis = {
            'upward': '지속적 상승 트렌드 - 성장 동력 확보',
            'downward': '지속적 하락 트렌드 - 구조적 문제 가능성',
            'stable': '변동성 있는 안정 - 일시적 변화로 추정'
        }
        
        if trend in trend_analysis:
            analyses.append(trend_analysis[trend])
        
        # 변동성 분석
        if volatility > 10000:
            analyses.append(f"높은 변동성 ({volatility:,.0f}) - 불안정한 유저 기반")
        elif volatility > 1000:
            analyses.append(f"보통 변동성 ({volatility:,.0f}) - 정상적 일일 변동")
        else:
            analyses.append(f"낮은 변동성 ({volatility:,.0f}) - 안정적 유저 기반")
        
        return " | ".join(analyses)
    
    def generate_cash_change_analysis(self, platform: str, change_percent: float, trend: str) -> str:
        """캐시게임 변화 분석"""
        
        if abs(change_percent) > 40:
            return f"캐시게임 급변 ({change_percent:+.1f}%) - 게임 정책 변화나 프로모션 영향 추정"
        elif abs(change_percent) > 20:
            return f"캐시게임 중간 변화 ({change_percent:+.1f}%) - 유저 선호도 변화 가능성"
        else:
            return f"캐시게임 일반 변화 ({change_percent:+.1f}%) - 정상적 변동 범위"
    
    def generate_change_report(self) -> Dict:
        """변화 감지 보고서 생성"""
        
        # 기간 설정
        end_date = datetime(2025, 8, 10)
        
        if self.report_type == 'weekly':
            start_date = end_date - timedelta(days=6)
            period_name = "주간"
        else:  # monthly
            start_date = datetime(2025, 7, 30)
            period_name = "월간"
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n{'='*80}")
        print(f"{period_name} 변화 감지 분석 ({start_str} ~ {end_str})")
        print(f"{'='*80}")
        
        # 시계열 데이터 수집
        time_series = self.collect_time_series_data(start_str, end_str)
        
        if not time_series:
            return None
        
        # 변화 감지
        changes = self.detect_significant_changes(time_series)
        
        # 보고서 생성
        report = {
            'report_type': self.report_type,
            'period': f"{start_str} ~ {end_str}",
            'analysis_date': datetime.now().isoformat(),
            'total_platforms_analyzed': len(time_series),
            'significant_changes_detected': len(changes),
            'changes': changes[:10],  # 상위 10개만
            'summary': self.generate_summary(changes)
        }
        
        return report
    
    def generate_summary(self, changes: List[Dict]) -> Dict:
        """변화 요약 생성"""
        
        if not changes:
            return {
                'total_changes': 0,
                'major_changes': 0,
                'market_status': 'stable',
                'key_insight': '유의미한 변화 없음 - 안정적 시장 상태'
            }
        
        major_changes = [c for c in changes if c['severity'] == 'major']
        increases = [c for c in changes if c['direction'] == 'increase']
        decreases = [c for c in changes if c['direction'] == 'decrease']
        
        # 시장 상태 판단
        if len(major_changes) > 3:
            market_status = 'volatile'
            status_kr = '변동성 높음'
        elif len(major_changes) > 1:
            market_status = 'changing'
            status_kr = '변화 중'
        else:
            market_status = 'stable'
            status_kr = '안정적'
        
        # 주요 인사이트
        insights = []
        
        if len(increases) > len(decreases):
            insights.append(f"시장 전반 성장세 ({len(increases)}개 증가 vs {len(decreases)}개 감소)")
        elif len(decreases) > len(increases):
            insights.append(f"시장 전반 위축세 ({len(decreases)}개 감소 vs {len(increases)}개 증가)")
        else:
            insights.append("시장 균형 상태 유지")
        
        if major_changes:
            top_change = major_changes[0]
            insights.append(f"최대 변화: {top_change['platform']} ({top_change['change_percent']:+.1f}%)")
        
        return {
            'total_changes': len(changes),
            'major_changes': len(major_changes),
            'moderate_changes': len([c for c in changes if c['severity'] == 'moderate']),
            'minor_changes': len([c for c in changes if c['severity'] == 'minor']),
            'increases': len(increases),
            'decreases': len(decreases),
            'market_status': market_status,
            'market_status_kr': status_kr,
            'key_insights': insights
        }
    
    def display_report(self, report: Dict):
        """보고서 출력"""
        
        if not report:
            print("[ERROR] 보고서 생성 실패")
            return
        
        print(f"\n{report['report_type'].upper()} 변화 감지 보고서")
        print(f"기간: {report['period']}")
        print(f"분석 대상: {report['total_platforms_analyzed']}개 플랫폼")
        print(f"감지된 변화: {report['significant_changes_detected']}건")
        
        # 요약
        summary = report['summary']
        print(f"\n[요약]")
        print(f"- 시장 상태: {summary['market_status_kr']}")
        print(f"- 주요 변화: {summary['major_changes']}건")
        print(f"- 증가: {summary['increases']}건 / 감소: {summary['decreases']}건")
        
        print(f"\n[핵심 인사이트]")
        for insight in summary['key_insights']:
            print(f"- {insight}")
        
        # 상위 변화들
        print(f"\n[TOP 변화 감지]")
        print("-" * 80)
        
        for i, change in enumerate(report['changes'][:5], 1):
            direction_icon = "[UP]" if change['direction'] == 'increase' else "[DOWN]"
            severity_icon = "[HIGH]" if change['severity'] == 'major' else ("[MID]" if change['severity'] == 'moderate' else "[LOW]")
            
            print(f"\n{i}. {change['platform']} - {change['metric']}")
            print(f"   {change['start_value']:,} → {change['end_value']:,} ({change['change_percent']:+.1f}%)")
            severity_text = change.get('severity_kr', change['severity'])
            print(f"   심각도: {severity_text} | 기간: {change['start_date']} ~ {change['end_date']}")
            print(f"   분석: {change['analysis']}")
        
        # JSON 저장
        filename = f"change_detection_{report['report_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] {filename}")
    
    def extract_value(self, field_data, default_value=''):
        """Firebase 필드 값 추출"""
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
        else:
            return default_value

def main():
    """메인 실행"""
    
    print("플랫폼 변화 감지 시스템")
    print("="*50)
    
    # 주간 분석
    print("\n1. 주간 변화 분석")
    weekly_analyzer = PlatformChangeAnalyzer('weekly')
    weekly_report = weekly_analyzer.generate_change_report()
    if weekly_report:
        weekly_analyzer.display_report(weekly_report)
    
    # 월간 분석
    print("\n\n2. 월간 변화 분석")
    monthly_analyzer = PlatformChangeAnalyzer('monthly')
    monthly_report = monthly_analyzer.generate_change_report()
    if monthly_report:
        monthly_analyzer.display_report(monthly_report)

if __name__ == "__main__":
    main()