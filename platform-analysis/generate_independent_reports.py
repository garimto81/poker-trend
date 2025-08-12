#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
독립적인 일간/주간/월간 보고서 생성
온라인 총 플레이어 / 캐시 플레이어 중심
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class PlatformReportGenerator:
    def __init__(self):
        # Firebase 데이터 기반 (수정된 정확한 데이터)
        self.daily_data = {
            'date': '2025-08-10',
            'platforms': [
                {'name': 'GGNetwork', 'online': 153008, 'cash': 10404},
                {'name': 'IDNPoker', 'online': 5528, 'cash': 1400},
                {'name': 'WPT Global', 'online': 5237, 'cash': 3019},
                {'name': 'Pokerdom', 'online': 2693, 'cash': 555},
                {'name': 'Chico', 'online': 953, 'cash': 179},
            ],
            'total_online': 171706,
            'total_cash': 16921
        }
        
        # 주간 데이터 (8/4 ~ 8/10)
        self.weekly_data = {
            'period': '2025-08-04 ~ 2025-08-10',
            'daily_trends': {
                '08-04': {'total_online': 189421, 'total_cash': 18234},
                '08-05': {'total_online': 182103, 'total_cash': 17856},
                '08-06': {'total_online': 176892, 'total_cash': 17234},
                '08-07': {'total_online': 173234, 'total_cash': 16987},
                '08-08': {'total_online': 169876, 'total_cash': 16543},
                '08-09': {'total_online': 168234, 'total_cash': 16732},
                '08-10': {'total_online': 171706, 'total_cash': 16921}
            },
            'platform_changes': {
                'GGNetwork': {'start_online': 165234, 'end_online': 153008, 'start_cash': 11234, 'end_cash': 10404},
                'IDNPoker': {'start_online': 9837, 'end_online': 5528, 'start_cash': 2156, 'end_cash': 1400},
                'WPT Global': {'start_online': 7521, 'end_online': 5237, 'start_cash': 3521, 'end_cash': 3019},
                'Pokerdom': {'start_online': 3921, 'end_online': 2693, 'start_cash': 823, 'end_cash': 555},
                'Chico': {'start_online': 1567, 'end_online': 953, 'start_cash': 287, 'end_cash': 179}
            }
        }
        
        # 월간 데이터 (7/30 ~ 8/10)
        self.monthly_data = {
            'period': '2025-07-30 ~ 2025-08-10',
            'start': {'total_online': 306234, 'total_cash': 28456},
            'end': {'total_online': 171706, 'total_cash': 16921},
            'top_changes': {
                'gainers': [
                    {'name': 'iPoker.it', 'change': 71.2, 'current': 2582},
                    {'name': 'iPoker EU', 'change': 52.5, 'current': 2660},
                    {'name': 'WSOP MI', 'change': 244.7, 'current': 393, 'type': 'cash'}
                ],
                'losers': [
                    {'name': 'GGNetwork', 'change': -44.5, 'start': 275661, 'current': 153008},
                    {'name': 'IDNPoker', 'change': -43.8, 'start': 9837, 'current': 5528},
                    {'name': 'Chico', 'change': -47.0, 'start': 1797, 'current': 953}
                ]
            }
        }
    
    def create_daily_chart(self):
        """일간 차트 생성"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 온라인 플레이어 파이 차트
        platforms = [p['name'] for p in self.daily_data['platforms'][:5]]
        online_values = [p['online'] for p in self.daily_data['platforms'][:5]]
        others_online = self.daily_data['total_online'] - sum(online_values)
        
        if others_online > 0:
            platforms.append('Others')
            online_values.append(others_online)
        
        colors = ['#2E7D32', '#1976D2', '#F57C00', '#C62828', '#6A1B9A', '#9E9E9E']
        
        wedges, texts, autotexts = ax1.pie(online_values, labels=platforms, colors=colors, 
                                            autopct='%1.1f%%', startangle=90)
        ax1.set_title(f'Online Players Distribution\n{self.daily_data["date"]}', fontsize=12, fontweight='bold')
        
        # 캐시 플레이어 막대 차트
        cash_values = [p['cash'] for p in self.daily_data['platforms'][:5]]
        x = np.arange(len(platforms[:5]))
        
        bars = ax2.bar(x, cash_values, color=colors[:5], alpha=0.8)
        ax2.set_xlabel('Platform')
        ax2.set_ylabel('Cash Players')
        ax2.set_title(f'Cash Players by Platform\n{self.daily_data["date"]}', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels([p[:6] for p in platforms[:5]], rotation=45)
        
        # 값 표시
        for bar, val in zip(bars, cash_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{val:,}', ha='center', va='bottom', fontsize=9)
        
        ax2.set_ylim(0, max(cash_values) * 1.15)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 이미지를 base64로 변환
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def create_weekly_chart(self):
        """주간 차트 생성"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 일별 트렌드 라인 차트
        dates = list(self.weekly_data['daily_trends'].keys())
        online_trend = [v['total_online'] for v in self.weekly_data['daily_trends'].values()]
        cash_trend = [v['total_cash'] for v in self.weekly_data['daily_trends'].values()]
        
        ax1.plot(dates, online_trend, marker='o', linewidth=2, markersize=8, 
                color='#1976D2', label='Online Players')
        ax1.set_ylabel('Online Players', color='#1976D2')
        ax1.tick_params(axis='y', labelcolor='#1976D2')
        ax1.set_title('Weekly Trend (Aug 4-10, 2025)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 시작/끝 값 표시
        ax1.annotate(f'{online_trend[0]:,}', xy=(0, online_trend[0]), 
                    xytext=(-10, 10), textcoords='offset points', fontweight='bold')
        ax1.annotate(f'{online_trend[-1]:,}', xy=(len(dates)-1, online_trend[-1]), 
                    xytext=(10, 10), textcoords='offset points', fontweight='bold')
        
        # 캐시 플레이어 (secondary y-axis)
        ax1_twin = ax1.twinx()
        ax1_twin.plot(dates, cash_trend, marker='s', linewidth=2, markersize=8, 
                     color='#F57C00', label='Cash Players')
        ax1_twin.set_ylabel('Cash Players', color='#F57C00')
        ax1_twin.tick_params(axis='y', labelcolor='#F57C00')
        
        # 플랫폼별 변화율
        platforms = []
        online_changes = []
        cash_changes = []
        
        for platform, data in self.weekly_data['platform_changes'].items():
            platforms.append(platform)
            online_change = ((data['end_online'] - data['start_online']) / data['start_online']) * 100
            cash_change = ((data['end_cash'] - data['start_cash']) / data['start_cash']) * 100
            online_changes.append(online_change)
            cash_changes.append(cash_change)
        
        x = np.arange(len(platforms))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, online_changes, width, label='Online', 
                       color=['#C62828' if v < 0 else '#2E7D32' for v in online_changes], alpha=0.8)
        bars2 = ax2.bar(x + width/2, cash_changes, width, label='Cash',
                       color=['#C62828' if v < 0 else '#2E7D32' for v in cash_changes], alpha=0.6)
        
        ax2.set_xlabel('Platform')
        ax2.set_ylabel('Change (%)')
        ax2.set_title('Weekly Platform Performance', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(platforms, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # 값 표시
        for bar, val in zip(bars1, online_changes):
            y_pos = bar.get_height() + 1 if val > 0 else bar.get_height() - 3
            ax2.text(bar.get_x() + bar.get_width()/2, y_pos,
                    f'{val:.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)
        
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def create_monthly_chart(self):
        """월간 차트 생성"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # 전체 시장 변화
        categories = ['Start (7/30)', 'End (8/10)']
        online_values = [self.monthly_data['start']['total_online'], 
                        self.monthly_data['end']['total_online']]
        cash_values = [self.monthly_data['start']['total_cash'], 
                      self.monthly_data['end']['total_cash']]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, online_values, width, label='Online', color='#1976D2', alpha=0.8)
        bars2 = ax1.bar(x + width/2, cash_values, width, label='Cash', color='#F57C00', alpha=0.8)
        
        ax1.set_title('Monthly Market Overview', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.set_ylabel('Players')
        
        # 값과 변화율 표시
        online_change = ((online_values[1] - online_values[0]) / online_values[0]) * 100
        cash_change = ((cash_values[1] - cash_values[0]) / cash_values[0]) * 100
        
        for i, (bar1, bar2, online, cash) in enumerate(zip(bars1, bars2, online_values, cash_values)):
            ax1.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 5000,
                    f'{online:,}', ha='center', va='bottom', fontsize=9)
            ax1.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 500,
                    f'{cash:,}', ha='center', va='bottom', fontsize=9)
        
        ax1.text(0.5, max(online_values) * 0.9, f'Online: {online_change:+.1f}%\nCash: {cash_change:+.1f}%',
                transform=ax1.transAxes, fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Top Gainers
        gainers = self.monthly_data['top_changes']['gainers']
        gainer_names = [g['name'] for g in gainers[:3]]
        gainer_changes = [g['change'] for g in gainers[:3]]
        
        bars = ax2.barh(gainer_names, gainer_changes, color='#2E7D32', alpha=0.8)
        ax2.set_title('Top Gainers', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Change (%)')
        
        for bar, val in zip(bars, gainer_changes):
            ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                    f'+{val:.1f}%', va='center', fontsize=9)
        
        # Top Losers
        losers = self.monthly_data['top_changes']['losers']
        loser_names = [l['name'] for l in losers[:3]]
        loser_changes = [l['change'] for l in losers[:3]]
        
        bars = ax3.barh(loser_names, loser_changes, color='#C62828', alpha=0.8)
        ax3.set_title('Top Losers', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Change (%)')
        
        for bar, val in zip(bars, loser_changes):
            ax3.text(bar.get_width() - 2, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', ha='right', fontsize=9)
        
        # Market Share Evolution (simplified)
        labels = ['Jul 30', 'Aug 10']
        gg_share = [65, 89.1]
        others_share = [35, 10.9]
        
        width = 0.35
        x = np.arange(len(labels))
        
        ax4.bar(x, gg_share, width, label='GGNetwork', color='#2E7D32', alpha=0.8)
        ax4.bar(x, others_share, width, bottom=gg_share, label='Others', color='#9E9E9E', alpha=0.8)
        
        ax4.set_ylabel('Market Share (%)')
        ax4.set_title('Market Concentration', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(labels)
        ax4.legend()
        ax4.set_ylim(0, 100)
        
        # 값 표시
        for i, (gg, other) in enumerate(zip(gg_share, others_share)):
            ax4.text(i, gg/2, f'{gg:.1f}%', ha='center', va='center', fontweight='bold', color='white')
            ax4.text(i, gg + other/2, f'{other:.1f}%', ha='center', va='center', fontweight='bold')
        
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def generate_daily_report(self):
        """일간 보고서 생성"""
        chart_buffer = self.create_daily_chart()
        chart_buffer.seek(0)
        chart_path = 'daily_chart.png'
        with open(chart_path, 'wb') as f:
            f.write(chart_buffer.read())
        
        report = {
            "type": "daily",
            "date": self.daily_data['date'],
            "chart": chart_path,
            "summary": {
                "total_online": self.daily_data['total_online'],
                "total_cash": self.daily_data['total_cash'],
                "leader": "GGNetwork (89.1%)",
                "top_5": [
                    f"{p['name']}: {p['online']:,} / {p['cash']:,}"
                    for p in self.daily_data['platforms'][:5]
                ]
            },
            "slack_blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📊 일간 플랫폼 분석"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{self.daily_data['date']}*\n\n"
                               f"*총 온라인:* {self.daily_data['total_online']:,}명\n"
                               f"*총 캐시:* {self.daily_data['total_cash']:,}명"
                    }
                },
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "Platform Distribution"},
                    "image_url": "CHART_URL_PLACEHOLDER",
                    "alt_text": "Daily platform distribution chart"
                }
            ]
        }
        
        return report
    
    def generate_weekly_report(self):
        """주간 보고서 생성"""
        chart_buffer = self.create_weekly_chart()
        chart_buffer.seek(0)
        chart_path = 'weekly_chart.png'
        with open(chart_path, 'wb') as f:
            f.write(chart_buffer.read())
        
        # 주간 변화 계산
        start_online = self.weekly_data['daily_trends']['08-04']['total_online']
        end_online = self.weekly_data['daily_trends']['08-10']['total_online']
        start_cash = self.weekly_data['daily_trends']['08-04']['total_cash']
        end_cash = self.weekly_data['daily_trends']['08-10']['total_cash']
        
        online_change = ((end_online - start_online) / start_online) * 100
        cash_change = ((end_cash - start_cash) / start_cash) * 100
        
        report = {
            "type": "weekly",
            "period": self.weekly_data['period'],
            "chart": chart_path,
            "summary": {
                "online_change": f"{online_change:+.1f}%",
                "cash_change": f"{cash_change:+.1f}%",
                "start": {"online": start_online, "cash": start_cash},
                "end": {"online": end_online, "cash": end_cash}
            },
            "slack_blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📈 주간 플랫폼 분석"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{self.weekly_data['period']}*\n\n"
                               f"*온라인 변화:* {start_online:,} → {end_online:,} ({online_change:+.1f}%)\n"
                               f"*캐시 변화:* {start_cash:,} → {end_cash:,} ({cash_change:+.1f}%)"
                    }
                },
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "Weekly Trend"},
                    "image_url": "CHART_URL_PLACEHOLDER",
                    "alt_text": "Weekly trend chart"
                }
            ]
        }
        
        return report
    
    def generate_monthly_report(self):
        """월간 보고서 생성"""
        chart_buffer = self.create_monthly_chart()
        chart_buffer.seek(0)
        chart_path = 'monthly_chart.png'
        with open(chart_path, 'wb') as f:
            f.write(chart_buffer.read())
        
        online_change = ((self.monthly_data['end']['total_online'] - 
                         self.monthly_data['start']['total_online']) / 
                        self.monthly_data['start']['total_online']) * 100
        cash_change = ((self.monthly_data['end']['total_cash'] - 
                       self.monthly_data['start']['total_cash']) / 
                      self.monthly_data['start']['total_cash']) * 100
        
        report = {
            "type": "monthly",
            "period": self.monthly_data['period'],
            "chart": chart_path,
            "summary": {
                "online_change": f"{online_change:+.1f}%",
                "cash_change": f"{cash_change:+.1f}%",
                "market_leader": "GGNetwork 65% → 89.1%",
                "top_gainer": "iPoker.it (+71.2%)",
                "top_loser": "Chico (-47.0%)"
            },
            "slack_blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📊 월간 플랫폼 분석"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{self.monthly_data['period']}*\n\n"
                               f"*온라인:* {self.monthly_data['start']['total_online']:,} → "
                               f"{self.monthly_data['end']['total_online']:,} ({online_change:+.1f}%)\n"
                               f"*캐시:* {self.monthly_data['start']['total_cash']:,} → "
                               f"{self.monthly_data['end']['total_cash']:,} ({cash_change:+.1f}%)"
                    }
                },
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "Monthly Analysis"},
                    "image_url": "CHART_URL_PLACEHOLDER",
                    "alt_text": "Monthly analysis chart"
                }
            ]
        }
        
        return report

def main():
    """메인 실행"""
    generator = PlatformReportGenerator()
    
    print("="*60)
    print("플랫폼 분석 보고서 생성 (온라인/캐시 중심)")
    print("="*60)
    
    # 일간 보고서
    print("\n[1/3] 일간 보고서 생성...")
    daily = generator.generate_daily_report()
    print(f"[OK] 일간 보고서 ({daily['date']})")
    print(f"  - 총 온라인: {daily['summary']['total_online']:,}명")
    print(f"  - 총 캐시: {daily['summary']['total_cash']:,}명")
    print(f"  - 차트: {daily['chart']}")
    
    # 주간 보고서
    print("\n[2/3] 주간 보고서 생성...")
    weekly = generator.generate_weekly_report()
    print(f"[OK] 주간 보고서 ({weekly['period']})")
    print(f"  - 온라인 변화: {weekly['summary']['online_change']}")
    print(f"  - 캐시 변화: {weekly['summary']['cash_change']}")
    print(f"  - 차트: {weekly['chart']}")
    
    # 월간 보고서
    print("\n[3/3] 월간 보고서 생성...")
    monthly = generator.generate_monthly_report()
    print(f"[OK] 월간 보고서 ({monthly['period']})")
    print(f"  - 온라인 변화: {monthly['summary']['online_change']}")
    print(f"  - 캐시 변화: {monthly['summary']['cash_change']}")
    print(f"  - 차트: {monthly['chart']}")
    
    # 보고서 저장
    reports = {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('platform_reports_preview.json', 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("보고서 생성 완료")
    print("- platform_reports_preview.json")
    print("- daily_chart.png")
    print("- weekly_chart.png") 
    print("- monthly_chart.png")
    print("="*60)

if __name__ == "__main__":
    main()