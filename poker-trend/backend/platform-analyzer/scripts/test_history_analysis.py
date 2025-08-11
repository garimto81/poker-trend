#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test history-based analysis
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from history_based_analyzer import HistoryBasedAnalyzer

def main():
    print("🧪 히스토리 기반 분석 테스트 시작...")
    
    analyzer = HistoryBasedAnalyzer()
    
    # Test weekly analysis
    print("\n📊 주간 분석 실행 중...")
    result = analyzer.show_comprehensive_analysis('weekly')
    
    if result:
        print("\n✅ 히스토리 기반 분석 성공!")
    else:
        print("\n❌ 히스토리 기반 분석 실패!")

if __name__ == "__main__":
    main()