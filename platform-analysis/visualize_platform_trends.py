#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 트렌드 시각화 - 누적 영역형 차트
"""

import matplotlib
matplotlib.use('Agg')  # GUI 없이 파일로만 저장
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime, timedelta
import json

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def create_weekly_stacked_area_chart():
    """주간 누적 영역 차트 생성"""
    
    # 주간 데이터 (8/4 ~ 8/10)
    dates = ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10']
    
    # TOP 5 온라인 플레이어 데이터
    ggnetwork = [165234, 158472, 151683, 149295, 147516, 150842, 153008]
    pokerstars_it = [11145, 0, 0, 0, 0, 0, 0]  # 8/4 이후 데이터 없음
    idnpoker = [9837, 8956, 8423, 7891, 6987, 6234, 5528]
    wpt_global = [7521, 7234, 6987, 6754, 6521, 6843, 5237]
    pokerdom = [3921, 3845, 3768, 3692, 3615, 3701, 2693]
    others = [5000, 4800, 4600, 4400, 4200, 4100, 4000]  # 기타 플랫폼들
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 온라인 플레이어 누적 영역 차트
    ax1.fill_between(dates, 0, ggnetwork, label='GGNetwork', color='#2E7D32', alpha=0.8)
    ax1.fill_between(dates, ggnetwork, 
                     np.array(ggnetwork) + np.array(idnpoker), 
                     label='IDNPoker', color='#1976D2', alpha=0.8)
    ax1.fill_between(dates, 
                     np.array(ggnetwork) + np.array(idnpoker),
                     np.array(ggnetwork) + np.array(idnpoker) + np.array(wpt_global),
                     label='WPT Global', color='#F57C00', alpha=0.8)
    ax1.fill_between(dates,
                     np.array(ggnetwork) + np.array(idnpoker) + np.array(wpt_global),
                     np.array(ggnetwork) + np.array(idnpoker) + np.array(wpt_global) + np.array(pokerdom),
                     label='Pokerdom', color='#C62828', alpha=0.8)
    ax1.fill_between(dates,
                     np.array(ggnetwork) + np.array(idnpoker) + np.array(wpt_global) + np.array(pokerdom),
                     np.array(ggnetwork) + np.array(idnpoker) + np.array(wpt_global) + np.array(pokerdom) + np.array(pokerstars_it),
                     label='PokerStars.it', color='#6A1B9A', alpha=0.8)
    
    ax1.set_title('Weekly Online Players Trend (Aug 4-10, 2025)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Online Players')
    ax1.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 200000)
    
    # 주요 수치 표시 (GGNetwork만)
    for i, (date, value) in enumerate(zip(dates, ggnetwork)):
        if i == 0 or i == len(dates)-1:  # 시작과 끝만 표시
            ax1.annotate(f'{value:,}', 
                        xy=(i, value/2), 
                        ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white')
    
    # 포맷팅
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))
    
    # 캐시 플레이어 데이터
    gg_cash = [11234, 10987, 10756, 10523, 10291, 10347, 10404]
    wpt_cash = [3521, 3445, 3378, 3301, 3234, 3287, 3019]
    idn_cash = [2156, 2089, 1987, 1876, 1654, 1523, 1400]
    pokerdom_cash = [823, 798, 775, 751, 728, 739, 555]
    others_cash = [500, 480, 460, 440, 420, 410, 400]
    
    # 캐시 플레이어 누적 영역 차트
    ax2.fill_between(dates, 0, gg_cash, label='GGNetwork', color='#2E7D32', alpha=0.8)
    ax2.fill_between(dates, gg_cash,
                     np.array(gg_cash) + np.array(wpt_cash),
                     label='WPT Global', color='#F57C00', alpha=0.8)
    ax2.fill_between(dates,
                     np.array(gg_cash) + np.array(wpt_cash),
                     np.array(gg_cash) + np.array(wpt_cash) + np.array(idn_cash),
                     label='IDNPoker', color='#1976D2', alpha=0.8)
    ax2.fill_between(dates,
                     np.array(gg_cash) + np.array(wpt_cash) + np.array(idn_cash),
                     np.array(gg_cash) + np.array(wpt_cash) + np.array(idn_cash) + np.array(pokerdom_cash),
                     label='Pokerdom', color='#C62828', alpha=0.8)
    
    ax2.set_title('Weekly Cash Players Trend (Aug 4-10, 2025)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Cash Players')
    ax2.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 20000)
    
    # 주요 수치 표시 (GGNetwork만)
    for i, (date, value) in enumerate(zip(dates, gg_cash)):
        if i == 0 or i == len(dates)-1:  # 시작과 끝만 표시
            ax2.annotate(f'{value:,}', 
                        xy=(i, value/2), 
                        ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white')
    
    # 포맷팅
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))
    
    plt.tight_layout()
    plt.savefig('weekly_platform_trends.png', dpi=150, bbox_inches='tight')
    print("[SAVED] weekly_platform_trends.png")
    plt.close()

def create_monthly_comparison_chart():
    """월간 변화 비교 차트"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 온라인 플레이어 변화율 TOP 5
    platforms = ['GGNetwork\n-44.5%', 'iPoker.it\n+71.2%', 'iPoker EU\n+52.5%', 
                 'Chico\n-47.0%', 'PokerMatch\n-44.4%']
    start_values = [275661, 1508, 1744, 1797, 554]
    end_values = [153008, 2582, 2660, 953, 308]
    
    x = np.arange(len(platforms))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, start_values, width, label='Jul 30', color='#1976D2', alpha=0.8)
    bars2 = ax1.bar(x + width/2, end_values, width, label='Aug 10', color='#C62828', alpha=0.8)
    
    # 막대 위에 값 표시
    for i, (bar1, bar2, s, e) in enumerate(zip(bars1, bars2, start_values, end_values)):
        # 시작값 표시
        if s > 10000:  # 큰 값은 K 단위로
            ax1.text(bar1.get_x() + bar1.get_width()/2, s + 2000, f'{s/1000:.0f}K',
                    ha='center', va='bottom', fontsize=7)
        else:
            ax1.text(bar1.get_x() + bar1.get_width()/2, s + 100, f'{s:,.0f}',
                    ha='center', va='bottom', fontsize=7)
        
        # 종료값 표시
        if e > 10000:  # 큰 값은 K 단위로
            ax1.text(bar2.get_x() + bar2.get_width()/2, e + 2000, f'{e/1000:.0f}K',
                    ha='center', va='bottom', fontsize=7)
        else:
            ax1.text(bar2.get_x() + bar2.get_width()/2, e + 100, f'{e:,.0f}',
                    ha='center', va='bottom', fontsize=7)
    
    # 변화율 표시 (상단에)
    for i, (s, e) in enumerate(zip(start_values, end_values)):
        change = ((e - s) / s) * 100
        color = '#2E7D32' if change > 0 else '#C62828'
        y_pos = max(s, e) * 1.3  # 막대 위 30% 위치
        ax1.text(i, y_pos, f'{change:+.0f}%', 
                ha='center', fontweight='bold', color=color, fontsize=9)
    
    ax1.set_title('Monthly Online Players Change (Jul 30 - Aug 10)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Players')
    ax1.set_xticks(x)
    ax1.set_xticklabels(platforms, fontsize=8)
    ax1.legend(loc='upper left', framealpha=0.9)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_yscale('log')  # 로그 스케일로 큰 차이 표현
    
    # 캐시 플레이어 변화율 TOP 5
    cash_platforms = ['WSOP MI\n+244.7%', 'BetMGM MI\n+140.7%', 'Ray.fi\n+74.4%',
                      'GGPoker ON\n-54.7%', 'Chico\n-49.9%']
    cash_start = [114, 167, 313, 234, 357]
    cash_end = [393, 402, 546, 106, 179]
    
    x2 = np.arange(len(cash_platforms))
    
    bars3 = ax2.bar(x2 - width/2, cash_start, width, label='Jul 30', color='#1976D2', alpha=0.8)
    bars4 = ax2.bar(x2 + width/2, cash_end, width, label='Aug 10', color='#C62828', alpha=0.8)
    
    # 막대 위에 값 표시
    for i, (bar3, bar4, s, e) in enumerate(zip(bars3, bars4, cash_start, cash_end)):
        # 시작값 표시
        ax2.text(bar3.get_x() + bar3.get_width()/2, s + 5, f'{s}',
                ha='center', va='bottom', fontsize=7)
        # 종료값 표시
        ax2.text(bar4.get_x() + bar4.get_width()/2, e + 5, f'{e}',
                ha='center', va='bottom', fontsize=7)
    
    # 변화율 표시 (상단에)
    for i, (s, e) in enumerate(zip(cash_start, cash_end)):
        change = ((e - s) / s) * 100
        color = '#2E7D32' if change > 0 else '#C62828'
        y_pos = max(s, e) * 1.15  # 막대 위 15% 위치
        ax2.text(i, y_pos, f'{change:+.0f}%',
                ha='center', fontweight='bold', color=color, fontsize=9)
    
    ax2.set_title('Monthly Cash Players Change (Jul 30 - Aug 10)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Players')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(cash_platforms, fontsize=8)
    ax2.legend(loc='upper left', framealpha=0.9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('monthly_platform_changes.png', dpi=150, bbox_inches='tight')
    print("[SAVED] monthly_platform_changes.png")
    plt.close()

def create_market_share_pie():
    """시장 점유율 파이 차트"""
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 일간 점유율
    daily_labels = ['GGNetwork\n89.1%', 'IDNPoker\n3.2%', 'WPT Global\n3.1%', 'Others\n4.6%']
    daily_sizes = [89.1, 3.2, 3.1, 4.6]
    colors = ['#2E7D32', '#1976D2', '#F57C00', '#9E9E9E']
    
    axes[0].pie(daily_sizes, labels=daily_labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'edgecolor': 'white'})
    axes[0].set_title('Daily Market Share (Aug 10)', fontweight='bold')
    
    # 주간 점유율
    weekly_labels = ['GGNetwork\n77.9%', 'PokerStars.it\n5.7%', 'IDNPoker\n4.3%', 'Others\n12.1%']
    weekly_sizes = [77.9, 5.7, 4.3, 12.1]
    
    axes[1].pie(weekly_sizes, labels=weekly_labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'edgecolor': 'white'})
    axes[1].set_title('Weekly Market Share (Aug 4-10)', fontweight='bold')
    
    # 월간 점유율
    monthly_labels = ['GGNetwork\n81.8%', 'PokerStars.it\n4.6%', 'IDNPoker\n3.4%', 'Others\n10.2%']
    monthly_sizes = [81.8, 4.6, 3.4, 10.2]
    
    axes[2].pie(monthly_sizes, labels=monthly_labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'edgecolor': 'white'})
    axes[2].set_title('Monthly Market Share (Jul 30 - Aug 10)', fontweight='bold')
    
    plt.suptitle('Platform Market Share Comparison', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('market_share_comparison.png', dpi=150, bbox_inches='tight')
    print("[SAVED] market_share_comparison.png")
    plt.close()

def main():
    """메인 실행"""
    print("="*60)
    print("플랫폼 트렌드 시각화 생성")
    print("="*60)
    
    print("\n1. 주간 누적 영역 차트 생성...")
    create_weekly_stacked_area_chart()
    
    print("\n2. 월간 변화 비교 차트 생성...")
    create_monthly_comparison_chart()
    
    print("\n3. 시장 점유율 비교 차트 생성...")
    create_market_share_pie()
    
    print("\n[완료] 모든 차트가 생성되었습니다.")
    print("- weekly_platform_trends.png")
    print("- monthly_platform_changes.png")
    print("- market_share_comparison.png")

if __name__ == "__main__":
    main()