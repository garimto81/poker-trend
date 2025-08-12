#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상위 10위권 플랫폼 확인
"""

import os
from firebase_platform_analyzer import FirebasePlatformAnalyzer

def get_current_top10():
    """현재 상위 10위권 플랫폼 조회"""
    
    print("현재 상위 10위권 플랫폼 조회 (8월 10일 기준)")
    print("="*60)
    
    # 일간 분석으로 8월 10일 데이터 확인
    os.environ['REPORT_TYPE'] = 'daily'
    analyzer = FirebasePlatformAnalyzer()
    report = analyzer.generate_report()
    
    if report and report['top_platforms']:
        print(f"\n상위 10위권 플랫폼 ({report['data_period']['start']} 기준):")
        print("-" * 60)
        
        top10_names = []
        for i, platform in enumerate(report['top_platforms'][:10], 1):
            name = platform['platform_name']
            online = platform['online_players']
            share = platform.get('market_share', 0)
            
            print(f"{i:2}. {name:<25} {online:>10,}명 ({share:>5.1f}%)")
            top10_names.append(name)
        
        print(f"\nTOP 10 플랫폼 목록:")
        print(top10_names)
        
        return top10_names
    else:
        print("[ERROR] 상위 10위권 데이터를 가져올 수 없습니다")
        return []

if __name__ == "__main__":
    get_current_top10()