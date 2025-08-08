#!/usr/bin/env python3
"""
통합 포커 보고 스케줄링 시스템 검증 스크립트

이 스크립트는 GitHub Actions 워크플로우의 스케줄 결정 로직을
로컬에서 테스트하고 검증하는 도구입니다.
"""

import os
import sys
from datetime import datetime, timedelta, date
from typing import Tuple, Dict, Any
import json
import argparse

def get_week_of_month(target_date: date) -> int:
    """월에서 몇 번째 주인지 계산 (첫째주는 1)"""
    return (target_date.day - 1) // 7 + 1

def get_last_monday(target_date: date) -> date:
    """지난주 월요일 날짜 계산"""
    days_since_monday = (target_date.weekday()) % 7
    last_monday = target_date - timedelta(days=days_since_monday + 7)
    return last_monday

def get_last_month_range(target_date: date) -> Tuple[date, date]:
    """지난달 시작일과 종료일 계산"""
    # 지난달의 첫날
    if target_date.month == 1:
        start_date = date(target_date.year - 1, 12, 1)
    else:
        start_date = date(target_date.year, target_date.month - 1, 1)
    
    # 지난달의 마지막날
    if target_date.month == 1:
        end_date = date(target_date.year - 1, 12, 31)
    else:
        next_month = target_date.replace(day=1)
        end_date = next_month - timedelta(days=1)
    
    return start_date, end_date

def determine_schedule(target_date: date, force_type: str = None) -> Dict[str, Any]:
    """
    스케줄 결정 로직 (GitHub Actions 워크플로우와 동일)
    """
    day_of_month = target_date.day
    day_of_week = target_date.weekday() + 1  # Python: 0=월요일, GitHub: 1=월요일
    week_of_month = get_week_of_month(target_date)
    
    result = {
        'current_date': target_date.strftime('%Y-%m-%d'),
        'day_of_month': day_of_month,
        'day_of_week': day_of_week,
        'week_of_month': week_of_month,
        'weekday_name': target_date.strftime('%A'),
        'is_weekend': day_of_week in [6, 7],  # 토, 일
    }
    
    # 강제 타입 설정이 있는 경우
    if force_type:
        report_type = force_type
        result['forced_type'] = True
    else:
        result['forced_type'] = False
        
        # 자동 스케줄 결정 로직
        if day_of_week == 1 and week_of_month == 1:
            # 첫째주 월요일 → 월간 리포트
            report_type = "monthly"
        elif day_of_week == 1:
            # 일반 월요일 → 주간 리포트  
            report_type = "weekly"
        elif 2 <= day_of_week <= 5:
            # 평일 (화-금) → 일간 리포트
            report_type = "daily"
        else:
            # 주말 → 실행하지 않음
            report_type = "none"
    
    result['report_type'] = report_type
    
    # 데이터 기간 계산
    if report_type == "monthly":
        start_date, end_date = get_last_month_range(target_date)
        description = f"월간 보고서 - 지난달 ({start_date} ~ {end_date}) 데이터 분석"
        priority = 3
    elif report_type == "weekly":
        last_monday = get_last_monday(target_date)
        last_sunday = last_monday + timedelta(days=6)
        start_date = last_monday
        end_date = last_sunday
        description = f"주간 보고서 - 지난주 ({start_date} ~ {end_date}) 데이터 분석"
        priority = 2
    elif report_type == "daily":
        yesterday = target_date - timedelta(days=1)
        start_date = end_date = yesterday
        description = f"일간 보고서 - 어제 ({start_date}) 데이터 분석"
        priority = 1
    else:  # none
        start_date = end_date = None
        description = "주말 - 실행하지 않음"
        priority = 0
    
    result.update({
        'data_period_start': start_date.strftime('%Y-%m-%d') if start_date else None,
        'data_period_end': end_date.strftime('%Y-%m-%d') if end_date else None,
        'schedule_description': description,
        'execution_priority': priority,
        'should_run_pokernews': report_type != "none",
        'should_run_youtube': report_type != "none", 
        'should_run_platform': report_type != "none",
    })
    
    return result

def run_test_cases():
    """다양한 날짜에 대한 테스트 케이스 실행"""
    
    test_cases = [
        # 첫째주 월요일들 (월간 보고서)
        ('2024-01-01', '2024년 1월 첫째주 월요일'),  # 신정
        ('2024-02-05', '2024년 2월 첫째주 월요일'),
        ('2024-03-04', '2024년 3월 첫째주 월요일'),
        ('2024-04-01', '2024년 4월 첫째주 월요일'),
        ('2024-07-01', '2024년 7월 첫째주 월요일'),
        
        # 일반 월요일들 (주간 보고서)
        ('2024-01-08', '2024년 1월 둘째주 월요일'),
        ('2024-01-15', '2024년 1월 셋째주 월요일'),
        ('2024-02-12', '2024년 2월 둘째주 월요일'),
        ('2024-03-11', '2024년 3월 둘째주 월요일'),
        
        # 평일들 (일간 보고서)
        ('2024-01-09', '2024년 1월 9일 화요일'),
        ('2024-01-10', '2024년 1월 10일 수요일'),
        ('2024-01-11', '2024년 1월 11일 목요일'),
        ('2024-01-12', '2024년 1월 12일 금요일'),
        ('2024-02-13', '2024년 2월 13일 화요일'),
        
        # 주말들 (실행 안함)
        ('2024-01-13', '2024년 1월 13일 토요일'),
        ('2024-01-14', '2024년 1월 14일 일요일'),
        ('2024-02-10', '2024년 2월 10일 토요일'),
        ('2024-02-11', '2024년 2월 11일 일요일'),
    ]
    
    print("통합 포커 보고 스케줄링 시스템 - 테스트 케이스 실행")
    print("=" * 80)
    
    results = []
    
    for date_str, description in test_cases:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        result = determine_schedule(target_date)
        
        print(f"\n* {description}")
        print(f"   날짜: {result['current_date']} ({result['weekday_name']})")
        print(f"   요일 번호: {result['day_of_week']} (1=월, 7=일)")
        print(f"   월 중 몇째 주: {result['week_of_month']}주차")
        print(f"   -> 리포트 타입: {result['report_type']}")
        
        if result['report_type'] != 'none':
            print(f"   데이터 기간: {result['data_period_start']} ~ {result['data_period_end']}")
            print(f"   우선순위: {result['execution_priority']}")
            print(f"   실행 여부: PokerNews={result['should_run_pokernews']}, " +
                  f"YouTube={result['should_run_youtube']}, Platform={result['should_run_platform']}")
        else:
            print(f"   주말로 인한 실행 건너뛰기")
        
        results.append(result)
    
    print("\n" + "=" * 80)
    
    # 통계 요약
    monthly_count = sum(1 for r in results if r['report_type'] == 'monthly')
    weekly_count = sum(1 for r in results if r['report_type'] == 'weekly')
    daily_count = sum(1 for r in results if r['report_type'] == 'daily')
    none_count = sum(1 for r in results if r['report_type'] == 'none')
    
    print(f"테스트 결과 요약:")
    print(f"   월간 보고서: {monthly_count}개")
    print(f"   주간 보고서: {weekly_count}개")
    print(f"   일간 보고서: {daily_count}개")
    print(f"   실행 안함 (주말): {none_count}개")
    print(f"   총 테스트 케이스: {len(results)}개")
    
    return results

def validate_specific_date(date_str: str, force_type: str = None):
    """특정 날짜에 대한 스케줄 검증"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"날짜 형식 오류: {e}")
        return None
        
    result = determine_schedule(target_date, force_type)
    
    print(f"날짜별 스케줄 검증: {date_str}")
    print("=" * 50)
    print(f"대상 날짜: {result['current_date']} ({result['weekday_name']})")
    print(f"요일 정보: {result['day_of_week']} (1=월, 7=일)")
    print(f"월 중 주차: {result['week_of_month']}주차")
    
    if result['forced_type']:
        print(f"강제 설정: {force_type}")
    
    print(f"-> 결정된 리포트 타입: {result['report_type']}")
    
    if result['report_type'] != 'none':
        print(f"데이터 분석 기간: {result['data_period_start']} ~ {result['data_period_end']}")
        print(f"스케줄 설명: {result['schedule_description']}")
        print(f"실행 우선순위: {result['execution_priority']}")
        print(f"분석 단계 실행:")
        print(f"   - PokerNews: {'O' if result['should_run_pokernews'] else 'X'}")
        print(f"   - YouTube: {'O' if result['should_run_youtube'] else 'X'}")
        print(f"   - Platform: {'O' if result['should_run_platform'] else 'X'}")
    else:
        print(f"주말로 인해 실행하지 않음")
    
    return result

def export_test_results(results, filename='schedule_test_results.json'):
    """테스트 결과를 JSON 파일로 내보내기"""
    
    # 날짜 객체를 문자열로 변환하여 JSON 직렬화 가능하게 만듦
    json_results = []
    for result in results:
        json_result = result.copy()
        # 필요시 추가 변환 작업
        json_results.append(json_result)
    
    output_data = {
        'test_timestamp': datetime.now().isoformat(),
        'total_test_cases': len(results),
        'summary': {
            'monthly': sum(1 for r in results if r['report_type'] == 'monthly'),
            'weekly': sum(1 for r in results if r['report_type'] == 'weekly'),
            'daily': sum(1 for r in results if r['report_type'] == 'daily'),
            'none': sum(1 for r in results if r['report_type'] == 'none'),
        },
        'test_cases': json_results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"테스트 결과가 {filename}에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(
        description='통합 포커 보고 스케줄링 시스템 검증 도구'
    )
    
    parser.add_argument(
        '--date', 
        type=str,
        help='검증할 특정 날짜 (YYYY-MM-DD 형식)'
    )
    
    parser.add_argument(
        '--force-type',
        choices=['daily', 'weekly', 'monthly'],
        help='강제로 설정할 리포트 타입'
    )
    
    parser.add_argument(
        '--run-tests',
        action='store_true',
        help='전체 테스트 케이스 실행'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='테스트 결과를 JSON 파일로 내보내기'
    )
    
    args = parser.parse_args()
    
    if args.date:
        # 특정 날짜 검증
        result = validate_specific_date(args.date, args.force_type)
        if result and args.export:
            export_test_results([result], args.export)
            
    elif args.run_tests:
        # 전체 테스트 케이스 실행
        results = run_test_cases()
        if args.export:
            export_test_results(results, args.export)
            
    else:
        # 오늘 날짜로 기본 검증
        today = date.today()
        print("오늘 날짜 기준 스케줄 검증\n")
        result = validate_specific_date(today.strftime('%Y-%m-%d'), args.force_type)
        
        if args.export:
            export_test_results([result], args.export)

if __name__ == '__main__':
    main()