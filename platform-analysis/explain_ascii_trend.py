#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII 차트 의미 설명
"""

def main():
    # 주간 데이터
    dates = ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10']
    weekly_online = [189421, 182103, 175892, 173234, 169876, 170234, 168706]
    
    print("=" * 60)
    print("주간 ASCII 차트 의미 설명")
    print("=" * 60)
    
    print("\n[1] 실제 데이터 (일별 온라인 플레이어)")
    for i, (date, total) in enumerate(zip(dates, weekly_online)):
        change = ""
        if i > 0:
            diff = total - weekly_online[i-1]
            pct = (diff / weekly_online[i-1]) * 100
            change = f" ({diff:+,}, {pct:+.1f}%)"
        print(f"  {date}: {total:,}명{change}")
    
    print(f"\n[2] 전체 변화")
    print(f"  시작: {weekly_online[0]:,}명")
    print(f"  종료: {weekly_online[-1]:,}명")
    print(f"  감소: {weekly_online[0] - weekly_online[-1]:,}명 (-{((weekly_online[0] - weekly_online[-1]) / weekly_online[0]) * 100:.1f}%)")
    
    print(f"\n[3] ASCII 트렌드 의미")
    print("  ASCII 문자:")
    print("  ▇ = 높음 (최대값 기준)")
    print("  ▅ = 중간")  
    print("  ▂ = 낮음")
    print("  ▁ = 최저 (최소값 기준)")
    
    # 정규화된 값 계산
    min_val = min(weekly_online)
    max_val = max(weekly_online)
    
    print(f"\n[4] 각 날짜별 ASCII 의미")
    trend_chars = ["▁", "▂", "▅", "▇"]
    
    for i, (date, total) in enumerate(zip(dates, weekly_online)):
        # 0-3 범위로 정규화
        normalized = (total - min_val) / (max_val - min_val)
        level = int(normalized * 3)
        level = min(level, 3)  # 최대 3
        
        char = trend_chars[level]
        level_name = ["최저", "낮음", "중간", "높음"][level]
        
        print(f"  {date}: {char} = {level_name} ({total:,}명)")
    
    print(f"\n[5] 트렌드 해석")
    print("  - 8/4가 최고점이므로 ▇")
    print("  - 8/5~8/6은 지속 감소로 ▅▂")
    print("  - 8/7~8/10은 최저 구간이므로 ▁▁▁▁")
    print("  - 전체적으로 하향 추세")
    
    print(f"\n[6] 실제 ASCII 차트 예시")
    print("  8/4  8/5  8/6  8/7  8/8  8/9  8/10")
    
    # 실제 트렌드 생성
    trend_line = ""
    for total in weekly_online:
        normalized = (total - min_val) / (max_val - min_val)
        level = int(normalized * 3)
        level = min(level, 3)
        trend_line += trend_chars[level]
    
    print(f"  {trend_line}")
    print(f"  {weekly_online[0]:,} → {weekly_online[-1]:,} (-10.9%)")

if __name__ == "__main__":
    main()