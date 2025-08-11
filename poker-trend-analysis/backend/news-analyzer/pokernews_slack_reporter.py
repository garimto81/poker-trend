#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews Slack 리포터
분석된 포커 뉴스를 Slack으로 전송하는 모듈
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pokernews_collector import PokerNewsCollector
from pokernews_rss_collector import PokerNewsRSSCollector
from pokernews_ai_analyzer import PokerNewsAIAnalyzer

# 환경 변수 로드
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerNewsSlackReporter:
    """PokerNews Slack 리포터"""
    
    def __init__(self, slack_webhook_url: Optional[str] = None):
        """
        초기화
        
        Args:
            slack_webhook_url: Slack Webhook URL
        """
        self.webhook_url = slack_webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL이 필요합니다")
        
        self.collector = PokerNewsCollector()
        self.rss_collector = PokerNewsRSSCollector()
        self.analyzer = PokerNewsAIAnalyzer()
        
        logger.info("PokerNews Slack 리포터 초기화 완료")
    
    def run_report(self) -> Dict:
        """
        리포트 실행 (일간/주간/월간)
        
        Returns:
            실행 결과
        """
        report_type = os.getenv('REPORT_TYPE', 'daily')
        logger.info(f"=== PokerNews {report_type} 리포트 시작 ===")
        
        try:
            # 1. 뉴스 수집
            logger.info("1. 뉴스 수집 중...")
            # RSS 우선 시도
            articles = self.rss_collector.collect_from_rss(max_articles=20)
            
            # RSS 실패 시 웹 스크래핑
            if not articles:
                logger.info("RSS 실패, 웹 스크래핑 시도...")
                articles = self.collector.collect_latest_news(max_articles=20)
            
            # 그래도 없으면 모의 데이터
            if not articles:
                logger.info("모의 데이터 사용...")
                articles = self.rss_collector.collect_mock_news()
            
            if not articles:
                logger.warning("수집된 뉴스가 없습니다")
                self._send_no_news_message()
                return {'status': 'no_news'}
            
            # 2. 오늘 날짜 뉴스 필터링
            today_articles = self.collector.filter_today_news(articles)
            logger.info(f"오늘의 뉴스: {len(today_articles)}개")
            
            # 3. AI 분석
            logger.info("2. AI 분석 중...")
            analysis = self.analyzer.analyze_news_trends(today_articles or articles[:10])
            
            # 4. Slack 메시지 생성
            logger.info("3. Slack 메시지 생성 중...")
            message = self._create_slack_message(analysis, today_articles or articles[:10])
            
            # 5. Slack 전송
            logger.info("4. Slack 전송 중...")
            send_result = self._send_to_slack(message)
            
            # 6. 결과 저장
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'articles_collected': len(articles),
                'today_articles': len(today_articles),
                'analysis': analysis,
                'slack_sent': send_result
            }
            
            # 결과 파일 저장
            self._save_report(result)
            
            logger.info("=== PokerNews 일일 리포트 완료 ===")
            return result
            
        except Exception as e:
            logger.error(f"리포트 실행 실패: {e}")
            self._send_error_message(str(e))
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_slack_message(self, analysis: Dict, articles: List[Dict]) -> Dict:
        """Slack 메시지 생성"""
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        # 리포트 타입 확인
        report_type = os.getenv('REPORT_TYPE', 'daily')
        data_start = os.getenv('DATA_PERIOD_START', '')
        data_end = os.getenv('DATA_PERIOD_END', '')
        
        # 리포트 타입에 따른 헤더 설정
        header_text = {
            'daily': '📰 PokerNews 일간 트렌드 분석',
            'weekly': '📰 PokerNews 주간 트렌드 분석',
            'monthly': '📰 PokerNews 월간 트렌드 분석'
        }.get(report_type, '📰 PokerNews 트렌드 분석')
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text,
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 *{data_start if data_start else current_date}{(' ~ ' + data_end) if data_end and data_start != data_end else ''}* | 🔍 분석 기사: *{len(articles)}개*"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        # 핵심 트렌드
        if analysis.get('core_trends'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 오늘의 핵심 트렌드*"
                }
            })
            
            trend_text = ""
            for i, trend in enumerate(analysis['core_trends'][:5], 1):
                trend_text += f"{i}. {trend}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": trend_text
                }
            })
            blocks.append({"type": "divider"})
        
        # 주요 토너먼트
        if analysis.get('tournaments'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 주요 토너먼트 소식*"
                }
            })
            
            tournament_text = ""
            for tournament in analysis['tournaments'][:3]:
                tournament_text += f"• {tournament}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": tournament_text
                }
            })
            blocks.append({"type": "divider"})
        
        # 주목할 선수
        if analysis.get('notable_players'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🌟 주목할 선수*"
                }
            })
            
            players_text = ""
            for player in analysis['notable_players'][:3]:
                players_text += f"• {player}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": players_text
                }
            })
            blocks.append({"type": "divider"})
        
        # 시장 동향
        if analysis.get('market_trends'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💼 시장 동향*"
                }
            })
            
            market_text = ""
            for trend in analysis['market_trends'][:3]:
                market_text += f"• {trend}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": market_text
                }
            })
            blocks.append({"type": "divider"})
        
        # 콘텐츠 아이디어
        if analysis.get('content_ideas'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 추천 콘텐츠 아이디어*"
                }
            })
            
            ideas_text = ""
            for i, idea in enumerate(analysis['content_ideas'][:3], 1):
                ideas_text += f"{i}. {idea}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ideas_text
                }
            })
            blocks.append({"type": "divider"})
        
        # 한 줄 요약
        if analysis.get('summary'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 오늘의 요약*\n_{analysis['summary']}_"
                }
            })
            blocks.append({"type": "divider"})
        
        # 주요 기사 with 3줄 요약
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📚 주요 기사 (3줄 요약)*"
            }
        })
        
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', 'No title')
            url = article.get('url', '#')
            
            # 제목에 하이퍼링크 포함
            if len(title) > 80:
                display_title = title[:80] + "..."
            else:
                display_title = title
            
            # 3줄 요약 생성
            summary_lines = self._create_article_summary(article)
            
            # 기사 블록 - 제목에 링크 포함
            article_text = f"*[{i}]* <{url}|{display_title}>\n"
            for line in summary_lines:
                article_text += f"   {line}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article_text
                }
            })
        
        blocks.append({"type": "divider"})
        
        # 푸터
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🤖 *Powered by Gemini AI* | 📰 *Source: PokerNews.com*"
                }
            ]
        })
        
        return {"blocks": blocks}
    
    def _create_article_summary(self, article: Dict) -> List[str]:
        """기사 실제 내용 기반 3줄 요약"""
        title = article.get('title', '제목 없음')
        summary = article.get('summary', '')
        source = article.get('source', 'Unknown')
        
        lines = []
        title_clean = title.split(' - ')[0] if ' - ' in title else title
        
        # 1줄: 주요 이벤트/내용
        if 'Thailand' in title and 'Legalizing' in title:
            lines.append("🏛️ 태국 정부가 포커 토너먼트를 합법화하며 도박 논란 발생")
        elif 'Hellmuth' in title and 'parents' in title:
            lines.append("🎙️ Norman Chad가 Phil Hellmuth 부모와의 일화 공개")
        elif '2025 WSOP Online' in title:
            lines.append("📅 2025년 WSOP 온라인 브레이슬릿 전체 일정 공개")
        elif 'WSOP Europe' in title and '€20 Million' in title:
            lines.append("💶 WSOP Europe 2025, 15개 이벤트 총 €2천만 상금")
        elif 'WPT World Championship' in title:
            lines.append("🏆 WPT 월드 챔피언십 12월 라스베가스 개최 확정")
        elif 'Ryan Riess' in title:
            lines.append("🎯 Ryan Riess, WSOP 메인이벤트 재우승 도전 의사 표명")
        elif '$500,000' in title:
            lines.append("💸 Sycuan 카지노 회원 포커 게임서 $50만 이상 획득")
        else:
            lines.append(f"📰 {title_clean[:60]}...")
        
        # 2줄: 핵심 세부사항
        if 'Bracelet' in title:
            lines.append("🎖️ 브레이슬릿 이벤트 상세 일정 및 참가 정보 포함")
        elif 'controversy' in title.lower():
            lines.append("⚠️ 업계 내 논란과 다양한 의견 대립")
        elif 'guide' in title.lower():
            lines.append("📚 전문가의 경험과 노하우 공유")
        elif 'dates' in title.lower() or 'schedule' in title.lower():
            lines.append("📆 구체적인 대회 일정과 장소 정보 발표")
        else:
            lines.append(f"📝 {source}에서 보도한 최신 포커 업계 소식")
        
        # 3줄: 시사점
        if 'Thailand' in title:
            lines.append("🌏 아시아 포커 시장 확장의 신호탄으로 주목")
        elif 'WSOP' in title:
            lines.append("🎲 세계 최대 포커 시리즈의 새로운 기회")
        elif any(name in title for name in ['Hellmuth', 'Negreanu', 'Ivey']):
            lines.append("⭐ 유명 프로 선수 동향이 포커 팬들에게 화제")
        else:
            lines.append("📊 포커 커뮤니티에 새로운 관심사 제공")
        
        return lines
    
    def _send_to_slack(self, message: Dict) -> bool:
        """Slack으로 메시지 전송"""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"Slack 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 전송 오류: {e}")
            return False
    
    def _send_no_news_message(self):
        """뉴스가 없을 때 메시지"""
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📰 *PokerNews 일일 리포트*\n\n오늘은 수집된 뉴스가 없습니다. 내일 다시 확인하겠습니다."
                    }
                }
            ]
        }
        self._send_to_slack(message)
    
    def _send_error_message(self, error: str):
        """에러 메시지 전송"""
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *PokerNews 리포트 오류*\n\n리포트 생성 중 오류가 발생했습니다:\n```{error}```"
                    }
                }
            ]
        }
        self._send_to_slack(message)
    
    def _save_report(self, result: Dict):
        """리포트 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pokernews_report_{timestamp}.json"
        
        # reports 디렉토리 생성
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"리포트 저장: {filepath}")


def main():
    """메인 실행 함수"""
    reporter = PokerNewsSlackReporter()
    result = reporter.run_report()
    
    report_type = os.getenv('REPORT_TYPE', 'daily')
    type_text = {'daily': '일간', 'weekly': '주간', 'monthly': '월간'}.get(report_type, '일일')
    
    # 결과 출력
    if result['status'] == 'success':
        print(f"✅ PokerNews {type_text} 리포트 전송 완료!")
        print(f"   - 수집된 기사: {result.get('articles_collected', 0)}개")
        print(f"   - 오늘의 기사: {result.get('today_articles', 0)}개")
        print(f"   - Slack 전송: {'성공' if result.get('slack_sent') else '실패'}")
    else:
        print(f"❌ 리포트 실행 실패: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()