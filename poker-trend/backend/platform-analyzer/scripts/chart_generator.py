#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Generator for Poker Analysis
포커 분석용 차트 생성 모듈
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import base64
import io

# 차트 생성 라이브러리
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Rectangle, FancyBboxPatch
    import matplotlib.font_manager as fm
    import numpy as np
    import seaborn as sns
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False
    print("⚠️ matplotlib/seaborn이 설치되지 않았습니다.")
    print("설치: pip install matplotlib seaborn")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        if not CHART_AVAILABLE:
            logger.warning("차트 생성 라이브러리가 없습니다.")
            return
        
        # 스타일 설정
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 한글 폰트 설정 (Windows)
        try:
            plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
        except:
            plt.rcParams['font.family'] = ['DejaVu Sans']
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # 색상 팔레트
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'dark': '#343a40',
            'light': '#f8f9fa'
        }
        
        # 그라데이션 색상
        self.gradient_colors = [
            '#667eea', '#764ba2',  # 보라
            '#f093fb', '#f5576c',  # 핑크
            '#4facfe', '#00f2fe',  # 블루
            '#43e97b', '#38f9d7',  # 민트
            '#fa709a', '#fee140',  # 선셋
            '#30cfd0', '#330867'   # 오션
        ]
    
    def create_daily_comparison_chart(self, data: Dict) -> bytes:
        """일일 비교 차트 생성"""
        if not CHART_AVAILABLE:
            return None
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('일일 포커 시장 분석 대시보드', fontsize=16, fontweight='bold', y=1.02)
            
            changes = data['changes']
            
            # 1. 총 플레이어 변화 (막대 차트)
            ax1 = axes[0, 0]
            categories = ['전일', '오늘']
            values = [changes['total_players']['old'], changes['total_players']['new']]
            colors = ['#e0e0e0', self.colors['primary']]
            
            bars = ax1.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
            
            # 막대 위에 값 표시
            for i, (bar, val) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:,.0f}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # 변화율 표시
            change_pct = changes['total_players']['change_pct']
            arrow = '↑' if change_pct > 0 else '↓' if change_pct < 0 else '→'
            color = self.colors['success'] if change_pct > 0 else self.colors['danger'] if change_pct < 0 else self.colors['warning']
            
            ax1.text(0.5, 0.95, f'{arrow} {change_pct:+.1f}%',
                    transform=ax1.transAxes, fontsize=14, fontweight='bold',
                    color=color, ha='center', va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            ax1.set_title('총 플레이어 수', fontsize=12, fontweight='bold', pad=20)
            ax1.set_ylabel('플레이어 수', fontsize=10)
            ax1.grid(axis='y', alpha=0.3)
            
            # 2. 평균 플레이어 변화 (라인 차트)
            ax2 = axes[0, 1]
            
            x = [0, 1]
            y_avg = [changes['avg_players']['old'], changes['avg_players']['new']]
            y_cash = [changes['avg_cash_players']['old'], changes['avg_cash_players']['new']]
            
            ax2.plot(x, y_avg, 'o-', color=self.colors['primary'], linewidth=3,
                    markersize=10, label='평균 플레이어', markeredgewidth=2, markeredgecolor='white')
            ax2.plot(x, y_cash, 's-', color=self.colors['secondary'], linewidth=2,
                    markersize=8, label='캐시 플레이어', markeredgewidth=2, markeredgecolor='white')
            
            ax2.fill_between(x, y_avg, alpha=0.3, color=self.colors['primary'])
            ax2.fill_between(x, y_cash, alpha=0.3, color=self.colors['secondary'])
            
            ax2.set_xticks(x)
            ax2.set_xticklabels(['전일', '오늘'])
            ax2.set_title('평균 플레이어 추이', fontsize=12, fontweight='bold')
            ax2.set_ylabel('플레이어 수', fontsize=10)
            ax2.legend(loc='best', framealpha=0.9)
            ax2.grid(True, alpha=0.3)
            
            # 3. 시장 집중도 (도넛 차트)
            ax3 = axes[1, 0]
            
            concentration = changes['market_concentration']['new']
            sizes = [concentration, 100 - concentration]
            colors = [self.colors['primary'], '#e0e0e0']
            
            wedges, texts, autotexts = ax3.pie(sizes, colors=colors, autopct='',
                                                startangle=90, counterclock=False,
                                                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
            
            # 중앙에 텍스트
            ax3.text(0, 0, f'{concentration:.1f}%',
                    ha='center', va='center', fontsize=20, fontweight='bold',
                    color=self.colors['primary'])
            ax3.text(0, -0.15, '상위 3개 사이트',
                    ha='center', va='center', fontsize=10, color='gray')
            
            # 변화 표시
            conc_change = changes['market_concentration']['change']
            change_text = f'{conc_change:+.1f}%p'
            change_color = self.colors['danger'] if abs(conc_change) > 5 else self.colors['warning'] if abs(conc_change) > 2 else self.colors['success']
            
            ax3.text(0.5, 1.1, change_text,
                    transform=ax3.transAxes, fontsize=12, fontweight='bold',
                    color=change_color, ha='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            ax3.set_title('시장 집중도', fontsize=12, fontweight='bold', pad=20)
            
            # 4. 상위 변동 사이트 (수평 막대)
            ax4 = axes[1, 1]
            
            site_comparison = data.get('site_comparison', {})
            top_gainers = site_comparison.get('top_gainers', [])[:3]
            top_losers = site_comparison.get('top_losers', [])[-3:] if site_comparison.get('top_losers') else []
            
            all_sites = []
            all_changes = []
            all_colors = []
            
            for site in top_gainers:
                all_sites.append(site['site_name'][:15])  # 이름 길이 제한
                all_changes.append(site['change_pct'])
                all_colors.append(self.colors['success'])
            
            for site in reversed(top_losers):
                all_sites.append(site['site_name'][:15])
                all_changes.append(site['change_pct'])
                all_colors.append(self.colors['danger'])
            
            if all_sites:
                y_pos = np.arange(len(all_sites))
                bars = ax4.barh(y_pos, all_changes, color=all_colors, edgecolor='white', linewidth=2)
                
                # 값 표시
                for i, (bar, val) in enumerate(zip(bars, all_changes)):
                    x_pos = bar.get_width()
                    ha = 'left' if val > 0 else 'right'
                    offset = 1 if val > 0 else -1
                    ax4.text(x_pos + offset, bar.get_y() + bar.get_height()/2,
                            f'{val:+.1f}%',
                            ha=ha, va='center', fontsize=10, fontweight='bold')
                
                ax4.set_yticks(y_pos)
                ax4.set_yticklabels(all_sites, fontsize=10)
                ax4.axvline(x=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
                ax4.set_xlabel('변화율 (%)', fontsize=10)
                ax4.set_title('상위 변동 사이트', fontsize=12, fontweight='bold')
                ax4.grid(axis='x', alpha=0.3)
            else:
                ax4.text(0.5, 0.5, '데이터 없음',
                        transform=ax4.transAxes, ha='center', va='center',
                        fontsize=14, color='gray')
                ax4.set_title('상위 변동 사이트', fontsize=12, fontweight='bold')
            
            # 레이아웃 조정
            plt.tight_layout()
            
            # 이미지를 바이트로 변환
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            image_bytes = buf.read()
            plt.close()
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"일일 차트 생성 실패: {e}")
            return None
    
    def create_weekly_trend_chart(self, data: Dict) -> bytes:
        """주간 트렌드 차트 생성"""
        if not CHART_AVAILABLE:
            return None
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('주간 포커 시장 트렌드 분석', fontsize=16, fontweight='bold', y=1.02)
            
            changes = data['changes']
            
            # 1. 주간 성장 지표 (게이지 차트 스타일)
            ax1 = axes[0, 0]
            
            # 반원형 게이지 생성
            growth_rate = changes['total_players']['change_pct']
            self._create_gauge_chart(ax1, growth_rate, '주간 성장률', -20, 20)
            
            # 2. 일별 평균 비교 (그룹 막대)
            ax2 = axes[0, 1]
            
            categories = ['총 플레이어', '캐시 플레이어']
            last_week = [changes['avg_players']['old'], changes['avg_cash_players']['old']]
            this_week = [changes['avg_players']['new'], changes['avg_cash_players']['new']]
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax2.bar(x - width/2, last_week, width, label='지난주',
                           color='#b0b0b0', edgecolor='white', linewidth=2)
            bars2 = ax2.bar(x + width/2, this_week, width, label='이번주',
                           color=self.colors['primary'], edgecolor='white', linewidth=2)
            
            ax2.set_xlabel('카테고리', fontsize=10)
            ax2.set_ylabel('일평균 플레이어', fontsize=10)
            ax2.set_title('주간 일평균 비교', fontsize=12, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categories)
            ax2.legend(framealpha=0.9)
            ax2.grid(axis='y', alpha=0.3)
            
            # 막대 위 값 표시
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f}',
                            ha='center', va='bottom', fontsize=9)
            
            # 3. 변동성 히트맵
            ax3 = axes[1, 0]
            
            # 더미 데이터로 변동성 매트릭스 생성
            volatility_data = np.random.randn(7, 4) * 10 + np.array([5, 3, -2, 1])
            
            im = ax3.imshow(volatility_data, cmap='RdYlGn', aspect='auto', vmin=-20, vmax=20)
            
            ax3.set_xticks(np.arange(4))
            ax3.set_yticks(np.arange(7))
            ax3.set_xticklabels(['1주차', '2주차', '3주차', '4주차'])
            ax3.set_yticklabels(['월', '화', '수', '목', '금', '토', '일'])
            ax3.set_title('주간 변동성 패턴', fontsize=12, fontweight='bold')
            
            # 컬러바 추가
            cbar = plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
            cbar.set_label('변화율 (%)', rotation=270, labelpad=15)
            
            # 4. Top 5 성과 (폭포 차트 스타일)
            ax4 = axes[1, 1]
            
            site_comparison = data.get('site_comparison', {})
            top_sites = site_comparison.get('top_gainers', [])[:5]
            
            if top_sites:
                sites = [s['site_name'][:12] for s in top_sites]
                changes_pct = [s['change_pct'] for s in top_sites]
                
                colors = []
                for c in changes_pct:
                    if c > 10:
                        colors.append(self.colors['success'])
                    elif c > 0:
                        colors.append(self.colors['info'])
                    else:
                        colors.append(self.colors['danger'])
                
                y_pos = np.arange(len(sites))
                bars = ax4.barh(y_pos, changes_pct, color=colors, edgecolor='white', linewidth=2)
                
                ax4.set_yticks(y_pos)
                ax4.set_yticklabels(sites, fontsize=10)
                ax4.set_xlabel('성장률 (%)', fontsize=10)
                ax4.set_title('Top 5 성과', fontsize=12, fontweight='bold')
                ax4.grid(axis='x', alpha=0.3)
                
                # 값 표시
                for bar, val in zip(bars, changes_pct):
                    width = bar.get_width()
                    ax4.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                            f'+{val:.1f}%',
                            ha='left', va='center', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            image_bytes = buf.read()
            plt.close()
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"주간 차트 생성 실패: {e}")
            return None
    
    def create_monthly_dashboard(self, data: Dict) -> bytes:
        """월간 대시보드 차트 생성"""
        if not CHART_AVAILABLE:
            return None
        
        try:
            # 더 큰 대시보드 스타일
            fig = plt.figure(figsize=(16, 12))
            
            # 그리드 레이아웃
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # 타이틀
            fig.suptitle('월간 포커 시장 종합 대시보드', fontsize=18, fontweight='bold', y=0.98)
            
            changes = data['changes']
            trends = data.get('trends', {})
            
            # 1. KPI 카드들 (상단)
            ax1 = fig.add_subplot(gs[0, :])
            ax1.axis('off')
            
            kpis = [
                ('총 성장률', f"{changes['total_players']['change_pct']:+.1f}%", self._get_kpi_color(changes['total_players']['change_pct'])),
                ('일평균', f"{changes['avg_players']['change_pct']:+.1f}%", self._get_kpi_color(changes['avg_players']['change_pct'])),
                ('캐시게임', f"{changes['avg_cash_players']['change_pct']:+.1f}%", self._get_kpi_color(changes['avg_cash_players']['change_pct'])),
                ('시장집중도', f"{changes['market_concentration']['change']:+.1f}%p", 'orange')
            ]
            
            for i, (label, value, color) in enumerate(kpis):
                x = 0.125 + i * 0.25
                
                # KPI 박스
                rect = FancyBboxPatch(
                    (x - 0.08, 0.3), 0.16, 0.5,
                    boxstyle="round,pad=0.01",
                    facecolor=color, alpha=0.15,
                    edgecolor=color, linewidth=2
                )
                ax1.add_patch(rect)
                
                # 값
                ax1.text(x, 0.65, value, ha='center', va='center',
                        fontsize=20, fontweight='bold', color=color)
                
                # 라벨
                ax1.text(x, 0.35, label, ha='center', va='center',
                        fontsize=11, color='gray')
            
            # 2. 월간 트렌드 라인 차트
            ax2 = fig.add_subplot(gs[1, :2])
            
            # 시뮬레이션 데이터 (실제로는 데이터에서 가져와야 함)
            days = np.arange(1, 31)
            last_month = 150000 + np.random.randn(30) * 5000 + np.linspace(0, 5000, 30)
            this_month = 160000 + np.random.randn(30) * 5000 + np.linspace(0, 8000, 30)
            
            ax2.fill_between(days, last_month, alpha=0.3, color='gray', label='지난달')
            ax2.fill_between(days, this_month, alpha=0.3, color=self.colors['primary'], label='이번달')
            
            ax2.plot(days, last_month, '-', color='gray', linewidth=2)
            ax2.plot(days, this_month, '-', color=self.colors['primary'], linewidth=3)
            
            ax2.set_xlabel('일자', fontsize=11)
            ax2.set_ylabel('플레이어 수', fontsize=11)
            ax2.set_title('월간 플레이어 추이', fontsize=13, fontweight='bold')
            ax2.legend(loc='upper left', framealpha=0.9)
            ax2.grid(True, alpha=0.3)
            
            # 3. 시장 점유율 파이
            ax3 = fig.add_subplot(gs[1, 2])
            
            # Top 5 사이트 점유율 (시뮬레이션)
            sizes = [30, 25, 20, 15, 10]
            labels = ['PokerStars', 'GGPoker', '888poker', 'PartyPoker', '기타']
            colors = sns.color_palette('husl', len(sizes))
            
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors,
                                                autopct='%1.1f%%', startangle=90,
                                                wedgeprops=dict(edgecolor='white', linewidth=2))
            
            ax3.set_title('시장 점유율 분포', fontsize=13, fontweight='bold')
            
            # 4. 성과 매트릭스
            ax4 = fig.add_subplot(gs[2, :])
            
            site_comparison = data.get('site_comparison', {})
            top_gainers = site_comparison.get('top_gainers', [])[:10]
            
            if top_gainers:
                sites = [s['site_name'][:15] for s in top_gainers]
                old_avg = [s['old_avg'] for s in top_gainers]
                new_avg = [s['new_avg'] for s in top_gainers]
                changes_data = [s['change_pct'] for s in top_gainers]
                
                x = np.arange(len(sites))
                width = 0.35
                
                bars1 = ax4.bar(x - width/2, old_avg, width, label='지난달 평균',
                               color='#b0b0b0', edgecolor='white', linewidth=1)
                bars2 = ax4.bar(x + width/2, new_avg, width, label='이번달 평균',
                               color=self.colors['primary'], edgecolor='white', linewidth=1)
                
                # 변화율 표시
                for i, (x_pos, change) in enumerate(zip(x, changes_data)):
                    color = self.colors['success'] if change > 0 else self.colors['danger']
                    ax4.text(x_pos, max(old_avg[i], new_avg[i]) + 500,
                            f'{change:+.1f}%',
                            ha='center', va='bottom', fontsize=9,
                            color=color, fontweight='bold')
                
                ax4.set_xlabel('사이트', fontsize=11)
                ax4.set_ylabel('평균 플레이어', fontsize=11)
                ax4.set_title('Top 10 사이트 월간 성과', fontsize=13, fontweight='bold')
                ax4.set_xticks(x)
                ax4.set_xticklabels(sites, rotation=45, ha='right')
                ax4.legend(loc='upper left', framealpha=0.9)
                ax4.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            image_bytes = buf.read()
            plt.close()
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"월간 대시보드 생성 실패: {e}")
            return None
    
    def _create_gauge_chart(self, ax, value, title, min_val, max_val):
        """게이지 차트 생성 헬퍼"""
        # 반원 그리기
        theta = np.linspace(np.pi, 0, 100)
        radius = 1
        
        # 배경 반원
        ax.fill_between(np.cos(theta), np.sin(theta), color='#e0e0e0', alpha=0.3)
        
        # 값에 따른 각도 계산
        angle = np.pi - (value - min_val) / (max_val - min_val) * np.pi
        
        # 포인터
        ax.plot([0, np.cos(angle)], [0, np.sin(angle)], 'k-', linewidth=3)
        ax.scatter([0], [0], s=100, c='black', zorder=5)
        
        # 색상 구간
        if value > 10:
            color = self.colors['success']
        elif value > 0:
            color = self.colors['info']
        elif value > -10:
            color = self.colors['warning']
        else:
            color = self.colors['danger']
        
        # 값 표시
        ax.text(0, -0.3, f'{value:+.1f}%',
               ha='center', va='center', fontsize=16,
               fontweight='bold', color=color)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.5, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
    
    def _get_kpi_color(self, value):
        """KPI 값에 따른 색상 반환"""
        if value > 10:
            return 'green'
        elif value > 5:
            return 'lightgreen'
        elif value > 0:
            return 'blue'
        elif value > -5:
            return 'orange'
        else:
            return 'red'
    
    def save_chart_to_file(self, image_bytes: bytes, filename: str = None) -> str:
        """차트를 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chart_{timestamp}.png"
        
        with open(filename, 'wb', encoding='utf-8') as f:
            f.write(image_bytes)
        
        logger.info(f"차트 저장 완료: {filename}")
        return filename

def main():
    print("📊 포커 분석 차트 생성기")
    print("=" * 60)
    
    if not CHART_AVAILABLE:
        print("❌ matplotlib이 설치되지 않았습니다.")
        print("설치: pip install matplotlib seaborn")
        return
    
    generator = ChartGenerator()
    
    # 테스트 데이터
    test_data = {
        'changes': {
            'total_players': {'old': 150000, 'new': 160000, 'change': 10000, 'change_pct': 6.7},
            'avg_players': {'old': 3200, 'new': 3400, 'change': 200, 'change_pct': 6.3},
            'avg_cash_players': {'old': 1500, 'new': 1600, 'change': 100, 'change_pct': 6.7},
            'market_concentration': {'old': 45.2, 'new': 47.8, 'change': 2.6, 'change_pct': 5.8}
        },
        'site_comparison': {
            'top_gainers': [
                {'site_name': 'PokerStars', 'change_pct': 15.2, 'old_avg': 50000, 'new_avg': 57600},
                {'site_name': 'GGPoker', 'change_pct': 12.5, 'old_avg': 40000, 'new_avg': 45000},
                {'site_name': '888poker', 'change_pct': 8.3, 'old_avg': 20000, 'new_avg': 21660}
            ],
            'top_losers': [
                {'site_name': 'PartyPoker', 'change_pct': -5.2, 'old_avg': 15000, 'new_avg': 14220}
            ]
        }
    }
    
    print("\n차트 유형 선택:")
    print("1. 일일 비교 차트")
    print("2. 주간 트렌드 차트")
    print("3. 월간 대시보드")
    print("4. 모든 차트 생성")
    
    choice = input("\n선택 (1-4): ").strip()
    
    try:
        if choice == '1':
            print("\n📊 일일 비교 차트 생성 중...")
            image_bytes = generator.create_daily_comparison_chart(test_data)
            if image_bytes:
                filename = generator.save_chart_to_file(image_bytes, 'daily_chart.png')
                print(f"✅ 차트 생성 완료: {filename}")
            
        elif choice == '2':
            print("\n📊 주간 트렌드 차트 생성 중...")
            image_bytes = generator.create_weekly_trend_chart(test_data)
            if image_bytes:
                filename = generator.save_chart_to_file(image_bytes, 'weekly_chart.png')
                print(f"✅ 차트 생성 완료: {filename}")
            
        elif choice == '3':
            print("\n📊 월간 대시보드 생성 중...")
            image_bytes = generator.create_monthly_dashboard(test_data)
            if image_bytes:
                filename = generator.save_chart_to_file(image_bytes, 'monthly_dashboard.png')
                print(f"✅ 차트 생성 완료: {filename}")
            
        elif choice == '4':
            print("\n📊 모든 차트 생성 중...")
            
            charts = [
                ('daily_chart.png', generator.create_daily_comparison_chart(test_data)),
                ('weekly_chart.png', generator.create_weekly_trend_chart(test_data)),
                ('monthly_dashboard.png', generator.create_monthly_dashboard(test_data))
            ]
            
            for filename, image_bytes in charts:
                if image_bytes:
                    saved = generator.save_chart_to_file(image_bytes, filename)
                    print(f"✅ {saved} 생성 완료")
            
        else:
            print("❌ 잘못된 선택입니다.")
            
    except Exception as e:
        print(f"❌ 차트 생성 실패: {e}")

if __name__ == "__main__":
    main()