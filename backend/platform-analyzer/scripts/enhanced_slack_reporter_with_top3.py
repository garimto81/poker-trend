#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Slack Reporter with TOP 3 Sites
온라인/캐시 TOP 3 사이트 포함 Slack 리포터
"""

import os
import sys
import json
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enhanced_dual_metric_analyzer import EnhancedDualMetricAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSlackReporter:
    """
    강화된 Slack 리포터
    - 온라인 TOP 3
    - 캐시 TOP 3
    - 전날 대비 변화
    - 트렌드 분석
    """
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.analyzer = EnhancedDualMetricAnalyzer()
        
    def generate_enhanced_report(self, target_date: str = None) -> Dict:
        """강화된 리포트 생성"""
        # 분석 실행
        analysis = self.analyzer.analyze_enhanced_daily(target_date)
        
        # Slack 블록 생성
        blocks = self._create_enhanced_blocks(analysis)
        
        return {
            'text': '📊 포커 시장 종합 분석 리포트 (TOP 3 포함)',
            'blocks': blocks,
            'analysis': analysis
        }
    
    def _create_enhanced_blocks(self, analysis: Dict) -> List[Dict]:
        """강화된 Slack 블록 생성"""
        blocks = []
        
        # 1. 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📊 포커 시장 종합 분석 리포트',
                'emoji': True
            }
        })
        
        # 2. 기간 정보
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*분석 기간:* {analysis['period']}\n*분석 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 3. 종합 스코어
        score = analysis['comprehensive_score']
        score_emoji = self._get_grade_emoji(score['grade'])
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*종합 평가: {score['score']}/{score['max_score']}점 {score_emoji}*\n{score['interpretation']}"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 4. 시장 전체 변화
        market = analysis['daily_changes']['market_changes']
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📈 시장 전체 변화*'
            }
        })
        
        # 온라인 전체
        online_emoji = self._get_trend_emoji(market['total_online']['change_pct'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*🌐 총 온라인 플레이어*\n{market['total_online']['yesterday']:,} → {market['total_online']['today']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화*\n{online_emoji} {market['total_online']['change_pct']:+.1f}% ({market['total_online']['change']:+,}명)"
                }
            ]
        })
        
        # 캐시 전체
        cash_emoji = self._get_trend_emoji(market['total_cash']['change_pct'])
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*💰 총 캐시 플레이어*\n{market['total_cash']['yesterday']:,} → {market['total_cash']['today']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화*\n{cash_emoji} {market['total_cash']['change_pct']:+.1f}% ({market['total_cash']['change']:+,}명)"
                }
            ]
        })
        
        # 캐시 비율
        cash_ratio = analysis['daily_changes']['cash_ratio']
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*💵 캐시 비율*\n{cash_ratio['today']:.1f}% ({cash_ratio['change']:+.1f}%p)"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*활성 사이트*\n{analysis['daily_changes']['active_sites']['today']}개"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 5. 온라인 TOP 3
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🌐 온라인 플레이어 TOP 3*'
            }
        })
        
        if analysis['top_sites']['online_top3']:
            for site in analysis['top_sites']['online_top3']:
                medal = self._get_medal(site['rank'])
                trend = self._get_trend_emoji(site['change_pct'])
                
                rank_change_text = ""
                if site['rank_change'] > 0:
                    rank_change_text = f" ⬆️{site['rank_change']}"
                elif site['rank_change'] < 0:
                    rank_change_text = f" ⬇️{abs(site['rank_change'])}"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"{medal} *{site['site_name']}*{rank_change_text}\n"
                                f"오늘: {site['players_today']:,}명 | 어제: {site['players_yesterday']:,}명\n"
                                f"변화: {trend} {site['change_pct']:+.1f}% ({site['change']:+,}명)"
                    }
                })
        else:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '데이터 없음'
                }
            })
        
        blocks.append({'type': 'divider'})
        
        # 6. 캐시 TOP 3
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💰 캐시 플레이어 TOP 3*'
            }
        })
        
        if analysis['top_sites']['cash_top3']:
            for site in analysis['top_sites']['cash_top3']:
                medal = self._get_medal(site['rank'])
                trend = self._get_trend_emoji(site['change_pct'])
                
                rank_change_text = ""
                if site['rank_change'] > 0:
                    rank_change_text = f" ⬆️{site['rank_change']}"
                elif site['rank_change'] < 0:
                    rank_change_text = f" ⬇️{abs(site['rank_change'])}"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"{medal} *{site['site_name']}*{rank_change_text}\n"
                                f"오늘: {site['cash_today']:,}명 | 어제: {site['cash_yesterday']:,}명\n"
                                f"변화: {trend} {site['change_pct']:+.1f}% ({site['change']:+,}명)"
                    }
                })
        else:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '데이터 없음'
                }
            })
        
        blocks.append({'type': 'divider'})
        
        # 7. 트렌드 분석
        trend = analysis['trend_analysis']
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📊 트렌드 분석*'
            }
        })
        
        trend_emoji = self._get_trend_direction_emoji(trend['trend_direction'])
        momentum_emoji = self._get_momentum_emoji(trend['momentum'])
        
        trend_text = f"*방향:* {trend_emoji} {trend['trend_direction']}\n"
        trend_text += f"*모멘텀:* {momentum_emoji} {trend['momentum']}\n"
        
        if trend['weekly_growth']:
            trend_text += f"*주간 성장:* 온라인 {trend['weekly_growth']['online']:.1f}% | 캐시 {trend['weekly_growth']['cash']:.1f}%\n"
        
        if trend['volatility']:
            trend_text += f"*변동성:* 온라인 {trend['volatility']['online']:.1f}% | 캐시 {trend['volatility']['cash']:.1f}%"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': trend_text
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 8. 주요 인사이트
        if analysis['insights']:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*💡 주요 인사이트*'
                }
            })
            
            insights_text = ""
            for insight in analysis['insights'][:8]:
                insights_text += f"• {insight}\n"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': insights_text.strip()
                }
            })
        
        # 9. Footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"📊 Enhanced Analysis | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def _get_medal(self, rank: int) -> str:
        """순위별 메달"""
        medals = {1: '🥇', 2: '🥈', 3: '🥉'}
        return medals.get(rank, f'{rank}.')
    
    def _get_trend_emoji(self, change_pct: float) -> str:
        """변화율 이모지"""
        if change_pct >= 10:
            return '🚀'
        elif change_pct >= 5:
            return '📈'
        elif change_pct >= -5:
            return '➡️'
        elif change_pct >= -10:
            return '📉'
        else:
            return '⬇️'
    
    def _get_grade_emoji(self, grade: str) -> str:
        """등급 이모지"""
        grades = {
            'S': '🏆',
            'A': '🥇',
            'B': '🥈',
            'C': '🥉',
            'D': '⚠️'
        }
        return grades.get(grade, '❓')
    
    def _get_trend_direction_emoji(self, direction: str) -> str:
        """트렌드 방향 이모지"""
        directions = {
            'uptrend': '📈',
            'downtrend': '📉',
            'mixed': '↔️',
            'insufficient_data': '❓'
        }
        return directions.get(direction, '')
    
    def _get_momentum_emoji(self, momentum: str) -> str:
        """모멘텀 이모지"""
        momentums = {
            'strong_bullish': '🔥',
            'bullish': '💪',
            'neutral': '⚖️',
            'bearish': '💔',
            'strong_bearish': '❄️'
        }
        return momentums.get(momentum, '')
    
    def send_to_slack(self, message: Dict) -> bool:
        """Slack 전송"""
        if not self.webhook_url:
            logger.error("Slack Webhook URL이 설정되지 않았습니다.")
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ 리포트 전송 성공")
                return True
            else:
                logger.error(f"❌ 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"전송 중 오류: {e}")
            return False

def preview_enhanced_report():
    """강화된 리포트 미리보기"""
    print("\n" + "="*80)
    print("📊 강화된 Slack 리포트 미리보기")
    print("="*80)
    
    reporter = EnhancedSlackReporter()
    report = reporter.generate_enhanced_report()
    
    # 분석 결과 출력
    analysis = report['analysis']
    
    print(f"\n📅 분석 기간: {analysis['period']}")
    
    # 종합 점수
    score = analysis['comprehensive_score']
    print(f"\n🏆 종합 평가: {score['score']}/{score['max_score']}점 ({score['grade']}등급)")
    print(f"   {score['interpretation']}")
    
    # 시장 전체
    market = analysis['daily_changes']['market_changes']
    print(f"\n📈 시장 전체 변화:")
    print(f"  온라인: {market['total_online']['yesterday']:,} → {market['total_online']['today']:,} ({market['total_online']['change_pct']:+.1f}%)")
    print(f"  캐시: {market['total_cash']['yesterday']:,} → {market['total_cash']['today']:,} ({market['total_cash']['change_pct']:+.1f}%)")
    
    # 온라인 TOP 3
    print(f"\n🌐 온라인 플레이어 TOP 3:")
    if analysis['top_sites']['online_top3']:
        for site in analysis['top_sites']['online_top3']:
            print(f"  {site['rank']}. {site['site_name']}: {site['players_today']:,}명 ({site['change_pct']:+.1f}%)")
    else:
        print("  데이터 없음")
    
    # 캐시 TOP 3
    print(f"\n💰 캐시 플레이어 TOP 3:")
    if analysis['top_sites']['cash_top3']:
        for site in analysis['top_sites']['cash_top3']:
            print(f"  {site['rank']}. {site['site_name']}: {site['cash_today']:,}명 ({site['change_pct']:+.1f}%)")
    else:
        print("  데이터 없음")
    
    # 트렌드
    trend = analysis['trend_analysis']
    print(f"\n📊 트렌드 분석:")
    print(f"  방향: {trend['trend_direction']}")
    print(f"  모멘텀: {trend['momentum']}")
    if trend['weekly_growth']:
        print(f"  주간 성장: 온라인 {trend['weekly_growth']['online']:.1f}% | 캐시 {trend['weekly_growth']['cash']:.1f}%")
    
    # 인사이트
    print(f"\n💡 주요 인사이트:")
    for insight in analysis['insights'][:5]:
        print(f"  • {insight}")
    
    # Slack 블록 수
    print(f"\n📋 Slack 블록: {len(report['blocks'])}개 생성")
    
    # JSON 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    preview_file = f"enhanced_slack_preview_{timestamp}.json"
    
    with open(preview_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 미리보기 저장: {preview_file}")
    
    return report

if __name__ == "__main__":
    preview_enhanced_report()