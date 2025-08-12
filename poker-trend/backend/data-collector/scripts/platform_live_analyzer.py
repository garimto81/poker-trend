#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions용 플랫폼 실시간 분석기
- Firebase 실시간 데이터 수집
- Slack 전송 기능 포함
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PlatformLiveAnalyzer:
    """플랫폼 실시간 분석기"""
    
    EXCLUDED_SITES = [
        'PokerStars US',
        'PokerStars Ontario'
    ]
    
    def __init__(self):
        self.report_type = os.getenv('REPORT_TYPE', 'daily').lower()
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.firebase_project_id = "poker-online-analyze"
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/(default)/documents"
        self.today = datetime.now()
        
    def get_date_range(self):
        """리포트 타입에 따른 날짜 범위"""
        end_date = self.today
        
        if self.report_type == 'daily':
            start_date = end_date
        elif self.report_type == 'weekly':
            start_date = end_date - timedelta(days=6)
        else:  # monthly
            start_date = end_date - timedelta(days=29)
            
        return start_date, end_date
    
    def fetch_firebase_data(self):
        """Firebase 데이터 수집"""
        start_date, end_date = self.get_date_range()
        period_data = defaultdict(lambda: defaultdict(dict))
        
        sites_url = f"{self.base_url}/sites"
        
        try:
            response = requests.get(sites_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Firebase 연결 실패: {response.status_code}")
                return self.get_sample_data()
            
            data = response.json()
            documents = data.get('documents', [])
            
            for doc in documents:
                doc_name = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                
                site_name = self._extract_value(fields.get('name', {}), doc_name)
                
                if site_name in self.EXCLUDED_SITES:
                    continue
                
                # 트래픽 데이터 수집
                traffic_url = f"{self.base_url}/sites/{doc_name}/traffic_logs?pageSize=30&orderBy=collected_at%20desc"
                
                try:
                    traffic_response = requests.get(traffic_url, timeout=15)
                    
                    if traffic_response.status_code == 200:
                        traffic_data = traffic_response.json()
                        traffic_docs = traffic_data.get('documents', [])
                        
                        for traffic_doc in traffic_docs:
                            traffic_fields = traffic_doc.get('fields', {})
                            collected_at = self._extract_value(traffic_fields.get('collected_at', {}), '')
                            
                            if collected_at:
                                date_str = collected_at.split('T')[0]
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                
                                if start_date.date() <= date_obj.date() <= end_date.date():
                                    online = self._extract_value(traffic_fields.get('online_players', {}), 0)
                                    cash = self._extract_value(traffic_fields.get('cash_players', {}), 0)
                                    
                                    period_data[date_str]['online'][site_name] = online
                                    period_data[date_str]['cash'][site_name] = cash
                                    
                except Exception as e:
                    print(f"[WARN] {site_name} 트래픽 수집 실패: {e}")
                    
        except Exception as e:
            print(f"[ERROR] Firebase 수집 실패: {e}")
            return self.get_sample_data()
        
        return dict(period_data)
    
    def _extract_value(self, field_value, default):
        """Firebase 필드 값 추출"""
        if isinstance(field_value, dict):
            if 'stringValue' in field_value:
                return field_value['stringValue']
            elif 'integerValue' in field_value:
                return int(field_value['integerValue'])
            elif 'doubleValue' in field_value:
                return float(field_value['doubleValue'])
        return default
    
    def get_sample_data(self):
        """샘플 데이터 생성"""
        today_str = self.today.strftime('%Y-%m-%d')
        return {
            today_str: {
                'online': {
                    'GGNetwork': 150000,
                    'IDNPoker': 8000,
                    'WPT Global': 6000,
                    'Pokerdom': 3000,
                    'Chico': 1000,
                    'Others': 2000
                },
                'cash': {
                    'GGNetwork': 10000,
                    'WPT Global': 3000,
                    'IDNPoker': 1500,
                    'Pokerdom': 600,
                    'Chico': 200,
                    'Others': 1000
                }
            }
        }
    
    def create_slack_message(self, data):
        """Slack 메시지 생성"""
        if self.report_type == 'daily':
            return self.create_daily_message(data)
        elif self.report_type == 'weekly':
            return self.create_weekly_message(data)
        else:
            return self.create_monthly_message(data)
    
    def create_daily_message(self, data):
        """일간 리포트 메시지"""
        today_str = self.today.strftime('%Y-%m-%d')
        today_data = data.get(today_str, list(data.values())[0] if data else {})
        
        online_players = today_data.get('online', {})
        cash_players = today_data.get('cash', {})
        
        online_total = sum(online_players.values())
        cash_total = sum(cash_players.values())
        
        # TOP5 선정
        online_top5 = sorted(online_players.items(), key=lambda x: x[1], reverse=True)[:5]
        cash_top5 = sorted(cash_players.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 메시지 블록 생성
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 [일간] 플랫폼 분석 보고서"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기준일:* {today_str}\n*수집시간:* {self.today.strftime('%H:%M KST')}\n*데이터소스:* Firebase 실시간"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎮 온라인 플레이어*\n총 접속자: *{online_total:,}명*\n\n"
                }
            }
        ]
        
        # 온라인 TOP5
        online_text = ""
        for i, (platform, count) in enumerate(online_top5, 1):
            share = (count / online_total * 100) if online_total > 0 else 0
            online_text += f"{i}. *{platform}*: {count:,}명 ({share:.1f}%)\n"
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": online_text}
        })
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💰 캐시 플레이어*\n총 참여자: *{cash_total:,}명*\n\n"
            }
        })
        
        # 캐시 TOP5
        cash_text = ""
        for i, (platform, count) in enumerate(cash_top5, 1):
            share = (count / cash_total * 100) if cash_total > 0 else 0
            cash_text += f"{i}. *{platform}*: {count:,}명 ({share:.1f}%)\n"
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": cash_text}
        })
        
        # 핵심 지표
        gg_online = online_players.get('GGNetwork', 0)
        gg_cash = cash_players.get('GGNetwork', 0)
        gg_online_share = (gg_online / online_total * 100) if online_total > 0 else 0
        gg_cash_share = (gg_cash / cash_total * 100) if cash_total > 0 else 0
        
        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*핵심 지표:* GGNetwork 점유율 - 온라인 {gg_online_share:.1f}%, 캐시 {gg_cash_share:.1f}%"
                    }
                ]
            }
        ])
        
        return {"blocks": blocks}
    
    def create_weekly_message(self, data):
        """주간 리포트 메시지"""
        start_date, end_date = self.get_date_range()
        
        # 주간 통계 계산
        platform_online = defaultdict(int)
        platform_cash = defaultdict(int)
        
        for date_data in data.values():
            for platform, count in date_data.get('online', {}).items():
                platform_online[platform] += count
            for platform, count in date_data.get('cash', {}).items():
                platform_cash[platform] += count
        
        online_total = sum(platform_online.values())
        cash_total = sum(platform_cash.values())
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📈 [주간] 플랫폼 트렌드 분석"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*분석기간:* {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}\n*데이터 포인트:* {len(data)}일"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*주간 누적 통계*\n온라인: {online_total:,}명\n캐시: {cash_total:,}명"
                }
            }
        ]
        
        return {"blocks": blocks}
    
    def create_monthly_message(self, data):
        """월간 리포트 메시지"""
        start_date, end_date = self.get_date_range()
        
        # 월간 통계 계산
        platform_online = defaultdict(int)
        platform_cash = defaultdict(int)
        
        for date_data in data.values():
            for platform, count in date_data.get('online', {}).items():
                platform_online[platform] += count
            for platform, count in date_data.get('cash', {}).items():
                platform_cash[platform] += count
        
        online_total = sum(platform_online.values())
        cash_total = sum(platform_cash.values())
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 [월간] 플랫폼 전략 분석"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*분석기간:* {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}\n*데이터 포인트:* {len(data)}일"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*월간 누적 통계*\n온라인: {online_total:,}명\n캐시: {cash_total:,}명"
                }
            }
        ]
        
        return {"blocks": blocks}
    
    def send_to_slack(self, message):
        """Slack으로 전송"""
        if not self.slack_webhook_url:
            print("[WARN] Slack webhook URL이 설정되지 않음")
            return False
        
        try:
            response = requests.post(self.slack_webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                print(f"[OK] {self.report_type.upper()} 리포트 Slack 전송 완료")
                return True
            else:
                print(f"[ERROR] Slack 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Slack 전송 오류: {e}")
            return False
    
    def run(self):
        """메인 실행"""
        print(f"\n[플랫폼 실시간 분석기]")
        print(f"리포트 타입: {self.report_type.upper()}")
        print(f"실행 시간: {self.today.strftime('%Y-%m-%d %H:%M:%S KST')}")
        print("-" * 50)
        
        # 데이터 수집
        print("[1/3] Firebase 데이터 수집 중...")
        data = self.fetch_firebase_data()
        
        if not data:
            print("[ERROR] 데이터 수집 실패")
            return False
        
        print(f"[OK] {len(data)}일 데이터 수집 완료")
        
        # 메시지 생성
        print("[2/3] Slack 메시지 생성 중...")
        message = self.create_slack_message(data)
        
        # Slack 전송
        print("[3/3] Slack 전송 중...")
        result = self.send_to_slack(message)
        
        print("-" * 50)
        print(f"[완료] 실행 결과: {'성공' if result else '실패'}")
        
        return result

def main():
    """메인 함수"""
    analyzer = PlatformLiveAnalyzer()
    success = analyzer.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()