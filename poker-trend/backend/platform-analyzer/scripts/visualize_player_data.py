#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Online vs Cash Players Visualization
"""

import os
import sys
import io
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from io import BytesIO
import base64

# UTF-8 output handled automatically

# Import analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_live_data import LivePokerDataAnalyzer

# Configure matplotlib for English
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class PokerPlayerVisualizer:
    def __init__(self):
        self.color_palette = {
            'online': '#2E86DE',   # Blue
            'cash': '#10AC84',     # Green
            'ratio': '#F39C12',    # Orange
            'background': '#F8F9FA'
        }
        
        # Set style
        sns.set_style("whitegrid")
        
    def create_online_vs_cash_chart(self, data: List[Dict], top_n: int = 15):
        """Create comprehensive online vs cash players visualization"""
        
        # Sort by online players
        sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)[:top_n]
        
        # Create figure with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Online Poker Platform Analysis: Online vs Cash Players', 
                    fontsize=20, fontweight='bold', y=0.95)
        
        # 1. Dual Bar Chart (Top Left)
        platforms = [site['site_name'][:15] for site in sorted_data]
        online_players = [site['players_online'] for site in sorted_data]
        cash_players = [site['cash_players'] for site in sorted_data]
        
        x = np.arange(len(platforms))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, online_players, width, 
                       label='Online Players', color=self.color_palette['online'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, cash_players, width,
                       label='Cash Players', color=self.color_palette['cash'], alpha=0.8)
        
        ax1.set_title('Online vs Cash Players by Platform', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Platform', fontsize=12)
        ax1.set_ylabel('Number of Players', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(platforms, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=9)
        
        # 2. Cash-to-Online Ratio (Top Right)
        ratios = []
        ratio_platforms = []
        for site in sorted_data:
            if site['players_online'] > 0:
                ratio = (site['cash_players'] / site['players_online']) * 100
                ratios.append(ratio)
                ratio_platforms.append(site['site_name'][:15])
        
        if ratios:
            bars3 = ax2.bar(range(len(ratios)), ratios, 
                           color=self.color_palette['ratio'], alpha=0.7)
            ax2.set_title('Cash Players as % of Online Players', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Platform', fontsize=12)
            ax2.set_ylabel('Cash/Online Ratio (%)', fontsize=12)
            ax2.set_xticks(range(len(ratio_platforms)))
            ax2.set_xticklabels(ratio_platforms, rotation=45, ha='right')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add percentage labels
            for i, bar in enumerate(bars3):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', fontsize=9)
        
        # 3. Scatter Plot: Online vs Cash (Bottom Left)
        online_vals = [site['players_online'] for site in sorted_data if site['players_online'] > 0]
        cash_vals = [site['cash_players'] for site in sorted_data if site['players_online'] > 0]
        names = [site['site_name'] for site in sorted_data if site['players_online'] > 0]
        
        scatter = ax3.scatter(online_vals, cash_vals, 
                             s=[p/100 for p in online_vals], # Size by online players
                             alpha=0.6, c=range(len(online_vals)), cmap='viridis')
        
        # Add trend line
        if len(online_vals) > 1:
            z = np.polyfit(online_vals, cash_vals, 1)
            p = np.poly1d(z)
            ax3.plot(online_vals, p(online_vals), "r--", alpha=0.8, linewidth=2)
        
        ax3.set_title('Online vs Cash Players Correlation', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Online Players', fontsize=12)
        ax3.set_ylabel('Cash Players', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # Add labels for top platforms
        for i, (x, y, name) in enumerate(zip(online_vals[:5], cash_vals[:5], names[:5])):
            ax3.annotate(name[:10], (x, y), xytext=(5, 5), textcoords='offset points',
                        fontsize=9, alpha=0.8)
        
        # 4. Market Share Pie Charts (Bottom Right)
        # Online players pie (left half)
        online_sizes = [site['players_online'] for site in sorted_data[:8]]
        online_labels = [site['site_name'][:12] for site in sorted_data[:8]]
        
        # Create two pie charts side by side
        ax4_left = plt.subplot2grid((2, 2), (1, 1), colspan=1)
        ax4_right = ax4_left.twinx()
        ax4.remove()  # Remove the original ax4
        
        # Online players pie (left side)
        wedges1, texts1, autotexts1 = ax4_left.pie(online_sizes, labels=online_labels, 
                                                   autopct='%1.1f%%', startangle=90,
                                                   colors=plt.cm.Blues(np.linspace(0.3, 0.9, len(online_sizes))))
        ax4_left.set_title('Online Players\nMarket Share', fontsize=12, fontweight='bold', pad=20)
        
        # Cash players pie (create new subplot)
        ax4_cash = fig.add_subplot(2, 4, 8)
        cash_sizes = [site['cash_players'] for site in sorted_data[:8] if site['cash_players'] > 0]
        cash_labels = [site['site_name'][:12] for site in sorted_data[:8] if site['cash_players'] > 0]
        
        if cash_sizes:
            wedges2, texts2, autotexts2 = ax4_cash.pie(cash_sizes, labels=cash_labels,
                                                       autopct='%1.1f%%', startangle=90,
                                                       colors=plt.cm.Greens(np.linspace(0.3, 0.9, len(cash_sizes))))
            ax4_cash.set_title('Cash Players\nMarket Share', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def create_ascii_visualization(self, data: List[Dict], top_n: int = 10):
        """Create ASCII visualization for console output"""
        sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)[:top_n]
        
        print("\n" + "="*100)
        print("ONLINE vs CASH PLAYERS ANALYSIS (ASCII VISUALIZATION)")
        print("="*100)
        
        # Header
        print(f"{'Rank':<4} {'Platform':<20} {'Online Players':<15} {'Cash Players':<15} {'Ratio':<8} {'Visualization':<25}")
        print("-"*100)
        
        max_online = max(site['players_online'] for site in sorted_data) if sorted_data else 1
        
        for i, site in enumerate(sorted_data, 1):
            online = site['players_online']
            cash = site['cash_players']
            ratio = (cash / online * 100) if online > 0 else 0
            
            # Create visualization bars
            online_bar_len = int((online / max_online) * 20) if max_online > 0 else 0
            cash_bar_len = int((cash / max_online) * 20) if max_online > 0 else 0
            
            online_bar = "█" * online_bar_len
            cash_bar = "▓" * cash_bar_len
            
            vis = f"O:{online_bar:<20}\nC:{cash_bar:<20}"
            
            print(f"{i:<4} {site['site_name'][:19]:<20} {online:<15,} {cash:<15,} {ratio:<7.1f}% O:{'█' * min(online_bar_len, 20)}")
            print(f"{'':26}{'':16}{'':16}{'':9} C:{'▓' * min(cash_bar_len, 20)}")
            print()
        
        # Summary statistics
        total_online = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        overall_ratio = (total_cash / total_online * 100) if total_online > 0 else 0
        
        print("="*100)
        print("SUMMARY STATISTICS")
        print("="*100)
        print(f"Total Online Players: {total_online:,}")
        print(f"Total Cash Players: {total_cash:,}")
        print(f"Overall Cash/Online Ratio: {overall_ratio:.2f}%")
        
        # Find interesting insights
        print("\n" + "="*100)
        print("KEY INSIGHTS")
        print("="*100)
        
        # Highest ratio platforms
        ratio_data = [(site['site_name'], (site['cash_players']/site['players_online']*100) if site['players_online'] > 0 else 0) 
                      for site in sorted_data[:10]]
        ratio_sorted = sorted(ratio_data, key=lambda x: x[1], reverse=True)
        
        print("🎯 Highest Cash/Online Ratios:")
        for name, ratio in ratio_sorted[:5]:
            if ratio > 0:
                print(f"   • {name}: {ratio:.1f}%")
        
        # Largest cash player bases
        cash_sorted = sorted(sorted_data, key=lambda x: x['cash_players'], reverse=True)
        print("\n💰 Largest Cash Player Bases:")
        for site in cash_sorted[:5]:
            if site['cash_players'] > 0:
                print(f"   • {site['site_name']}: {site['cash_players']:,} cash players")
        
        # Market concentration
        top3_online = sum(site['players_online'] for site in sorted_data[:3])
        top3_cash = sum(site['cash_players'] for site in sorted_data[:3])
        
        print(f"\n📊 Market Concentration (TOP 3):")
        print(f"   • Online Players: {top3_online:,} ({top3_online/total_online*100:.1f}% of market)")
        print(f"   • Cash Players: {top3_cash:,} ({top3_cash/total_cash*100:.1f}% of market)")
    
    def save_charts_and_report(self, data: List[Dict], analysis_result: Dict):
        """Save visual charts and generate HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create charts directory
        charts_dir = "reports/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Generate main visualization
        fig = self.create_online_vs_cash_chart(data)
        chart_path = f"{charts_dir}/online_vs_cash_{timestamp}.png"
        fig.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        print(f"[OK] Chart saved: {chart_path}")
        
        # Generate base64 for HTML
        fig2 = self.create_online_vs_cash_chart(data)
        buffer = BytesIO()
        fig2.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        chart_b64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig2)
        
        # Generate HTML report
        html_report = self.generate_html_report(data, analysis_result, chart_b64)
        html_path = f"reports/online_vs_cash_report_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"[OK] HTML report saved: {html_path}")
        print(f"[WEB] Open in browser: file:///{os.path.abspath(html_path)}")
        
        return chart_path, html_path
    
    def generate_html_report(self, data: List[Dict], analysis_result: Dict, chart_b64: str):
        """Generate comprehensive HTML report"""
        
        sorted_data = sorted(data, key=lambda x: x['players_online'], reverse=True)
        total_online = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        overall_ratio = (total_cash / total_online * 100) if total_online > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Online vs Cash Players Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
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
            background: linear-gradient(135deg, #2E86DE 0%, #10AC84 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-value.online {{ color: #2E86DE; }}
        .stat-value.cash {{ color: #10AC84; }}
        .stat-value.ratio {{ color: #F39C12; }}
        .chart-container {{
            padding: 30px;
            text-align: center;
        }}
        .chart-image {{
            width: 100%;
            max-width: 1200px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .data-table {{
            margin: 30px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #2E86DE;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .insights {{
            margin: 30px;
            padding: 25px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .insight-item {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #2E86DE;
            border-radius: 8px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Online vs Cash Players Analysis</h1>
            <p>Real-time Poker Platform Data Analysis</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')} KST</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value online">{total_online:,}</div>
                <div class="stat-label">Total Online Players</div>
            </div>
            <div class="stat-card">
                <div class="stat-value cash">{total_cash:,}</div>
                <div class="stat-label">Total Cash Players</div>
            </div>
            <div class="stat-card">
                <div class="stat-value ratio">{overall_ratio:.1f}%</div>
                <div class="stat-label">Cash/Online Ratio</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([s for s in data if s['players_online'] > 0])}</div>
                <div class="stat-label">Active Platforms</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📊 Comprehensive Player Analysis</h2>
            <img src="data:image/png;base64,{chart_b64}" class="chart-image" alt="Online vs Cash Players Chart">
        </div>
        
        <div class="data-table">
            <h2>📋 Platform Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Platform</th>
                        <th>Online Players</th>
                        <th>Cash Players</th>
                        <th>Cash/Online Ratio</th>
                        <th>Peak 24h</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, site in enumerate(sorted_data[:15], 1):
            ratio = (site['cash_players'] / site['players_online'] * 100) if site['players_online'] > 0 else 0
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{site['site_name']}</strong></td>
                        <td>{site['players_online']:,}</td>
                        <td>{site['cash_players']:,}</td>
                        <td>{ratio:.1f}%</td>
                        <td>{site['peak_24h']:,}</td>
                    </tr>
            """
        
        # Add insights
        ratio_sorted = sorted(sorted_data[:10], key=lambda x: (x['cash_players']/x['players_online']*100) if x['players_online'] > 0 else 0, reverse=True)
        cash_sorted = sorted(sorted_data, key=lambda x: x['cash_players'], reverse=True)
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="insights">
            <h2>🔍 Key Insights</h2>
            <div class="insight-item">
                <h3>🎯 Highest Cash/Online Ratios</h3>
                <ul>
        """
        
        for site in ratio_sorted[:5]:
            if site['players_online'] > 0:
                ratio = (site['cash_players'] / site['players_online'] * 100)
                if ratio > 0:
                    html += f"<li><strong>{site['site_name']}</strong>: {ratio:.1f}%</li>"
        
        html += f"""
                </ul>
            </div>
            <div class="insight-item">
                <h3>💰 Largest Cash Player Bases</h3>
                <ul>
        """
        
        for site in cash_sorted[:5]:
            if site['cash_players'] > 0:
                html += f"<li><strong>{site['site_name']}</strong>: {site['cash_players']:,} cash players</li>"
        
        top3_online = sum(site['players_online'] for site in sorted_data[:3])
        top3_cash = sum(site['cash_players'] for site in sorted_data[:3])
        
        html += f"""
                </ul>
            </div>
            <div class="insight-item">
                <h3>📊 Market Concentration</h3>
                <p><strong>TOP 3 Platforms Control:</strong></p>
                <ul>
                    <li>Online Players: {top3_online:,} ({top3_online/total_online*100:.1f}% of market)</li>
                    <li>Cash Players: {top3_cash:,} ({top3_cash/total_cash*100:.1f}% of market)</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Poker Platform Analyzer | Data Source: PokerScout.com</p>
            <p>Real-time data collected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html

def main():
    print("="*80)
    print("ONLINE vs CASH PLAYERS VISUALIZATION SYSTEM")
    print("="*80)
    
    # Fetch live data
    analyzer = LivePokerDataAnalyzer()
    data = analyzer.crawl_pokerscout_data()
    
    if not data:
        print("[ERROR] No data available for visualization")
        return
    
    print(f"[OK] Successfully collected {len(data)} platforms")
    
    # Create visualizer
    visualizer = PokerPlayerVisualizer()
    
    # Show ASCII visualization first
    visualizer.create_ascii_visualization(data, top_n=15)
    
    # Generate analysis
    analysis_result = analyzer.analyze_data(data)
    
    # Create and save charts
    print("\n" + "="*80)
    print("GENERATING VISUAL CHARTS")
    print("="*80)
    
    chart_path, html_path = visualizer.save_charts_and_report(data, analysis_result)
    
    print("\n" + "="*80)
    print("[SUCCESS] Visualization Complete!")
    print("="*80)
    print(f"📊 Chart Image: {chart_path}")
    print(f"🌐 HTML Report: {html_path}")
    print("="*80)

if __name__ == "__main__":
    main()