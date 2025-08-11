#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플랫폼 Slack 리포터
- REPORT_TYPE에 따른 동적 리포트 생성
- 일간/주간/월간 구분된 메시지
- 자동화된 Slack 전송
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

# 자동화된 분석기 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from automated_platform_analyzer import AutomatedPlatformAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformSlackReporter:
    """플랫폼 분석 Slack 리포터"""
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.report_type = os.getenv('REPORT_TYPE', 'daily')
        self.data_start = os.getenv('DATA_PERIOD_START', '')
        self.data_end = os.getenv('DATA_PERIOD_END', '')
        
        # 분석기 초기화
        self.analyzer = AutomatedPlatformAnalyzer()
        
        logger.info(f"Slack 리포터 초기화 - 리포트 타입: {self.report_type}")
    
    def create_slack_blocks(self, report: Dict) -> List[Dict]:
        """Slack 메시지 블록 생성"""
        blocks = []
        
        # 1. 헤더 (리포트 타입에 따라 동적)
        header_text = {
            'daily': 'Platform Daily Analysis Report',
            'weekly': 'Platform Weekly Analysis Report',
            'monthly': 'Platform Monthly Analysis Report'
        }.get(self.report_type, 'Platform Analysis Report')
        
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': header_text,
                'emoji': True
            }
        })
        
        # 2. 기간 및 요약
        period_text = f"{self.data_start} ~ {self.data_end}" if self.data_start and self.data_end else "최근 데이터"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"""*📅 분석 기간:* {period_text}
*⏰ 생성 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M')}
*🎮 전체 온라인:* {report['summary']['total_online_players']:,}명
*💰 전체 캐시:* {report['summary']['total_cash_players']:,}명"""
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 3. 시장 리더 현황
        competition = report.get('competition_analysis', {})
        leader = competition.get('leader', {})
        
        if leader:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*👑 시장 리더*'
                }
            })
            
            growth_emoji = self._get_trend_emoji(leader.get('growth', 0))
            
            blocks.append({
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f"*플랫폼:* {leader['name']}"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*점유율:* {leader['share']:.1f}%"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*온라인:* {leader['players']:,}명"
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f"*성장률:* {growth_emoji} {leader['growth']:+.1f}%"
                    }
                ]
            })
            
            blocks.append({'type': 'divider'})
        
        # 4. TOP 10 플랫폼 랭킹
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🏆 TOP 10 플랫폼*'
            }
        })
        
        rank_text = ""
        for i, platform in enumerate(report['top_platforms'][:10], 1):
            medal = self._get_medal(i)
            trend = self._get_trend_emoji(platform['growth_rate'])
            
            # 리포트 타입에 따른 표시 조정
            if self.report_type == 'daily':
                # 일간: 현재 플레이어 수와 피크 표시
                rank_text += f"{medal} *{platform['platform_name']}*\n"
                rank_text += f"   온라인: {platform['online_players']:,} | 피크: {platform['peak_24h']:,} | {trend} {platform['growth_rate']:+.1f}%\n"
            elif self.report_type == 'weekly':
                # 주간: 7일 평균 포함
                rank_text += f"{medal} *{platform['platform_name']}*\n"
                rank_text += f"   온라인: {platform['online_players']:,} | 7일평균: {platform['seven_day_avg']:,} | {trend} {platform['growth_rate']:+.1f}%\n"
            else:  # monthly
                # 월간: 시장 점유율 강조
                rank_text += f"{medal} *{platform['platform_name']}* ({platform['market_share']:.1f}%)\n"
                rank_text += f"   온라인: {platform['online_players']:,} | 캐시: {platform['cash_players']:,} | {trend} {platform['growth_rate']:+.1f}%\n"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': rank_text.strip()
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 5. 경쟁 구도 분석
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*⚔️ 경쟁 구도*'
            }
        })
        
        competition_text = f"""*시장 구조:* {competition.get('competition_intensity', 'N/A')}
*HHI 지수:* {competition.get('market_concentration', 0):.0f}
*2-3위 격차:* {competition.get('gap_2_3', 0):,}명 ({competition.get('gap_2_3_percentage', 0):.1f}%)"""
        
        # 2-3위 플랫폼 정보
        if competition.get('second'):
            competition_text += f"\n*2위:* {competition['second']['name']} ({competition['second']['share']:.1f}%)"
        if competition.get('third'):
            competition_text += f"\n*3위:* {competition['third']['name']} ({competition['third']['share']:.1f}%)"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': competition_text
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 6. 핵심 인사이트
        insights = report.get('insights', [])
        if insights:
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*💡 핵심 인사이트*'
                }
            })
            
            insights_text = "\n".join(insights[:6])  # 최대 6개까지
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': insights_text
                }
            })
        
        # 7. Footer
        footer_text = {
            'daily': '📊 Daily Platform Analysis',
            'weekly': '📊 Weekly Platform Analysis',
            'monthly': '📊 Monthly Platform Analysis'
        }.get(self.report_type, '📊 Platform Analysis')
        
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"{footer_text} | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} | 🎯 Automated Report"
                }
            ]
        })
        
        return blocks
    
    def _get_medal(self, rank: int) -> str:
        """순위별 메달 이모지"""
        medals = {
            1: '🥇', 2: '🥈', 3: '🥉', 
            4: '4️⃣', 5: '5️⃣', 6: '6️⃣',
            7: '7️⃣', 8: '8️⃣', 9: '9️⃣', 10: '🔟'
        }
        return medals.get(rank, f'{rank}.')
    
    def _get_trend_emoji(self, change_pct: float) -> str:
        """변화율에 따른 이모지"""
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
    
    def send_to_slack(self, blocks: List[Dict]) -> bool:
        """Slack으로 메시지 전송"""
        if not self.webhook_url:
            logger.warning("Slack Webhook URL이 설정되지 않았습니다")
            # 테스트 모드: 블록 내용 출력
            print("\n[TEST MODE] Slack 메시지 미리보기:")
            print(json.dumps({'blocks': blocks[:3]}, indent=2, ensure_ascii=False))  # 처음 3개 블록만
            return False
        
        try:
            message = {
                'text': f'플랫폼 {self.report_type} 분석 리포트',
                'blocks': blocks
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ Slack 전송 실패: {response.status_code}")
                logger.error(f"응답: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 전송 중 오류: {e}")
            return False
    
    def run_report(self) -> Dict:
        """리포트 실행 메인 함수"""
        logger.info(f"=== 플랫폼 {self.report_type} 리포트 시작 ===")
        
        try:
            # 1. 분석 실행
            report = self.analyzer.generate_report()
            
            # 2. Slack 블록 생성
            blocks = self.create_slack_blocks(report)
            
            # 3. Slack 전송
            success = self.send_to_slack(blocks)
            
            # 4. 결과 반환
            result = {
                'success': success,
                'report_type': self.report_type,
                'timestamp': datetime.now().isoformat(),
                'summary': report['summary'],
                'platforms_analyzed': len(report['top_platforms']),
                'message': 'Platform analysis completed successfully' if success else 'Platform analysis completed (Slack send failed)'
            }
            
            logger.info(f"=== 플랫폼 {self.report_type} 리포트 완료 ===")
            return result
            
        except Exception as e:
            logger.error(f"리포트 실행 중 오류: {e}")
            return {
                'success': False,
                'report_type': self.report_type,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'message': f'Platform analysis failed: {e}'
            }

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("Platform Slack Reporter")
    print("=" * 80)
    
    reporter = PlatformSlackReporter()
    result = reporter.run_report()
    
    # 결과 출력
    if result['success']:
        print(f"[SUCCESS] Report sent successfully")
    else:
        print(f"[FAILED] Report send failed")
    
    print(f"Report Type: {result['report_type']}")
    print(f"Platforms Analyzed: {result.get('platforms_analyzed', 0)}")
    
    if 'summary' in result:
        print(f"Total Online Players: {result['summary']['total_online_players']:,}")
        print(f"Market Leader: {result['summary']['market_leader']} ({result['summary']['market_leader_share']:.1f}%)")
    
    return 0 if result['success'] else 1

if __name__ == "__main__":
    sys.exit(main())