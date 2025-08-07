#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Integrated Slack Reporter
GGNetwork 독점 상황에서 2-3위 경쟁 중심 최종 Slack 리포터
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
from competitive_analysis_reporter import CompetitiveAnalysisReporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalSlackReporter:
    """
    최종 통합 Slack 리포터
    - GGNetwork 트렌드 추적
    - 2-3위 경쟁 상세 분석
    - 시장 전체 동향
    """
    
    def __init__(self, webhook_url: str = None):
        # 직접 웹훅 URL 설정 (환경 변수 우회)
        if not webhook_url:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL') or "https://hooks.slack.com/services/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"
        self.webhook_url = webhook_url
        self.analyzer = CompetitiveAnalysisReporter()
        
    def generate_final_report(self, target_date: str = None) -> Dict:
        """최종 통합 리포트 생성"""
        # 경쟁 구도 분석 실행
        analysis = self.analyzer.analyze_competitive_landscape(target_date)
        
        # Slack 블록 생성
        blocks = self._create_final_blocks(analysis)
        
        return {
            'text': '📊 포커 시장 일일 분석 리포트',
            'blocks': blocks,
            'analysis': analysis
        }
    
    def _create_final_blocks(self, analysis: Dict) -> List[Dict]:
        """최종 Slack 블록 생성"""
        blocks = []
        
        # 1. 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📊 포커 시장 일일 분석 리포트',
                'emoji': True
            }
        })
        
        # 2. 기간 및 시간
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*📅 분석 기간:* {analysis['period']}\n*⏰ 생성 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 3. GGNetwork 독점 현황
        gg = analysis['ggnetwork_dominance']
        if gg.get('status') == 'dominant':
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*👑 GGNetwork 독점 현황*'
                }
            })
            
            trend_emoji = self._get_trend_emoji(gg['online_players']['change_pct'])
            
            blocks.append({
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f"*온라인 플레이어*\n{gg['online_players']['current']:,}명 ({trend_emoji} {gg['online_players']['change_pct']:+.1f}%)"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*캐시 플레이어*\n{gg['cash_players']['current']:,}명 ({gg['cash_players']['change_pct']:+.1f}%)"
                    }
                ]
            })
            
            blocks.append({
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f"*시장 점유율*\n온라인: {gg['market_dominance']['online_share']:.1f}% | 캐시: {gg['market_dominance']['cash_share']:.1f}%"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*주간 트렌드*\n{self._get_weekly_trend_text(gg['weekly_trend'])}"
                    }
                ]
            })
            
            blocks.append({'type': 'divider'})
        
        # 4. 온라인 2-3위 경쟁
        online = analysis['online_competition']
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🌐 온라인 플레이어 2-3위 경쟁*'
            }
        })
        
        # TOP 5 표시 (실제 경쟁 구도)
        if online.get('top5_today'):
            rank_text = ""
            for site_data in online['top5_today'][:5]:
                if site_data['rank'] == 1:
                    continue  # GGNetwork는 이미 표시했으므로 건너뜀
                
                medal = self._get_medal(site_data['rank'])
                trend = self._get_trend_emoji(site_data['change_pct'])
                rank_change = ""
                if site_data['rank_change'] > 0:
                    rank_change = f" ⬆️{site_data['rank_change']}"
                elif site_data['rank_change'] < 0:
                    rank_change = f" ⬇️{abs(site_data['rank_change'])}"
                
                rank_text += f"{medal} *{site_data['site_name']}*{rank_change}\n"
                rank_text += f"   {site_data['players']:,}명 ({trend} {site_data['change_pct']:+.1f}%)\n"
            
            if rank_text:
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': rank_text.strip()
                    }
                })
        
        # 2-3위 격차 분석
        if online.get('second_place_battle') and online.get('third_place_battle'):
            second = online['second_place_battle']
            third = online['third_place_battle']
            
            gap_text = f"*2-3위 격차:* {second['gap_to_third']:,}명\n"
            gap_text += f"*2위 안정성:* {self._translate_stability(second['stability'])}"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': gap_text
                }
            })
        
        blocks.append({'type': 'divider'})
        
        # 5. 캐시 2-3위 경쟁
        cash = analysis['cash_competition']
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💰 캐시 플레이어 2-3위 경쟁*'
            }
        })
        
        # 캐시 TOP 5
        if cash.get('top5_today'):
            cash_text = ""
            for site_data in cash['top5_today'][:5]:
                if site_data['rank'] == 1:
                    continue  # GGNetwork 건너뜀
                
                medal = self._get_medal(site_data['rank'])
                trend = self._get_trend_emoji(site_data['change_pct'])
                
                cash_text += f"{medal} *{site_data['site_name']}*\n"
                cash_text += f"   캐시: {site_data['cash_players']:,}명 ({trend} {site_data['change_pct']:+.1f}%)\n"
                cash_text += f"   캐시 비율: {site_data['cash_ratio']:.1f}%\n"
            
            if cash_text:
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': cash_text.strip()
                    }
                })
        
        # 캐시 2위 수익성 분석
        if cash.get('second_place_battle'):
            second = cash['second_place_battle']
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*캐시 2위 수익 잠재력:* {self._translate_revenue_potential(second['revenue_potential'])}"
                }
            })
        
        blocks.append({'type': 'divider'})
        
        # 6. 주요 도전자
        challengers = analysis.get('challenger_analysis', {})
        if challengers.get('fastest_growing') or challengers.get('most_threatening'):
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*🔥 주목할 도전자*'
                }
            })
            
            challenger_text = ""
            if challengers.get('fastest_growing'):
                fastest = challengers['fastest_growing']
                if fastest['online_growth'] > 0:
                    challenger_text += f"*가장 빠른 성장:* {fastest['site_name']} (+{fastest['online_growth']:.1f}%)\n"
            
            if challengers.get('most_threatening'):
                threat = challengers['most_threatening']
                challenger_text += f"*가장 위협적:* {threat['site_name']} ({threat['online_players']:,}명)\n"
            
            if challenger_text:
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': challenger_text.strip()
                    }
                })
            
            blocks.append({'type': 'divider'})
        
        # 7. 시장 역학
        dynamics = analysis.get('market_dynamics', {})
        if dynamics:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*📈 시장 구조*'
                }
            })
            
            structure_text = f"*시장 형태:* {self._translate_market_structure(dynamics.get('market_structure', ''))}\n"
            structure_text += f"*경쟁 수준:* {self._translate_competition_level(dynamics.get('competition_level', ''))}"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': structure_text
                }
            })
        
        # 8. 핵심 인사이트
        if analysis.get('insights'):
            blocks.append({'type': 'divider'})
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*💡 핵심 인사이트*'
                }
            })
            
            # 이모지를 제거한 인사이트
            clean_insights = []
            for insight in analysis['insights'][:6]:
                # 이모지를 제거하고 텍스트만 추출
                clean_insight = insight
                if len(insight) > 2 and insight[1] == ' ':
                    clean_insight = insight[2:]  # 이모지 제거
                clean_insights.append(f"• {clean_insight}")
            
            insights_text = "\n".join(clean_insights)
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': insights_text
                }
            })
        
        # 9. Footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"📊 Daily Analysis | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} | 🎯 Focus: 2nd-3rd Competition"
                }
            ]
        })
        
        return blocks
    
    def _get_medal(self, rank: int) -> str:
        """순위별 메달"""
        medals = {1: '🥇', 2: '🥈', 3: '🥉', 4: '4️⃣', 5: '5️⃣'}
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
    
    def _get_weekly_trend_text(self, trend: str) -> str:
        """주간 트렌드 텍스트"""
        trends = {
            'growing': '📈 상승세',
            'stable': '➡️ 안정세',
            'declining': '📉 하락세'
        }
        return trends.get(trend, trend)
    
    def _translate_stability(self, stability: str) -> str:
        """안정성 번역"""
        translations = {
            'stable': '✅ 안정적',
            'volatile': '⚠️ 불안정'
        }
        return translations.get(stability, stability)
    
    def _translate_revenue_potential(self, potential: str) -> str:
        """수익 잠재력 번역"""
        translations = {
            'high': '💎 높음',
            'medium': '⭐ 중간',
            'low': '📊 낮음'
        }
        return translations.get(potential, potential)
    
    def _translate_market_structure(self, structure: str) -> str:
        """시장 구조 번역"""
        translations = {
            'monopolistic': '독점 체제',
            'dominant_leader': '1강 체제',
            'competitive': '경쟁 체제'
        }
        return translations.get(structure, structure)
    
    def _translate_competition_level(self, level: str) -> str:
        """경쟁 수준 번역"""
        translations = {
            'intense': '🔥 치열',
            'moderate': '⚖️ 보통',
            'low': '💤 낮음'
        }
        return translations.get(level, level)
    
    def send_to_slack(self, message: Dict = None) -> bool:
        """Slack 전송"""
        if not message:
            message = self.generate_final_report()
        
        if not self.webhook_url:
            logger.error("Slack Webhook URL not configured")
            print("\n[Test Mode] Slack message preview:")
            # JSON 출력 시 ensure_ascii=True로 변경
            preview_json = json.dumps(message, indent=2, ensure_ascii=True)[:1000]
            print(preview_json)
            return False
        
        try:
            # 블록만 전송 (text 필드 포함)
            slack_message = {
                'text': message['text'],
                'blocks': message['blocks']
            }
            
            response = requests.post(
                self.webhook_url,
                json=slack_message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ 리포트 전송 성공")
                return True
            else:
                logger.error(f"❌ 전송 실패: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"전송 중 오류: {e}")
            return False

def preview_and_send():
    """리포트 미리보기 및 전송"""
    print("\n" + "="*80)
    print("Final Integrated Slack Report")
    print("="*80)
    
    reporter = FinalSlackReporter()
    report = reporter.generate_final_report()
    
    # 분석 결과 요약
    analysis = report['analysis']
    
    print(f"\nAnalysis Period: {analysis['period']}")
    
    # GGNetwork 현황
    gg = analysis.get('ggnetwork_dominance', {})
    if gg.get('status') == 'dominant':
        print(f"\n[GGNetwork Dominance]")
        print(f"  Online: {gg['online_players']['current']:,} ({gg['online_players']['change_pct']:+.1f}%)")
        print(f"  Cash: {gg['cash_players']['current']:,} ({gg['cash_players']['change_pct']:+.1f}%)")
        print(f"  Market Share: Online {gg['market_dominance']['online_share']:.1f}% | Cash {gg['market_dominance']['cash_share']:.1f}%")
    
    # 2-3위 경쟁
    online = analysis.get('online_competition', {})
    if online.get('second_place_battle'):
        second = online['second_place_battle']
        print(f"\n[Online] 2nd: {second['current_holder']} ({second['players']:,})")
    
    if online.get('third_place_battle'):
        third = online['third_place_battle']
        print(f"[Online] 3rd: {third['current_holder']} ({third['players']:,})")
    
    cash = analysis.get('cash_competition', {})
    if cash.get('second_place_battle'):
        second = cash['second_place_battle']
        print(f"\n[Cash] 2nd: {second['current_holder']} ({second['cash_players']:,})")
    
    if cash.get('third_place_battle'):
        third = cash['third_place_battle']
        print(f"[Cash] 3rd: {third['current_holder']} ({third['cash_players']:,})")
    
    print(f"\nSlack blocks generated: {len(report['blocks'])}")
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    preview_file = f"final_slack_report_{timestamp}.json"
    
    try:
        with open(preview_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved: {preview_file}")
    except Exception as e:
        print(f"Error saving report: {e}")
        # ASCII 모드로 재시도
        with open(preview_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=True)
        print(f"Report saved (ASCII mode): {preview_file}")
    
    # Slack 전송 여부 확인
    print("\n" + "="*80)
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        print("Slack Webhook URL configured")
        choice = input("\nSend to Slack? (y/n): ").strip().lower()
        if choice == 'y':
            success = reporter.send_to_slack(report)
            print("Sent successfully!" if success else "Failed to send")
        else:
            print("Send cancelled")
    else:
        print("Warning: SLACK_WEBHOOK_URL not configured")
        print("Running in test mode.")
        reporter.send_to_slack(report)
    
    return report

if __name__ == "__main__":
    preview_and_send()