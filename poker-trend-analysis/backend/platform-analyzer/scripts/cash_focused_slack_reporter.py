#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cash-Focused Slack Reporter
캐시 플레이어 중심 Slack 리포트 시스템
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cash_player_analyzer import CashPlayerAnalyzer
from multi_period_analyzer import MultiPeriodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CashFocusedSlackReporter:
    """
    캐시 카우 모델 기반 Slack 리포트
    - 캐시 플레이어 수가 핵심 지표
    - 시장 점유율 변화가 트렌드 판단 기준
    """
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.cash_analyzer = CashPlayerAnalyzer()
        self.period_analyzer = MultiPeriodAnalyzer()
        
        # 캐시 카우 이모지 맵
        self.emoji = {
            'cash': '💰',
            'cash_growth': '💵',
            'market_share': '📊',
            'surge': '🚀',
            'growth': '📈',
            'stable': '➡️',
            'decline': '📉',
            'crash': '⬇️',
            'excellent': '🔥',
            'good': '⭐',
            'normal': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            'crown': '👑',
            'trophy': '🏆',
            'medal_gold': '🥇',
            'medal_silver': '🥈',
            'medal_bronze': '🥉'
        }
    
    def send_cash_focused_daily_report(self, target_date: str = None) -> bool:
        """캐시 중심 일일 리포트 전송"""
        try:
            logger.info("💰 캐시 카우 일일 리포트 생성 중...")
            
            # 캐시 중심 분석 실행
            analysis = self.cash_analyzer.analyze_cash_focused_daily(target_date)
            
            # Slack 블록 생성
            blocks = self._create_cash_daily_blocks(analysis)
            
            # 메시지 전송
            message = {
                'text': '💰 캐시 카우 일일 분석 리포트',
                'blocks': blocks
            }
            
            return self._send_to_slack(message)
            
        except Exception as e:
            logger.error(f"캐시 일일 리포트 전송 실패: {e}")
            return False
    
    def _create_cash_daily_blocks(self, analysis: Dict) -> List[Dict]:
        """캐시 중심 일일 리포트 블록 생성"""
        blocks = []
        
        cash = analysis['cash_analysis']
        market = analysis['market_share_analysis']
        score = analysis['cash_cow_score']
        insights = analysis['insights']
        
        # 1. 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '💰 캐시 카우 일일 분석 리포트',
                'emoji': True
            }
        })
        
        # 2. 캐시 카우 스코어 (핵심 요약)
        score_emoji = self._get_score_emoji(score['grade'])
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*캐시 카우 스코어: {score['total_score']}/100 {score_emoji}*\n{score['interpretation']}"
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
        
        blocks.append({'type': 'divider'})
        
        # 3. 캐시 플레이어 핵심 지표 (가장 중요)
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💵 캐시 플레이어 핵심 지표*'
            }
        })
        
        # 캐시 플레이어 변화
        cash_emoji = self._get_growth_emoji(cash['cash_players']['change_pct'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 플레이어 수*\n{cash['cash_players']['yesterday']:,} → {cash['cash_players']['today']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화율*\n{cash_emoji} {cash['cash_players']['change_pct']:+.1f}% ({cash['cash_players']['change']:+,}명)"
                }
            ]
        })
        
        # 캐시 비율과 성과
        ratio_quality = self._get_ratio_quality_emoji(cash['cash_ratio']['quality'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 비율*\n{cash['cash_ratio']['today']:.1f}% {ratio_quality}\n({cash['cash_ratio']['change']:+.1f}%p)"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 vs 총플레이어*\n{cash['cash_vs_total']['multiplier']:.1f}배 성장\n{cash['cash_vs_total']['interpretation']}"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 4. 시장 점유율 변화 (두 번째 핵심)
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📊 시장 점유율 변화 (캐시 플레이어 기준)*'
            }
        })
        
        # Top 3 점유율 변화
        share_text = ""
        for i, site in enumerate(market['site_shares'][:3], 1):
            medal = self.emoji['medal_gold'] if i == 1 else self.emoji['medal_silver'] if i == 2 else self.emoji['medal_bronze']
            trend_emoji = self._get_share_trend_emoji(site['share_change'])
            share_text += f"{medal} *{site['site_name']}*: {site['today_share']:.1f}% ({site['share_change']:+.2f}%p) {trend_emoji}\n"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': share_text.strip()
            }
        })
        
        # 시장 집중도와 변동성
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*Top 3 집중도*\n{market['top3_concentration']:.1f}%"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*시장 변동성*\n{self._evaluate_volatility(market['market_volatility'])}"
                }
            ]
        })
        
        # 5. 점유율 급변 사이트 (있는 경우)
        if market['share_movements']['gainers'] or market['share_movements']['losers']:
            blocks.append({'type': 'divider'})
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*🎯 점유율 급변 사이트*'
                }
            })
            
            movements_text = ""
            
            if market['share_movements']['gainers']:
                movements_text += "*🚀 급상승*\n"
                for site in market['share_movements']['gainers'][:2]:
                    movements_text += f"• {site['site_name']}: +{site['share_change']:.2f}%p\n"
            
            if market['share_movements']['losers']:
                movements_text += "\n*📉 급하락*\n"
                for site in market['share_movements']['losers'][:2]:
                    movements_text += f"• {site['site_name']}: {site['share_change']:.2f}%p\n"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': movements_text.strip()
                }
            })
        
        blocks.append({'type': 'divider'})
        
        # 6. 핵심 인사이트
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💡 핵심 인사이트*'
            }
        })
        
        # 주요 인사이트 통합
        all_insights = []
        all_insights.extend(insights['primary'][:2])
        all_insights.extend(insights['market_dynamics'][:2])
        if insights['strategic']:
            all_insights.append(insights['strategic'][0])
        
        insights_text = ""
        for insight in all_insights:
            insights_text += f"• {insight}\n"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': insights_text.strip()
            }
        })
        
        # 7. 경고 사항 (있는 경우)
        if insights.get('warnings'):
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*⚠️ 주의 사항*\n" + "\n".join(f"• {w}" for w in insights['warnings'][:2])
                }
            })
        
        # 8. 스코어 구성 요소
        blocks.append({'type': 'divider'})
        
        components = score['components']
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📈 성과 평가*'
            },
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 성장*\n{components['cash_growth']}/30점"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 비율*\n{components['cash_ratio']}/25점"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*시장 안정성*\n{components['stability']}/25점"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*캐시 성과*\n{components['cash_performance']}/20점"
                }
            ]
        })
        
        # 9. Footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"💰 캐시 카우 모델 | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def send_cash_weekly_comparison(self) -> bool:
        """캐시 중심 주간 비교 리포트"""
        try:
            # 주간 데이터 수집
            weekly_result = self.period_analyzer.weekly_comparison_analysis()
            
            # 캐시 플레이어 중심으로 재분석
            blocks = self._create_cash_weekly_blocks(weekly_result)
            
            message = {
                'text': '💰 캐시 카우 주간 비교 리포트',
                'blocks': blocks
            }
            
            return self._send_to_slack(message)
            
        except Exception as e:
            logger.error(f"캐시 주간 리포트 전송 실패: {e}")
            return False
    
    def _create_cash_weekly_blocks(self, weekly_data: Dict) -> List[Dict]:
        """캐시 중심 주간 리포트 블록"""
        blocks = []
        
        changes = weekly_data['changes']
        
        # 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '💰 캐시 카우 주간 비교 리포트',
                'emoji': True
            }
        })
        
        # 기간 정보
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*📅 분석 기간*\n{weekly_data['period']}"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 캐시 플레이어 주간 성과
        cash_change = changes.get('total_cash_players', {})
        cash_avg_change = changes.get('avg_cash_players', {})
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💵 캐시 플레이어 주간 성과*'
            }
        })
        
        cash_emoji = self._get_growth_emoji(cash_change.get('change_pct', 0))
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*주간 총 캐시 플레이어*\n{cash_emoji} {cash_change.get('change_pct', 0):+.1f}%\n({cash_change.get('change', 0):+,}명)"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*일평균 캐시 플레이어*\n{cash_avg_change.get('change_pct', 0):+.1f}%\n({cash_avg_change.get('change', 0):+,.0f}명)"
                }
            ]
        })
        
        # 캐시 vs 총 플레이어 비교
        total_change_pct = changes.get('total_players', {}).get('change_pct', 0)
        cash_change_pct = cash_change.get('change_pct', 0)
        
        if total_change_pct != 0:
            multiplier = cash_change_pct / total_change_pct
            performance = "캐시 게임 강세" if multiplier > 1 else "토너먼트 강세"
        else:
            multiplier = 0
            performance = "데이터 부족"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*📊 캐시 vs 총 플레이어*\n캐시 성장이 전체 대비 {multiplier:.1f}배\n{performance}"
            }
        })
        
        # Footer
        blocks.append({'type': 'divider'})
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"💰 캐시 카우 모델 | 📊 주간 분석 | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def _get_growth_emoji(self, change_pct: float) -> str:
        """성장률 이모지"""
        if change_pct >= 15:
            return '🚀'
        elif change_pct >= 10:
            return '🔥'
        elif change_pct >= 5:
            return '📈'
        elif change_pct >= 0:
            return '➡️'
        elif change_pct >= -5:
            return '📉'
        else:
            return '⬇️'
    
    def _get_score_emoji(self, grade: str) -> str:
        """스코어 등급 이모지"""
        return {
            'S': '🏆',
            'A': '⭐',
            'B': '✅',
            'C': '⚠️',
            'D': '🔴'
        }.get(grade, '❓')
    
    def _get_ratio_quality_emoji(self, quality: str) -> str:
        """캐시 비율 품질 이모지"""
        return {
            'excellent': '🔥',
            'good': '⭐',
            'normal': '✅',
            'warning': '⚠️',
            'critical': '🔴'
        }.get(quality, '')
    
    def _get_share_trend_emoji(self, change: float) -> str:
        """점유율 변화 이모지"""
        if change >= 2:
            return '🚀'
        elif change >= 0.5:
            return '📈'
        elif change >= -0.5:
            return '➡️'
        elif change >= -2:
            return '📉'
        else:
            return '⬇️'
    
    def _evaluate_volatility(self, volatility: float) -> str:
        """변동성 평가"""
        if volatility < 1:
            return f"{volatility:.2f} (안정적)"
        elif volatility < 2:
            return f"{volatility:.2f} (보통)"
        elif volatility < 3:
            return f"{volatility:.2f} (변동적)"
        else:
            return f"{volatility:.2f} (매우 불안정)"
    
    def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """Slack 메시지 전송"""
        if not self.webhook_url:
            logger.error("Slack Webhook URL이 설정되지 않았습니다.")
            print("\n[디버그] 전송하려던 캐시 카우 메시지:")
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
                logger.info("✅ 캐시 카우 리포트 전송 성공")
                return True
            else:
                logger.error(f"❌ 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"전송 중 오류: {e}")
            return False

def main():
    print("💰 캐시 카우 Slack 리포트 시스템")
    print("=" * 60)
    print("핵심: 캐시 플레이어와 시장 점유율 변화 중심 분석")
    print("=" * 60)
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        webhook_url = input("Webhook URL 입력 (엔터시 테스트 모드): ").strip()
    
    reporter = CashFocusedSlackReporter(webhook_url)
    
    print("\n작업 선택:")
    print("1. 캐시 카우 일일 리포트")
    print("2. 캐시 카우 주간 비교")
    print("3. 캐시 플레이어 분석 테스트")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            print("\n💰 캐시 카우 일일 리포트 전송 중...")
            success = reporter.send_cash_focused_daily_report()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '2':
            print("\n💰 캐시 카우 주간 비교 전송 중...")
            success = reporter.send_cash_weekly_comparison()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '3':
            print("\n🧪 캐시 플레이어 분석 테스트...")
            analyzer = CashPlayerAnalyzer()
            result = analyzer.analyze_cash_focused_daily()
            
            print(f"\n캐시 카우 스코어: {result['cash_cow_score']['total_score']}/100")
            print(f"등급: {result['cash_cow_score']['grade']}")
            print(f"평가: {result['cash_cow_score']['interpretation']}")
            
            print("\n주요 인사이트:")
            for insight in result['insights']['primary'][:3]:
                print(f"• {insight}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()