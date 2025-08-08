#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron 표현식 검증기
"""

def validate_cron_expressions():
    cron_expressions = [
        ('30 1 * * *', '매일 오전 10시 30분 (KST)'),
        ('30 2 * * 1', '매주 월요일 오전 11시 30분 (KST)'),
        ('0 6 1 * *', '매월 1일 오후 3시 (KST)')
    ]

    print('=== CRON 표현식 검증 ===')
    all_valid = True

    for cron_expr, description in cron_expressions:
        print(f'검증 중: {cron_expr} - {description}')
        
        parts = cron_expr.split()
        if len(parts) != 5:
            print('[ERROR] Cron 표현식 형식 오류 (5개 필드 필요)')
            all_valid = False
            continue
        
        minute, hour, day, month, dow = parts
        
        # 기본 검증
        try:
            if minute != '*':
                min_val = int(minute)
                if not (0 <= min_val <= 59):
                    print(f'[ERROR] 분 범위 오류: {minute} (0-59)')
                    all_valid = False
                    continue
                    
            if hour != '*':
                hour_val = int(hour)
                if not (0 <= hour_val <= 23):
                    print(f'[ERROR] 시간 범위 오류: {hour} (0-23)')
                    all_valid = False
                    continue
                    
            if day != '*':
                day_val = int(day)
                if not (1 <= day_val <= 31):
                    print(f'[ERROR] 일 범위 오류: {day} (1-31)')
                    all_valid = False
                    continue
                    
            if month != '*':
                month_val = int(month)
                if not (1 <= month_val <= 12):
                    print(f'[ERROR] 월 범위 오류: {month} (1-12)')
                    all_valid = False
                    continue
                    
            if dow != '*':
                dow_val = int(dow)
                if not (0 <= dow_val <= 7):  # 0과 7 모두 일요일
                    print(f'[ERROR] 요일 범위 오류: {dow} (0-7)')
                    all_valid = False
                    continue
                    
            print('[OK] 유효한 Cron 표현식')
            
        except ValueError as e:
            print(f'[ERROR] 값 파싱 오류: {e}')
            all_valid = False
        
        print()
    
    return all_valid

if __name__ == "__main__":
    result = validate_cron_expressions()
    if result:
        print("[SUCCESS] 모든 Cron 표현식이 유효합니다.")
    else:
        print("[FAILED] 일부 Cron 표현식에 문제가 있습니다.")