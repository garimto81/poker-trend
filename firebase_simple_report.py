#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase 플랫폼 분석 - 간결한 보고서 형식
"""

import os
import json
from datetime import datetime
from firebase_platform_analyzer import FirebasePlatformAnalyzer

def format_number(num):
    """숫자 포맷팅"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.0f}K"
    else:
        return str(num)

def generate_ai_analysis(report_type, data):
    """AI 분석 결과 생성"""
    insights = []
    
    if report_type == 'daily':
        # 일간 분석
        leader = data['online_top3'][0] if data['online_top3'] else None
        if leader:
            if leader['players'] > 100000:
                insights.append(f"시장 지배: {leader['name']}가 일일 {format_number(leader['players'])} 플레이어로 압도적 우위")
            else:
                insights.append(f"시장 분산: 1위 {leader['name']}도 {format_number(leader['players'])}에 불과")
        
        # 캐시게임 분석
        cash_leader = data['cash_top3'][0] if data['cash_top3'] else None
        if cash_leader and cash_leader['players'] > 5000:
            insights.append(f"캐시게임 강세: {cash_leader['name']}가 {format_number(cash_leader['players'])} 캐시 플레이어 확보")
        
        # 시장 집중도
        if data['total_platforms'] < 10:
            insights.append("플랫폼 수 제한적: 실제 활성 플랫폼 10개 미만")
        
    elif report_type == 'weekly':
        # 주간 분석
        leader = data['online_top3'][0] if data['online_top3'] else None
        if leader and leader.get('share', 0) > 50:
            insights.append(f"독점적 지위: {leader['name']}가 주간 평균 {leader['share']:.1f}% 점유")
        
        # 경쟁 구도
        if len(data['online_top3']) >= 3:
            gap = data['online_top3'][0]['players'] - data['online_top3'][2]['players']
            if gap > 100000:
                insights.append(f"격차 심화: 1위와 3위 간 {format_number(gap)} 차이")
        
        # 주간 트렌드
        insights.append(f"주간 시장 규모: 평균 {format_number(data['total_online'])} 동시접속")
        
    else:  # monthly
        # 월간 분석
        leader = data['online_top3'][0] if data['online_top3'] else None
        if leader:
            insights.append(f"월간 리더: {leader['name']}가 {leader['share']:.1f}% 시장 점유율 기록")
        
        # 시장 구조
        if data['total_platforms'] > 40:
            insights.append(f"다양한 플랫폼: 총 {data['total_platforms']}개 플랫폼 운영 중")
        
        # 캐시게임 비중
        if data['total_cash'] > 0 and data['total_online'] > 0:
            cash_ratio = (data['total_cash'] / data['total_online']) * 100
            insights.append(f"캐시게임 비중: 전체의 {cash_ratio:.1f}%가 캐시게임 참여")
    
    # 공통 분석
    if data['total_online'] < 200000:
        insights.append("시장 규모 제한적: 전체 시장 20만명 미만")
    
    return insights

def generate_simple_report(report_type):
    """간결한 보고서 생성"""
    
    # 환경변수 설정
    os.environ['REPORT_TYPE'] = report_type
    
    # 분석기 실행
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if not report:
        return None
    
    # 데이터 추출
    summary = report['summary']
    platforms = report.get('top_platforms', [])
    
    # 온라인 TOP 3
    online_top3 = []
    for i, p in enumerate(platforms[:3]):
        online_top3.append({
            'rank': i + 1,
            'name': p['platform_name'],
            'players': p['online_players'],
            'share': p.get('market_share', 0)
        })
    
    # 캐시게임 TOP 3
    cash_sorted = sorted(platforms, key=lambda x: x['cash_players'], reverse=True)
    cash_top3 = []
    for i, p in enumerate(cash_sorted[:3]):
        cash_top3.append({
            'rank': i + 1,
            'name': p['platform_name'],
            'players': p['cash_players']
        })
    
    # 구조화된 데이터
    data = {
        'report_type': report_type,
        'period': f"{report['data_period']['start']} ~ {report['data_period']['end']}",
        'total_platforms': summary['total_platforms'],
        'total_online': summary['total_online_players'],
        'total_cash': summary['total_cash_players'],
        'online_top3': online_top3,
        'cash_top3': cash_top3
    }
    
    # AI 분석 생성
    ai_insights = generate_ai_analysis(report_type, data)
    
    # 보고서 출력
    output = []
    
    # 제목
    title_map = {
        'daily': '일간 보고서',
        'weekly': '주간 보고서',
        'monthly': '월간 보고서'
    }
    
    output.append("=" * 60)
    output.append(f"{title_map[report_type]}")
    output.append(f"기간: {data['period']}")
    output.append("=" * 60)
    
    # 기본 통계
    output.append(f"총 플랫폼 수: {data['total_platforms']}개")
    output.append(f"총 온라인 플레이어: {format_number(data['total_online'])}명")
    
    # 온라인 TOP 3
    output.append("")
    output.append("[온라인 플레이어 TOP 3]")
    for item in data['online_top3']:
        output.append(f"TOP {item['rank']} {item['name']:20} {format_number(item['players']):>10}명")
    
    # 캐시게임 TOP 3
    output.append("")
    output.append(f"총 캐시 플레이어: {format_number(data['total_cash'])}명")
    output.append("")
    output.append("[캐시게임 플레이어 TOP 3]")
    for item in data['cash_top3']:
        output.append(f"TOP {item['rank']} {item['name']:20} {format_number(item['players']):>10}명")
    
    # AI 분석
    output.append("")
    output.append("[AI 분석 결과]")
    for i, insight in enumerate(ai_insights, 1):
        output.append(f"{i}. {insight}")
    
    output.append("=" * 60)
    output.append("")
    
    return "\n".join(output)

def main():
    """메인 실행"""
    
    print("\nFirebase 플랫폼 분석 - 간결한 보고서")
    print("="*60)
    
    # 일간 보고서
    print("\n")
    daily = generate_simple_report('daily')
    if daily:
        print(daily)
    
    # 주간 보고서  
    print("\n")
    weekly = generate_simple_report('weekly')
    if weekly:
        print(weekly)
    
    # 월간 보고서
    print("\n")
    monthly = generate_simple_report('monthly')
    if monthly:
        print(monthly)
    
    print("\n[데이터 출처]")
    print("- Firebase 실시간 데이터")
    print("- PokerStars US/Ontario 제외 (데이터 오염)")
    print("- 생성 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()