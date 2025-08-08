#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test daily analysis
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from history_based_analyzer import HistoryBasedAnalyzer

def main():
    print("🧪 일일 분석 테스트 시작...")
    
    analyzer = HistoryBasedAnalyzer()
    
    # Test daily analysis
    print("\n📊 일일 분석 실행 중...")
    result = analyzer.show_comprehensive_analysis('daily')
    
    if result:
        print("\n✅ 일일 분석 성공!")
    else:
        print("\n❌ 일일 분석 실패!")

if __name__ == "__main__":
    main()