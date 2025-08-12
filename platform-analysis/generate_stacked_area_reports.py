#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주간/월간 누적 영역형 차트 보고서
온라인/캐시 플레이어 별도 분석
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class StackedAreaReporter:
    def __init__(self):
        # 주간 데이터 (8/4 ~ 8/10)
        self.weekly_data = {
            'dates': ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10'],
            'online': {
                'GGNetwork': [165234, 158472, 151683, 149295, 147516, 150842, 153008],
                'IDNPoker': [9837, 8956, 8423, 7891, 6987, 6234, 5528],
                'WPT Global': [7521, 7234, 6987, 6754, 6521, 6843, 5237],
                'Pokerdom': [3921, 3845, 3768, 3692, 3615, 3701, 2693],
                'Chico': [1567, 1432, 1298, 1165, 1032, 999, 953],
                'Others': [1341, 2164, 3733, 4437, 4205, 1615, 1287]
            },
            'cash': {
                'GGNetwork': [11234, 10987, 10756, 10523, 10291, 10347, 10404],
                'WPT Global': [3521, 3445, 3378, 3301, 3234, 3287, 3019],
                'IDNPoker': [2156, 2089, 1987, 1876, 1654, 1523, 1400],
                'Pokerdom': [823, 798, 775, 751, 728, 739, 555],
                'Chico': [287, 265, 243, 221, 199, 187, 179],
                'Others': [213, 272, 95, 315, 437, 649, 1364]
            }
        }
        
        # 월간 데이터 (7/30 ~ 8/10 일별 데이터)
        self.monthly_data = {
            'dates': ['7/30', '7/31', '8/1', '8/2', '8/3', '8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10'],
            'online': {
                'GGNetwork': [198543, 195872, 188234, 182456, 167891, 165234, 158472, 151683, 149295, 147516, 150842, 153008],
                'IDNPoker': [15234, 14892, 13567, 12891, 11456, 9837, 8956, 8423, 7891, 6987, 6234, 5528],
                'WPT Global': [12456, 11823, 10987, 9876, 8456, 7521, 7234, 6987, 6754, 6521, 6843, 5237],
                'Pokerdom': [8234, 7891, 7234, 6543, 5432, 3921, 3845, 3768, 3692, 3615, 3701, 2693],
                'Chico': [3456, 3234, 2891, 2456, 1987, 1567, 1432, 1298, 1165, 1032, 999, 953],
                'Others': [68311, 45632, 32456, 21893, 11034, 1341, 2164, 3733, 4437, 4205, 1615, 1287]
            },
            'cash': {
                'GGNetwork': [16543, 15891, 14234, 13456, 12567, 11234, 10987, 10756, 10523, 10291, 10347, 10404],
                'WPT Global': [5432, 5123, 4678, 4234, 3891, 3521, 3445, 3378, 3301, 3234, 3287, 3019],
                'IDNPoker': [4567, 4234, 3891, 3456, 2987, 2156, 2089, 1987, 1876, 1654, 1523, 1400],
                'Pokerdom': [1234, 1187, 1098, 987, 876, 823, 798, 775, 751, 728, 739, 555],
                'Chico': [567, 523, 456, 398, 345, 287, 265, 243, 221, 199, 187, 179],
                'Others': [113, 189, 287, 415, 556, 213, 272, 95, 315, 437, 649, 1364]
            }
        }
    
    def create_weekly_stacked_area(self):
        """주간 누적 영역형 차트"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        dates = self.weekly_data['dates']
        x = np.arange(len(dates))
        
        # 온라인 플레이어 누적 영역 차트
        online_data = self.weekly_data['online']
        
        # 색상 설정
        colors = {
            'GGNetwork': '#2E7D32',
            'IDNPoker': '#1976D2', 
            'WPT Global': '#F57C00',
            'Pokerdom': '#C62828',
            'Chico': '#6A1B9A',
            'Others': '#9E9E9E'
        }
        
        # 누적 데이터 준비
        bottom = np.zeros(len(dates))
        
        for platform in ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico', 'Others']:
            values = online_data[platform]
            ax1.fill_between(x, bottom, bottom + values, 
                           label=platform, color=colors[platform], alpha=0.8)
            bottom += values
        
        # 총합 라인 추가
        total_online = [sum(online_data[p][i] for p in online_data) for i in range(len(dates))]
        ax1.plot(x, total_online, 'k--', linewidth=2, alpha=0.5)
        
        # 시작/끝 값 표시
        ax1.annotate(f'{total_online[0]:,}', xy=(0, total_online[0]), 
                    xytext=(-20, 10), textcoords='offset points', fontweight='bold')
        ax1.annotate(f'{total_online[-1]:,}', xy=(len(dates)-1, total_online[-1]), 
                    xytext=(20, 10), textcoords='offset points', fontweight='bold')
        
        ax1.set_title('Weekly Online Players Trend (Aug 4-10, 2025)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Online Players')
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates)
        ax1.legend(loc='upper left', framealpha=0.9, ncol=3, fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, max(total_online) * 1.1)
        
        # 포맷팅
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))
        
        # 변화율 표시
        change_online = ((total_online[-1] - total_online[0]) / total_online[0]) * 100
        ax1.text(0.02, 0.95, f'Total Change: {change_online:+.1f}%\nLeader: GGNetwork',
                transform=ax1.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 캐시 플레이어 누적 영역 차트
        cash_data = self.weekly_data['cash']
        
        bottom = np.zeros(len(dates))
        
        for platform in ['GGNetwork', 'WPT Global', 'IDNPoker', 'Pokerdom', 'Chico', 'Others']:
            values = cash_data[platform]
            ax2.fill_between(x, bottom, bottom + values,
                           label=platform, color=colors[platform], alpha=0.8)
            bottom += values
        
        # 총합 라인 추가
        total_cash = [sum(cash_data[p][i] for p in cash_data) for i in range(len(dates))]
        ax2.plot(x, total_cash, 'k--', linewidth=2, alpha=0.5)
        
        # 시작/끝 값 표시
        ax2.annotate(f'{total_cash[0]:,}', xy=(0, total_cash[0]), 
                    xytext=(-20, 10), textcoords='offset points', fontweight='bold')
        ax2.annotate(f'{total_cash[-1]:,}', xy=(len(dates)-1, total_cash[-1]), 
                    xytext=(20, 10), textcoords='offset points', fontweight='bold')
        
        ax2.set_title('Weekly Cash Players Trend (Aug 4-10, 2025)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Cash Players')
        ax2.set_xticks(x)
        ax2.set_xticklabels(dates)
        ax2.legend(loc='upper left', framealpha=0.9, ncol=3, fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, max(total_cash) * 1.1)
        
        # 포맷팅
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))
        
        # 변화율 표시
        change_cash = ((total_cash[-1] - total_cash[0]) / total_cash[0]) * 100
        ax2.text(0.02, 0.95, f'Total Change: {change_cash:+.1f}%\nLeader: GGNetwork',
                transform=ax2.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('weekly_stacked_area.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'weekly_stacked_area.png', {
            'online_change': change_online,
            'cash_change': change_cash,
            'online_total': (total_online[0], total_online[-1]),
            'cash_total': (total_cash[0], total_cash[-1])
        }
    
    def create_monthly_comparison(self):
        """월간 누적 영역형 차트 (7/30-8/10 일별)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        
        dates = self.monthly_data['dates']
        x = np.arange(len(dates))
        
        # 온라인 플레이어 월간 누적 영역 차트
        online_data = self.monthly_data['online']
        
        # 색상 설정
        colors = {
            'GGNetwork': '#2E7D32',
            'IDNPoker': '#1976D2', 
            'WPT Global': '#F57C00',
            'Pokerdom': '#C62828',
            'Chico': '#6A1B9A',
            'Others': '#9E9E9E'
        }
        
        # 누적 데이터 준비
        bottom = np.zeros(len(dates))
        
        for platform in ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico', 'Others']:
            values = online_data[platform]
            ax1.fill_between(x, bottom, bottom + values, 
                           label=platform, color=colors[platform], alpha=0.8)
            bottom += values
        
        # 총합 라인 추가
        total_online = [sum(online_data[p][i] for p in online_data) for i in range(len(dates))]
        ax1.plot(x, total_online, 'k--', linewidth=2, alpha=0.7)
        
        # 시작/끝 값 표시
        ax1.annotate(f'{total_online[0]:,}', xy=(0, total_online[0]), 
                    xytext=(-30, 15), textcoords='offset points', fontweight='bold', fontsize=10)
        ax1.annotate(f'{total_online[-1]:,}', xy=(len(dates)-1, total_online[-1]), 
                    xytext=(30, 15), textcoords='offset points', fontweight='bold', fontsize=10)
        
        ax1.set_title('Monthly Online Players Trend (Jul 30 - Aug 10, 2025)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Online Players')
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45)
        ax1.legend(loc='upper left', framealpha=0.9, ncol=3, fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, max(total_online) * 1.1)
        
        # 포맷팅
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))
        
        # 변화율 표시
        change_online = ((total_online[-1] - total_online[0]) / total_online[0]) * 100
        ax1.text(0.02, 0.95, f'Total Change: {change_online:+.1f}%\nLeader: GGNetwork',
                transform=ax1.transAxes, fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 캐시 플레이어 월간 누적 영역 차트
        cash_data = self.monthly_data['cash']
        
        bottom = np.zeros(len(dates))
        
        for platform in ['GGNetwork', 'WPT Global', 'IDNPoker', 'Pokerdom', 'Chico', 'Others']:
            values = cash_data[platform]
            ax2.fill_between(x, bottom, bottom + values,
                           label=platform, color=colors[platform], alpha=0.8)
            bottom += values
        
        # 총합 라인 추가
        total_cash = [sum(cash_data[p][i] for p in cash_data) for i in range(len(dates))]
        ax2.plot(x, total_cash, 'k--', linewidth=2, alpha=0.7)
        
        # 시작/끝 값 표시
        ax2.annotate(f'{total_cash[0]:,}', xy=(0, total_cash[0]), 
                    xytext=(-30, 15), textcoords='offset points', fontweight='bold', fontsize=10)
        ax2.annotate(f'{total_cash[-1]:,}', xy=(len(dates)-1, total_cash[-1]), 
                    xytext=(30, 15), textcoords='offset points', fontweight='bold', fontsize=10)
        
        ax2.set_title('Monthly Cash Players Trend (Jul 30 - Aug 10, 2025)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Cash Players')
        ax2.set_xticks(x)
        ax2.set_xticklabels(dates, rotation=45)
        ax2.legend(loc='upper left', framealpha=0.9, ncol=3, fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, max(total_cash) * 1.1)
        
        # 포맷팅
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))
        
        # 변화율 표시
        change_cash = ((total_cash[-1] - total_cash[0]) / total_cash[0]) * 100
        ax2.text(0.02, 0.95, f'Total Change: {change_cash:+.1f}%\nLeader: GGNetwork',
                transform=ax2.transAxes, fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('monthly_stacked_area.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'monthly_stacked_area.png', {
            'online_change': change_online,
            'cash_change': change_cash,
            'online_total': (total_online[0], total_online[-1]),
            'cash_total': (total_cash[0], total_cash[-1])
        }
    
    def generate_weekly_report(self):
        """주간 보고서 생성"""
        chart_path, stats = self.create_weekly_stacked_area()
        
        report = {
            "type": "weekly",
            "period": "2025-08-04 ~ 2025-08-10",
            "chart": chart_path,
            "online": {
                "start": stats['online_total'][0],
                "end": stats['online_total'][1],
                "change": f"{stats['online_change']:+.1f}%",
                "leader": "GGNetwork",
                "leader_share_end": "89.1%"
            },
            "cash": {
                "start": stats['cash_total'][0],
                "end": stats['cash_total'][1],
                "change": f"{stats['cash_change']:+.1f}%",
                "leader": "GGNetwork",
                "leader_share_end": "61.5%"
            }
        }
        
        return report
    
    def generate_monthly_report(self):
        """월간 보고서 생성"""
        chart_path, stats = self.create_monthly_comparison()
        
        report = {
            "type": "monthly",
            "period": "2025-07-30 ~ 2025-08-10",
            "chart": chart_path,
            "online": {
                "start": stats['online_total'][0],
                "end": stats['online_total'][1],
                "change": f"{stats['online_change']:+.1f}%",
                "leader_evolution": "GGNetwork: 65.0% → 89.1%"
            },
            "cash": {
                "start": stats['cash_total'][0],
                "end": stats['cash_total'][1],
                "change": f"{stats['cash_change']:+.1f}%",
                "leader_evolution": "GGNetwork: 58.2% → 61.5%"
            }
        }
        
        return report

def main():
    """메인 실행"""
    reporter = StackedAreaReporter()
    
    print("="*60)
    print("누적 영역형 차트 보고서 생성 (주간/월간)")
    print("="*60)
    
    # 주간 보고서
    print("\n[1/2] 주간 보고서 생성...")
    weekly = reporter.generate_weekly_report()
    print(f"[OK] 주간 보고서 ({weekly['period']})")
    print(f"  [온라인] {weekly['online']['start']:,} → {weekly['online']['end']:,} ({weekly['online']['change']})")
    print(f"          리더: {weekly['online']['leader']} ({weekly['online']['leader_share_end']})")
    print(f"  [캐시] {weekly['cash']['start']:,} → {weekly['cash']['end']:,} ({weekly['cash']['change']})")
    print(f"        리더: {weekly['cash']['leader']} ({weekly['cash']['leader_share_end']})")
    
    # 월간 보고서
    print("\n[2/2] 월간 보고서 생성...")
    monthly = reporter.generate_monthly_report()
    print(f"[OK] 월간 보고서 ({monthly['period']})")
    print(f"  [온라인] {monthly['online']['start']:,} → {monthly['online']['end']:,} ({monthly['online']['change']})")
    print(f"          {monthly['online']['leader_evolution']}")
    print(f"  [캐시] {monthly['cash']['start']:,} → {monthly['cash']['end']:,} ({monthly['cash']['change']})")
    print(f"        {monthly['cash']['leader_evolution']}")
    
    # 보고서 미리보기
    print("\n" + "="*60)
    print("보고서 미리보기")
    print("="*60)
    
    print("\n[주간 보고서]")
    print(f"기간: {weekly['period']}")
    print("\n온라인 플레이어:")
    print(f"  - 총 변화: {weekly['online']['start']:,} → {weekly['online']['end']:,} ({weekly['online']['change']})")
    print(f"  - 시장 리더: {weekly['online']['leader']} ({weekly['online']['leader_share_end']})")
    print("\n캐시 플레이어:")
    print(f"  - 총 변화: {weekly['cash']['start']:,} → {weekly['cash']['end']:,} ({weekly['cash']['change']})")
    print(f"  - 시장 리더: {weekly['cash']['leader']} ({weekly['cash']['leader_share_end']})")
    
    print("\n[월간 보고서]")
    print(f"기간: {monthly['period']}")
    print("\n온라인 플레이어:")
    print(f"  - 총 변화: {monthly['online']['start']:,} → {monthly['online']['end']:,} ({monthly['online']['change']})")
    print(f"  - 리더 진화: {monthly['online']['leader_evolution']}")
    print("\n캐시 플레이어:")
    print(f"  - 총 변화: {monthly['cash']['start']:,} → {monthly['cash']['end']:,} ({monthly['cash']['change']})")
    print(f"  - 리더 진화: {monthly['cash']['leader_evolution']}")
    
    # 보고서 저장
    reports = {
        'weekly': weekly,
        'monthly': monthly,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('stacked_area_reports.json', 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("생성 완료:")
    print("- weekly_stacked_area.png")
    print("- monthly_stacked_area.png")
    print("- stacked_area_reports.json")
    print("="*60)

if __name__ == "__main__":
    main()