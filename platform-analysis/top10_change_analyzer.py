#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상위 10위권 플랫폼 변화 감지 시스템
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class Top10ChangeAnalyzer:
    """상위 10위권 플랫폼 변화 감지 및 분석기"""
    
    def __init__(self, report_type='weekly'):
        self.report_type = report_type
        self.firebase_project_id = "poker-online-analyze"
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        
        # 변화 감지 임계값 (상위권 플랫폼용으로 낮춤)
        self.change_thresholds = {
            'weekly': {
                'major': 15,      # 15% 이상 주요 변화
                'moderate': 8,    # 8% 이상 보통 변화
                'minor': 3        # 3% 이상 경미한 변화
            },
            'monthly': {
                'major': 25,      # 25% 이상 주요 변화
                'moderate': 12,   # 12% 이상 보통 변화
                'minor': 5        # 5% 이상 경미한 변화
            }
        }
    
    def get_top10_platforms(self, date: str) -> List[str]:
        """특정 날짜의 상위 10위권 플랫폼 조회"""
        
        sites_url = f"{self.base_url}/sites"
        platform_data = []
        
        try:
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            documents = data.get('documents', [])
            
            excluded_sites = ['PokerStars US', 'PokerStars Ontario']
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                site_name = self.extract_value(fields.get('name', {}), doc_name)
                
                if site_name in excluded_sites:
                    continue
                
                # 해당 날짜의 데이터 찾기
                traffic_url = f"{self.base_url}/sites/{doc_name}/traffic_logs?pageSize=20&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=10)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        for traffic_doc in traffic_docs:
                            traffic_fields = traffic_doc.get('fields', {})
                            collected_at = self.extract_value(traffic_fields.get('collected_at', {}), '')
                            
                            if date in collected_at:
                                online = self.extract_value(traffic_fields.get('players_online', {}), 0)
                                platform_data.append({
                                    'platform': site_name,
                                    'online_players': online
                                })
                                break
                        
                        # 날짜 데이터가 없으면 최신 데이터 사용
                        if not any(p['platform'] == site_name for p in platform_data) and traffic_docs:
                            latest = traffic_docs[0]
                            traffic_fields = latest.get('fields', {})
                            online = self.extract_value(traffic_fields.get('players_online', {}), 0)
                            
                            if online > 0:  # 유효한 데이터만
                                platform_data.append({
                                    'platform': site_name,
                                    'online_players': online
                                })
                            
                except Exception as e:
                    pass
            
            # 온라인 플레이어 기준 상위 10개 추출
            platform_data.sort(key=lambda x: x['online_players'], reverse=True)
            top10_names = [p['platform'] for p in platform_data[:10]]
            
            print(f"[INFO] {date} 상위 10위권: {', '.join(top10_names[:5])}...")
            return top10_names
            
        except Exception as e:
            print(f"[ERROR] 상위 10위권 조회 실패: {e}")
            return []
    
    def collect_top10_time_series(self, start_date: str, end_date: str) -> Dict:
        """상위 10위권 플랫폼의 시계열 데이터 수집"""
        
        # 최종일 기준으로 상위 10위권 결정
        top10_platforms = self.get_top10_platforms(end_date)
        
        if not top10_platforms:
            print("[ERROR] 상위 10위권 플랫폼을 찾을 수 없습니다")
            return {}
        
        print(f"상위 10위권 플랫폼 시계열 데이터 수집: {start_date} ~ {end_date}")
        print(f"대상 플랫폼: {top10_platforms}")
        
        sites_url = f"{self.base_url}/sites"
        time_series = {}
        
        try:
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            documents = data.get('documents', [])
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                site_name = self.extract_value(fields.get('name', {}), doc_name)
                
                # 상위 10위권에 포함된 플랫폼만 분석
                if site_name not in top10_platforms:
                    continue
                
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
            
            print(f"[SUCCESS] {len(time_series)}개 상위권 플랫폼 데이터 수집")
            return time_series
            
        except Exception as e:
            print(f"[ERROR] 데이터 수집 오류: {e}")
            return {}
    
    def detect_top10_changes(self, time_series: Dict) -> List[Dict]:
        """상위 10위권 변화 감지"""
        
        changes = []
        thresholds = self.change_thresholds[self.report_type]
        
        for platform, data_points in time_series.items():
            if len(data_points) < 2:
                continue
            
            # 기간 내 첫날과 마지막날 비교
            first_day = data_points[0]
            last_day = data_points[-1]
            
            # 온라인 플레이어 변화 분석
            if first_day['online'] > 1000:  # 상위권이므로 최소 1000명 이상
                online_change = ((last_day['online'] - first_day['online']) / first_day['online']) * 100
                
                if abs(online_change) >= thresholds['minor']:
                    
                    # 변화 심각도
                    if abs(online_change) >= thresholds['major']:
                        severity = 'major'
                        severity_kr = '주요'
                    elif abs(online_change) >= thresholds['moderate']:
                        severity = 'moderate'  
                        severity_kr = '보통'
                    else:
                        severity = 'minor'
                        severity_kr = '경미'
                    
                    direction = 'increase' if online_change > 0 else 'decrease'
                    direction_kr = '증가' if online_change > 0 else '감소'
                    
                    # 상위권 플랫폼용 상세 분석
                    values = [dp['online'] for dp in data_points]
                    trend = self.analyze_trend(values)
                    volatility = statistics.stdev(values) if len(values) > 1 else 0
                    
                    # 순위 변동 분석
                    rank_impact = self.analyze_rank_impact(platform, online_change, first_day['online'])
                    
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
                        'rank_impact': rank_impact,
                        'analysis': self.generate_top10_analysis(platform, online_change, trend, volatility, rank_impact)
                    }
                    
                    changes.append(change_info)
            
            # 캐시 플레이어 변화 (상위권 플랫폼은 보통 캐시도 많음)
            if first_day['cash'] > 500:  # 최소 500명 이상
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
                        'analysis': self.generate_cash_analysis(platform, cash_change, cash_trend, True)
                    }
                    
                    changes.append(change_info)
        
        # 변화 크기 순 정렬
        changes.sort(key=lambda x: abs(x['change_percent']), reverse=True)
        
        return changes
    
    def analyze_trend(self, values: List[int]) -> str:
        """트렌드 분석"""
        if len(values) < 3:
            return 'insufficient_data'
        
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
        
        if increases > decreases * 1.5:
            return 'upward'
        elif decreases > increases * 1.5:
            return 'downward'
        else:
            return 'stable'
    
    def analyze_rank_impact(self, platform: str, change_percent: float, base_value: int) -> str:
        """순위 영향 분석"""
        
        if base_value > 100000:  # 1위급 (GGNetwork)
            if abs(change_percent) > 10:
                return "시장 리더 지위 변화 - 전체 시장에 큰 영향"
            else:
                return "시장 리더 안정성 유지"
        elif base_value > 10000:  # 2-3위급
            if abs(change_percent) > 15:
                return "상위권 경쟁 구도 변화 가능성"
            else:
                return "상위권 안정적 유지"
        elif base_value > 1000:  # 4-10위급
            if abs(change_percent) > 20:
                return "중위권 순위 변동 예상"
            else:
                return "중위권 소폭 변동"
        else:
            return "하위권 미미한 영향"
    
    def generate_top10_analysis(self, platform: str, change_percent: float, trend: str, volatility: float, rank_impact: str) -> str:
        """상위권 플랫폼 분석 생성"""
        
        analyses = []
        
        # 변화 규모 분석 (상위권 기준)
        if abs(change_percent) > 20:
            analyses.append(f"상위권 대규모 변화 ({abs(change_percent):.1f}%) - 전략적 의사결정 필요")
        elif abs(change_percent) > 10:
            analyses.append(f"상위권 중간 변화 ({abs(change_percent):.1f}%) - 경쟁 상황 변화")
        else:
            analyses.append(f"상위권 일반 변화 ({abs(change_percent):.1f}%) - 정상적 변동")
        
        # 트렌드 분석
        trend_analysis = {
            'upward': '성장 모멘텀 확보 - 시장 점유율 확대 기회',
            'downward': '하락 추세 - 경쟁력 강화 필요',
            'stable': '안정적 변동 - 현 상태 유지'
        }
        
        if trend in trend_analysis:
            analyses.append(trend_analysis[trend])
        
        # 순위 영향 추가
        analyses.append(rank_impact)
        
        return " | ".join(analyses)
    
    def generate_cash_analysis(self, platform: str, change_percent: float, trend: str, is_top10: bool) -> str:
        """캐시게임 분석 (상위권 특화)"""
        
        prefix = "상위권 " if is_top10 else ""
        
        if abs(change_percent) > 25:
            return f"{prefix}캐시게임 급변 ({change_percent:+.1f}%) - 수익 구조 변화 가능성"
        elif abs(change_percent) > 15:
            return f"{prefix}캐시게임 중간 변화 ({change_percent:+.1f}%) - 유저 행동 패턴 변화"
        else:
            return f"{prefix}캐시게임 일반 변화 ({change_percent:+.1f}%) - 정상적 변동"
    
    def generate_top10_report(self) -> Dict:
        """상위 10위권 변화 보고서 생성"""
        
        # 기간 설정
        end_date = datetime(2025, 8, 10)
        
        if self.report_type == 'weekly':
            start_date = end_date - timedelta(days=6)
            period_name = "주간 상위 10위권"
        else:  # monthly
            start_date = datetime(2025, 7, 30)
            period_name = "월간 상위 10위권"
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n{'='*80}")
        print(f"{period_name} 변화 감지 분석 ({start_str} ~ {end_str})")
        print(f"{'='*80}")
        
        # 상위 10위권 시계열 데이터 수집
        time_series = self.collect_top10_time_series(start_str, end_str)
        
        if not time_series:
            return None
        
        # 변화 감지
        changes = self.detect_top10_changes(time_series)
        
        # 보고서 생성
        report = {
            'report_type': f"{self.report_type}_top10",
            'period': f"{start_str} ~ {end_str}",
            'analysis_date': datetime.now().isoformat(),
            'top10_platforms_analyzed': len(time_series),
            'significant_changes_detected': len(changes),
            'changes': changes,
            'summary': self.generate_top10_summary(changes, time_series),
            'top10_list': list(time_series.keys())
        }
        
        return report
    
    def generate_top10_summary(self, changes: List[Dict], time_series: Dict) -> Dict:
        """상위 10위권 요약 생성"""
        
        if not changes:
            return {
                'total_changes': 0,
                'major_changes': 0,
                'market_status': 'stable_top10',
                'key_insight': '상위 10위권 안정적 - 큰 변화 없음'
            }
        
        major_changes = [c for c in changes if c['severity'] == 'major']
        increases = [c for c in changes if c['direction'] == 'increase']
        decreases = [c for c in changes if c['direction'] == 'decrease']
        
        # 상위권 시장 상태
        if len(major_changes) > 2:
            market_status = 'volatile_top10'
            status_kr = '상위권 변동성 높음'
        elif len(major_changes) > 0:
            market_status = 'changing_top10'
            status_kr = '상위권 변화 중'
        else:
            market_status = 'stable_top10'
            status_kr = '상위권 안정적'
        
        # 인사이트 생성
        insights = []
        
        if len(increases) > len(decreases):
            insights.append(f"상위권 전반 성장 ({len(increases)}개 증가 vs {len(decreases)}개 감소)")
        elif len(decreases) > len(increases):
            insights.append(f"상위권 전반 위축 ({len(decreases)}개 감소 vs {len(increases)}개 증가)")
        else:
            insights.append("상위권 균형 상태")
        
        if major_changes:
            top_change = major_changes[0]
            insights.append(f"상위권 최대 변화: {top_change['platform']} ({top_change['change_percent']:+.1f}%)")
        
        # 상위 3개 플랫폼 안정성 체크
        top3_platforms = list(time_series.keys())[:3]
        top3_changes = [c for c in changes if c['platform'] in top3_platforms]
        
        if len(top3_changes) > 0:
            insights.append(f"TOP 3 플랫폼 중 {len(top3_changes)}개 변화 감지")
        else:
            insights.append("TOP 3 플랫폼 안정적 유지")
        
        return {
            'total_changes': len(changes),
            'major_changes': len(major_changes),
            'moderate_changes': len([c for c in changes if c['severity'] == 'moderate']),
            'minor_changes': len([c for c in changes if c['severity'] == 'minor']),
            'increases': len(increases),
            'decreases': len(decreases),
            'market_status': market_status,
            'market_status_kr': status_kr,
            'key_insights': insights,
            'top3_stability': len(top3_changes) == 0
        }
    
    def display_top10_report(self, report: Dict):
        """상위 10위권 보고서 출력"""
        
        if not report:
            print("[ERROR] 보고서 생성 실패")
            return
        
        print(f"\n{report['report_type'].upper()} 변화 감지 보고서")
        print(f"기간: {report['period']}")
        print(f"분석 대상: TOP 10 플랫폼 ({report['top10_platforms_analyzed']}개)")
        print(f"감지된 변화: {report['significant_changes_detected']}건")
        
        print(f"\n[상위 10위권 플랫폼]")
        for i, platform in enumerate(report['top10_list'], 1):
            print(f"{i:2}. {platform}")
        
        # 요약
        summary = report['summary']
        print(f"\n[요약]")
        print(f"- 상위권 시장 상태: {summary['market_status_kr']}")
        print(f"- 주요 변화: {summary['major_changes']}건")
        print(f"- 증가: {summary['increases']}건 / 감소: {summary['decreases']}건")
        print(f"- TOP 3 안정성: {'유지' if summary['top3_stability'] else '변화 있음'}")
        
        print(f"\n[핵심 인사이트]")
        for insight in summary['key_insights']:
            print(f"- {insight}")
        
        # 상위 변화들
        if report['changes']:
            print(f"\n[TOP 변화 감지 - 상위 10위권 내]")
            print("-" * 80)
            
            for i, change in enumerate(report['changes'][:5], 1):
                direction_icon = "[UP]" if change['direction'] == 'increase' else "[DOWN]"
                severity_text = change.get('severity_kr', change['severity'])
                
                print(f"\n{i}. {change['platform']} - {change['metric']}")
                print(f"   {change['start_value']:,} → {change['end_value']:,} ({change['change_percent']:+.1f}%)")
                print(f"   심각도: {severity_text} | 기간: {change['start_date']} ~ {change['end_date']}")
                print(f"   분석: {change['analysis']}")
        else:
            print(f"\n[결과] 상위 10위권 내에서 유의미한 변화 없음")
        
        # JSON 저장
        filename = f"top10_change_{report['report_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    print("상위 10위권 플랫폼 변화 감지 시스템")
    print("="*60)
    
    # 주간 분석
    print("\n1. 상위 10위권 주간 변화 분석")
    weekly_analyzer = Top10ChangeAnalyzer('weekly')
    weekly_report = weekly_analyzer.generate_top10_report()
    if weekly_report:
        weekly_analyzer.display_top10_report(weekly_report)
    
    # 월간 분석
    print("\n\n2. 상위 10위권 월간 변화 분석")
    monthly_analyzer = Top10ChangeAnalyzer('monthly')
    monthly_report = monthly_analyzer.generate_top10_report()
    if monthly_report:
        monthly_analyzer.display_top10_report(monthly_report)

if __name__ == "__main__":
    main()