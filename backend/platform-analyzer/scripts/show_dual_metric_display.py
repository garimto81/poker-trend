#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show Dual Metric Display Format
이중 지표 표시 형식 시연
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dual_metric_analyzer import DualMetricAnalyzer
from dual_metric_slack_reporter import DualMetricSlackReporter

def show_slack_display():
    """Slack에서 표시되는 형식을 텍스트로 시연"""
    
    print("\n" + "="*80)
    print("📱 SLACK 메시지 표시 형식")
    print("="*80)
    
    # 실제 데이터 분석
    analyzer = DualMetricAnalyzer()
    result = analyzer.analyze_dual_metrics_daily()
    
    # Slack 형식으로 변환
    reporter = DualMetricSlackReporter()
    blocks = reporter._create_dual_metric_blocks(result)
    
    # 시각적 표현
    print("\n┌─────────────────────────────────────────────────────────────────┐")
    print("│                                                                 │")
    print("│  🎯 이중 지표 종합 분석 리포트                                  │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    score = result['comprehensive_score']
    online = result['online_players']
    cash = result['cash_players']
    correlation = result['correlation']
    market = result['market_share']
    
    # 종합 스코어 섹션
    print("│                                                                 │")
    print(f"│  종합 평가: {score['total_score']}/200점 {reporter._get_grade_emoji(score['grade'])}                              │")
    print(f"│  {score['interpretation']}                                      │")
    print("│                                                                 │")
    print("│  분석 기간: {result['period'][:10]}                            │")
    print(f"│  등급: {score['grade']}등급                                           │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 균형 지수
    print("│                                                                 │")
    print(f"│  ⚖️ 균형 지수                                                  │")
    print(f"│  온라인 {score['online_score']}/100 | 캐시 {score['cash_score']}/100                            │")
    balance_text = reporter._get_balance_interpretation(score['balance_ratio'])
    print(f"│  {balance_text}                                              │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 총 온라인 플레이어 섹션
    print("│                                                                 │")
    print("│  🌐 총 온라인 플레이어                                         │")
    print("│                                                                 │")
    print(f"│  플레이어 수:                                                  │")
    print(f"│  {online['metrics']['total']['yesterday']:,} → {online['metrics']['total']['today']:,}                          │")
    print("│                                                                 │")
    online_emoji = reporter._get_growth_emoji(online['metrics']['total']['change_pct'])
    print(f"│  변화율: {online_emoji} {online['metrics']['total']['change_pct']:+.1f}% ({online['metrics']['total']['change']:+,}명)              │")
    print("│                                                                 │")
    print(f"│  시장 규모: {reporter._get_market_size_text(online['market_size'])}                           │")
    print(f"│  성장 등급: {online['growth_grade']}                                     │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 캐시 플레이어 섹션
    print("│                                                                 │")
    print("│  💰 캐시 플레이어                                              │")
    print("│                                                                 │")
    print(f"│  플레이어 수:                                                  │")
    print(f"│  {cash['metrics']['total']['yesterday']:,} → {cash['metrics']['total']['today']:,}                            │")
    print("│                                                                 │")
    cash_emoji = reporter._get_growth_emoji(cash['metrics']['total']['change_pct'])
    print(f"│  변화율: {cash_emoji} {cash['metrics']['total']['change_pct']:+.1f}% ({cash['metrics']['total']['change']:+,}명)                │")
    print("│                                                                 │")
    ratio_quality_emoji = reporter._get_quality_emoji(cash['cash_ratio']['quality'])
    print(f"│  캐시 비율: {cash['cash_ratio']['today']:.1f}% {ratio_quality_emoji}                                    │")
    print(f"│  ({cash['cash_ratio']['change']:+.1f}%p)                                              │")
    print(f"│                                                                 │")
    print(f"│  수익 잠재력: {cash['revenue_potential']}                                     │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 상관관계 분석
    print("│                                                                 │")
    print("│  🔄 상관관계 분석                                              │")
    print("│                                                                 │")
    print(f"│  패턴: {correlation['interpretation']}                              │")
    print(f"│  성장 배수: 캐시가 온라인 대비 {correlation['growth_multiplier']:.1f}배                    │")
    print(f"│                                                                 │")
    print(f"│  건전성 지수: {correlation['health_index']:.1f}/100                                 │")
    print(f"│  동조 수준: {correlation['sync_level']}                                      │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 시장 점유율
    print("│                                                                 │")
    print("│  📊 시장 점유율 변화                                           │")
    print("│                                                                 │")
    
    if market['market_leaders']['composite']:
        leader = market['market_leaders']['composite']
        print(f"│  👑 종합 리더: {leader['site_name'][:15]:<15}                      │")
        print(f"│  종합 점유율: {leader['composite_share']:.1f}%                                    │")
        print("│                                                                 │")
    
    print("│  Top 3 점유율 변화                                             │")
    for i, site in enumerate(market['dual_shares'][:3], 1):
        medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉'
        print(f"│  {medal} {site['site_name'][:12]:<12}                                      │")
        print(f"│     • 온라인: {site['online_share']['today']:.1f}% ({site['online_share']['change']:+.2f}%p)                 │")
        print(f"│     • 캐시: {site['cash_share']['today']:.1f}% ({site['cash_share']['change']:+.2f}%p)                   │")
    
    print("│                                                                 │")
    print(f"│  Top 3 집중도 (온라인): {market['top3_concentration']['online']:.1f}%                         │")
    print(f"│  Top 3 집중도 (캐시): {market['top3_concentration']['cash']:.1f}%                           │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 핵심 인사이트
    print("│                                                                 │")
    print("│  💡 핵심 인사이트                                              │")
    print("│                                                                 │")
    
    insights = result['insights']
    
    # 온라인 인사이트
    if insights['online_insights']:
        print("│  [온라인]                                                      │")
        for insight in insights['online_insights'][:1]:
            # 긴 텍스트를 적절히 잘라서 표시
            if len(insight) > 60:
                insight = insight[:57] + "..."
            print(f"│  • {insight:<60} │")
    
    # 캐시 인사이트
    if insights['cash_insights']:
        print("│  [캐시]                                                        │")
        for insight in insights['cash_insights'][:1]:
            if len(insight) > 60:
                insight = insight[:57] + "..."
            print(f"│  • {insight:<60} │")
    
    # 상관관계 인사이트
    if insights['correlation_insights']:
        print("│  [상관관계]                                                    │")
        for insight in insights['correlation_insights'][:1]:
            if len(insight) > 60:
                insight = insight[:57] + "..."
            print(f"│  • {insight:<60} │")
    
    # 전략 인사이트
    if insights['strategic_insights']:
        print("│  [전략]                                                        │")
        for insight in insights['strategic_insights'][:1]:
            if len(insight) > 60:
                insight = insight[:57] + "..."
            print(f"│  • {insight:<60} │")
    
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    # 성과 평가 상세
    print("│                                                                 │")
    print("│  📊 성과 평가 상세                                             │")
    print("│                                                                 │")
    print(f"│  온라인 부문 ({score['online_score']}/100)                                    │")
    print(f"│    성장: {score['score_details'].get('online_growth', 0)}/40  규모: {score['score_details'].get('market_size', 0)}/10                     │")
    print(f"│    상관: {score['score_details'].get('online_correlation', 0)}/25  시장: {score['score_details'].get('online_market', 0)}/25                  │")
    print("│                                                                 │")
    print(f"│  캐시 부문 ({score['cash_score']}/100)                                      │")
    print(f"│    성장: {score['score_details'].get('cash_growth', 0)}/40  비율: {score['score_details'].get('cash_ratio', 0)}/10                     │")
    print(f"│    상관: {score['score_details'].get('cash_correlation', 0)}/25  시장: {score['score_details'].get('cash_market', 0)}/25                    │")
    print("│                                                                 │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│  🎯 이중 지표 분석 | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}                    │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    # 데이터 표시 특징 설명
    print("\n" + "="*80)
    print("📊 데이터 표시 특징")
    print("="*80)
    
    features = [
        "1️⃣ 종합 점수 (200점 만점)",
        "   • 온라인 부문: 100점 (성장 40 + 규모 10 + 상관 25 + 시장 25)",
        "   • 캐시 부문: 100점 (성장 40 + 비율 10 + 상관 25 + 시장 25)",
        "",
        "2️⃣ 균형 지수",
        "   • 온라인과 캐시 점수 비율로 균형 평가",
        "   • 0.8~1.2: 균형적 발전",
        "   • >1.2: 캐시 중심 성장",
        "   • <0.8: 온라인 중심 성장",
        "",
        "3️⃣ 이중 지표 분석",
        "   • 총 온라인 플레이어: 시장 규모와 성장성",
        "   • 캐시 플레이어: 수익성과 실질 가치",
        "   • 두 지표를 동등하게 중요하게 다룸",
        "",
        "4️⃣ 상관관계 패턴",
        "   • cash_dominant: 캐시 게임 강세",
        "   • cash_leading: 캐시 게임 선호 증가",
        "   • balanced: 균형적 성장",
        "   • tournament_leading: 토너먼트 선호 증가",
        "   • tournament_dominant: 토너먼트 강세",
        "",
        "5️⃣ 시장 점유율",
        "   • 온라인 점유율: 총 온라인 플레이어 기준",
        "   • 캐시 점유율: 캐시 플레이어 기준",
        "   • 종합 점유율: 온라인 40% + 캐시 60% 가중평균",
        "",
        "6️⃣ 동적 이모지 시스템",
        "   • 🚀 15% 이상: 폭발적 성장",
        "   • 🔥 10% 이상: 강력한 성장",
        "   • 📈 5% 이상: 양호한 성장",
        "   • ➡️ 0% 이상: 안정적",
        "   • 📉 -5% 이상: 소폭 하락",
        "   • ⬇️ -5% 미만: 급락",
        "",
        "7️⃣ 등급 시스템",
        "   • S등급 (170+): 🏆 탁월한 종합 성과",
        "   • A등급 (140+): 🥇 우수한 종합 성과",
        "   • B등급 (110+): 🥈 양호한 종합 성과",
        "   • C등급 (80+): 🥉 보통 수준의 성과",
        "   • D등급 (<80): ⚠️ 개선이 필요한 성과"
    ]
    
    for feature in features:
        print(feature)
    
    # 실제 데이터 예시
    print("\n" + "="*80)
    print("📈 실제 데이터 예시")
    print("="*80)
    
    print("\n현재 분석 결과:")
    print(f"• 종합 점수: {score['total_score']}/200 ({score['grade']}등급)")
    print(f"• 온라인 점수: {score['online_score']}/100")
    print(f"• 캐시 점수: {score['cash_score']}/100")
    print(f"• 균형 비율: {score['balance_ratio']:.2f}")
    print(f"• 온라인 플레이어: {online['metrics']['total']['today']:,}명 ({online['metrics']['total']['change_pct']:+.1f}%)")
    print(f"• 캐시 플레이어: {cash['metrics']['total']['today']:,}명 ({cash['metrics']['total']['change_pct']:+.1f}%)")
    print(f"• 캐시 비율: {cash['cash_ratio']['today']:.1f}%")
    print(f"• 건전성 지수: {correlation['health_index']:.1f}/100")

if __name__ == "__main__":
    show_slack_display()