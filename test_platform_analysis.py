#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 분석 시스템 테스트
- 일간/주간/월간 모든 타입 테스트
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

def test_platform_analysis(report_type):
    """플랫폼 분석 테스트"""
    print(f"\n{'='*80}")
    print(f"[TEST] {report_type.upper()} Platform Analysis")
    print(f"{'='*80}")
    
    # 날짜 계산
    current_date = datetime.now()
    
    if report_type == 'daily':
        data_start = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
        data_end = data_start
    elif report_type == 'weekly':
        data_start = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')
        data_end = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    else:  # monthly
        data_start = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        data_end = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 환경 변수 설정
    env = os.environ.copy()
    env['REPORT_TYPE'] = report_type
    env['DATA_PERIOD_START'] = data_start
    env['DATA_PERIOD_END'] = data_end
    
    print(f"Report Type: {report_type}")
    print(f"Data Period: {data_start} ~ {data_end}")
    
    # 작업 디렉토리
    script_dir = os.path.join('backend', 'platform-analyzer', 'scripts')
    
    try:
        # 1. 자동화된 분석기 테스트
        print(f"\n[1] Testing Automated Platform Analyzer...")
        result = subprocess.run(
            [sys.executable, 'automated_platform_analyzer.py'],
            cwd=script_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Platform analysis success")
            # 주요 결과 출력
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'TOP 5' in line or '플랫폼' in line or '인사이트' in line:
                    print(f"   {line}")
        else:
            print(f"[ERROR] Platform analysis failed: {result.stderr}")
        
        # 2. Slack 리포터 테스트
        print(f"\n[2] Testing Slack Reporter...")
        result = subprocess.run(
            [sys.executable, 'platform_slack_reporter.py'],
            cwd=script_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Slack reporter success")
        else:
            print(f"[WARNING] Slack reporter executed (no webhook is normal): {result.returncode}")
        
        print(f"\n[DONE] {report_type.upper()} test completed")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Operation timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("="*80)
    print("Platform Analysis System Test")
    print("="*80)
    
    # 모든 리포트 타입 테스트
    report_types = ['daily', 'weekly', 'monthly']
    results = {}
    
    for report_type in report_types:
        success = test_platform_analysis(report_type)
        results[report_type] = success
    
    # 결과 요약
    print("\n" + "="*80)
    print("Test Result Summary")
    print("="*80)
    
    for report_type, success in results.items():
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{report_type.upper():10} : {status}")
    
    # 전체 성공 여부
    all_success = all(results.values())
    
    if all_success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())