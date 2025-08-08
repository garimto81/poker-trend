#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Firebase data preview
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from firebase_data_importer import FirebaseDataImporter

def main():
    print("🧪 Firebase 데이터 미리보기 테스트...")
    
    importer = FirebaseDataImporter()
    
    # 1. 비교 분석
    print("\n📊 현재 시스템 vs Firebase 비교:")
    comparison = importer.show_comparison_with_current()
    
    # 2. 미리보기
    print("\n👀 Firebase 데이터 미리보기:")
    preview = importer.show_import_preview(sample_sites=5)
    
    if preview:
        print("\n📋 미리보기 결과:")
        for site_name, info in preview.items():
            print(f"\n🎯 {site_name}:")
            print(f"   총 로그: {info['total_logs']}개")
            print(f"   기간: {info['date_range']}")
            print(f"   최신 플레이어: {info['latest_players']:,}명")
            
            if info.get('sample_log'):
                sample = info['sample_log']
                print(f"   샘플 데이터: 온라인 {sample.get('players_online', 0):,}명, 캐시 {sample.get('cash_players', 0):,}명")
    else:
        print("❌ Firebase 데이터를 가져올 수 없습니다.")

if __name__ == "__main__":
    main()