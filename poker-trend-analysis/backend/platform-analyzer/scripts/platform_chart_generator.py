#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인 포커 플랫폼 데이터 시각화 및 차트 생성
정량 데이터 분석과 시각적 차트를 통한 트렌드 파악

기능:
- ASCII 차트 생성 (콘솔 출력용)
- 누적 영역 그래프 생성
- HTML 리포트 생성
- 차트 이미지 파일 생성
- Slack 이미지 업로드
"""

import os
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from io import BytesIO
import requests

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class PlatformChartGenerator:
    """플랫폼 데이터 차트 생성기"""
    
    def __init__(self):
        """초기화"""
        # 색상 팔레트 정의 (각 플랫폼별 고유 색상)
        self.color_palette = {
            'GGNetwork': '#FF6B6B',      # 빨강
            'PokerStars': '#4ECDC4',     # 청록
            '888poker': '#45B7D1',        # 하늘
            'partypoker': '#96CEB4',     # 민트
            'Natural8': '#FECA57',        # 노랑
            'PPPoker': '#DDA0DD',         # 보라
            'PokerBros': '#98D8C8',      # 청록
            'Americas Cardroom': '#FFB6C1', # 분홍
            'Ignition': '#FFA07A',        # 연어
            'BetOnline': '#87CEEB',      # 하늘
            'Others': '#C0C0C0'          # 회색
        }
        
        # 차트 스타일 설정
        sns.set_style("whitegrid")
        
    def generate_ascii_chart(self, trends: Dict, market_share: Dict, width: int = 60) -> str:
        """
        ASCII 차트 생성 (콘솔 출력용)
        
        Args:
            trends: 트렌드 데이터
            market_share: 시장 점유율 데이터
            width: 차트 너비
            
        Returns:
            ASCII 차트 문자열
        """
        chart = []
        chart.append("=" * width)
        chart.append("[CHART] Market Share Bar Chart (TOP 10)")
        chart.append("=" * width)
        
        # TOP 10 플랫폼 데이터 준비
        top_platforms = market_share['top_platforms'][:10]
        max_share = 0
        
        platform_data = []
        for platform in top_platforms:
            if platform in market_share['platform_shares']:
                share = market_share['platform_shares'][platform]['share_percentage']
                growth = trends.get(platform, {}).get('growth_rate', 0)
                platform_data.append((platform, share, growth))
                max_share = max(max_share, share)
        
        # 막대 차트 그리기
        for platform, share, growth in platform_data:
            # 막대 길이 계산 (최대 40자)
            bar_length = int((share / max_share) * 40) if max_share > 0 else 0
            bar = "#" * bar_length
            
            # 성장률 표시
            if growth > 0:
                growth_icon = "^"
                growth_color = "+"
            elif growth < 0:
                growth_icon = "v"
                growth_color = ""
            else:
                growth_icon = "-"
                growth_color = ""
            
            # 플랫폼 이름 고정 너비 (15자)
            platform_display = f"{platform[:13]:13}"
            
            # 차트 라인 생성
            line = f"{platform_display} |{bar:40} {share:5.1f}% ({growth_color}{growth:.1f}%{growth_icon})"
            chart.append(line)
        
        chart.append("=" * width)
        
        # 변화율 스파크라인 추가
        chart.append("\n[TREND] 7-Day Change Rate Trend (Sparkline)")
        chart.append("-" * width)
        
        spark_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        for platform in top_platforms[:5]:
            if platform in trends:
                trend = trends[platform]
                # 가상의 7일 데이터 생성 (실제로는 historical_data 사용)
                sparkline = self._generate_sparkline(trend.get('growth_rate', 0))
                chart.append(f"{platform[:13]:13} | {sparkline} | Current: {trend.get('current_players', 0):,}")
        
        chart.append("=" * width)
        
        return "\n".join(chart)
    
    def _generate_sparkline(self, growth_rate: float, length: int = 20) -> str:
        """스파크라인 생성"""
        # 간단한 시뮬레이션 (실제로는 historical data 사용)
        spark_chars = ['_', '.', '-', '=', '+', '*', '#', '@']
        
        # 성장률 기반 트렌드 시뮬레이션
        if growth_rate > 10:
            pattern = "_.=+*#@#"  # 상승
        elif growth_rate > 0:
            pattern = "===++***"  # 완만한 상승
        elif growth_rate < -10:
            pattern = "@#*+=._"  # 하락
        elif growth_rate < 0:
            pattern = "***++=="  # 완만한 하락
        else:
            pattern = "++++++++"  # 안정
        
        # 패턴 반복으로 길이 맞추기
        result = (pattern * 3)[:length]
        return result
    
    def generate_area_chart(self, platform_data: Dict, save_path: str = None) -> str:
        """
        누적 영역 차트 생성 (시장 점유율 변화)
        
        Args:
            platform_data: 플랫폼별 시계열 데이터
            save_path: 저장 경로
            
        Returns:
            차트 이미지 경로 또는 base64 인코딩
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # 데이터 준비
        dates = []
        platform_series = {}
        
        # 시계열 데이터 추출
        for platform_name, data in platform_data.items():
            historical = data.get('historical_data', [])
            if historical:
                if not dates:
                    dates = [record.get('timestamp', datetime.now()) for record in historical]
                
                platform_series[platform_name] = [
                    record.get('cash_players', 0) for record in historical
                ]
        
        if not dates:
            dates = [datetime.now() - timedelta(days=i) for i in range(7, -1, -1)]
        
        # 상위 10개 플랫폼만 선택
        top_platforms = sorted(platform_series.items(), 
                              key=lambda x: sum(x[1]), reverse=True)[:10]
        
        # 누적 영역 차트 (상단)
        ax1.set_title('Online Poker Platform Market Share Trend (Stacked Area Chart)', 
                     fontsize=16, fontweight='bold', pad=20)
        
        # 데이터 정규화 (백분율로 변환)
        y_data = []
        labels = []
        colors = []
        
        for platform, values in top_platforms:
            y_data.append(values)
            labels.append(platform)
            colors.append(self.color_palette.get(platform, '#808080'))
        
        # 누적 영역 그래프 그리기
        ax1.stackplot(dates, *y_data, labels=labels, colors=colors, alpha=0.8)
        
        # 포맷팅
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Number of Players', fontsize=12)
        ax1.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
        ax1.grid(True, alpha=0.3)
        
        # X축 날짜 포맷
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator())
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 변화율 차트 (하단)
        ax2.set_title('Daily Change Rate (%)', fontsize=14, fontweight='bold')
        
        # 각 플랫폼별 변화율 계산 및 표시
        for i, (platform, values) in enumerate(top_platforms[:5]):
            if len(values) > 1:
                changes = []
                for j in range(1, len(values)):
                    if values[j-1] > 0:
                        change = ((values[j] - values[j-1]) / values[j-1]) * 100
                    else:
                        change = 0
                    changes.append(change)
                
                # 변화율 라인 차트
                ax2.plot(dates[1:], changes, 
                        label=platform, 
                        color=self.color_palette.get(platform, '#808080'),
                        marker='o', markersize=4, linewidth=2, alpha=0.7)
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Change Rate (%)', fontsize=12)
        ax2.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
        ax2.grid(True, alpha=0.3)
        
        # X축 날짜 포맷
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # 레이아웃 조정
        plt.tight_layout()
        
        # 저장 또는 base64 인코딩
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # base64 인코딩하여 반환
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def generate_comparison_chart(self, trends: Dict, market_share: Dict, 
                                 save_path: str = None) -> str:
        """
        비교 차트 생성 (현재 vs 이전 주)
        
        Args:
            trends: 트렌드 데이터
            market_share: 시장 점유율
            save_path: 저장 경로
            
        Returns:
            차트 이미지 경로
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 시장 점유율 파이 차트 (좌상단)
        top_5 = market_share['top_platforms'][:5]
        sizes = []
        labels = []
        colors_list = []
        
        for platform in top_5:
            share = market_share['platform_shares'][platform]['share_percentage']
            sizes.append(share)
            labels.append(f"{platform}\n{share:.1f}%")
            colors_list.append(self.color_palette.get(platform, '#808080'))
        
        # 나머지
        others_share = 100 - sum(sizes)
        if others_share > 0:
            sizes.append(others_share)
            labels.append(f"Others\n{others_share:.1f}%")
            colors_list.append('#C0C0C0')
        
        ax1.pie(sizes, labels=labels, colors=colors_list, autopct='',
                startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax1.set_title('Current Market Share (TOP 5)', fontsize=14, fontweight='bold')
        
        # 2. 성장률 막대 차트 (우상단)
        platforms = []
        growth_rates = []
        bar_colors = []
        
        for platform in market_share['top_platforms'][:10]:
            if platform in trends:
                platforms.append(platform[:10])  # 이름 축약
                rate = trends[platform]['growth_rate']
                growth_rates.append(rate)
                
                # 색상 설정 (양수: 녹색, 음수: 빨강)
                if rate > 0:
                    bar_colors.append('#2ECC71')
                else:
                    bar_colors.append('#E74C3C')
        
        bars = ax2.bar(platforms, growth_rates, color=bar_colors, alpha=0.7)
        ax2.set_title('7-Day Growth Rate (%)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Platform', fontsize=12)
        ax2.set_ylabel('Growth Rate (%)', fontsize=12)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 값 표시
        for bar, rate in zip(bars, growth_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{rate:.1f}%',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=9)
        
        # 3. 플레이어 수 히트맵 (좌하단)
        # 시간대별 플레이어 분포 (예시 데이터)
        heatmap_data = []
        heatmap_labels = []
        
        for platform in market_share['top_platforms'][:8]:
            if platform in trends:
                # 간단한 시뮬레이션 데이터 (실제로는 시간대별 데이터 사용)
                current = trends[platform]['current_players']
                row = [current * np.random.uniform(0.7, 1.3) for _ in range(7)]
                heatmap_data.append(row)
                heatmap_labels.append(platform[:12])
        
        if heatmap_data:
            im = ax3.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
            ax3.set_xticks(np.arange(7))
            ax3.set_yticks(np.arange(len(heatmap_labels)))
            ax3.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            ax3.set_yticklabels(heatmap_labels)
            ax3.set_title('Weekly Player Activity Heatmap', fontsize=14, fontweight='bold')
            
            # 컬러바 추가
            cbar = plt.colorbar(im, ax=ax3)
            cbar.set_label('Number of Players', rotation=270, labelpad=15)
        
        # 4. 변동성 산점도 (우하단)
        x_volatility = []
        y_players = []
        s_sizes = []
        c_colors = []
        annotations = []
        
        for platform in market_share['top_platforms'][:15]:
            if platform in trends:
                trend = trends[platform]
                x_volatility.append(trend.get('volatility', 0))
                y_players.append(trend.get('current_players', 0))
                s_sizes.append(trend.get('current_players', 0) / 100)  # 크기 조정
                
                # 색상: 성장률 기반
                growth = trend.get('growth_rate', 0)
                if growth > 10:
                    c_colors.append('#2ECC71')
                elif growth < -10:
                    c_colors.append('#E74C3C')
                else:
                    c_colors.append('#3498DB')
                
                annotations.append(platform[:8])
        
        scatter = ax4.scatter(x_volatility, y_players, s=s_sizes, 
                            c=c_colors, alpha=0.6, edgecolors='black', linewidth=1)
        
        # 라벨 추가
        for i, txt in enumerate(annotations[:5]):  # 상위 5개만 라벨 표시
            ax4.annotate(txt, (x_volatility[i], y_players[i]),
                        fontsize=8, ha='center')
        
        ax4.set_title('Volatility vs Player Count', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Volatility (%)', fontsize=12)
        ax4.set_ylabel('Current Players', fontsize=12)
        ax4.grid(True, alpha=0.3)
        
        # 전체 레이아웃 조정
        plt.suptitle('Online Poker Platform Analysis Dashboard', 
                    fontsize=18, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # 저장
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def generate_html_report(self, analysis_results: Dict, charts: Dict) -> str:
        """
        HTML 리포트 생성
        
        Args:
            analysis_results: 분석 결과
            charts: 차트 이미지 (base64)
            
        Returns:
            HTML 문자열
        """
        html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Online Poker Platform Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header .date {{
            margin-top: 10px;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            padding: 30px;
        }}
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        .chart-image {{
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .issues {{
            padding: 30px;
            background: #fff3cd;
            margin: 20px 30px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
        }}
        .no-issues {{
            background: #d4edda;
            border-left-color: #28a745;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status-normal {{
            background: #28a745;
            color: white;
        }}
        .status-warning {{
            background: #ffc107;
            color: #333;
        }}
        .status-critical {{
            background: #dc3545;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎰 Online Poker Platform Analysis Report</h1>
            <div class="date">{timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="metric-card">
                <div class="metric-value">{total_players:,}</div>
                <div class="metric-label">Total Active Players</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{platform_count}</div>
                <div class="metric-label">Analyzed Platforms</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{market_volatility:.1f}%</div>
                <div class="metric-label">Market Volatility</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analysis_period}일</div>
                <div class="metric-label">Analysis Period</div>
            </div>
        </div>
        
        <div class="{issue_class}">
            <h3>Issue Detection Status 
                <span class="status-badge {status_class}">{status_text}</span>
            </h3>
            <p>{issue_summary}</p>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">📊 Stacked Area Chart - Market Share Trend</h2>
            <img src="{area_chart}" class="chart-image" alt="누적 영역 차트">
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">📈 Comprehensive Analysis Dashboard</h2>
            <img src="{comparison_chart}" class="chart-image" alt="종합 분석 차트">
        </div>
        
        <div class="footer">
            <p>Generated by Poker Platform Analyzer | Data Source: poker-online-analyze</p>
            <p>© 2025 All rights reserved</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 데이터 추출
        issue_detection = analysis_results.get('issue_detection', {})
        market_share = analysis_results.get('market_share', {})
        
        # 이슈 상태에 따른 스타일
        if issue_detection.get('has_issue'):
            issue_class = 'issues'
            status_class = 'status-warning' if issue_detection['issue_level'] != 'critical' else 'status-critical'
            status_text = 'Issue Detected' if issue_detection['issue_level'] != 'critical' else 'Critical Issue'
            issue_summary = issue_detection.get('issue_summary', '')
        else:
            issue_class = 'issues no-issues'
            status_class = 'status-normal'
            status_text = 'Normal'
            issue_summary = 'The market is operating stably.'
        
        # HTML 생성
        html = html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M KST'),
            total_players=market_share.get('total_players', 0),
            platform_count=len(analysis_results.get('trends', {})),
            market_volatility=issue_detection.get('market_volatility', 0),
            analysis_period=f"{analysis_results.get('analysis_period_days', 7)} days",
            issue_class=issue_class,
            status_class=status_class,
            status_text=status_text,
            issue_summary=issue_summary,
            area_chart=charts.get('area_chart', ''),
            comparison_chart=charts.get('comparison_chart', '')
        )
        
        return html
    
    def upload_to_slack(self, image_path: str, webhook_url: str, comment: str = ""):
        """
        Slack에 이미지 업로드 (Webhook은 이미지 직접 전송 불가, 링크만 가능)
        실제로는 이미지 호스팅 서비스나 Slack API 사용 필요
        
        Args:
            image_path: 이미지 파일 경로
            webhook_url: Slack webhook URL
            comment: 코멘트
        """
        # 주의: Webhook으로는 이미지 직접 전송 불가
        # 대안 1: 이미지를 외부 서버에 업로드 후 URL 전송
        # 대안 2: Slack API (files.upload) 사용
        # 대안 3: base64 인코딩하여 HTML 리포트 링크 전송
        
        message = {
            "text": comment,
            "attachments": [
                {
                    "title": "📊 플랫폼 분석 차트",
                    "text": "차트를 확인하려면 HTML 리포트를 다운로드하세요.",
                    "color": "#667eea"
                }
            ]
        }
        
        try:
            response = requests.post(webhook_url, json=message)
            if response.status_code == 200:
                print("✅ Slack 메시지 전송 성공")
            else:
                print(f"❌ Slack 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ Slack 전송 오류: {e}")


def integrate_with_analyzer(analyzer_instance, analysis_results: Dict):
    """
    기존 분석기와 통합
    
    Args:
        analyzer_instance: OnlinePlatformTrendAnalyzer 인스턴스
        analysis_results: 분석 결과
    """
    # 차트 생성기 초기화
    chart_gen = PlatformChartGenerator()
    
    # ASCII 차트 생성 및 출력
    ascii_chart = chart_gen.generate_ascii_chart(
        analysis_results['trends'],
        analysis_results['market_share']
    )
    print("\n" + ascii_chart)
    
    # 플랫폼 데이터 준비 (실제 Firebase 데이터 필요)
    # 여기서는 trends 데이터를 간단히 변환
    platform_data = {}
    for platform, trend in analysis_results['trends'].items():
        platform_data[platform] = {
            'current_data': {'cash_players': trend['current_players']},
            'historical_data': []  # 실제로는 Firebase에서 가져온 데이터
        }
    
    # 차트 이미지 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 누적 영역 차트
    area_chart_path = f"reports/area_chart_{timestamp}.png"
    area_chart = chart_gen.generate_area_chart(platform_data, area_chart_path)
    
    # 종합 비교 차트
    comparison_chart_path = f"reports/comparison_chart_{timestamp}.png"
    comparison_chart = chart_gen.generate_comparison_chart(
        analysis_results['trends'],
        analysis_results['market_share'],
        comparison_chart_path
    )
    
    # HTML 리포트 생성
    charts = {
        'area_chart': area_chart,
        'comparison_chart': comparison_chart
    }
    
    html_report = chart_gen.generate_html_report(analysis_results, charts)
    
    # HTML 파일 저장
    html_path = f"reports/platform_report_{timestamp}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\n📄 HTML 리포트 생성: {html_path}")
    print(f"📊 차트 이미지 저장: {area_chart_path}, {comparison_chart_path}")
    
    return {
        'ascii_chart': ascii_chart,
        'html_report_path': html_path,
        'charts': {
            'area': area_chart_path,
            'comparison': comparison_chart_path
        }
    }


if __name__ == "__main__":
    # 테스트 실행
    print("📊 차트 생성 시스템 테스트")
    
    # 테스트 데이터
    test_trends = {
        'GGNetwork': {'current_players': 45230, 'growth_rate': 7.7, 'volatility': 5.2},
        'PokerStars': {'current_players': 38120, 'growth_rate': 1.6, 'volatility': 3.1},
        'Natural8': {'current_players': 12500, 'growth_rate': 25.0, 'volatility': 12.3},
        'PartyPoker': {'current_players': 8500, 'growth_rate': -19.0, 'volatility': 15.7},
        '888poker': {'current_players': 7200, 'growth_rate': 5.3, 'volatility': 4.2},
    }
    
    test_market = {
        'total_players': 111550,
        'top_platforms': ['GGNetwork', 'PokerStars', 'Natural8', 'PartyPoker', '888poker'],
        'platform_shares': {
            'GGNetwork': {'share_percentage': 40.6},
            'PokerStars': {'share_percentage': 34.2},
            'Natural8': {'share_percentage': 11.2},
            'PartyPoker': {'share_percentage': 7.6},
            '888poker': {'share_percentage': 6.4},
        }
    }
    
    # 차트 생성
    generator = PlatformChartGenerator()
    
    # ASCII 차트
    ascii = generator.generate_ascii_chart(test_trends, test_market)
    print(ascii)
    
    print("\n✅ 차트 생성 테스트 완료!")