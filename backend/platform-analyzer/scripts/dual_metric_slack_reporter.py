#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual Metric Slack Reporter
총 온라인 & 캐시 플레이어 통합 Slack 리포트 시스템
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dual_metric_analyzer import DualMetricAnalyzer
from chart_generator import ChartGenerator, CHART_AVAILABLE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualMetricSlackReporter:
    """
    이중 지표 기반 Slack 리포트
    - 총 온라인 플레이어: 시장 규모와 성장성
    - 캐시 플레이어: 수익성과 실질 가치
    - 두 지표 모두 동등하게 중요
    """
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.analyzer = DualMetricAnalyzer()
        self.chart_generator = ChartGenerator() if CHART_AVAILABLE else None
        
        # 이중 지표 이모지 맵
        self.emoji = {
            # 성장 관련
            'explosive': '🚀',
            'strong': '🔥',
            'growth': '📈',
            'stable': '➡️',
            'decline': '📉',
            'crash': '⬇️',
            # 품질 관련
            'excellent': '💎',
            'good': '⭐',
            'normal': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            # 메트릭 관련
            'online': '🌐',
            'cash': '💰',
            'correlation': '🔄',
            'market': '📊',
            # 등급 관련
            'grade_s': '🏆',
            'grade_a': '🥇',
            'grade_b': '🥈',
            'grade_c': '🥉',
            'grade_d': '⚠️',
            # 기타
            'crown': '👑',
            'chart': '📊',
            'insight': '💡',
            'balance': '⚖️'
        }
    
    def send_dual_metric_daily_report(self, target_date: str = None) -> bool:
        """이중 지표 일일 리포트 전송"""
        try:
            logger.info("🎯 이중 지표 일일 리포트 생성 중...")
            
            # 이중 지표 분석 실행
            analysis = self.analyzer.analyze_dual_metrics_daily(target_date)
            
            # Slack 블록 생성
            blocks = self._create_dual_metric_blocks(analysis)
            
            # 메시지 전송
            message = {
                'text': '🎯 이중 지표 종합 분석 리포트',
                'blocks': blocks
            }
            
            return self._send_to_slack(message)
            
        except Exception as e:
            logger.error(f"이중 지표 리포트 전송 실패: {e}")
            return False
    
    def _create_dual_metric_blocks(self, analysis: Dict) -> List[Dict]:
        """이중 지표 리포트 블록 생성"""
        blocks = []
        
        online = analysis['online_players']
        cash = analysis['cash_players']
        correlation = analysis['correlation']
        market = analysis['market_share']
        score = analysis['comprehensive_score']
        insights = analysis['insights']
        
        # 1. 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '🎯 이중 지표 종합 분석 리포트',
                'emoji': True
            }
        })
        
        # 2. 종합 스코어 (핵심 요약)
        grade_emoji = self._get_grade_emoji(score['grade'])
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*종합 평가: {score['total_score']}/200점 {grade_emoji}*\n{score['interpretation']}"
            },
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*분석 기간*\n{analysis['period']}"
                },
                {
                    'type': 'mrkdwn', 
                    'text': f"*등급*\n{score['grade']}등급"
                }
            ]
        })
        
        # 밸런스 지표
        balance_ratio = score['balance_ratio']
        balance_text = self._get_balance_interpretation(balance_ratio)
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['balance']} 균형 지수*\n온라인 {score['online_score']}/100 | 캐시 {score['cash_score']}/100\n{balance_text}"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 3. 총 온라인 플레이어 섹션
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['online']} 총 온라인 플레이어*"
            }
        })
        
        online_emoji = self._get_growth_emoji(online['metrics']['total']['change_pct'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*플레이어 수*\n{online['metrics']['total']['yesterday']:,} → {online['metrics']['total']['today']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화율*\n{online_emoji} {online['metrics']['total']['change_pct']:+.1f}% ({online['metrics']['total']['change']:+,}명)"
                }
            ]
        })
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*시장 규모*\n{self._get_market_size_text(online['market_size'])}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*성장 등급*\n{online['growth_grade']}"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 4. 캐시 플레이어 섹션
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['cash']} 캐시 플레이어*"
            }
        })
        
        cash_emoji = self._get_growth_emoji(cash['metrics']['total']['change_pct'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*플레이어 수*\n{cash['metrics']['total']['yesterday']:,} → {cash['metrics']['total']['today']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화율*\n{cash_emoji} {cash['metrics']['total']['change_pct']:+.1f}% ({cash['metrics']['total']['change']:+,}명)"
                }
            ]
        })
        
        ratio_quality_emoji = self._get_quality_emoji(cash['cash_ratio']['quality'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 비율*\n{cash['cash_ratio']['today']:.1f}% {ratio_quality_emoji}\n({cash['cash_ratio']['change']:+.1f}%p)"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*수익 잠재력*\n{cash['revenue_potential']}"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 5. 상관관계 분석
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['correlation']} 상관관계 분석*"
            }
        })
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*패턴*\n{correlation['interpretation']}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*성장 배수*\n캐시가 온라인 대비 {correlation['growth_multiplier']:.1f}배"
                }
            ]
        })
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*건전성 지수*\n{correlation['health_index']:.1f}/100"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*동조 수준*\n{correlation['sync_level']}"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 6. 시장 점유율 (이중 지표)
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['market']} 시장 점유율 변화*"
            }
        })
        
        # 종합 리더
        if market['market_leaders']['composite']:
            leader = market['market_leaders']['composite']
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"{self.emoji['crown']} *종합 리더: {leader['site_name']}*\n종합 점유율: {leader['composite_share']:.1f}% (변화: {leader['composite_change']:+.2f}%p)"
                }
            })
        
        # Top 3 점유율 변화
        share_text = "*Top 3 점유율 변화*\n"
        for i, site in enumerate(market['dual_shares'][:3], 1):
            medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉'
            share_text += f"{medal} {site['site_name']}\n"
            share_text += f"   • 온라인: {site['online_share']['today']:.1f}% ({site['online_share']['change']:+.2f}%p)\n"
            share_text += f"   • 캐시: {site['cash_share']['today']:.1f}% ({site['cash_share']['change']:+.2f}%p)\n"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': share_text.strip()
            }
        })
        
        # 시장 집중도
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*Top 3 집중도 (온라인)*\n{market['top3_concentration']['online']:.1f}%"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*Top 3 집중도 (캐시)*\n{market['top3_concentration']['cash']:.1f}%"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 7. 핵심 인사이트
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*{self.emoji['insight']} 핵심 인사이트*"
            }
        })
        
        # 카테고리별 인사이트
        all_insights = []
        
        # 온라인 인사이트
        if insights['online_insights']:
            all_insights.append(f"*[온라인]*")
            for insight in insights['online_insights'][:2]:
                all_insights.append(f"• {insight}")
        
        # 캐시 인사이트
        if insights['cash_insights']:
            all_insights.append(f"*[캐시]*")
            for insight in insights['cash_insights'][:2]:
                all_insights.append(f"• {insight}")
        
        # 상관관계 인사이트
        if insights['correlation_insights']:
            all_insights.append(f"*[상관관계]*")
            for insight in insights['correlation_insights'][:1]:
                all_insights.append(f"• {insight}")
        
        # 전략 인사이트
        if insights['strategic_insights']:
            all_insights.append(f"*[전략]*")
            for insight in insights['strategic_insights'][:1]:
                all_insights.append(f"• {insight}")
        
        insights_text = "\n".join(all_insights)
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': insights_text
            }
        })
        
        # 8. 성과 평가 상세
        blocks.append({'type': 'divider'})
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📊 성과 평가 상세*'
            }
        })
        
        # 온라인 부문
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*온라인 부문 ({score['online_score']}/100)*"
            },
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"성장: {score['score_details'].get('online_growth', 0)}/40"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"규모: {score['score_details'].get('market_size', 0)}/10"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"상관: {score['score_details'].get('online_correlation', 0)}/25"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"시장: {score['score_details'].get('online_market', 0)}/25"
                }
            ]
        })
        
        # 캐시 부문
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*캐시 부문 ({score['cash_score']}/100)*"
            },
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"성장: {score['score_details'].get('cash_growth', 0)}/40"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"비율: {score['score_details'].get('cash_ratio', 0)}/10"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"상관: {score['score_details'].get('cash_correlation', 0)}/25"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"시장: {score['score_details'].get('cash_market', 0)}/25"
                }
            ]
        })
        
        # 9. Footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"🎯 이중 지표 분석 | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def _get_growth_emoji(self, change_pct: float) -> str:
        """성장률 이모지"""
        if change_pct >= 15:
            return self.emoji['explosive']
        elif change_pct >= 10:
            return self.emoji['strong']
        elif change_pct >= 5:
            return self.emoji['growth']
        elif change_pct >= 0:
            return self.emoji['stable']
        elif change_pct >= -5:
            return self.emoji['decline']
        else:
            return self.emoji['crash']
    
    def _get_grade_emoji(self, grade: str) -> str:
        """등급 이모지"""
        emoji_map = {
            'S': self.emoji['grade_s'],
            'A': self.emoji['grade_a'],
            'B': self.emoji['grade_b'],
            'C': self.emoji['grade_c'],
            'D': self.emoji['grade_d']
        }
        return emoji_map.get(grade, '❓')
    
    def _get_quality_emoji(self, quality: str) -> str:
        """품질 이모지"""
        quality_map = {
            'excellent': self.emoji['excellent'],
            'good': self.emoji['good'],
            'normal': self.emoji['normal'],
            'low': self.emoji['warning'],
            'critical': self.emoji['critical']
        }
        return quality_map.get(quality, '')
    
    def _get_market_size_text(self, size: str) -> str:
        """시장 규모 텍스트"""
        size_map = {
            'massive': '초대형 (50만+)',
            'large': '대형 (20만+)',
            'medium': '중형 (10만+)',
            'small': '소형 (10만 미만)'
        }
        return size_map.get(size, size)
    
    def _get_balance_interpretation(self, ratio: float) -> str:
        """균형 해석"""
        if 0.9 <= ratio <= 1.1:
            return "⚖️ 완벽한 균형 상태"
        elif 0.8 <= ratio <= 1.2:
            return "✅ 균형적 발전"
        elif ratio > 1.2:
            return "💰 캐시 중심 성장"
        elif ratio < 0.8:
            return "🌐 온라인 중심 성장"
        else:
            return "불균형 상태"
    
    def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """Slack 메시지 전송"""
        if not self.webhook_url:
            logger.error("Slack Webhook URL이 설정되지 않았습니다.")
            print("\n[디버그] 전송하려던 이중 지표 메시지:")
            print(json.dumps(message, indent=2, ensure_ascii=False))
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ 이중 지표 리포트 전송 성공")
                return True
            else:
                logger.error(f"❌ 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"전송 중 오류: {e}")
            return False

def main():
    print("🎯 이중 지표 Slack 리포트 시스템")
    print("=" * 60)
    print("총 온라인 플레이어 & 캐시 플레이어 통합 분석")
    print("=" * 60)
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        webhook_url = input("Webhook URL 입력 (엔터시 테스트 모드): ").strip()
    
    reporter = DualMetricSlackReporter(webhook_url)
    
    print("\n작업 선택:")
    print("1. 이중 지표 일일 리포트 전송")
    print("2. 이중 지표 분석 테스트")
    print("3. Slack 메시지 미리보기")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            print("\n🎯 이중 지표 일일 리포트 전송 중...")
            success = reporter.send_dual_metric_daily_report()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '2':
            print("\n🧪 이중 지표 분석 테스트...")
            analyzer = DualMetricAnalyzer()
            result = analyzer.analyze_dual_metrics_daily()
            
            score = result['comprehensive_score']
            print(f"\n종합 점수: {score['total_score']}/200")
            print(f"  - 온라인 부문: {score['online_score']}/100")
            print(f"  - 캐시 부문: {score['cash_score']}/100")
            print(f"등급: {score['grade']}")
            print(f"평가: {score['interpretation']}")
            
            print("\n주요 인사이트:")
            for category, items in result['insights'].items():
                if items:
                    print(f"\n[{category}]")
                    for insight in items[:2]:
                        print(f"• {insight}")
            
        elif choice == '3':
            print("\n📋 Slack 메시지 미리보기 생성 중...")
            analyzer = DualMetricAnalyzer()
            result = analyzer.analyze_dual_metrics_daily()
            blocks = reporter._create_dual_metric_blocks(result)
            
            print(f"\n총 {len(blocks)}개 블록 생성")
            print("\n처음 3개 블록:")
            for i, block in enumerate(blocks[:3], 1):
                print(f"\n블록 {i}: {block.get('type')}")
                if block.get('type') == 'section' and block.get('text'):
                    print(f"  텍스트: {block['text'].get('text', '')[:100]}...")
            
    except KeyboardInterrupt:
        print("\n\n작업 취소됨")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()