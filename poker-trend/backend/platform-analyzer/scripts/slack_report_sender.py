#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack Report Sender
다기간 분석 결과를 Slack으로 전송하는 시스템
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackReportSender:
    def __init__(self, webhook_url: str = None):
        # Slack Webhook URL 설정
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            logger.warning("Slack Webhook URL이 설정되지 않았습니다.")
        
        self.report_generator = ReportGenerator()
        
        # Slack 메시지 기본 설정
        self.default_config = {
            'username': '포커 시장 분석봇',
            'icon_emoji': ':chart_with_upwards_trend:',
            'channel': '#poker-analytics'  # 필요시 변경
        }
    
    def send_daily_report(self, target_date: str = None, channel: str = None) -> bool:
        """일일 보고서를 Slack으로 전송"""
        try:
            logger.info("일일 보고서 Slack 전송 시작...")
            
            # 보고서 생성
            report_data = self.report_generator.generate_daily_report(
                target_date=target_date, 
                format_type='slack'
            )
            
            # Slack 메시지 구성
            message = {
                'text': '📅 일일 포커 시장 분석 리포트가 도착했습니다!',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': report_data['formatted_report']
                        }
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"🤖 자동 생성 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # 채널 설정
            if channel:
                message['channel'] = channel
            
            # 전송
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ 일일 보고서 Slack 전송 완료")
                return True
            else:
                logger.error("❌ 일일 보고서 Slack 전송 실패")
                return False
                
        except Exception as e:
            logger.error(f"일일 보고서 전송 중 오류: {e}")
            return False
    
    def send_weekly_report(self, target_week_start: str = None, channel: str = None) -> bool:
        """주간 보고서를 Slack으로 전송"""
        try:
            logger.info("주간 보고서 Slack 전송 시작...")
            
            # 보고서 생성
            report_data = self.report_generator.generate_weekly_report(
                target_week_start=target_week_start,
                format_type='slack'
            )
            
            # Slack 메시지 구성 (주간은 더 상세하게)
            message = {
                'text': '📊 주간 포커 시장 분석 리포트',
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': '📊 주간 포커 시장 분석 리포트'
                        }
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': report_data['formatted_report']
                        }
                    },
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"🤖 주간 자동 분석 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # 채널 설정
            if channel:
                message['channel'] = channel
            
            # 전송
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ 주간 보고서 Slack 전송 완료")
                return True
            else:
                logger.error("❌ 주간 보고서 Slack 전송 실패")
                return False
                
        except Exception as e:
            logger.error(f"주간 보고서 전송 중 오류: {e}")
            return False
    
    def send_monthly_report(self, target_month: str = None, channel: str = None) -> bool:
        """월간 보고서를 Slack으로 전송"""
        try:
            logger.info("월간 보고서 Slack 전송 시작...")
            
            # 보고서 생성
            report_data = self.report_generator.generate_monthly_report(
                target_month=target_month,
                format_type='slack'
            )
            
            # Slack 메시지 구성 (월간은 가장 상세하게)
            message = {
                'text': '📈 월간 포커 시장 분석 리포트',
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': '📈 월간 포커 시장 분석 리포트'
                        }
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': report_data['formatted_report']
                        }
                    },
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': '*📊 상세 데이터가 필요하시면 팀에 문의해주세요.*'
                        }
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"🤖 월간 전략 리포트 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # 채널 설정
            if channel:
                message['channel'] = channel
            
            # 전송
            success = self._send_to_slack(message)
            
            if success:
                logger.info("✅ 월간 보고서 Slack 전송 완료")
                return True
            else:
                logger.error("❌ 월간 보고서 Slack 전송 실패")
                return False
                
        except Exception as e:
            logger.error(f"월간 보고서 전송 중 오류: {e}")
            return False
    
    def send_custom_message(self, message: str, channel: str = None, title: str = None) -> bool:
        """커스텀 메시지 전송"""
        try:
            slack_message = {
                'text': title or '포커 시장 분석 알림',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': message
                        }
                    }
                ]
            }
            
            if channel:
                slack_message['channel'] = channel
            
            return self._send_to_slack(slack_message)
            
        except Exception as e:
            logger.error(f"커스텀 메시지 전송 중 오류: {e}")
            return False
    
    def send_error_notification(self, error_message: str, context: str = None) -> bool:
        """에러 알림 전송"""
        try:
            message = {
                'text': '🚨 포커 분석 시스템 오류 발생',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"🚨 *포커 분석 시스템 오류*\\n\\n*오류 내용:*\\n```{error_message}```"
                        }
                    }
                ]
            }
            
            if context:
                message['blocks'].append({
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*발생 컨텍스트:*\\n{context}"
                    }
                })
            
            message['blocks'].append({
                'type': 'context',
                'elements': [
                    {
                        'type': 'mrkdwn',
                        'text': f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            })
            
            return self._send_to_slack(message)
            
        except Exception as e:
            logger.error(f"에러 알림 전송 중 오류: {e}")
            return False
    
    def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """실제 Slack 전송 로직"""
        if not self.webhook_url:
            logger.error("Slack Webhook URL이 설정되지 않았습니다.")
            print("⚠️  Slack 전송을 건너뜁니다. (Webhook URL 없음)")
            return False
        
        try:
            # 기본 설정 적용
            final_message = {**self.default_config, **message}
            
            # HTTP POST 요청
            response = requests.post(
                self.webhook_url,
                json=final_message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"Slack 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Slack 전송 중 네트워크 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"Slack 전송 중 예기치 못한 오류: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Slack 연결 테스트"""
        test_message = {
            'text': '🧪 포커 분석 시스템 연결 테스트',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '🧪 *연결 테스트*\\n\\n포커 분석 시스템이 정상적으로 작동하고 있습니다!'
                    }
                },
                {
                    'type': 'context',
                    'elements': [
                        {
                            'type': 'mrkdwn',
                            'text': f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
        
        success = self._send_to_slack(test_message)
        if success:
            logger.info("✅ Slack 연결 테스트 성공")
            print("✅ Slack 연결이 정상적으로 작동합니다!")
        else:
            logger.error("❌ Slack 연결 테스트 실패")
            print("❌ Slack 연결에 문제가 있습니다.")
        
        return success
    
    def schedule_reports(self, schedule_config: Dict[str, Any]) -> Dict[str, bool]:
        """스케줄에 따른 보고서 전송"""
        results = {}
        
        # 일일 보고서 (매일)
        if schedule_config.get('daily', {}).get('enabled', False):
            daily_channel = schedule_config['daily'].get('channel')
            results['daily'] = self.send_daily_report(channel=daily_channel)
        
        # 주간 보고서 (월요일)
        if schedule_config.get('weekly', {}).get('enabled', False):
            if datetime.now().weekday() == 0:  # 월요일
                weekly_channel = schedule_config['weekly'].get('channel')
                results['weekly'] = self.send_weekly_report(channel=weekly_channel)
        
        # 월간 보고서 (매월 1일)
        if schedule_config.get('monthly', {}).get('enabled', False):
            if datetime.now().day == 1:  # 매월 1일
                monthly_channel = schedule_config['monthly'].get('channel')
                results['monthly'] = self.send_monthly_report(channel=monthly_channel)
        
        return results

def main():
    print("🚀 Slack 보고서 전송 시스템")
    print("=" * 50)
    
    # Webhook URL 확인
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️  SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        webhook_url = input("Slack Webhook URL을 입력하세요 (또는 엔터로 건너뛰기): ").strip()
    
    sender = SlackReportSender(webhook_url)
    
    print("\\n작업을 선택하세요:")
    print("1. 연결 테스트")
    print("2. 일일 보고서 전송")
    print("3. 주간 보고서 전송")
    print("4. 월간 보고서 전송")
    print("5. 모든 보고서 전송")
    print("6. 커스텀 메시지 전송")
    
    try:
        choice = input("\\n선택 (1-6): ").strip()
        
        if choice == '1':
            print("\\n🧪 Slack 연결 테스트 중...")
            sender.test_connection()
            
        elif choice == '2':
            date_input = input("분석할 날짜 (YYYY-MM-DD, 엔터시 오늘): ").strip()
            target_date = date_input if date_input else None
            
            print(f"\\n📅 일일 보고서 전송 중... ({target_date or '오늘'})")
            success = sender.send_daily_report(target_date)
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '3':
            week_input = input("주간 시작일 (YYYY-MM-DD, 엔터시 이번주): ").strip()
            target_week = week_input if week_input else None
            
            print(f"\\n📊 주간 보고서 전송 중... ({target_week or '이번주'})")
            success = sender.send_weekly_report(target_week)
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '4':
            month_input = input("분석할 월 (YYYY-MM, 엔터시 이번달): ").strip()
            target_month = month_input if month_input else None
            
            print(f"\\n📈 월간 보고서 전송 중... ({target_month or '이번달'})")
            success = sender.send_monthly_report(target_month)
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        elif choice == '5':
            print("\\n🎯 모든 보고서 전송 중...")
            
            daily_success = sender.send_daily_report()
            weekly_success = sender.send_weekly_report()
            monthly_success = sender.send_monthly_report()
            
            print(f"일일 보고서: {'✅' if daily_success else '❌'}")
            print(f"주간 보고서: {'✅' if weekly_success else '❌'}")
            print(f"월간 보고서: {'✅' if monthly_success else '❌'}")
            
        elif choice == '6':
            message = input("전송할 메시지를 입력하세요: ").strip()
            title = input("제목 (엔터시 기본값): ").strip()
            channel = input("채널명 (엔터시 기본값): ").strip()
            
            success = sender.send_custom_message(
                message=message,
                title=title if title else None,
                channel=channel if channel else None
            )
            print("✅ 전송 완료!" if success else "❌ 전송 실패")
            
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\\n\\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()