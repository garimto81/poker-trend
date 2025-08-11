#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
온라인 포커 플랫폼 트렌드 분석 시스템
poker-online-analyze 프로젝트의 Firebase 데이터를 활용한 트렌드 분석

기능:
- Firebase Firestore에서 실시간 트래픽 데이터 수집
- 플랫폼별 성장률 및 트렌드 분석
- 시장 점유율 변화 감지
- AI 기반 인사이트 생성
- Slack으로 분석 결과 리포팅
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import numpy as np
from collections import defaultdict
import google.generativeai as genai

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OnlinePlatformTrendAnalyzer:
    """온라인 포커 플랫폼 트렌드 분석기"""
    
    def __init__(self, firebase_config_path: str = None, test_mode: bool = False):
        """
        초기화
        
        Args:
            firebase_config_path: Firebase 서비스 계정 키 파일 경로
            test_mode: 테스트 모드 (Slack 전송 안함)
        """
        # 테스트 모드 설정
        self.test_mode = test_mode
        
        # Firebase 초기화
        self.initialize_firebase(firebase_config_path)
        
        # Gemini AI 초기화
        self.initialize_gemini()
        
        # 분석 타입 (daily, weekly, monthly)
        self.analysis_type = 'daily'
        
        # 분석 설정
        self.top_platforms_count = 10  # 상위 10개 플랫폼 분석
        self.analysis_period_days = 1  # 기본 1일 (분석 타입에 따라 변경)
        
        # 플랫폼 카테고리 정의
        self.platform_categories = {
            'major_networks': ['GGNetwork', 'PokerStars', '888poker', 'partypoker'],
            'asian_focused': ['Natural8', 'PPPoker', 'PokerBros'],
            'crypto_friendly': ['CoinPoker', 'SwC Poker', 'Blockchain.Poker'],
            'us_friendly': ['Americas Cardroom', 'Ignition', 'BetOnline']
        }
        
        # 트렌드 임계값 (일간/주간/월간별로 다르게 설정)
        self.trend_thresholds = {
            'daily': {
                'significant_change': 0.10,    # 10% 이상 변동이 있어야 유의미
                'rapid_growth': 0.15,          # 15% 이상 급성장
                'rapid_decline': -0.15         # -15% 이상 급락
            },
            'weekly': {
                'significant_change': 0.15,    # 15% 이상 변동이 있어야 유의미
                'rapid_growth': 0.25,          # 25% 이상 급성장
                'rapid_decline': -0.20         # -20% 이상 급락
            },
            'monthly': {
                'significant_change': 0.20,    # 20% 이상 변동이 있어야 유의미
                'rapid_growth': 0.30,          # 30% 이상 급성장
                'rapid_decline': -0.25         # -25% 이상 급락
            }
        }
        
        # 이슈 감지 설정
        self.issue_detection = {
            'min_platforms_with_change': 3,    # 최소 3개 이상 플랫폼에서 변화가 있어야 이슈
            'market_volatility_threshold': 0.15 # 시장 전체 변동성 15% 이상이면 이슈
        }
    
    def initialize_firebase(self, config_path: str = None):
        """Firebase 초기화"""
        try:
            if config_path and os.path.exists(config_path):
                cred = credentials.Certificate(config_path)
            else:
                # 환경 변수에서 Firebase 설정 로드
                firebase_config = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                }
                cred = credentials.Certificate(firebase_config)
            
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("✅ Firebase 초기화 성공")
            
        except Exception as e:
            logger.error(f"❌ Firebase 초기화 실패: {e}")
            raise
    
    def initialize_gemini(self):
        """Gemini AI 초기화"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("⚠️ Gemini API 키가 설정되지 않음")
                self.gemini_model = None
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini AI 초기화 성공")
            
        except Exception as e:
            logger.error(f"❌ Gemini AI 초기화 실패: {e}")
            self.gemini_model = None
    
    def fetch_platform_data(self) -> Dict[str, Any]:
        """
        Firebase에서 플랫폼 데이터 가져오기
        
        Returns:
            플랫폼별 데이터 딕셔너리
        """
        try:
            logger.info("📊 Firebase에서 플랫폼 데이터 수집 중...")
            
            # sites 컬렉션에서 모든 사이트 데이터 가져오기
            sites_ref = self.db.collection('sites')
            sites_docs = sites_ref.stream()
            
            platform_data = {}
            
            for doc in sites_docs:
                site_data = doc.to_dict()
                site_name = doc.id
                
                # 최근 7일간 일일 통계 가져오기
                daily_stats_ref = sites_ref.document(site_name).collection('daily_stats')
                
                # 시간 범위 설정
                end_date = datetime.now()
                start_date = end_date - timedelta(days=self.analysis_period_days)
                
                # 날짜 범위로 쿼리
                daily_stats = daily_stats_ref.where(
                    'timestamp', '>=', start_date
                ).where(
                    'timestamp', '<=', end_date
                ).order_by('timestamp').stream()
                
                daily_data = []
                for stat_doc in daily_stats:
                    stat_data = stat_doc.to_dict()
                    daily_data.append(stat_data)
                
                platform_data[site_name] = {
                    'current_data': site_data,
                    'historical_data': daily_data
                }
            
            logger.info(f"✅ {len(platform_data)}개 플랫폼 데이터 수집 완료")
            return platform_data
            
        except Exception as e:
            logger.error(f"❌ 데이터 수집 실패: {e}")
            return {}
    
    def calculate_trends(self, platform_data: Dict) -> Dict:
        """
        플랫폼별 트렌드 계산
        
        Args:
            platform_data: 플랫폼 데이터
            
        Returns:
            트렌드 분석 결과
        """
        trends = {}
        
        for platform_name, data in platform_data.items():
            try:
                historical = data.get('historical_data', [])
                current = data.get('current_data', {})
                
                if not historical or len(historical) < 2:
                    continue
                
                # 플레이어 수 추출
                player_counts = [d.get('cash_players', 0) for d in historical]
                timestamps = [d.get('timestamp') for d in historical]
                
                if not player_counts:
                    continue
                
                # 트렌드 지표 계산
                avg_players = np.mean(player_counts)
                std_players = np.std(player_counts)
                
                # 성장률 계산 (첫날 대비 마지막날)
                if player_counts[0] > 0:
                    growth_rate = (player_counts[-1] - player_counts[0]) / player_counts[0]
                else:
                    growth_rate = 0
                
                # 일일 변화율 계산
                daily_changes = []
                for i in range(1, len(player_counts)):
                    if player_counts[i-1] > 0:
                        change = (player_counts[i] - player_counts[i-1]) / player_counts[i-1]
                        daily_changes.append(change)
                
                avg_daily_change = np.mean(daily_changes) if daily_changes else 0
                volatility = np.std(daily_changes) if daily_changes else 0
                
                # 트렌드 방향 결정
                trend_direction = self._determine_trend_direction(growth_rate)
                
                # 피크 시간 분석
                peak_players = max(player_counts) if player_counts else 0
                peak_index = player_counts.index(peak_players) if player_counts else 0
                
                trends[platform_name] = {
                    'current_players': current.get('cash_players', 0),
                    'avg_players': round(avg_players, 1),
                    'peak_players': peak_players,
                    'growth_rate': round(growth_rate * 100, 2),  # 퍼센트로 변환
                    'daily_change_avg': round(avg_daily_change * 100, 2),
                    'volatility': round(volatility * 100, 2),
                    'trend_direction': trend_direction,
                    'data_points': len(player_counts),
                    'last_updated': current.get('last_updated', '')
                }
                
            except Exception as e:
                logger.warning(f"⚠️ {platform_name} 트렌드 계산 실패: {e}")
                continue
        
        return trends
    
    def _determine_trend_direction(self, growth_rate: float) -> str:
        """트렌드 방향 결정"""
        thresholds = self.trend_thresholds.get(self.analysis_type, self.trend_thresholds['daily'])
        
        if growth_rate >= thresholds['rapid_growth']:
            return '🚀 급성장'
        elif growth_rate >= thresholds['significant_change']:
            return '📈 성장'
        elif growth_rate <= thresholds['rapid_decline']:
            return '⚠️ 급락'
        elif growth_rate <= -thresholds['significant_change']:
            return '📉 하락'
        else:
            return '➡️ 안정'
    
    def analyze_market_share(self, trends: Dict) -> Dict:
        """
        시장 점유율 분석
        
        Args:
            trends: 트렌드 데이터
            
        Returns:
            시장 점유율 분석 결과
        """
        # 전체 플레이어 수 계산
        total_players = sum(t['current_players'] for t in trends.values())
        
        market_share = {}
        for platform, trend in trends.items():
            if total_players > 0:
                share = (trend['current_players'] / total_players) * 100
                market_share[platform] = {
                    'share_percentage': round(share, 2),
                    'players': trend['current_players'],
                    'rank': 0  # 나중에 설정
                }
        
        # 순위 매기기
        sorted_platforms = sorted(
            market_share.items(), 
            key=lambda x: x[1]['share_percentage'], 
            reverse=True
        )
        
        for rank, (platform, data) in enumerate(sorted_platforms, 1):
            market_share[platform]['rank'] = rank
        
        return {
            'total_players': total_players,
            'platform_shares': market_share,
            'top_platforms': [p[0] for p in sorted_platforms[:self.top_platforms_count]]
        }
    
    def detect_market_issues(self, trends: Dict, market_share: Dict) -> Dict:
        """
        시장 이슈 감지 - AI가 판단하여 유의미한 변화가 있는지 확인
        
        Args:
            trends: 트렌드 데이터
            market_share: 시장 점유율
            
        Returns:
            이슈 감지 결과
        """
        thresholds = self.trend_thresholds.get(self.analysis_type, self.trend_thresholds['daily'])
        
        # 유의미한 변화가 있는 플랫폼 수 계산
        platforms_with_change = 0
        significant_changes = []
        
        for platform, trend in trends.items():
            change_rate = abs(trend['growth_rate'] / 100)  # 퍼센트를 비율로 변환
            
            # 유의미한 변화 감지
            if change_rate >= thresholds['significant_change']:
                platforms_with_change += 1
                
                # 급격한 변화 기록
                if trend['growth_rate'] / 100 >= thresholds['rapid_growth']:
                    significant_changes.append({
                        'type': 'rapid_growth',
                        'platform': platform,
                        'change': trend['growth_rate'],
                        'message': f"🚀 {platform}이(가) {trend['growth_rate']:.1f}% 급성장"
                    })
                elif trend['growth_rate'] / 100 <= thresholds['rapid_decline']:
                    significant_changes.append({
                        'type': 'rapid_decline',
                        'platform': platform,
                        'change': trend['growth_rate'],
                        'message': f"⚠️ {platform}이(가) {abs(trend['growth_rate']):.1f}% 급락"
                    })
                else:
                    significant_changes.append({
                        'type': 'notable_change',
                        'platform': platform,
                        'change': trend['growth_rate'],
                        'message': f"📊 {platform}이(가) {abs(trend['growth_rate']):.1f}% 변동"
                    })
        
        # 시장 전체 변동성 계산
        all_changes = [abs(t['growth_rate'] / 100) for t in trends.values()]
        market_volatility = np.mean(all_changes) if all_changes else 0
        
        # 이슈 판단
        has_issue = False
        issue_level = 'none'
        issue_summary = ""
        
        if platforms_with_change >= self.issue_detection['min_platforms_with_change']:
            has_issue = True
            issue_level = 'moderate'
            issue_summary = f"{platforms_with_change}개 플랫폼에서 유의미한 변화 감지"
        
        if market_volatility >= self.issue_detection['market_volatility_threshold']:
            has_issue = True
            issue_level = 'high'
            issue_summary = f"시장 전체 변동성 {market_volatility*100:.1f}%로 높음"
        
        # 상위 플랫폼의 급격한 변화 체크
        top_platforms = market_share.get('top_platforms', [])[:3]
        top_platform_issues = [
            change for change in significant_changes 
            if change['platform'] in top_platforms and 
            change['type'] in ['rapid_growth', 'rapid_decline']
        ]
        
        if top_platform_issues:
            has_issue = True
            issue_level = 'critical'
            issue_summary = f"상위 플랫폼에서 급격한 변화 발생"
        
        return {
            'has_issue': has_issue,
            'issue_level': issue_level,
            'issue_summary': issue_summary,
            'platforms_with_change': platforms_with_change,
            'market_volatility': market_volatility * 100,
            'significant_changes': significant_changes,
            'analysis_needed': has_issue  # AI 상세 분석 필요 여부
        }
    
    def generate_ai_insights(self, trends: Dict, market_share: Dict, issue_detection: Dict) -> str:
        """
        Gemini AI를 활용한 인사이트 생성 (이슈가 있을 때만 상세 분석)
        
        Args:
            trends: 트렌드 데이터
            market_share: 시장 점유율
            issue_detection: 이슈 감지 결과
            
        Returns:
            AI 생성 인사이트
        """
        if not self.gemini_model:
            if issue_detection['has_issue']:
                return "AI 인사이트를 사용할 수 없지만, 유의미한 변화가 감지되었습니다."
            else:
                return "특별한 이슈가 없습니다."
        
        try:
            # 이슈가 없으면 간단한 요약만
            if not issue_detection['has_issue']:
                prompt = f"""
                온라인 포커 플랫폼 시장 데이터를 검토한 결과, 
                시장 변동성: {issue_detection['market_volatility']:.1f}%
                유의미한 변화가 있는 플랫폼 수: {issue_detection['platforms_with_change']}개
                
                이 데이터를 보고 한 문장으로 간단히 요약해주세요.
                특별한 이슈가 없다면 "온라인 포커 플랫폼 시장은 안정적으로 유지되고 있습니다." 정도로 답변해주세요.
                """
            else:
                # 이슈가 있을 때만 상세 분석
                top_platforms = market_share['top_platforms'][:10]
                top_trends = {p: trends[p] for p in top_platforms if p in trends}
                
                prompt = f"""
                온라인 포커 플랫폼 시장에서 중요한 변화가 감지되었습니다.
                
                [이슈 감지 결과]
                - 이슈 레벨: {issue_detection['issue_level']}
                - 이슈 요약: {issue_detection['issue_summary']}
                - 시장 변동성: {issue_detection['market_volatility']:.1f}%
                
                [주요 변화 사항]
                {json.dumps(issue_detection['significant_changes'][:5], indent=2, ensure_ascii=False)}
                
                [상위 10개 플랫폼 현황]
                {json.dumps(top_trends, indent=2, ensure_ascii=False)}
                
                다음 내용을 포함하여 분석해주세요:
                1. 현재 발생한 주요 이슈와 그 원인 추정
                2. 플레이어들에게 미치는 영향
                3. 향후 예상되는 시장 변화
                4. 권장 대응 방안
                
                한국어로 명확하고 실용적으로 작성해주세요.
                구체적인 수치와 플랫폼명을 언급해주세요.
                """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"❌ AI 인사이트 생성 실패: {e}")
            if issue_detection['has_issue']:
                return f"AI 분석은 실패했지만, {issue_detection['issue_summary']}"
            else:
                return "온라인 포커 플랫폼 시장은 특별한 이슈 없이 안정적입니다."
    
    def format_slack_report(self, analysis_results: Dict) -> str:
        """
        Slack 리포트 포맷팅
        
        Args:
            analysis_results: 분석 결과
            
        Returns:
            포맷된 Slack 메시지
        """
        trends = analysis_results['trends']
        market = analysis_results['market_share']
        changes = analysis_results['significant_changes']
        ai_insights = analysis_results['ai_insights']
        
        # 헤더
        report = f"""
🎰 **온라인 포커 플랫폼 트렌드 분석**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 분석 기간: 최근 7일
⏰ 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')} KST
📊 총 활성 플레이어: {market['total_players']:,}명

**🏆 TOP 10 플랫폼 현황**
────────────────────────────
"""
        
        # 상위 10개 플랫폼
        for i, platform in enumerate(market['top_platforms'][:10], 1):
            if platform in trends:
                trend = trends[platform]
                share = market['platform_shares'][platform]
                
                # 트렌드 아이콘 선택
                if trend['growth_rate'] > 10:
                    icon = "🔺"
                elif trend['growth_rate'] < -10:
                    icon = "🔻"
                else:
                    icon = "➖"
                
                report += f"{i}. **{platform}** {icon}\n"
                report += f"   현재: {trend['current_players']:,}명 | "
                report += f"점유율: {share['share_percentage']:.1f}% | "
                report += f"7일 성장률: {trend['growth_rate']:+.1f}%\n\n"
        
        # 주요 변화 사항
        if changes:
            report += "\n**🔥 주목할 변화**\n────────────────────────────\n"
            for change in changes[:3]:
                report += f"• {change['message']}\n"
        
        # AI 인사이트
        if ai_insights and ai_insights != "AI 인사이트를 사용할 수 없습니다.":
            report += f"\n**🤖 AI 트렌드 분석**\n────────────────────────────\n{ai_insights}\n"
        
        # 카테고리별 요약
        report += "\n**📊 카테고리별 동향**\n────────────────────────────\n"
        
        # 네트워크별 분류
        categories_summary = self._categorize_platforms(trends, market)
        for category, summary in categories_summary.items():
            if summary['platforms']:
                report += f"• **{summary['name']}**: "
                report += f"평균 성장률 {summary['avg_growth']:+.1f}%\n"
        
        # 푸터
        report += f"""
────────────────────────────
📈 상세 분석: https://garimto81.github.io/poker-online-analyze
💡 데이터 출처: PokerScout.com
🔄 다음 업데이트: 내일 오전 10시
"""
        
        return report
    
    def _categorize_platforms(self, trends: Dict, market: Dict) -> Dict:
        """플랫폼 카테고리별 분류"""
        categories_summary = {}
        
        for category, platforms in self.platform_categories.items():
            category_trends = []
            for platform in platforms:
                if platform in trends:
                    category_trends.append(trends[platform]['growth_rate'])
            
            if category_trends:
                categories_summary[category] = {
                    'name': category.replace('_', ' ').title(),
                    'platforms': platforms,
                    'avg_growth': np.mean(category_trends)
                }
        
        return categories_summary
    
    def send_to_slack(self, message: str):
        """
        Slack으로 메시지 전송
        
        Args:
            message: 전송할 메시지
        """
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            logger.warning("⚠️ Slack Webhook URL이 설정되지 않음")
            print(message)  # 콘솔에 출력
            return
        
        try:
            response = requests.post(
                webhook_url,
                json={'text': message},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("✅ Slack 메시지 전송 성공")
            else:
                logger.error(f"❌ Slack 전송 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Slack 전송 오류: {e}")
    
    def run_analysis(self, analysis_type: str = 'daily', generate_charts: bool = True):
        """
        전체 분석 프로세스 실행 (차트 생성 포함)
        
        Args:
            analysis_type: 분석 타입 (daily, weekly, monthly)
            generate_charts: 차트 생성 여부
        """
        self.analysis_type = analysis_type
        
        # 분석 기간 설정
        if analysis_type == 'daily':
            self.analysis_period_days = 1
        elif analysis_type == 'weekly':
            self.analysis_period_days = 7
        elif analysis_type == 'monthly':
            self.analysis_period_days = 30
        
        logger.info(f"🚀 온라인 포커 플랫폼 {analysis_type} 분석 시작")
        
        try:
            # 1. 데이터 수집
            platform_data = self.fetch_platform_data()
            if not platform_data:
                logger.error("❌ 플랫폼 데이터가 없습니다")
                return
            
            # 2. 트렌드 계산
            trends = self.calculate_trends(platform_data)
            logger.info(f"📊 {len(trends)}개 플랫폼 트렌드 분석 완료")
            
            # 3. 시장 점유율 분석
            market_share = self.analyze_market_share(trends)
            
            # 4. 이슈 감지
            issue_detection = self.detect_market_issues(trends, market_share)
            
            # 5. 데이터 분석 결과 먼저 출력 (ASCII 차트 포함)
            self.print_analysis_summary(trends, market_share, issue_detection)
            
            # 6. 차트 생성 (이슈가 있거나 요청된 경우)
            chart_paths = {}
            if generate_charts and (issue_detection['has_issue'] or analysis_type in ['weekly', 'monthly']):
                chart_paths = self.generate_visual_charts(platform_data, trends, market_share, issue_detection)
            
            # 7. AI 인사이트 생성 (이슈가 있을 때만 상세 분석)
            ai_insights = self.generate_ai_insights(trends, market_share, issue_detection)
            
            # 8. 결과 종합
            analysis_results = {
                'analysis_type': analysis_type,
                'analysis_period_days': self.analysis_period_days,
                'trends': trends,
                'market_share': market_share,
                'issue_detection': issue_detection,
                'ai_insights': ai_insights,
                'charts': chart_paths,
                'platform_data': platform_data,  # 차트 생성을 위해 추가
                'timestamp': datetime.now().isoformat()
            }
            
            # 9. 결과 저장
            self.save_results(analysis_results)
            
            # 10. Slack 리포트 전송 (테스트 모드가 아닐 때만)
            if not self.test_mode:
                slack_report = self.format_enhanced_slack_report(analysis_results)
                self.send_to_slack(slack_report)
                logger.info("✅ Slack 리포트 전송 완료")
            else:
                logger.info("🧪 테스트 모드 - Slack 전송 생략")
            
            logger.info(f"✅ 온라인 포커 플랫폼 {analysis_type} 분석 완료")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ 분석 실행 실패: {e}")
            raise
    
    def generate_visual_charts(self, platform_data: Dict, trends: Dict, 
                              market_share: Dict, issue_detection: Dict) -> Dict:
        """
        시각적 차트 생성
        
        Args:
            platform_data: 플랫폼 데이터
            trends: 트렌드 데이터
            market_share: 시장 점유율
            issue_detection: 이슈 감지 결과
            
        Returns:
            생성된 차트 파일 경로
        """
        try:
            from platform_chart_generator import PlatformChartGenerator
            
            chart_gen = PlatformChartGenerator()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # reports 디렉토리 생성
            os.makedirs('reports/charts', exist_ok=True)
            
            chart_paths = {}
            
            # 1. 누적 영역 차트 생성
            if issue_detection['has_issue'] or self.analysis_type in ['weekly', 'monthly']:
                area_chart_path = f"reports/charts/area_chart_{self.analysis_type}_{timestamp}.png"
                chart_gen.generate_area_chart(platform_data, area_chart_path)
                chart_paths['area_chart'] = area_chart_path
                logger.info(f"📊 누적 영역 차트 생성: {area_chart_path}")
            
            # 2. 종합 분석 대시보드 생성
            comparison_chart_path = f"reports/charts/dashboard_{self.analysis_type}_{timestamp}.png"
            chart_gen.generate_comparison_chart(trends, market_share, comparison_chart_path)
            chart_paths['dashboard'] = comparison_chart_path
            logger.info(f"📈 종합 대시보드 생성: {comparison_chart_path}")
            
            # 3. HTML 리포트 생성
            analysis_results = {
                'trends': trends,
                'market_share': market_share,
                'issue_detection': issue_detection,
                'analysis_period_days': self.analysis_period_days
            }
            
            # base64 인코딩된 차트 생성
            area_chart_b64 = chart_gen.generate_area_chart(platform_data)
            dashboard_b64 = chart_gen.generate_comparison_chart(trends, market_share)
            
            charts_b64 = {
                'area_chart': area_chart_b64,
                'comparison_chart': dashboard_b64
            }
            
            html_report = chart_gen.generate_html_report(analysis_results, charts_b64)
            html_path = f"reports/html_report_{self.analysis_type}_{timestamp}.html"
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            chart_paths['html_report'] = html_path
            logger.info(f"📄 HTML 리포트 생성: {html_path}")
            
            return chart_paths
            
        except Exception as e:
            logger.error(f"차트 생성 실패: {e}")
            return {}
    
    def format_enhanced_slack_report(self, analysis_results: Dict) -> str:
        """
        향상된 Slack 리포트 (차트 정보 포함)
        
        Args:
            analysis_results: 분석 결과
            
        Returns:
            포맷된 Slack 메시지
        """
        # 기본 리포트 생성
        base_report = self.format_smart_slack_report(analysis_results)
        
        # 차트 정보 추가
        if analysis_results.get('charts'):
            charts = analysis_results['charts']
            
            # HTML 리포트 링크 추가
            if 'html_report' in charts:
                base_report += f"\n\n📊 **상세 분석 차트**"
                base_report += f"\n• HTML 리포트: `{charts['html_report']}`"
                base_report += f"\n• 차트 생성 완료: {len(charts)}개"
        
        return base_report
    
    def print_analysis_summary(self, trends: Dict, market_share: Dict, issue_detection: Dict):
        """
        데이터 분석 결과 콘솔 출력 (차트 포함)
        
        Args:
            trends: 트렌드 데이터
            market_share: 시장 점유율
            issue_detection: 이슈 감지 결과
        """
        print("\n" + "="*70)
        print(f"📊 온라인 포커 플랫폼 {self.analysis_type.upper()} 분석 결과")
        print("="*70)
        
        # 전체 시장 현황
        print(f"\n[전체 시장 현황]")
        print(f"• 총 활성 플레이어: {market_share['total_players']:,}명")
        print(f"• 분석 플랫폼 수: {len(trends)}개")
        print(f"• 분석 기간: {self.analysis_period_days}일")
        
        # 이슈 감지 결과
        print(f"\n[이슈 감지 결과]")
        print(f"• 이슈 여부: {'🔴 있음' if issue_detection['has_issue'] else '🟢 없음'}")
        if issue_detection['has_issue']:
            print(f"• 이슈 레벨: {issue_detection['issue_level']}")
            print(f"• 이슈 요약: {issue_detection['issue_summary']}")
        print(f"• 시장 변동성: {issue_detection['market_volatility']:.1f}%")
        print(f"• 유의미한 변화 플랫폼: {issue_detection['platforms_with_change']}개")
        
        # TOP 5 플랫폼
        print(f"\n[TOP 5 플랫폼 현황]")
        top_5 = market_share['top_platforms'][:5]
        for i, platform in enumerate(top_5, 1):
            if platform in trends:
                trend = trends[platform]
                share = market_share['platform_shares'][platform]
                growth_icon = "📈" if trend['growth_rate'] > 0 else "📉" if trend['growth_rate'] < 0 else "➖"
                print(f"{i}. {platform:20} | 플레이어: {trend['current_players']:6,}명 | "
                      f"점유율: {share['share_percentage']:5.1f}% | "
                      f"변화율: {trend['growth_rate']:+6.1f}% {growth_icon}")
        
        # 주요 변화 사항
        if issue_detection['significant_changes']:
            print(f"\n[주요 변화 사항]")
            for change in issue_detection['significant_changes'][:3]:
                print(f"• {change['message']}")
        
        # ASCII 차트 추가
        try:
            from platform_chart_generator import PlatformChartGenerator
            chart_gen = PlatformChartGenerator()
            ascii_chart = chart_gen.generate_ascii_chart(trends, market_share)
            print("\n" + ascii_chart)
        except Exception as e:
            logger.debug(f"차트 생성 실패: {e}")
        
        print("\n" + "="*70 + "\n")
    
    def save_results(self, results: Dict):
        """
        분석 결과 저장
        
        Args:
            results: 분석 결과
        """
        try:
            # 결과 파일 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/platform_analysis_{timestamp}.json"
            
            os.makedirs('reports', exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"📁 분석 결과 저장: {filename}")
            
            # Firebase에도 저장 (선택사항)
            if self.db:
                doc_ref = self.db.collection('trend_analysis').document(timestamp)
                doc_ref.set(results)
                logger.info("☁️ Firebase에 분석 결과 저장 완료")
                
        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")


    def format_smart_slack_report(self, analysis_results: Dict) -> str:
        """
        스마트 Slack 리포트 - 이슈가 없으면 간단히, 있으면 상세히
        
        Args:
            analysis_results: 분석 결과
            
        Returns:
            포맷된 Slack 메시지
        """
        issue_detection = analysis_results['issue_detection']
        analysis_type = analysis_results['analysis_type']
        
        # 분석 타입별 이모지
        type_emoji = {
            'daily': '📋',
            'weekly': '📅',
            'monthly': '📊'
        }
        
        # 이슈가 없는 경우 - 간단한 리포트
        if not issue_detection['has_issue']:
            report = f"""
{type_emoji.get(analysis_type, '📊')} **온라인 포커 플랫폼 {analysis_type.upper()} 리포트**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} KST

✅ **상태**: 정상 (특별한 이슈 없음)

**요약**
• 총 활성 플레이어: {analysis_results['market_share']['total_players']:,}명
• 시장 변동성: {issue_detection['market_volatility']:.1f}%
• AI 분석: {analysis_results['ai_insights']}

💡 온라인 포커 플랫폼 시장은 안정적으로 운영되고 있습니다.
"""
        
        # 이슈가 있는 경우 - 상세 리포트
        else:
            trends = analysis_results['trends']
            market = analysis_results['market_share']
            
            # 이슈 레벨별 헤더
            level_headers = {
                'critical': '🚨 **긴급 이슈 발생**',
                'high': '⚠️ **중요 변화 감지**',
                'moderate': '📊 **주목할 변화**'
            }
            
            report = f"""
{type_emoji.get(analysis_type, '📊')} **온라인 포커 플랫폼 {analysis_type.upper()} 리포트**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} KST

{level_headers.get(issue_detection['issue_level'], '📊 **변화 감지**')}
{issue_detection['issue_summary']}

**📈 주요 변화 사항**
"""
            # 주요 변화 리스트
            for change in issue_detection['significant_changes'][:5]:
                report += f"• {change['message']}\n"
            
            # TOP 5 플랫폼만 표시
            report += "\n**🏆 TOP 5 플랫폼 현황**\n"
            for i, platform in enumerate(market['top_platforms'][:5], 1):
                if platform in trends:
                    trend = trends[platform]
                    share = market['platform_shares'][platform]
                    report += f"{i}. **{platform}**: {trend['current_players']:,}명 ({trend['growth_rate']:+.1f}%)\n"
            
            # AI 인사이트
            report += f"\n**🤖 AI 분석**\n{analysis_results['ai_insights'][:500]}"  # 500자 제한
            
            report += f"\n\n📈 상세 분석: https://garimto81.github.io/poker-online-analyze"
        
        return report


def main():
    """메인 실행 함수"""
    import sys
    
    # 명령줄 인자 파싱
    test_mode = '--test' in sys.argv
    
    # 분석 타입 결정
    if '--daily' in sys.argv:
        analysis_type = 'daily'
    elif '--weekly' in sys.argv:
        analysis_type = 'weekly'
    elif '--monthly' in sys.argv:
        analysis_type = 'monthly'
    else:
        analysis_type = 'daily'  # 기본값
    
    # 분석기 실행
    analyzer = OnlinePlatformTrendAnalyzer(test_mode=test_mode)
    
    if test_mode:
        print("🧪 테스트 모드로 실행 중 (Slack 전송 없음)")
    
    analyzer.run_analysis(analysis_type)


if __name__ == "__main__":
    main()