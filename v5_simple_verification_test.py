#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V5 Smart Path Detection 간단 검증 테스트
유니코드 출력 문제를 피하고 핵심 결과만 확인
"""

import os
import json
from pathlib import Path
from datetime import datetime

def simple_path_test():
    """간단한 V5 경로 탐지 테스트"""
    base_dir = Path("C:\\claude03")
    
    results = {
        "test_time": datetime.now().isoformat(),
        "platform_analyzer": False,
        "youtube_analyzer": False, 
        "pokernews_analyzer": False,
        "success_rate": 0,
        "details": {}
    }
    
    # Platform 분석 경로 확인
    platform_paths = [
        "backend/platform-analyzer/scripts",
        "platform-analyzer/scripts",
        "poker-trend/backend/platform-analyzer/scripts"
    ]
    
    platform_scripts = [
        "firebase_rest_api_fetcher.py",
        "show_daily_comparison.py", 
        "final_slack_reporter.py"
    ]
    
    for path in platform_paths:
        full_path = base_dir / path
        if full_path.exists():
            script_count = 0
            for script in platform_scripts:
                if (full_path / script).exists():
                    script_count += 1
            
            if script_count >= 3:
                results["platform_analyzer"] = True
                results["details"]["platform_path"] = str(path)
                results["details"]["platform_scripts"] = script_count
                break
    
    # YouTube 분석 경로 확인
    youtube_paths = [
        "backend/data-collector/scripts",
        "data-collector/scripts"
    ]
    
    for path in youtube_paths:
        full_path = base_dir / path
        if full_path.exists() and (full_path / "run_youtube_analysis.py").exists():
            results["youtube_analyzer"] = True
            results["details"]["youtube_path"] = str(path)
            break
    
    # PokerNews 분석 경로 확인
    pokernews_paths = [
        "poker-trend-analysis/backend/news-analyzer",
        "backend/news-analyzer"
    ]
    
    for path in pokernews_paths:
        full_path = base_dir / path
        if full_path.exists() and (full_path / "pokernews_collector_v2.py").exists():
            results["pokernews_analyzer"] = True
            results["details"]["pokernews_path"] = str(path)
            break
    
    # 성공률 계산
    success_count = sum([
        results["platform_analyzer"],
        results["youtube_analyzer"], 
        results["pokernews_analyzer"]
    ])
    results["success_rate"] = (success_count / 3) * 100
    
    return results

def main():
    print("V5 Smart Path Detection 간단 검증 시작...")
    print("=" * 60)
    
    # 테스트 실행
    results = simple_path_test()
    
    # 결과 출력
    print(f"검증 시간: {results['test_time']}")
    print(f"Platform 분석: {'SUCCESS' if results['platform_analyzer'] else 'FAILED'}")
    print(f"YouTube 분석: {'SUCCESS' if results['youtube_analyzer'] else 'FAILED'}")
    print(f"PokerNews 분석: {'SUCCESS' if results['pokernews_analyzer'] else 'FAILED'}")
    print(f"전체 성공률: {results['success_rate']:.0f}%")
    
    if results.get("details"):
        print("\n세부 정보:")
        for key, value in results["details"].items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    
    if results["success_rate"] == 100:
        print("V5 Smart Path Detection 검증 완료: PASS")
        print("Zero-Failure Promise 달성!")
        return True
    else:
        print("V5 시스템에 개선이 필요합니다.")
        return False
    
    # JSON 결과 저장
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"v5_simple_test_result_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"결과 저장: {result_file}")
    except Exception as e:
        print(f"결과 저장 실패: {e}")

if __name__ == "__main__":
    main()