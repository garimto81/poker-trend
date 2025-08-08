#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Firebase data for testing
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from firebase_data_importer import FirebaseDataImporter

def main():
    print("🚀 Firebase 데이터 가져오기...")
    
    importer = FirebaseDataImporter()
    
    # 최근 7일 데이터 가져오기
    print("\n📥 최근 7일 Firebase 데이터 가져오기 중...")
    stats = importer.import_firebase_data(days_back=7)
    
    print(f"\n✅ Firebase 데이터 가져오기 완료:")
    print(f"   가져온 레코드: {stats['imported']}개")
    print(f"   건너뛴 사이트: {stats['skipped']}개")
    print(f"   오류 발생: {stats['errors']}개")
    
    if stats['imported'] > 0:
        print("\n🎉 Firebase 데이터가 성공적으로 통합되었습니다!")
        print("이제 히스토리 기반 분석에서 더 많은 데이터를 활용할 수 있습니다.")

if __name__ == "__main__":
    main()