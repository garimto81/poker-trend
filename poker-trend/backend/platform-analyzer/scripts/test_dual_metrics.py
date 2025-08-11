#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Dual Metrics System
이중 지표 시스템 통합 테스트
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dual_metric_analyzer import DualMetricAnalyzer
from dual_metric_slack_reporter import DualMetricSlackReporter

def test_dual_metric_system():
    """이중 지표 시스템 테스트"""
    print("=" * 80)
    print("🎯 이중 지표 시스템 통합 테스트")
    print("=" * 80)
    print("총 온라인 플레이어 & 캐시 플레이어 동등 분석")
    print("=" * 80)
    
    # 1. 분석기 테스트
    print("\n1️⃣ 이중 지표 분석기 테스트")
    print("-" * 40)
    
    analyzer = DualMetricAnalyzer()
    result = analyzer.analyze_dual_metrics_daily()
    
    # 종합 점수
    score = result['comprehensive_score']
    print(f"\n🏆 종합 평가: {score['grade']}등급")
    print(f"   총점: {score['total_score']}/200점")
    print(f"   - 온라인 부문: {score['online_score']}/100점")
    print(f"   - 캐시 부문: {score['cash_score']}/100점")
    print(f"   균형 비율: {score['balance_ratio']:.2f}")
    print(f"   평가: {score['interpretation']}")
    
    # 2. 온라인 플레이어 분석
    print("\n2️⃣ 총 온라인 플레이어 분석")
    print("-" * 40)
    
    online = result['online_players']
    print(f"플레이어 수: {online['metrics']['total']['yesterday']:,} → {online['metrics']['total']['today']:,}")
    print(f"변화: {online['metrics']['total']['change']:+,}명 ({online['metrics']['total']['change_pct']:+.1f}%)")
    print(f"성장 등급: {online['growth_grade']}")
    print(f"시장 규모: {online['market_size']}")
    print(f"트렌드: {online['trend']}")
    
    # 3. 캐시 플레이어 분석
    print("\n3️⃣ 캐시 플레이어 분석")
    print("-" * 40)
    
    cash = result['cash_players']
    print(f"플레이어 수: {cash['metrics']['total']['yesterday']:,} → {cash['metrics']['total']['today']:,}")
    print(f"변화: {cash['metrics']['total']['change']:+,}명 ({cash['metrics']['total']['change_pct']:+.1f}%)")
    print(f"캐시 비율: {cash['cash_ratio']['today']:.1f}% (품질: {cash['cash_ratio']['quality']})")
    print(f"비율 변화: {cash['cash_ratio']['change']:+.1f}%p")
    print(f"성장 등급: {cash['growth_grade']}")
    print(f"수익 잠재력: {cash['revenue_potential']}")
    
    # 4. 상관관계 분석
    print("\n4️⃣ 상관관계 분석")
    print("-" * 40)
    
    correlation = result['correlation']
    print(f"패턴: {correlation['pattern']}")
    print(f"해석: {correlation['interpretation']}")
    print(f"성장 배수: 캐시가 온라인 대비 {correlation['growth_multiplier']:.1f}배")
    print(f"건전성 지수: {correlation['health_index']:.1f}/100")
    print(f"동조 수준: {correlation['sync_level']}")
    
    # 5. 시장 점유율 (이중 지표)
    print("\n5️⃣ 시장 점유율 분석 (이중 지표)")
    print("-" * 40)
    
    market = result['market_share']
    
    # 종합 리더
    if market['market_leaders']['composite']:
        leader = market['market_leaders']['composite']
        print(f"\n👑 종합 리더: {leader['site_name']}")
        print(f"   종합 점유율: {leader['composite_share']:.1f}%")
        print(f"   종합 변화: {leader['composite_change']:+.2f}%p")
    
    # 온라인 리더
    if market['market_leaders']['online']:
        online_leader = market['market_leaders']['online']
        print(f"\n🌐 온라인 리더: {online_leader['site_name']}")
        print(f"   온라인 점유율: {online_leader['online_share']['today']:.1f}%")
    
    # 캐시 리더
    if market['market_leaders']['cash']:
        cash_leader = market['market_leaders']['cash']
        print(f"\n💰 캐시 리더: {cash_leader['site_name']}")
        print(f"   캐시 점유율: {cash_leader['cash_share']['today']:.1f}%")
    
    # Top 3 집중도
    print(f"\n📊 Top 3 집중도:")
    print(f"   온라인: {market['top3_concentration']['online']:.1f}%")
    print(f"   캐시: {market['top3_concentration']['cash']:.1f}%")
    print(f"   종합: {market['top3_concentration']['composite']:.1f}%")
    
    # 6. 주요 인사이트
    print("\n6️⃣ 주요 인사이트")
    print("-" * 40)
    
    insights = result['insights']
    
    # 온라인 인사이트
    if insights['online_insights']:
        print("\n[온라인 플레이어]")
        for insight in insights['online_insights'][:2]:
            print(f"• {insight}")
    
    # 캐시 인사이트
    if insights['cash_insights']:
        print("\n[캐시 플레이어]")
        for insight in insights['cash_insights'][:2]:
            print(f"• {insight}")
    
    # 상관관계 인사이트
    if insights['correlation_insights']:
        print("\n[상관관계]")
        for insight in insights['correlation_insights'][:2]:
            print(f"• {insight}")
    
    # 시장 인사이트
    if insights['market_insights']:
        print("\n[시장 동향]")
        for insight in insights['market_insights'][:2]:
            print(f"• {insight}")
    
    # 전략 인사이트
    if insights['strategic_insights']:
        print("\n[전략적 시사점]")
        for insight in insights['strategic_insights'][:2]:
            print(f"• {insight}")
    
    # 7. Slack 리포터 테스트
    print("\n7️⃣ Slack 리포터 테스트")
    print("-" * 40)
    
    reporter = DualMetricSlackReporter()
    blocks = reporter._create_dual_metric_blocks(result)
    
    print(f"✅ Slack 블록 생성 완료: {len(blocks)}개 블록")
    
    # 블록 타입 분석
    block_types = {}
    for block in blocks:
        block_type = block.get('type', 'unknown')
        block_types[block_type] = block_types.get(block_type, 0) + 1
    
    print("\n블록 구성:")
    for block_type, count in block_types.items():
        print(f"  - {block_type}: {count}개")
    
    # 8. 데이터 저장
    print("\n8️⃣ 분석 결과 저장")
    print("-" * 40)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"dual_metric_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 분석 결과 저장: {output_file}")
    
    # 9. 시스템 검증
    print("\n9️⃣ 시스템 검증")
    print("-" * 40)
    
    validations = []
    
    # 점수 검증
    if 0 <= score['total_score'] <= 200:
        validations.append("✅ 종합 점수 범위 정상")
    else:
        validations.append("❌ 종합 점수 범위 오류")
    
    if 0 <= score['online_score'] <= 100:
        validations.append("✅ 온라인 점수 범위 정상")
    else:
        validations.append("❌ 온라인 점수 범위 오류")
    
    if 0 <= score['cash_score'] <= 100:
        validations.append("✅ 캐시 점수 범위 정상")
    else:
        validations.append("❌ 캐시 점수 범위 오류")
    
    # 균형 검증
    if score['balance_ratio'] > 0:
        validations.append("✅ 균형 비율 계산 정상")
    else:
        validations.append("❌ 균형 비율 계산 오류")
    
    # 상관관계 검증
    if 0 <= correlation['health_index'] <= 100:
        validations.append("✅ 건전성 지수 범위 정상")
    else:
        validations.append("❌ 건전성 지수 범위 오류")
    
    for validation in validations:
        print(f"  {validation}")
    
    # 10. 최종 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    print(f"\n✅ 이중 지표 분석 완료")
    print(f"✅ 온라인 & 캐시 모두 분석")
    print(f"✅ 상관관계 분석 완료")
    print(f"✅ 시장 점유율 이중 분석 완료")
    print(f"✅ Slack 리포트 생성 완료")
    
    # 균형 평가
    print(f"\n균형 평가:")
    if 0.8 <= score['balance_ratio'] <= 1.2:
        print("  ⚖️ 온라인과 캐시가 균형적으로 발전 중")
    elif score['balance_ratio'] > 1.2:
        print("  💰 캐시 플레이어 중심의 성장")
    else:
        print("  🌐 온라인 플레이어 중심의 성장")
    
    print("\n💡 핵심 포인트:")
    print("  1. 총 온라인 플레이어와 캐시 플레이어를 동등하게 분석")
    print("  2. 각 지표별 독립적 평가 (각 100점)")
    print("  3. 상관관계와 균형 지수 제공")
    print("  4. 시장 점유율을 두 지표 모두로 분석")
    print("  5. 통합된 인사이트 제공")

if __name__ == "__main__":
    test_dual_metric_system()