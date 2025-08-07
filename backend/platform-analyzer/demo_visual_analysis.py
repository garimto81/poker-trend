#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인 포커 플랫폼 시각화 데모
실제 데이터 없이 시각화 결과를 미리 확인
"""

import os
import sys
import io
from datetime import datetime, timedelta
import random

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 스크립트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

def create_demo_data():
    """데모용 데이터 생성"""
    
    # 실제와 유사한 플랫폼 데이터 생성
    platforms = {
        'GGNetwork': {
            'base_players': 45000,
            'growth': 7.7,
            'volatility': 5.2,
            'trend': 'up'
        },
        'PokerStars': {
            'base_players': 38000,
            'growth': 1.6,
            'volatility': 3.1,
            'trend': 'stable'
        },
        'Natural8': {
            'base_players': 12000,
            'growth': 25.0,
            'volatility': 12.3,
            'trend': 'rapid_up'
        },
        'PartyPoker': {
            'base_players': 8500,
            'growth': -19.0,
            'volatility': 15.7,
            'trend': 'down'
        },
        '888poker': {
            'base_players': 7200,
            'growth': 5.3,
            'volatility': 4.2,
            'trend': 'up'
        },
        'Americas Cardroom': {
            'base_players': 5500,
            'growth': -3.2,
            'volatility': 6.8,
            'trend': 'stable'
        },
        'Ignition': {
            'base_players': 4800,
            'growth': 8.9,
            'volatility': 7.5,
            'trend': 'up'
        },
        'BetOnline': {
            'base_players': 3200,
            'growth': -5.5,
            'volatility': 9.2,
            'trend': 'down'
        },
        'PPPoker': {
            'base_players': 2800,
            'growth': 12.3,
            'volatility': 11.0,
            'trend': 'up'
        },
        'PokerBros': {
            'base_players': 2100,
            'growth': -8.7,
            'volatility': 13.5,
            'trend': 'down'
        }
    }
    
    # 7일간 히스토리 데이터 생성
    platform_data = {}
    
    for platform_name, info in platforms.items():
        base = info['base_players']
        growth_rate = info['growth'] / 100
        
        # 7일 데이터 시뮬레이션
        historical_data = []
        for i in range(7, -1, -1):
            # 트렌드에 따른 변동 생성
            if info['trend'] == 'rapid_up':
                daily_change = random.uniform(0.02, 0.05)
            elif info['trend'] == 'up':
                daily_change = random.uniform(0.005, 0.02)
            elif info['trend'] == 'stable':
                daily_change = random.uniform(-0.005, 0.005)
            elif info['trend'] == 'down':
                daily_change = random.uniform(-0.03, -0.01)
            else:
                daily_change = 0
            
            players = int(base * (1 - growth_rate * (i/7)) * (1 + daily_change))
            
            historical_data.append({
                'cash_players': players,
                'timestamp': datetime.now() - timedelta(days=i),
                'online_players': int(players * 1.2),
                'peak_players': int(players * 1.35)
            })
        
        platform_data[platform_name] = {
            'current_data': {
                'cash_players': int(base * (1 + growth_rate)),
                'online_players': int(base * 1.2 * (1 + growth_rate)),
                'peak_players': int(base * 1.35 * (1 + growth_rate))
            },
            'historical_data': historical_data
        }
    
    # 트렌드 데이터
    trends = {}
    for platform_name, info in platforms.items():
        current = platform_data[platform_name]['current_data']['cash_players']
        trends[platform_name] = {
            'current_players': current,
            'avg_players': int(current * 0.95),
            'peak_players': int(current * 1.1),
            'growth_rate': info['growth'],
            'daily_change_avg': info['growth'] / 7,
            'volatility': info['volatility'],
            'trend_direction': info['trend'],
            'data_points': 8
        }
    
    # 시장 점유율 계산
    total_players = sum(t['current_players'] for t in trends.values())
    
    market_share = {
        'total_players': total_players,
        'platform_shares': {},
        'top_platforms': []
    }
    
    for platform, trend in trends.items():
        share = (trend['current_players'] / total_players) * 100
        market_share['platform_shares'][platform] = {
            'share_percentage': share,
            'players': trend['current_players'],
            'rank': 0
        }
    
    # 순위 정렬
    sorted_platforms = sorted(
        market_share['platform_shares'].items(),
        key=lambda x: x[1]['share_percentage'],
        reverse=True
    )
    
    for rank, (platform, data) in enumerate(sorted_platforms, 1):
        market_share['platform_shares'][platform]['rank'] = rank
    
    market_share['top_platforms'] = [p[0] for p in sorted_platforms]
    
    return platform_data, trends, market_share


def demo_visual_analysis():
    """시각화 데모 실행"""
    
    print("""
========================================================================
           ONLINE POKER PLATFORM VISUAL ANALYSIS DEMO                        
========================================================================
    """)
    
    # 데모 데이터 생성
    print("[DATA] Generating demo data...")
    platform_data, trends, market_share = create_demo_data()
    
    # 이슈 감지 시뮬레이션
    significant_changes = []
    platforms_with_change = 0
    
    for platform, trend in trends.items():
        if abs(trend['growth_rate']) > 10:
            platforms_with_change += 1
            if trend['growth_rate'] > 15:
                change_type = 'rapid_growth'
                icon = '[RAPID+]'
            elif trend['growth_rate'] < -15:
                change_type = 'rapid_decline'
                icon = '[WARN]'
            else:
                change_type = 'notable_change'
                icon = '[CHART]'
            
            significant_changes.append({
                'type': change_type,
                'platform': platform,
                'change': trend['growth_rate'],
                'message': f"{icon} {platform} {abs(trend['growth_rate']):.1f}% {'surge' if trend['growth_rate'] > 0 else 'decline'}"
            })
    
    # 시장 변동성 계산
    all_volatilities = [t['volatility'] for t in trends.values()]
    market_volatility = sum(all_volatilities) / len(all_volatilities)
    
    issue_detection = {
        'has_issue': platforms_with_change >= 3,
        'issue_level': 'high' if platforms_with_change >= 3 else 'none',
        'issue_summary': f"Significant changes detected in {platforms_with_change} platforms" if platforms_with_change >= 3 else "Stable",
        'platforms_with_change': platforms_with_change,
        'market_volatility': market_volatility,
        'significant_changes': significant_changes
    }
    
    print("[OK] Data preparation complete\n")
    
    # 1. 정량 데이터 분석 결과 출력
    print("="*70)
    print("[CHART] ONLINE POKER PLATFORM DAILY ANALYSIS")
    print("="*70)
    
    print(f"\n[MARKET STATUS]")
    print(f"- Total Active Players: {market_share['total_players']:,}")
    print(f"- Analyzed Platforms: {len(trends)}")
    print(f"- Analysis Period: 7 days")
    
    print(f"\n[ISSUE DETECTION]")
    print(f"- Issue Status: {'[X] DETECTED' if issue_detection['has_issue'] else '[O] NORMAL'}")
    if issue_detection['has_issue']:
        print(f"- Issue Level: {issue_detection['issue_level']}")
        print(f"- Issue Summary: {issue_detection['issue_summary']}")
    print(f"- Market Volatility: {issue_detection['market_volatility']:.1f}%")
    print(f"- Platforms with Change: {issue_detection['platforms_with_change']}")
    
    print(f"\n[TOP 5 PLATFORMS]")
    top_5 = market_share['top_platforms'][:5]
    for i, platform in enumerate(top_5, 1):
        if platform in trends:
            trend = trends[platform]
            share = market_share['platform_shares'][platform]
            growth_icon = "[UP]" if trend['growth_rate'] > 0 else "[DOWN]" if trend['growth_rate'] < 0 else "[-]"
            print(f"{i}. {platform:20} | Players: {trend['current_players']:6,} | "
                  f"Share: {share['share_percentage']:5.1f}% | "
                  f"Change: {trend['growth_rate']:+6.1f}% {growth_icon}")
    
    if issue_detection['significant_changes']:
        print(f"\n[MAJOR CHANGES]")
        for change in issue_detection['significant_changes'][:5]:
            print(f"- {change['message']}")
    
    # 2. ASCII 차트 생성 및 출력
    try:
        from scripts.platform_chart_generator import PlatformChartGenerator
        
        chart_gen = PlatformChartGenerator()
        ascii_chart = chart_gen.generate_ascii_chart(trends, market_share)
        print("\n" + ascii_chart)
        
    except ImportError:
        # Simple ASCII chart generation
        print("\n" + "="*60)
        print("[CHART] Market Share Bar Chart (TOP 10)")
        print("="*60)
        
        top_10 = market_share['top_platforms'][:10]
        max_share = market_share['platform_shares'][top_10[0]]['share_percentage']
        
        for platform in top_10:
            share = market_share['platform_shares'][platform]['share_percentage']
            growth = trends[platform]['growth_rate']
            
            # 막대 길이 계산
            bar_length = int((share / max_share) * 40)
            bar = "#" * bar_length
            
            # Growth rate icon  
            if growth > 0:
                growth_icon = "^"
            elif growth < 0:
                growth_icon = "v"
            else:
                growth_icon = "-"
            
            platform_display = f"{platform[:13]:13}"
            print(f"{platform_display} |{bar:40} {share:5.1f}% ({growth:+.1f}%{growth_icon})")
        
        print("="*60)
    
    # 3. Create charts (if issues detected)
    if issue_detection['has_issue']:
        print("\n[UP] Generating visual charts...")
        
        try:
            from scripts.platform_chart_generator import PlatformChartGenerator
            
            chart_gen = PlatformChartGenerator()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # reports 디렉토리 생성
            os.makedirs('reports/charts', exist_ok=True)
            
            # Stacked area chart
            area_chart_path = f"reports/charts/demo_area_chart_{timestamp}.png"
            chart_gen.generate_area_chart(platform_data, area_chart_path)
            print(f"[OK] Stacked area chart created: {area_chart_path}")
            
            # Comprehensive dashboard
            dashboard_path = f"reports/charts/demo_dashboard_{timestamp}.png"
            chart_gen.generate_comparison_chart(trends, market_share, dashboard_path)
            print(f"[OK] Dashboard created: {dashboard_path}")
            
            # HTML 리포트
            analysis_results = {
                'trends': trends,
                'market_share': market_share,
                'issue_detection': issue_detection,
                'analysis_period_days': 7
            }
            
            # base64 차트 생성
            area_chart_b64 = chart_gen.generate_area_chart(platform_data)
            dashboard_b64 = chart_gen.generate_comparison_chart(trends, market_share)
            
            charts_b64 = {
                'area_chart': area_chart_b64,
                'comparison_chart': dashboard_b64
            }
            
            html_report = chart_gen.generate_html_report(analysis_results, charts_b64)
            html_path = f"reports/demo_html_report_{timestamp}.html"
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            print(f"[OK] HTML report created: {html_path}")
            print(f"\n[WEB] Open in browser: file:///{os.path.abspath(html_path)}")
            
        except Exception as e:
            print(f"[WARN] Chart generation failed (matplotlib required): {e}")
    else:
        print("\n[TIP] No issues detected, showing simple report only.")
    
    # 4. Slack message preview
    print("\n" + "="*70)
    print("[MSG] Slack Message Preview")
    print("="*70)
    
    if not issue_detection['has_issue']:
        slack_preview = f"""
[DOC] **Online Poker Platform DAILY Report**
----------------------------------
[DATE] {datetime.now().strftime('%Y-%m-%d %H:%M')} KST

[OK] **Status**: Normal (No special issues)

**Summary**
- Total Active Players: {market_share['total_players']:,}
- Market Volatility: {issue_detection['market_volatility']:.1f}%
- AI Analysis: Online poker platform market is maintaining stability.

[TIP] Operating stably without significant changes.
"""
    else:
        slack_preview = f"""
[DOC] **Online Poker Platform DAILY Report**
----------------------------------
[DATE] {datetime.now().strftime('%Y-%m-%d %H:%M')} KST

[WARN] **Significant Changes Detected**
{issue_detection['issue_summary']}

**[UP] Major Changes**
"""
        for change in issue_detection['significant_changes'][:3]:
            slack_preview += f"- {change['message']}\n"
        
        slack_preview += "\n**[TOP] TOP 5 Platform Status**\n"
        for i, platform in enumerate(top_5, 1):
            trend = trends[platform]
            slack_preview += f"{i}. **{platform}**: {trend['current_players']:,} players ({trend['growth_rate']:+.1f}%)\n"
        
        slack_preview += "\n[CHART] **Detailed Analysis Charts**"
        slack_preview += "\n- HTML report generated"
        slack_preview += "\n- 3 chart files created"
    
    print(slack_preview)
    
    print("\n" + "="*70)
    print("[OK] Visualization Demo Complete!")
    print("="*70)
    
    return {
        'platform_data': platform_data,
        'trends': trends,
        'market_share': market_share,
        'issue_detection': issue_detection
    }


if __name__ == "__main__":
    # Run demo
    results = demo_visual_analysis()
    
    print("""
[PIN] How to Run:
    
1. Real analysis with Firebase data:
   python scripts/online_platform_trend_analyzer.py --daily
   
2. Test mode (without Slack):
   python scripts/online_platform_trend_analyzer.py --test --daily
   
3. Generate charts only:
   python scripts/platform_chart_generator.py

[CHART] Generated Files Location:
   - reports/charts/ : PNG chart images
   - reports/ : HTML reports
    """)