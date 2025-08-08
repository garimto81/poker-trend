#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preview Real Slack Message
실제 데이터 기반 Slack 메시지 미리보기
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dual_metric_analyzer import DualMetricAnalyzer
from dual_metric_slack_reporter import DualMetricSlackReporter
from daily_data_collector import DailyDataCollector

def preview_real_slack_message():
    """실제 데이터로 Slack 메시지 미리보기"""
    
    print("\n" + "="*80)
    print("🔄 실제 데이터 수집 중...")
    print("="*80)
    
    # 1. 최신 데이터 수집
    collector = DailyDataCollector()
    
    # 오늘과 어제 데이터 수집
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    print(f"\n📅 수집 기간: {yesterday.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")
    
    # 데이터 수집 및 저장
    print("\n최신 데이터 수집 중...")
    try:
        collector.collect_and_save()
        print(f"✅ 데이터 수집 완료")
    except Exception as e:
        print(f"⚠️ 데이터 수집 중 오류: {e}")
        print("기존 데이터베이스 데이터를 사용합니다.")
    
    # 2. 이중 지표 분석 실행
    print("\n🎯 이중 지표 분석 실행 중...")
    analyzer = DualMetricAnalyzer()
    result = analyzer.analyze_dual_metrics_daily()
    
    # 3. Slack 메시지 생성
    print("\n📝 Slack 메시지 생성 중...")
    reporter = DualMetricSlackReporter()
    blocks = reporter._create_dual_metric_blocks(result)
    
    # 4. 실제 Slack 메시지 내용 표시
    print("\n" + "="*80)
    print("📱 SLACK 채널에 공유될 실제 메시지")
    print("="*80)
    
    # 메시지를 텍스트로 변환하여 표시
    score = result['comprehensive_score']
    online = result['online_players']
    cash = result['cash_players']
    correlation = result['correlation']
    market = result['market_share']
    insights = result['insights']
    
    # Slack 메시지 형식으로 출력
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                                                                       │")
    print("│                🎯 이중 지표 종합 분석 리포트                          │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 종합 평가
    grade_emoji = reporter._get_grade_emoji(score['grade'])
    print("│                                                                       │")
    print(f"│  종합 평가: {score['total_score']}/200점 {grade_emoji}                                      │")
    print(f"│  {score['interpretation']}                                             │")
    print("│                                                                       │")
    print(f"│  분석 기간: {result['period']}                          │")
    print(f"│  등급: {score['grade']}등급                                                    │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 균형 지수
    balance_text = reporter._get_balance_interpretation(score['balance_ratio'])
    print("│                                                                       │")
    print("│  ⚖️ 균형 지수                                                        │")
    print(f"│  온라인 {score['online_score']}/100 | 캐시 {score['cash_score']}/100                                 │")
    print(f"│  {balance_text}                                                       │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 총 온라인 플레이어
    print("│                                                                       │")
    print("│  🌐 총 온라인 플레이어                                               │")
    print("│                                                                       │")
    print("│  플레이어 수:                                                        │")
    print(f"│  {online['metrics']['total']['yesterday']:,} → {online['metrics']['total']['today']:,}                               │")
    print("│                                                                       │")
    online_emoji = reporter._get_growth_emoji(online['metrics']['total']['change_pct'])
    print(f"│  변화율: {online_emoji} {online['metrics']['total']['change_pct']:+.1f}% ({online['metrics']['total']['change']:+,}명)                    │")
    print("│                                                                       │")
    print(f"│  시장 규모: {reporter._get_market_size_text(online['market_size'])}                               │")
    print(f"│  성장 등급: {online['growth_grade']}                                          │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 캐시 플레이어
    print("│                                                                       │")
    print("│  💰 캐시 플레이어                                                    │")
    print("│                                                                       │")
    print("│  플레이어 수:                                                        │")
    print(f"│  {cash['metrics']['total']['yesterday']:,} → {cash['metrics']['total']['today']:,}                                 │")
    print("│                                                                       │")
    cash_emoji = reporter._get_growth_emoji(cash['metrics']['total']['change_pct'])
    print(f"│  변화율: {cash_emoji} {cash['metrics']['total']['change_pct']:+.1f}% ({cash['metrics']['total']['change']:+,}명)                      │")
    print("│                                                                       │")
    ratio_quality_emoji = reporter._get_quality_emoji(cash['cash_ratio']['quality'])
    print(f"│  캐시 비율: {cash['cash_ratio']['today']:.1f}% {ratio_quality_emoji}                                         │")
    print(f"│  (변화: {cash['cash_ratio']['change']:+.1f}%p)                                            │")
    print("│                                                                       │")
    print(f"│  수익 잠재력: {cash['revenue_potential']}                                          │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 상관관계 분석
    print("│                                                                       │")
    print("│  🔄 상관관계 분석                                                    │")
    print("│                                                                       │")
    print(f"│  패턴: {correlation['interpretation']}                                    │")
    print(f"│  성장 배수: 캐시가 온라인 대비 {correlation['growth_multiplier']:.1f}배                          │")
    print("│                                                                       │")
    print(f"│  건전성 지수: {correlation['health_index']:.1f}/100                                       │")
    print(f"│  동조 수준: {correlation['sync_level']}                                            │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 시장 점유율
    print("│                                                                       │")
    print("│  📊 시장 점유율 변화                                                 │")
    print("│                                                                       │")
    
    if market['market_leaders']['composite']:
        leader = market['market_leaders']['composite']
        print(f"│  👑 종합 리더: {leader['site_name'][:20]:<20}                          │")
        print(f"│  종합 점유율: {leader['composite_share']:.1f}% (변화: {leader['composite_change']:+.2f}%p)              │")
        print("│                                                                       │")
    
    print("│  🏆 Top 3 점유율 변화                                               │")
    for i, site in enumerate(market['dual_shares'][:3], 1):
        medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉'
        print(f"│                                                                       │")
        print(f"│  {medal} {site['site_name'][:20]:<20}                                     │")
        print(f"│     • 온라인: {site['online_share']['today']:5.1f}% ({site['online_share']['change']:+.2f}%p)                      │")
        print(f"│     • 캐시: {site['cash_share']['today']:5.1f}% ({site['cash_share']['change']:+.2f}%p)                        │")
    
    print("│                                                                       │")
    print(f"│  Top 3 집중도:                                                      │")
    print(f"│    • 온라인: {market['top3_concentration']['online']:.1f}%                                        │")
    print(f"│    • 캐시: {market['top3_concentration']['cash']:.1f}%                                          │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 핵심 인사이트
    print("│                                                                       │")
    print("│  💡 핵심 인사이트                                                    │")
    print("│                                                                       │")
    
    # 각 카테고리별 인사이트 출력
    if insights['online_insights']:
        print("│  [온라인]                                                            │")
        for insight in insights['online_insights'][:2]:
            # 긴 텍스트 처리
            if len(insight) > 65:
                insight_lines = [insight[i:i+65] for i in range(0, len(insight), 65)]
                for line in insight_lines[:2]:
                    print(f"│  • {line:<65}│")
            else:
                print(f"│  • {insight:<65}│")
    
    if insights['cash_insights']:
        print("│                                                                       │")
        print("│  [캐시]                                                              │")
        for insight in insights['cash_insights'][:2]:
            if len(insight) > 65:
                insight_lines = [insight[i:i+65] for i in range(0, len(insight), 65)]
                for line in insight_lines[:2]:
                    print(f"│  • {line:<65}│")
            else:
                print(f"│  • {insight:<65}│")
    
    if insights['correlation_insights']:
        print("│                                                                       │")
        print("│  [상관관계]                                                          │")
        for insight in insights['correlation_insights'][:1]:
            if len(insight) > 65:
                insight_lines = [insight[i:i+65] for i in range(0, len(insight), 65)]
                for line in insight_lines[:2]:
                    print(f"│  • {line:<65}│")
            else:
                print(f"│  • {insight:<65}│")
    
    if insights['strategic_insights']:
        print("│                                                                       │")
        print("│  [전략]                                                              │")
        for insight in insights['strategic_insights'][:2]:
            if len(insight) > 65:
                insight_lines = [insight[i:i+65] for i in range(0, len(insight), 65)]
                for line in insight_lines[:2]:
                    print(f"│  • {line:<65}│")
            else:
                print(f"│  • {insight:<65}│")
    
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    
    # 성과 평가 상세
    print("│                                                                       │")
    print("│  📊 성과 평가 상세                                                   │")
    print("│                                                                       │")
    print(f"│  온라인 부문 ({score['online_score']}/100)                                          │")
    details = score['score_details']
    print(f"│    • 성장: {details.get('online_growth', 0)}/40점                                   │")
    print(f"│    • 규모: {details.get('market_size', 0)}/10점                                     │")
    print(f"│    • 상관: {details.get('online_correlation', 0)}/25점                              │")
    print(f"│    • 시장: {details.get('online_market', 0)}/25점                                   │")
    print("│                                                                       │")
    print(f"│  캐시 부문 ({score['cash_score']}/100)                                            │")
    print(f"│    • 성장: {details.get('cash_growth', 0)}/40점                                     │")
    print(f"│    • 비율: {details.get('cash_ratio', 0)}/10점                                      │")
    print(f"│    • 상관: {details.get('cash_correlation', 0)}/25점                                │")
    print(f"│    • 시장: {details.get('cash_market', 0)}/25점                                     │")
    print("│                                                                       │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    print(f"│  🎯 이중 지표 분석 | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}                          │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # 5. 실제 데이터 요약
    print("\n" + "="*80)
    print("📊 실제 데이터 분석 요약")
    print("="*80)
    
    print(f"\n📅 분석 기간: {result['period']}")
    print(f"⏰ 분석 시간: {result['timestamp']}")
    
    print("\n🎯 종합 평가:")
    print(f"  • 총점: {score['total_score']}/200점 ({score['grade']}등급)")
    print(f"  • 온라인 부문: {score['online_score']}/100점")
    print(f"  • 캐시 부문: {score['cash_score']}/100점")
    print(f"  • 균형 비율: {score['balance_ratio']:.2f}")
    print(f"  • 평가: {score['interpretation']}")
    
    print("\n📈 주요 지표:")
    print(f"  • 총 온라인: {online['metrics']['total']['today']:,}명 ({online['metrics']['total']['change_pct']:+.1f}%)")
    print(f"  • 캐시: {cash['metrics']['total']['today']:,}명 ({cash['metrics']['total']['change_pct']:+.1f}%)")
    print(f"  • 캐시 비율: {cash['cash_ratio']['today']:.1f}%")
    print(f"  • 건전성 지수: {correlation['health_index']:.1f}/100")
    
    # 시장 리더 정보
    if market['market_leaders']['composite']:
        print("\n🏆 시장 리더:")
        leader = market['market_leaders']['composite']
        print(f"  • 종합: {leader['site_name']} ({leader['composite_share']:.1f}%)")
        
        if market['market_leaders']['online']:
            online_leader = market['market_leaders']['online']
            print(f"  • 온라인: {online_leader['site_name']} ({online_leader['online_share']['today']:.1f}%)")
        
        if market['market_leaders']['cash']:
            cash_leader = market['market_leaders']['cash']
            print(f"  • 캐시: {cash_leader['site_name']} ({cash_leader['cash_share']['today']:.1f}%)")
    
    # 주요 변동 사이트
    if market['movers']['online_gainers']:
        print("\n📈 온라인 상승 Top:")
        for site in market['movers']['online_gainers'][:2]:
            print(f"  • {site['site_name']}: +{site['online_share']['change']:.2f}%p")
    
    if market['movers']['cash_gainers']:
        print("\n💰 캐시 상승 Top:")
        for site in market['movers']['cash_gainers'][:2]:
            print(f"  • {site['site_name']}: +{site['cash_share']['change']:.2f}%p")
    
    # 6. JSON 형식 저장
    print("\n💾 분석 결과 저장...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    preview_file = f"slack_preview_{timestamp}.json"
    
    preview_data = {
        'analysis_result': result,
        'slack_blocks': blocks,
        'summary': {
            'total_score': score['total_score'],
            'grade': score['grade'],
            'online_score': score['online_score'],
            'cash_score': score['cash_score'],
            'balance_ratio': score['balance_ratio'],
            'online_players': online['metrics']['total']['today'],
            'cash_players': cash['metrics']['total']['today'],
            'timestamp': datetime.now().isoformat()
        }
    }
    
    with open(preview_file, 'w', encoding='utf-8') as f:
        json.dump(preview_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 미리보기 데이터 저장: {preview_file}")
    
    print("\n" + "="*80)
    print("✅ Slack 메시지 미리보기 완료!")
    print("="*80)
    print("\n이 메시지가 실제로 Slack 채널에 전송됩니다.")
    print("전송하려면 SLACK_WEBHOOK_URL 환경변수를 설정하고")
    print("dual_metric_slack_reporter.py를 실행하세요.")

if __name__ == "__main__":
    preview_real_slack_message()