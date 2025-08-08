#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Slack Report Sender V2
개선된 슬랙 메시지 포맷 및 UI/UX
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
import base64
import io

# 차트 생성용
try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from matplotlib.patches import Rectangle
    import numpy as np
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSlackReportSender:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            logger.warning("Slack Webhook URL이 설정되지 않았습니다.")
        
        self.report_generator = ReportGenerator()
        
        # 차트 설정
        if CHART_AVAILABLE:
            plt.rcParams['font.family'] = ['DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            plt.style.use('seaborn-v0_8-darkgrid')
        
        # 이모지 맵핑
        self.emoji_map = {
            'up': '📈',
            'down': '📉',
            'stable': '➡️',
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
            'warning': '⚠️',
            'success': '✅',
            'error': '❌',
            'trophy': '🏆',
            'star': '⭐',
            'fire': '🔥',
            'rocket': '🚀',
            'chart': '📊',
            'calendar': '📅',
            'clock': '⏰',
            'target': '🎯',
            'bulb': '💡',
            'eye': '👀'
        }
    
    def send_daily_report(self, target_date: str = None, channel: str = None) -> bool:
        """개선된 일일 보고서 전송"""
        try:
            logger.info("Enhanced 일일 보고서 생성 중...")
            
            # 보고서 데이터 생성
            report_data = self.report_generator.generate_daily_report(
                target_date=target_date,
                format_type='slack'
            )
            
            # Slack 블록 구성
            blocks = self._create_daily_report_blocks(report_data)
            
            # 메시지 전송
            message = {
                'text': '📅 일일 포커 시장 분석 리포트',
                'blocks': blocks
            }
            
            if channel:
                message['channel'] = channel
            
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ Enhanced 일일 보고서 전송 완료")
            else:
                logger.error("❌ Enhanced 일일 보고서 전송 실패")
                
            return success
            
        except Exception as e:
            logger.error(f"일일 보고서 전송 중 오류: {e}")
            return False
    
    def _create_daily_report_blocks(self, report_data: Dict) -> List[Dict]:
        """일일 보고서 블록 생성"""
        blocks = []
        
        analysis_data = report_data['data']
        insights = report_data['insights']
        changes = analysis_data['changes']
        
        # 헤더 블록
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📅 일일 포커 시장 분석 리포트',
                'emoji': True
            }
        })
        
        # 기간 정보
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*분석 기간*\n{analysis_data['period']}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*생성 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 핵심 지표 섹션
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🎯 핵심 지표*'
            }
        })
        
        # 총 플레이어 변화
        total_change = changes['total_players']
        total_emoji = self._get_trend_emoji(total_change['change_pct'])
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*총 플레이어*\n{total_change['old']:,} → {total_change['new']:,}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화율*\n{total_emoji} {total_change['change_pct']:+.1f}% ({total_change['change']:+,}명)"
                }
            ]
        })
        
        # 평균 플레이어 변화
        avg_change = changes['avg_players']
        avg_emoji = self._get_trend_emoji(avg_change['change_pct'])
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*평균 플레이어*\n{avg_change['old']:,.0f} → {avg_change['new']:,.0f}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*변화율*\n{avg_emoji} {avg_change['change_pct']:+.1f}%"
                }
            ]
        })
        
        # 시장 집중도
        concentration = changes['market_concentration']
        conc_emoji = '🔴' if abs(concentration['change']) > 5 else '🟡' if abs(concentration['change']) > 2 else '🟢'
        
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*시장 집중도 (상위 3개)*\n{concentration['old']:.1f}% → {concentration['new']:.1f}%"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*집중도 변화*\n{conc_emoji} {concentration['change']:+.1f}%p"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 인사이트 섹션
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*💡 주요 인사이트*'
            }
        })
        
        # 인사이트 리스트
        insight_text = f"• {insights['overall_trend']}\n"
        insight_text += f"• {insights['market_concentration_trend']}\n"
        
        if insights.get('key_movers'):
            for mover in insights['key_movers']:
                insight_text += f"• {mover}\n"
        
        insight_text += f"• {insights['data_quality_assessment']}"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': insight_text
            }
        })
        
        # 상위 변동 사이트
        site_comparison = analysis_data.get('site_comparison', {})
        
        if site_comparison.get('top_gainers') or site_comparison.get('top_losers'):
            blocks.append({'type': 'divider'})
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*🏆 상위 변동 사이트*'
                }
            })
            
            # 상위 증가 사이트
            if site_comparison.get('top_gainers'):
                gainers_text = '*📈 최대 성장*\n'
                for i, site in enumerate(site_comparison['top_gainers'][:3], 1):
                    gainers_text += f"{i}. {site['site_name']}: +{site['change_pct']:.1f}%\n"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': gainers_text.strip()
                    }
                })
            
            # 상위 감소 사이트
            if site_comparison.get('top_losers'):
                losers_text = '*📉 최대 하락*\n'
                for i, site in enumerate(reversed(site_comparison['top_losers'][-3:]), 1):
                    losers_text += f"{i}. {site['site_name']}: {site['change_pct']:.1f}%\n"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': losers_text.strip()
                    }
                })
        
        # 데이터 품질 정보
        blocks.append({'type': 'divider'})
        
        yesterday_count = analysis_data['yesterday']['data_count']
        today_count = analysis_data['today']['data_count']
        
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"📊 데이터: 전일 {yesterday_count}개 | 오늘 {today_count}개 레코드"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"🤖 자동 생성 시스템"
                }
            ]
        })
        
        return blocks
    
    def send_weekly_report(self, target_week_start: str = None, channel: str = None) -> bool:
        """개선된 주간 보고서 전송"""
        try:
            logger.info("Enhanced 주간 보고서 생성 중...")
            
            report_data = self.report_generator.generate_weekly_report(
                target_week_start=target_week_start,
                format_type='slack'
            )
            
            blocks = self._create_weekly_report_blocks(report_data)
            
            message = {
                'text': '📊 주간 포커 시장 분석 리포트',
                'blocks': blocks
            }
            
            if channel:
                message['channel'] = channel
            
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ Enhanced 주간 보고서 전송 완료")
            else:
                logger.error("❌ Enhanced 주간 보고서 전송 실패")
                
            return success
            
        except Exception as e:
            logger.error(f"주간 보고서 전송 중 오류: {e}")
            return False
    
    def _create_weekly_report_blocks(self, report_data: Dict) -> List[Dict]:
        """주간 보고서 블록 생성"""
        blocks = []
        
        analysis_data = report_data['data']
        trends = report_data['trends']
        changes = analysis_data['changes']
        
        # 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📊 주간 포커 시장 분석 리포트',
                'emoji': True
            }
        })
        
        # 기간 정보 섹션
        blocks.append({
            'type': 'section',
            'fields': [
                {
                    'type': 'mrkdwn',
                    'text': f"*분석 기간*\n{analysis_data['period']}"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"*데이터 수집*\n지난주 {analysis_data['last_week']['summary']['unique_dates']}일 | 이번주 {analysis_data['this_week']['summary']['unique_dates']}일"
                }
            ]
        })
        
        blocks.append({'type': 'divider'})
        
        # 주요 성과 지표
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🏆 주간 핵심 성과*'
            }
        })
        
        # 성과 카드 스타일
        perf_fields = []
        
        # 총 플레이어
        total_change = changes['total_players']
        total_emoji = self._get_trend_emoji(total_change['change_pct'])
        perf_fields.append({
            'type': 'mrkdwn',
            'text': f"*총 플레이어*\n{total_emoji} {total_change['change_pct']:+.1f}%\n({total_change['change']:+,}명)"
        })
        
        # 일평균
        avg_change = changes['avg_players']
        avg_emoji = self._get_trend_emoji(avg_change['change_pct'])
        perf_fields.append({
            'type': 'mrkdwn',
            'text': f"*일평균*\n{avg_emoji} {avg_change['change_pct']:+.1f}%\n({avg_change['change']:+,.0f}명)"
        })
        
        # 캐시 플레이어
        cash_change = changes['total_cash_players']
        cash_emoji = self._get_trend_emoji(cash_change['change_pct'])
        perf_fields.append({
            'type': 'mrkdwn',
            'text': f"*캐시 게임*\n{cash_emoji} {cash_change['change_pct']:+.1f}%\n({cash_change['change']:+,}명)"
        })
        
        # 시장 집중도
        conc_change = changes['market_concentration']
        conc_emoji = '🔴' if abs(conc_change['change']) > 5 else '🟡' if abs(conc_change['change']) > 2 else '🟢'
        perf_fields.append({
            'type': 'mrkdwn',
            'text': f"*시장 집중도*\n{conc_emoji} {conc_change['change']:+.1f}%p\n(상위 3개)"
        })
        
        blocks.append({
            'type': 'section',
            'fields': perf_fields
        })
        
        blocks.append({'type': 'divider'})
        
        # 트렌드 분석
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*📈 주간 트렌드 분석*'
            }
        })
        
        trend_text = f"*성장 동향*: {trends['growth_trend']}\n\n"
        trend_text += f"*변동성*: {trends['volatility_assessment']}\n\n"
        trend_text += f"*시장 역학*: {trends['market_dynamics']}\n\n"
        trend_text += f"*데이터 품질*: {trends['data_completeness']}"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': trend_text
            }
        })
        
        # 주요 발견사항
        if trends.get('weekly_insights'):
            blocks.append({'type': 'divider'})
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*💎 주요 발견사항*'
                }
            })
            
            insights_text = ''
            for insight in trends['weekly_insights']:
                insights_text += f"• {insight}\n"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': insights_text.strip()
                }
            })
        
        # 주간 챔피언 & 주의 대상
        site_comparison = analysis_data.get('site_comparison', {})
        
        if site_comparison.get('top_gainers') or site_comparison.get('top_losers'):
            blocks.append({'type': 'divider'})
            
            champions_fields = []
            
            if site_comparison.get('top_gainers'):
                champion = site_comparison['top_gainers'][0]
                champions_fields.append({
                    'type': 'mrkdwn',
                    'text': f"*🏆 주간 챔피언*\n{champion['site_name']}\n+{champion['change_pct']:.1f}%"
                })
            
            if site_comparison.get('top_losers'):
                concern = site_comparison['top_losers'][-1]
                champions_fields.append({
                    'type': 'mrkdwn',
                    'text': f"*⚠️ 주의 대상*\n{concern['site_name']}\n{concern['change_pct']:.1f}%"
                })
            
            if champions_fields:
                blocks.append({
                    'type': 'section',
                    'fields': champions_fields
                })
        
        # Footer
        blocks.append({'type': 'divider'})
        
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"📊 지난주 {analysis_data['last_week']['data_count']}개 | 이번주 {analysis_data['this_week']['data_count']}개 레코드"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def send_monthly_report(self, target_month: str = None, channel: str = None) -> bool:
        """개선된 월간 보고서 전송"""
        try:
            logger.info("Enhanced 월간 보고서 생성 중...")
            
            report_data = self.report_generator.generate_monthly_report(
                target_month=target_month,
                format_type='slack'
            )
            
            blocks = self._create_monthly_report_blocks(report_data)
            
            message = {
                'text': '📈 월간 포커 시장 분석 리포트',
                'blocks': blocks
            }
            
            if channel:
                message['channel'] = channel
            
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ Enhanced 월간 보고서 전송 완료")
            else:
                logger.error("❌ Enhanced 월간 보고서 전송 실패")
                
            return success
            
        except Exception as e:
            logger.error(f"월간 보고서 전송 중 오류: {e}")
            return False
    
    def _create_monthly_report_blocks(self, report_data: Dict) -> List[Dict]:
        """월간 보고서 블록 생성"""
        blocks = []
        
        analysis_data = report_data['data']
        trends = report_data['trends']
        changes = analysis_data['changes']
        
        # 헤더
        blocks.append({
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📈 월간 포커 시장 분석 리포트',
                'emoji': True
            }
        })
        
        # Executive Summary 섹션
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*📅 {analysis_data['period']} 비교 분석*"
            }
        })
        
        blocks.append({'type': 'divider'})
        
        # 핵심 성과 대시보드
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🎯 월간 핵심 성과 대시보드*'
            }
        })
        
        # KPI 카드들
        kpi_fields = []
        
        # 월간 성장률
        total_change = changes['total_players']
        growth_indicator = self._get_performance_indicator(total_change['change_pct'])
        kpi_fields.append({
            'type': 'mrkdwn',
            'text': f"*월간 성장률*\n{growth_indicator}\n{total_change['change_pct']:+.1f}%"
        })
        
        # 일평균 변화
        avg_change = changes['avg_players']
        avg_indicator = self._get_performance_indicator(avg_change['change_pct'])
        kpi_fields.append({
            'type': 'mrkdwn',
            'text': f"*일평균 변화*\n{avg_indicator}\n{avg_change['change_pct']:+.1f}%"
        })
        
        # 캐시 게임 성과
        cash_change = changes['avg_cash_players']
        cash_indicator = self._get_performance_indicator(cash_change['change_pct'])
        kpi_fields.append({
            'type': 'mrkdwn',
            'text': f"*캐시 게임*\n{cash_indicator}\n{cash_change['change_pct']:+.1f}%"
        })
        
        # 시장 건전성
        conc_change = changes['market_concentration']
        health_indicator = '🟢 건전' if abs(conc_change['change']) < 3 else '🟡 보통' if abs(conc_change['change']) < 7 else '🔴 주의'
        kpi_fields.append({
            'type': 'mrkdwn',
            'text': f"*시장 건전성*\n{health_indicator}\n집중도 {conc_change['change']:+.1f}%p"
        })
        
        blocks.append({
            'type': 'section',
            'fields': kpi_fields
        })
        
        blocks.append({'type': 'divider'})
        
        # 전략적 인사이트
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*🔍 전략적 인사이트*'
            }
        })
        
        strategy_text = f"📊 *성과 평가*\n{trends['monthly_performance']}\n\n"
        strategy_text += f"🏢 *시장 성숙도*\n{trends['market_maturity']}\n\n"
        strategy_text += f"⚔️ *경쟁 환경*\n{trends['competitive_landscape']}\n\n"
        strategy_text += f"🌡️ *계절 요인*\n{trends['seasonal_effects']}"
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': strategy_text
            }
        })
        
        # 핵심 발견사항
        if trends.get('key_findings'):
            blocks.append({'type': 'divider'})
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*💡 핵심 발견사항*'
                }
            })
            
            findings_text = ''
            for i, finding in enumerate(trends['key_findings'], 1):
                findings_text += f"{i}. {finding}\n"
            
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': findings_text.strip()
                }
            })
        
        # MVP & 관심 대상
        site_comparison = analysis_data.get('site_comparison', {})
        
        if site_comparison.get('top_gainers') or site_comparison.get('top_losers'):
            blocks.append({'type': 'divider'})
            
            # 상위 5개 성장/하락 사이트 테이블
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*🏆 월간 성과 랭킹*'
                }
            })
            
            if site_comparison.get('top_gainers'):
                top_text = '*🌟 Top Performers*\n'
                for i, site in enumerate(site_comparison['top_gainers'][:5], 1):
                    medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else f'{i}.'
                    top_text += f"{medal} {site['site_name']}: +{site['change_pct']:.1f}%\n"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': top_text.strip()
                    }
                })
            
            if site_comparison.get('top_losers'):
                bottom_text = '*📉 Attention Required*\n'
                for i, site in enumerate(reversed(site_comparison['top_losers'][-5:]), 1):
                    bottom_text += f"{i}. {site['site_name']}: {site['change_pct']:.1f}%\n"
                
                blocks.append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': bottom_text.strip()
                    }
                })
        
        # 데이터 신뢰도
        blocks.append({'type': 'divider'})
        
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*📊 데이터 신뢰도*\n{trends['data_reliability']}"
            }
        })
        
        # Footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': f"📈 지난달 {analysis_data['last_month']['data_count']}개 | 이번달 {analysis_data['this_month']['data_count']}개 레코드"
                },
                {
                    'type': 'mrkdwn',
                    'text': f"🤖 월간 전략 리포트 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def _get_trend_emoji(self, change_pct: float) -> str:
        """변화율에 따른 이모지 반환"""
        if change_pct > 5:
            return '🚀'
        elif change_pct > 2:
            return '📈'
        elif change_pct > -2:
            return '➡️'
        elif change_pct > -5:
            return '📉'
        else:
            return '⬇️'
    
    def _get_performance_indicator(self, change_pct: float) -> str:
        """성과 지표 시각화"""
        if change_pct > 10:
            return '🔥 탁월'
        elif change_pct > 5:
            return '⭐ 우수'
        elif change_pct > 0:
            return '✅ 양호'
        elif change_pct > -5:
            return '⚠️ 주의'
        else:
            return '🔴 위험'
    
    def send_alert(self, alert_type: str, message: str, data: Dict = None) -> bool:
        """즉시 알림 전송"""
        try:
            blocks = []
            
            # 알림 타입별 아이콘과 색상
            alert_config = {
                'critical': {'emoji': '🚨', 'color': 'danger', 'title': '긴급 알림'},
                'warning': {'emoji': '⚠️', 'color': 'warning', 'title': '주의 알림'},
                'info': {'emoji': 'ℹ️', 'color': 'good', 'title': '정보 알림'},
                'success': {'emoji': '✅', 'color': 'good', 'title': '성공 알림'}
            }
            
            config = alert_config.get(alert_type, alert_config['info'])
            
            # 헤더
            blocks.append({
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f"{config['emoji']} {config['title']}",
                    'emoji': True
                }
            })
            
            # 메시지 본문
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': message
                }
            })
            
            # 추가 데이터가 있으면 표시
            if data:
                blocks.append({'type': 'divider'})
                
                fields = []
                for key, value in data.items():
                    fields.append({
                        'type': 'mrkdwn',
                        'text': f"*{key}*\n{value}"
                    })
                
                if fields:
                    blocks.append({
                        'type': 'section',
                        'fields': fields[:10]  # 최대 10개 필드
                    })
            
            # 타임스탬프
            blocks.append({
                'type': 'context',
                'elements': [
                    {
                        'type': 'mrkdwn',
                        'text': f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            })
            
            slack_message = {
                'text': f"{config['emoji']} {config['title']}: {message[:100]}",
                'blocks': blocks,
                'attachments': [
                    {
                        'color': config['color'],
                        'fallback': message
                    }
                ]
            }
            
            return self._send_to_slack(slack_message)
            
        except Exception as e:
            logger.error(f"알림 전송 중 오류: {e}")
            return False
    
    def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """실제 Slack 전송"""
        if not self.webhook_url:
            logger.error("Slack Webhook URL이 설정되지 않았습니다.")
            print("⚠️ Slack 전송을 건너뜁니다. (Webhook URL 없음)")
            
            # 디버그용 출력
            print("\n[디버그] 전송하려던 메시지:")
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
                logger.info("✅ Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ Slack 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Slack 전송 중 네트워크 오류: {e}")
            return False
    
    def test_message_formatting(self) -> None:
        """메시지 포맷팅 테스트"""
        print("\n🧪 Slack 메시지 포맷팅 테스트")
        print("=" * 60)
        
        # 테스트 데이터 생성
        test_data = {
            'data': {
                'period': '2025-08-06 vs 2025-08-07',
                'yesterday': {'data_count': 42},
                'today': {'data_count': 47},
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
                    'market_concentration': {
                        'old': 45.2,
                        'new': 47.8,
                        'change': 2.6,
                        'change_pct': 5.8
                    }
                },
                'site_comparison': {
                    'top_gainers': [
                        {'site_name': 'PokerStars', 'change_pct': 15.2},
                        {'site_name': 'GGPoker', 'change_pct': 12.5}
                    ],
                    'top_losers': [
                        {'site_name': '888poker', 'change_pct': -8.3}
                    ]
                }
            },
            'insights': {
                'overall_trend': '포커 시장이 전일 대비 6.7% 성장했습니다.',
                'market_concentration_trend': '시장 집중도가 소폭 상승했습니다.',
                'key_movers': ['PokerStars가 15.2% 급성장'],
                'data_quality_assessment': '데이터 품질이 양호합니다.'
            }
        }
        
        # 블록 생성 테스트
        blocks = self._create_daily_report_blocks(test_data)
        
        print("📋 생성된 블록 구조:")
        for i, block in enumerate(blocks, 1):
            print(f"\n블록 {i}: {block.get('type', 'unknown')}")
            if block.get('text'):
                text = block['text'].get('text', '')[:100]
                print(f"  내용: {text}...")
        
        print(f"\n✅ 총 {len(blocks)}개 블록 생성 완료")
        print("=" * 60)

def main():
    print("🚀 Enhanced Slack Report Sender V2")
    print("=" * 60)
    
    # Webhook URL 확인
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        webhook_url = input("Slack Webhook URL 입력 (엔터시 테스트 모드): ").strip()
    
    sender = EnhancedSlackReportSender(webhook_url)
    
    print("\n작업을 선택하세요:")
    print("1. 메시지 포맷팅 테스트")
    print("2. 일일 보고서 전송")
    print("3. 주간 보고서 전송")
    print("4. 월간 보고서 전송")
    print("5. 긴급 알림 테스트")
    print("6. 모든 보고서 전송")
    
    try:
        choice = input("\n선택 (1-6): ").strip()
        
        if choice == '1':
            sender.test_message_formatting()
            
        elif choice == '2':
            print("\n📅 Enhanced 일일 보고서 전송 중...")
            success = sender.send_daily_report()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '3':
            print("\n📊 Enhanced 주간 보고서 전송 중...")
            success = sender.send_weekly_report()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '4':
            print("\n📈 Enhanced 월간 보고서 전송 중...")
            success = sender.send_monthly_report()
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '5':
            print("\n🚨 알림 테스트...")
            
            # 다양한 알림 타입 테스트
            sender.send_alert(
                'critical',
                '포커 시장에서 비정상적인 활동이 감지되었습니다!',
                {'변화율': '+50%', '영향 사이트': 'PokerStars'}
            )
            
            sender.send_alert(
                'success',
                '일일 분석이 성공적으로 완료되었습니다.',
                {'처리 시간': '2.5초', '분석 사이트': '47개'}
            )
            
            print("✅ 알림 테스트 완료!")
            
        elif choice == '6':
            print("\n🎯 모든 보고서 전송 중...")
            
            results = {
                '일일': sender.send_daily_report(),
                '주간': sender.send_weekly_report(),
                '월간': sender.send_monthly_report()
            }
            
            print("\n📊 전송 결과:")
            for report_type, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {report_type} 보고서")
            
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()