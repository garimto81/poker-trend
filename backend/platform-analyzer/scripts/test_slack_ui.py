#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Enhanced Slack UI/UX
개선된 슬랙 메시지 UI/UX 테스트
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from slack_report_sender_v2 import EnhancedSlackReportSender
from chart_generator import ChartGenerator

def test_slack_message_formatting():
    """슬랙 메시지 포맷팅 테스트"""
    print("=" * 80)
    print("🧪 Enhanced Slack Message UI/UX 테스트")
    print("=" * 80)
    
    # 테스트용 Webhook URL (실제 전송하지 않음)
    sender = EnhancedSlackReportSender(webhook_url=None)
    
    # 1. 메시지 포맷팅 테스트
    print("\n1️⃣ 메시지 포맷팅 테스트")
    print("-" * 40)
    sender.test_message_formatting()
    
    # 2. 테스트 데이터 생성
    test_data = {
        'data': {
            'analysis_type': 'daily',
            'period': '2025-08-06 vs 2025-08-07',
            'yesterday': {
                'date': '2025-08-06',
                'summary': {
                    'total_players': 150000,
                    'avg_players': 3200,
                    'unique_sites': 42
                },
                'data_count': 42
            },
            'today': {
                'date': '2025-08-07',
                'summary': {
                    'total_players': 160000,
                    'avg_players': 3400,
                    'unique_sites': 47
                },
                'data_count': 47
            },
            'changes': {
                'total_players': {
                    'old': 150000,
                    'new': 160000,
                    'change': 10000,
                    'change_pct': 6.7
                },
                'avg_players': {
                    'old': 3200,
                    'new': 3400,
                    'change': 200,
                    'change_pct': 6.3
                },
                'total_cash_players': {
                    'old': 75000,
                    'new': 82000,
                    'change': 7000,
                    'change_pct': 9.3
                },
                'avg_cash_players': {
                    'old': 1500,
                    'new': 1650,
                    'change': 150,
                    'change_pct': 10.0
                },
                'unique_sites': {
                    'old': 42,
                    'new': 47,
                    'change': 5,
                    'change_pct': 11.9
                },
                'market_concentration': {
                    'old': 45.2,
                    'new': 47.8,
                    'change': 2.6,
                    'change_pct': 5.8
                }
            },
            'site_comparison': {
                'top_gainers': [
                    {'site_name': 'PokerStars', 'old_avg': 50000, 'new_avg': 57600, 'change': 7600, 'change_pct': 15.2},
                    {'site_name': 'GGPoker', 'old_avg': 40000, 'new_avg': 45000, 'change': 5000, 'change_pct': 12.5},
                    {'site_name': '888poker', 'old_avg': 20000, 'new_avg': 21660, 'change': 1660, 'change_pct': 8.3}
                ],
                'top_losers': [
                    {'site_name': 'PartyPoker', 'old_avg': 15000, 'new_avg': 14220, 'change': -780, 'change_pct': -5.2},
                    {'site_name': 'Winamax', 'old_avg': 10000, 'new_avg': 9300, 'change': -700, 'change_pct': -7.0}
                ]
            },
            'last_week': {
                'summary': {
                    'unique_dates': 7
                },
                'data_count': 294
            },
            'this_week': {
                'summary': {
                    'unique_dates': 3
                },
                'data_count': 141
            },
            'last_month': {
                'summary': {
                    'unique_dates': 30
                },
                'data_count': 1260
            },
            'this_month': {
                'summary': {
                    'unique_dates': 7
                },
                'data_count': 329
            }
        },
        'insights': {
            'overall_trend': '포커 시장이 전일 대비 6.7% 성장했습니다.',
            'market_concentration_trend': '시장 집중도가 소폭 상승했습니다.',
            'key_movers': ['PokerStars가 15.2% 급성장', 'PartyPoker가 5.2% 하락'],
            'data_quality_assessment': '데이터 품질이 양호합니다.'
        },
        'trends': {
            'growth_trend': '포커 시장이 지난주 대비 8.5%의 양호한 성장을 기록했습니다.',
            'volatility_assessment': '시장 변동성이 보통입니다 (평균 11.1%)',
            'market_dynamics': '시장 집중도가 안정적으로 유지되고 있습니다.',
            'data_completeness': '데이터 수집이 양호합니다.',
            'weekly_insights': [
                '주간 최대 성장: PokerStars (+15.2%)',
                '캐시 게임 참여가 전체 대비 더 활발해졌습니다.'
            ],
            'monthly_performance': '포커 시장이 12.3%의 건전한 월간 성장을 보였습니다.',
            'market_maturity': '시장 구조가 안정적인 상태를 유지하고 있습니다.',
            'competitive_landscape': '경쟁사 간 적당한 수준의 변동이 있습니다.',
            'seasonal_effects': '일반적인 활동 패턴을 보이고 있습니다.',
            'data_reliability': '데이터 수집이 매우 양호하여 분석 신뢰도가 높습니다.',
            'key_findings': [
                '월간 최대 성장: PokerStars (+15.2%)',
                '캐시 게임 참여가 전체 대비 더 활발해졌습니다.',
                '총계와 일평균 변화율에 차이가 있어 수집 패턴 변화가 있었습니다.'
            ]
        }
    }
    
    # 3. 일일 보고서 블록 생성
    print("\n2️⃣ 일일 보고서 블록 생성")
    print("-" * 40)
    
    daily_blocks = sender._create_daily_report_blocks({
        'data': test_data['data'],
        'insights': test_data['insights']
    })
    
    print(f"✅ 일일 보고서: {len(daily_blocks)}개 블록 생성")
    
    # 블록 구조 출력
    for i, block in enumerate(daily_blocks[:3], 1):
        block_type = block.get('type', 'unknown')
        print(f"  블록 {i}: {block_type}")
        
        if block_type == 'header':
            print(f"    제목: {block['text']['text']}")
        elif block_type == 'section' and block.get('fields'):
            print(f"    필드 수: {len(block['fields'])}")
    
    # 4. 주간 보고서 블록 생성
    print("\n3️⃣ 주간 보고서 블록 생성")
    print("-" * 40)
    
    weekly_blocks = sender._create_weekly_report_blocks({
        'data': test_data['data'],
        'trends': test_data['trends']
    })
    
    print(f"✅ 주간 보고서: {len(weekly_blocks)}개 블록 생성")
    
    # 5. 월간 보고서 블록 생성
    print("\n4️⃣ 월간 보고서 블록 생성")
    print("-" * 40)
    
    monthly_blocks = sender._create_monthly_report_blocks({
        'data': test_data['data'],
        'trends': test_data['trends']
    })
    
    print(f"✅ 월간 보고서: {len(monthly_blocks)}개 블록 생성")
    
    # 6. 알림 메시지 테스트
    print("\n5️⃣ 알림 메시지 포맷 테스트")
    print("-" * 40)
    
    alert_types = ['critical', 'warning', 'info', 'success']
    
    for alert_type in alert_types:
        print(f"  • {alert_type} 알림: ", end='')
        sender.send_alert(
            alert_type,
            f'테스트 {alert_type} 메시지입니다.',
            {'테스트 데이터': '값'}
        )
        print("✅")
    
    # 7. UI 개선 사항 요약
    print("\n" + "=" * 80)
    print("📊 UI/UX 개선 사항 요약")
    print("=" * 80)
    
    improvements = [
        "✅ Slack Block Kit 활용한 구조화된 레이아웃",
        "✅ 헤더, 섹션, 구분선으로 명확한 정보 계층",
        "✅ 필드 레이아웃으로 공간 효율적 정보 표시",
        "✅ 이모지와 색상 코딩으로 시각적 구분",
        "✅ KPI 대시보드 스타일의 핵심 지표 표시",
        "✅ 컨텍스트 블록으로 메타 정보 분리",
        "✅ 변화율에 따른 동적 이모지 (🚀📈➡️📉⬇️)",
        "✅ 성과 지표 시각화 (🔥탁월/⭐우수/✅양호/⚠️주의/🔴위험)",
        "✅ 랭킹에 메달 이모지 (🥇🥈🥉)",
        "✅ 알림 타입별 색상과 아이콘 차별화"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    # 8. 차트 생성 테스트
    print("\n6️⃣ 차트 생성 기능 테스트")
    print("-" * 40)
    
    try:
        from chart_generator import ChartGenerator, CHART_AVAILABLE
        
        if CHART_AVAILABLE:
            chart_gen = ChartGenerator()
            
            # 일일 차트 생성
            daily_chart = chart_gen.create_daily_comparison_chart(test_data['data'])
            if daily_chart:
                print("  ✅ 일일 비교 차트 생성 성공")
                chart_gen.save_chart_to_file(daily_chart, 'test_daily_chart.png')
            
            # 주간 차트 생성
            weekly_chart = chart_gen.create_weekly_trend_chart(test_data['data'])
            if weekly_chart:
                print("  ✅ 주간 트렌드 차트 생성 성공")
                chart_gen.save_chart_to_file(weekly_chart, 'test_weekly_chart.png')
            
            # 월간 대시보드 생성
            monthly_chart = chart_gen.create_monthly_dashboard(test_data)
            if monthly_chart:
                print("  ✅ 월간 대시보드 생성 성공")
                chart_gen.save_chart_to_file(monthly_chart, 'test_monthly_dashboard.png')
        else:
            print("  ⚠️ matplotlib이 설치되지 않아 차트 생성 건너뜀")
            
    except Exception as e:
        print(f"  ❌ 차트 생성 중 오류: {e}")
    
    # 9. 최종 결과
    print("\n" + "=" * 80)
    print("✅ Enhanced Slack UI/UX 테스트 완료!")
    print("=" * 80)
    
    print("\n💡 다음 단계:")
    print("  1. SLACK_WEBHOOK_URL 환경변수 설정")
    print("  2. python slack_report_sender_v2.py 실행")
    print("  3. 실제 Slack 채널에서 메시지 확인")
    print("  4. 필요시 matplotlib 설치하여 차트 기능 활성화")
    
    # 샘플 Slack 메시지 JSON 출력
    print("\n📋 샘플 Slack 메시지 구조 (일일 보고서):")
    print("-" * 40)
    
    sample_message = {
        'text': '📅 일일 포커 시장 분석 리포트',
        'blocks': daily_blocks[:5]  # 처음 5개 블록만
    }
    
    print(json.dumps(sample_message, indent=2, ensure_ascii=False)[:1000] + "...")

if __name__ == "__main__":
    test_slack_message_formatting()