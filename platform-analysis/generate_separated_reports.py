#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인/캐시 플레이어 별도 분석 보고서
두 카테고리를 완전히 독립적으로 분석
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

class SeparatedPlatformReporter:
    def __init__(self):
        # 일간 데이터 (2025-08-10)
        self.daily_data = {
            'date': '2025-08-10',
            'online': {
                'total': 171706,
                'platforms': [
                    {'name': 'GGNetwork', 'value': 153008, 'share': 89.1},
                    {'name': 'IDNPoker', 'value': 5528, 'share': 3.2},
                    {'name': 'WPT Global', 'value': 5237, 'share': 3.1},
                    {'name': 'Pokerdom', 'value': 2693, 'share': 1.6},
                    {'name': 'Chico', 'value': 953, 'share': 0.6}
                ]
            },
            'cash': {
                'total': 16921,
                'platforms': [
                    {'name': 'GGNetwork', 'value': 10404, 'share': 61.5},
                    {'name': 'WPT Global', 'value': 3019, 'share': 17.8},
                    {'name': 'IDNPoker', 'value': 1400, 'share': 8.3},
                    {'name': 'Pokerdom', 'value': 555, 'share': 3.3},
                    {'name': 'Chico', 'value': 179, 'share': 1.1}
                ]
            }
        }
        
        # 주간 데이터
        self.weekly_data = {
            'period': '2025-08-04 ~ 2025-08-10',
            'online': {
                'start': 189421,
                'end': 171706,
                'change': -9.4,
                'daily': [189421, 182103, 176892, 173234, 169876, 168234, 171706],
                'top_changes': [
                    {'name': 'GGNetwork', 'change': -7.4},
                    {'name': 'IDNPoker', 'change': -43.8},
                    {'name': 'WPT Global', 'change': -30.4},
                    {'name': 'Pokerdom', 'change': -31.3},
                    {'name': 'Chico', 'change': -39.2}
                ]
            },
            'cash': {
                'start': 18234,
                'end': 16921,
                'change': -7.2,
                'daily': [18234, 17856, 17234, 16987, 16543, 16732, 16921],
                'top_changes': [
                    {'name': 'GGNetwork', 'change': -7.4},
                    {'name': 'WPT Global', 'change': -14.2},
                    {'name': 'IDNPoker', 'change': -35.1},
                    {'name': 'Pokerdom', 'change': -32.5},
                    {'name': 'Chico', 'change': -37.6}
                ]
            }
        }
        
        # 월간 데이터
        self.monthly_data = {
            'period': '2025-07-30 ~ 2025-08-10',
            'online': {
                'start': 306234,
                'end': 171706,
                'change': -43.9,
                'leader_start': {'name': 'GGNetwork', 'share': 65.0},
                'leader_end': {'name': 'GGNetwork', 'share': 89.1},
                'top_gainers': [
                    {'name': 'iPoker.it', 'change': 71.2},
                    {'name': 'iPoker EU', 'change': 52.5}
                ],
                'top_losers': [
                    {'name': 'GGNetwork', 'change': -44.5},
                    {'name': 'IDNPoker', 'change': -43.8},
                    {'name': 'Chico', 'change': -47.0}
                ]
            },
            'cash': {
                'start': 28456,
                'end': 16921,
                'change': -40.5,
                'leader_start': {'name': 'GGNetwork', 'share': 58.2},
                'leader_end': {'name': 'GGNetwork', 'share': 61.5},
                'top_gainers': [
                    {'name': 'WSOP MI', 'change': 244.7},
                    {'name': 'BetMGM MI', 'change': 140.7},
                    {'name': 'Ray.fi', 'change': 74.4}
                ],
                'top_losers': [
                    {'name': 'GGPoker ON', 'change': -54.7},
                    {'name': 'Chico', 'change': -49.9},
                    {'name': 'IDNPoker', 'change': -35.1}
                ]
            }
        }
    
    def create_daily_chart(self):
        """일간 차트 - 온라인/캐시 별도"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 온라인 플레이어 분석
        online_data = self.daily_data['online']['platforms']
        online_names = [p['name'] for p in online_data[:5]]
        online_values = [p['value'] for p in online_data[:5]]
        online_shares = [p['share'] for p in online_data[:5]]
        
        # 온라인 막대 차트
        colors_online = ['#2E7D32', '#1976D2', '#F57C00', '#C62828', '#6A1B9A']
        bars1 = ax1.bar(range(len(online_names)), online_values, color=colors_online, alpha=0.8)
        ax1.set_title(f'Online Players - {self.daily_data["date"]}\nTotal: {self.daily_data["online"]["total"]:,}', 
                     fontsize=12, fontweight='bold')
        ax1.set_xlabel('Platform')
        ax1.set_ylabel('Players')
        ax1.set_xticks(range(len(online_names)))
        ax1.set_xticklabels(online_names, rotation=45)
        
        # 값과 점유율 표시
        for i, (bar, val, share) in enumerate(zip(bars1, online_values, online_shares)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                    f'{val:,}\n({share}%)', ha='center', va='bottom', fontsize=9)
        
        # 리더 표시
        ax1.text(0.5, 0.95, f"Leader: {online_data[0]['name']} ({online_data[0]['share']}%)",
                transform=ax1.transAxes, ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
        # 캐시 플레이어 분석
        cash_data = self.daily_data['cash']['platforms']
        cash_names = [p['name'] for p in cash_data[:5]]
        cash_values = [p['value'] for p in cash_data[:5]]
        cash_shares = [p['share'] for p in cash_data[:5]]
        
        # 캐시 막대 차트
        colors_cash = ['#2E7D32', '#F57C00', '#1976D2', '#C62828', '#6A1B9A']
        bars2 = ax2.bar(range(len(cash_names)), cash_values, color=colors_cash, alpha=0.8)
        ax2.set_title(f'Cash Players - {self.daily_data["date"]}\nTotal: {self.daily_data["cash"]["total"]:,}', 
                     fontsize=12, fontweight='bold')
        ax2.set_xlabel('Platform')
        ax2.set_ylabel('Players')
        ax2.set_xticks(range(len(cash_names)))
        ax2.set_xticklabels(cash_names, rotation=45)
        
        # 값과 점유율 표시
        for i, (bar, val, share) in enumerate(zip(bars2, cash_values, cash_shares)):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                    f'{val:,}\n({share}%)', ha='center', va='bottom', fontsize=9)
        
        # 리더 표시
        ax2.text(0.5, 0.95, f"Leader: {cash_data[0]['name']} ({cash_data[0]['share']}%)",
                transform=ax2.transAxes, ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('daily_separated_chart.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'daily_separated_chart.png'
    
    def create_weekly_chart(self):
        """주간 차트 - 온라인/캐시 별도"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        dates = ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10']
        
        # 온라인 트렌드
        online_trend = self.weekly_data['online']['daily']
        ax1.plot(dates, online_trend, marker='o', linewidth=2, markersize=8, color='#1976D2')
        ax1.set_title(f'Online Players Trend\n{self.weekly_data["online"]["start"]:,} → {self.weekly_data["online"]["end"]:,} ({self.weekly_data["online"]["change"]:.1f}%)',
                     fontsize=12, fontweight='bold')
        ax1.set_ylabel('Players')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(range(len(dates)), online_trend, alpha=0.3, color='#1976D2')
        
        # 시작/끝 값 표시
        ax1.annotate(f'{online_trend[0]:,}', xy=(0, online_trend[0]), 
                    xytext=(-10, 10), textcoords='offset points', fontweight='bold')
        ax1.annotate(f'{online_trend[-1]:,}', xy=(len(dates)-1, online_trend[-1]), 
                    xytext=(10, 10), textcoords='offset points', fontweight='bold')
        
        # 캐시 트렌드
        cash_trend = self.weekly_data['cash']['daily']
        ax2.plot(dates, cash_trend, marker='s', linewidth=2, markersize=8, color='#F57C00')
        ax2.set_title(f'Cash Players Trend\n{self.weekly_data["cash"]["start"]:,} → {self.weekly_data["cash"]["end"]:,} ({self.weekly_data["cash"]["change"]:.1f}%)',
                     fontsize=12, fontweight='bold')
        ax2.set_ylabel('Players')
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(range(len(dates)), cash_trend, alpha=0.3, color='#F57C00')
        
        # 시작/끝 값 표시
        ax2.annotate(f'{cash_trend[0]:,}', xy=(0, cash_trend[0]), 
                    xytext=(-10, 10), textcoords='offset points', fontweight='bold')
        ax2.annotate(f'{cash_trend[-1]:,}', xy=(len(dates)-1, cash_trend[-1]), 
                    xytext=(10, 10), textcoords='offset points', fontweight='bold')
        
        # 온라인 플랫폼 변화
        online_changes = self.weekly_data['online']['top_changes']
        platforms = [p['name'] for p in online_changes]
        changes = [p['change'] for p in online_changes]
        colors = ['#C62828' if c < 0 else '#2E7D32' for c in changes]
        
        bars3 = ax3.barh(platforms, changes, color=colors, alpha=0.8)
        ax3.set_title('Online Players - Platform Changes', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Change (%)')
        ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        for bar, val in zip(bars3, changes):
            x_pos = bar.get_width() + 1 if val > 0 else bar.get_width() - 1
            ax3.text(x_pos, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', ha='left' if val > 0 else 'right', fontsize=9)
        
        # 캐시 플랫폼 변화
        cash_changes = self.weekly_data['cash']['top_changes']
        platforms = [p['name'] for p in cash_changes]
        changes = [p['change'] for p in cash_changes]
        colors = ['#C62828' if c < 0 else '#2E7D32' for c in changes]
        
        bars4 = ax4.barh(platforms, changes, color=colors, alpha=0.8)
        ax4.set_title('Cash Players - Platform Changes', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Change (%)')
        ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        for bar, val in zip(bars4, changes):
            x_pos = bar.get_width() + 1 if val > 0 else bar.get_width() - 1
            ax4.text(x_pos, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', ha='left' if val > 0 else 'right', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('weekly_separated_chart.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'weekly_separated_chart.png'
    
    def create_monthly_chart(self):
        """월간 차트 - 온라인/캐시 별도"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 온라인 시장 변화
        categories = ['Jul 30', 'Aug 10']
        online_values = [self.monthly_data['online']['start'], self.monthly_data['online']['end']]
        
        bars1 = ax1.bar(categories, online_values, color=['#1976D2', '#0D47A1'], alpha=0.8)
        ax1.set_title(f'Online Market Overview\nChange: {self.monthly_data["online"]["change"]:.1f}%',
                     fontsize=12, fontweight='bold')
        ax1.set_ylabel('Total Players')
        
        # 값 표시
        for bar, val in zip(bars1, online_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
                    f'{val:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 리더 변화 표시
        leader_text = f"Leader: {self.monthly_data['online']['leader_start']['name']}\n" \
                     f"{self.monthly_data['online']['leader_start']['share']:.1f}% → " \
                     f"{self.monthly_data['online']['leader_end']['share']:.1f}%"
        ax1.text(0.5, 0.85, leader_text, transform=ax1.transAxes, ha='center',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # 캐시 시장 변화
        cash_values = [self.monthly_data['cash']['start'], self.monthly_data['cash']['end']]
        
        bars2 = ax2.bar(categories, cash_values, color=['#F57C00', '#E65100'], alpha=0.8)
        ax2.set_title(f'Cash Market Overview\nChange: {self.monthly_data["cash"]["change"]:.1f}%',
                     fontsize=12, fontweight='bold')
        ax2.set_ylabel('Total Players')
        
        # 값 표시
        for bar, val in zip(bars2, cash_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                    f'{val:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 리더 변화 표시
        leader_text = f"Leader: {self.monthly_data['cash']['leader_start']['name']}\n" \
                     f"{self.monthly_data['cash']['leader_start']['share']:.1f}% → " \
                     f"{self.monthly_data['cash']['leader_end']['share']:.1f}%"
        ax2.text(0.5, 0.85, leader_text, transform=ax2.transAxes, ha='center',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 온라인 Top Movers
        all_movers_online = []
        for g in self.monthly_data['online']['top_gainers'][:2]:
            all_movers_online.append((g['name'], g['change'], '#2E7D32'))
        for l in self.monthly_data['online']['top_losers'][:3]:
            all_movers_online.append((l['name'], l['change'], '#C62828'))
        
        names = [m[0] for m in all_movers_online]
        changes = [m[1] for m in all_movers_online]
        colors = [m[2] for m in all_movers_online]
        
        bars3 = ax3.barh(range(len(names)), changes, color=colors, alpha=0.8)
        ax3.set_title('Online - Top Movers', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Change (%)')
        ax3.set_yticks(range(len(names)))
        ax3.set_yticklabels(names)
        ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        for i, (bar, val) in enumerate(zip(bars3, changes)):
            x_pos = bar.get_width() + 2 if val > 0 else bar.get_width() - 2
            ax3.text(x_pos, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', ha='left' if val > 0 else 'right', fontsize=9)
        
        # 캐시 Top Movers
        all_movers_cash = []
        for g in self.monthly_data['cash']['top_gainers'][:3]:
            all_movers_cash.append((g['name'], g['change'], '#2E7D32'))
        for l in self.monthly_data['cash']['top_losers'][:2]:
            all_movers_cash.append((l['name'], l['change'], '#C62828'))
        
        names = [m[0] for m in all_movers_cash]
        changes = [m[1] for m in all_movers_cash]
        colors = [m[2] for m in all_movers_cash]
        
        bars4 = ax4.barh(range(len(names)), changes, color=colors, alpha=0.8)
        ax4.set_title('Cash - Top Movers', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Change (%)')
        ax4.set_yticks(range(len(names)))
        ax4.set_yticklabels(names)
        ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        for i, (bar, val) in enumerate(zip(bars4, changes)):
            x_pos = bar.get_width() + 5 if val > 0 else bar.get_width() - 5
            ax4.text(x_pos, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', ha='left' if val > 0 else 'right', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('monthly_separated_chart.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'monthly_separated_chart.png'
    
    def generate_daily_report(self):
        """일간 보고서 생성"""
        chart_path = self.create_daily_chart()
        
        report = {
            "type": "daily",
            "date": self.daily_data['date'],
            "chart": chart_path,
            "online": {
                "total": self.daily_data['online']['total'],
                "leader": f"{self.daily_data['online']['platforms'][0]['name']} ({self.daily_data['online']['platforms'][0]['share']}%)",
                "top_3": [(p['name'], p['value'], p['share']) for p in self.daily_data['online']['platforms'][:3]]
            },
            "cash": {
                "total": self.daily_data['cash']['total'],
                "leader": f"{self.daily_data['cash']['platforms'][0]['name']} ({self.daily_data['cash']['platforms'][0]['share']}%)",
                "top_3": [(p['name'], p['value'], p['share']) for p in self.daily_data['cash']['platforms'][:3]]
            }
        }
        
        return report
    
    def generate_weekly_report(self):
        """주간 보고서 생성"""
        chart_path = self.create_weekly_chart()
        
        report = {
            "type": "weekly",
            "period": self.weekly_data['period'],
            "chart": chart_path,
            "online": {
                "start": self.weekly_data['online']['start'],
                "end": self.weekly_data['online']['end'],
                "change": self.weekly_data['online']['change'],
                "biggest_drop": min(self.weekly_data['online']['top_changes'], key=lambda x: x['change'])
            },
            "cash": {
                "start": self.weekly_data['cash']['start'],
                "end": self.weekly_data['cash']['end'],
                "change": self.weekly_data['cash']['change'],
                "biggest_drop": min(self.weekly_data['cash']['top_changes'], key=lambda x: x['change'])
            }
        }
        
        return report
    
    def generate_monthly_report(self):
        """월간 보고서 생성"""
        chart_path = self.create_monthly_chart()
        
        report = {
            "type": "monthly",
            "period": self.monthly_data['period'],
            "chart": chart_path,
            "online": {
                "start": self.monthly_data['online']['start'],
                "end": self.monthly_data['online']['end'],
                "change": self.monthly_data['online']['change'],
                "leader_evolution": f"{self.monthly_data['online']['leader_start']['name']} "
                                  f"{self.monthly_data['online']['leader_start']['share']}% → "
                                  f"{self.monthly_data['online']['leader_end']['share']}%",
                "top_gainer": self.monthly_data['online']['top_gainers'][0] if self.monthly_data['online']['top_gainers'] else None,
                "top_loser": self.monthly_data['online']['top_losers'][0] if self.monthly_data['online']['top_losers'] else None
            },
            "cash": {
                "start": self.monthly_data['cash']['start'],
                "end": self.monthly_data['cash']['end'],
                "change": self.monthly_data['cash']['change'],
                "leader_evolution": f"{self.monthly_data['cash']['leader_start']['name']} "
                                  f"{self.monthly_data['cash']['leader_start']['share']}% → "
                                  f"{self.monthly_data['cash']['leader_end']['share']}%",
                "top_gainer": self.monthly_data['cash']['top_gainers'][0] if self.monthly_data['cash']['top_gainers'] else None,
                "top_loser": self.monthly_data['cash']['top_losers'][0] if self.monthly_data['cash']['top_losers'] else None
            }
        }
        
        return report

def main():
    """메인 실행"""
    reporter = SeparatedPlatformReporter()
    
    print("="*60)
    print("온라인/캐시 분리 분석 보고서 생성")
    print("="*60)
    
    # 일간 보고서
    print("\n[1/3] 일간 보고서 생성...")
    daily = reporter.generate_daily_report()
    print(f"[OK] 일간 보고서 ({daily['date']})")
    print(f"  [온라인] 총: {daily['online']['total']:,}명 | 리더: {daily['online']['leader']}")
    print(f"  [캐시] 총: {daily['cash']['total']:,}명 | 리더: {daily['cash']['leader']}")
    
    # 주간 보고서
    print("\n[2/3] 주간 보고서 생성...")
    weekly = reporter.generate_weekly_report()
    print(f"[OK] 주간 보고서 ({weekly['period']})")
    print(f"  [온라인] {weekly['online']['start']:,} → {weekly['online']['end']:,} ({weekly['online']['change']:.1f}%)")
    print(f"  [캐시] {weekly['cash']['start']:,} → {weekly['cash']['end']:,} ({weekly['cash']['change']:.1f}%)")
    
    # 월간 보고서
    print("\n[3/3] 월간 보고서 생성...")
    monthly = reporter.generate_monthly_report()
    print(f"[OK] 월간 보고서 ({monthly['period']})")
    print(f"  [온라인] {monthly['online']['start']:,} → {monthly['online']['end']:,} ({monthly['online']['change']:.1f}%)")
    print(f"  [캐시] {monthly['cash']['start']:,} → {monthly['cash']['end']:,} ({monthly['cash']['change']:.1f}%)")
    
    # 보고서 미리보기
    print("\n" + "="*60)
    print("보고서 미리보기")
    print("="*60)
    
    print("\n[일간 보고서 요약]")
    print(f"날짜: {daily['date']}")
    print("\n온라인 플레이어:")
    print(f"  - 총합: {daily['online']['total']:,}명")
    print(f"  - 시장 리더: {daily['online']['leader']}")
    print(f"  - TOP 3:")
    for name, value, share in daily['online']['top_3']:
        print(f"    {name}: {value:,}명 ({share}%)")
    
    print("\n캐시 플레이어:")
    print(f"  - 총합: {daily['cash']['total']:,}명")
    print(f"  - 시장 리더: {daily['cash']['leader']}")
    print(f"  - TOP 3:")
    for name, value, share in daily['cash']['top_3']:
        print(f"    {name}: {value:,}명 ({share}%)")
    
    print("\n[주간 보고서 요약]")
    print(f"기간: {weekly['period']}")
    print(f"\n온라인: {weekly['online']['start']:,} → {weekly['online']['end']:,} ({weekly['online']['change']:.1f}%)")
    print(f"  최대 하락: {weekly['online']['biggest_drop']['name']} ({weekly['online']['biggest_drop']['change']:.1f}%)")
    print(f"\n캐시: {weekly['cash']['start']:,} → {weekly['cash']['end']:,} ({weekly['cash']['change']:.1f}%)")
    print(f"  최대 하락: {weekly['cash']['biggest_drop']['name']} ({weekly['cash']['biggest_drop']['change']:.1f}%)")
    
    print("\n[월간 보고서 요약]")
    print(f"기간: {monthly['period']}")
    print(f"\n온라인 시장:")
    print(f"  - 변화: {monthly['online']['start']:,} → {monthly['online']['end']:,} ({monthly['online']['change']:.1f}%)")
    print(f"  - 리더 진화: {monthly['online']['leader_evolution']}")
    if monthly['online']['top_gainer']:
        print(f"  - 최대 성장: {monthly['online']['top_gainer']['name']} (+{monthly['online']['top_gainer']['change']:.1f}%)")
    if monthly['online']['top_loser']:
        print(f"  - 최대 하락: {monthly['online']['top_loser']['name']} ({monthly['online']['top_loser']['change']:.1f}%)")
    
    print(f"\n캐시 시장:")
    print(f"  - 변화: {monthly['cash']['start']:,} → {monthly['cash']['end']:,} ({monthly['cash']['change']:.1f}%)")
    print(f"  - 리더 진화: {monthly['cash']['leader_evolution']}")
    if monthly['cash']['top_gainer']:
        print(f"  - 최대 성장: {monthly['cash']['top_gainer']['name']} (+{monthly['cash']['top_gainer']['change']:.1f}%)")
    if monthly['cash']['top_loser']:
        print(f"  - 최대 하락: {monthly['cash']['top_loser']['name']} ({monthly['cash']['top_loser']['change']:.1f}%)")
    
    # 보고서 저장
    reports = {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('separated_reports.json', 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("생성 완료:")
    print("- daily_separated_chart.png")
    print("- weekly_separated_chart.png")
    print("- monthly_separated_chart.png")
    print("- separated_reports.json")
    print("="*60)

if __name__ == "__main__":
    main()