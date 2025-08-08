#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews 미리보기
Slack 전송 전 데이터 확인 및 미리보기
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pokernews_collector import PokerNewsCollector
from pokernews_rss_collector import PokerNewsRSSCollector
from pokernews_ai_analyzer import PokerNewsAIAnalyzer

# 환경 변수 로드
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class PokerNewsPreview:
    """PokerNews 미리보기"""
    
    def __init__(self):
        self.collector = PokerNewsCollector()
        self.rss_collector = PokerNewsRSSCollector()
        self.analyzer = None
        # Gemini API 키가 있을 때만 AI 분석기 초기화
        if os.getenv('GEMINI_API_KEY'):
            self.analyzer = PokerNewsAIAnalyzer()
        
    def preview_data_collection(self, max_articles: int = 10) -> Dict:
        """데이터 수집 미리보기"""
        print("\n" + "="*60)
        print("📰 PokerNews 데이터 수집 미리보기")
        print("="*60)
        
        print("\n⏳ 뉴스 수집 중... (최대 " + str(max_articles) + "개)")
        
        # RSS 수집 시도
        print("📡 RSS 피드에서 수집 시도...")
        articles = self.rss_collector.collect_from_rss(max_articles=max_articles)
        
        # RSS 실패 시 웹 스크래핑 시도
        if not articles:
            print("🌐 웹 스크래핑 시도...")
            articles = self.collector.collect_latest_news(max_articles=max_articles)
        
        # 그래도 없으면 모의 데이터
        if not articles:
            print("📋 모의 데이터 사용...")
            articles = self.rss_collector.collect_mock_news()
        
        if not articles:
            print("\n❌ 수집된 뉴스가 없습니다.")
            return {'status': 'no_data', 'articles': []}
        
        # 수집 결과 표시
        print(f"\n✅ 총 {len(articles)}개 기사 수집 완료!")
        print("\n" + "-"*60)
        
        # 섹션별 분류
        sections = {}
        for article in articles:
            section = article.get('section', 'unknown')
            if section not in sections:
                sections[section] = []
            sections[section].append(article)
        
        print("\n📊 섹션별 분포:")
        for section, items in sections.items():
            print(f"  • {section}: {len(items)}개")
        
        # 오늘/어제 날짜 필터링
        today_articles = self.collector.filter_today_news(articles)
        print(f"\n📅 최근 기사 (오늘/어제): {len(today_articles)}개")
        
        print("\n" + "-"*60)
        print("\n📋 수집된 기사 목록:\n")
        
        # 기사 목록 표시
        for i, article in enumerate(articles, 1):
            print(f"{i}. [{article.get('section', 'unknown')}] {article.get('title', 'No title')}")
            
            # URL 표시
            url = article.get('url', 'No URL')
            if url != 'No URL':
                print(f"   🔗 {url}")
            
            # 날짜 표시
            date = article.get('published_date', 'Unknown date')
            print(f"   📅 {date}")
            
            # 요약 표시 (있을 경우)
            if article.get('summary'):
                summary = article['summary'][:150]
                if len(article['summary']) > 150:
                    summary += "..."
                print(f"   📝 {summary}")
            
            # 태그 표시 (있을 경우)
            if article.get('tags'):
                tags = ', '.join(article['tags'][:5])
                print(f"   🏷️ {tags}")
            
            print()
        
        return {
            'status': 'success',
            'articles': articles,
            'today_articles': today_articles,
            'sections': sections
        }
    
    def preview_ai_analysis(self, articles: List[Dict]) -> Dict:
        """AI 분석 미리보기"""
        print("\n" + "="*60)
        print("🤖 Gemini AI 분석 미리보기")
        print("="*60)
        
        if not self.analyzer:
            print("\n⚠️ Gemini API 키가 설정되지 않았습니다.")
            print("AI 분석을 건너뜁니다.")
            return {'status': 'skipped', 'reason': 'no_api_key'}
        
        if not articles:
            print("\n❌ 분석할 기사가 없습니다.")
            return {'status': 'no_data'}
        
        print(f"\n⏳ {len(articles[:10])}개 기사 AI 분석 중...")
        
        try:
            # AI 분석 실행
            analysis = self.analyzer.analyze_news_trends(articles[:10])
            
            if analysis.get('status') == 'error':
                print(f"\n❌ AI 분석 실패: {analysis.get('error')}")
                if analysis.get('fallback_summary'):
                    print("\n📝 대체 요약:")
                    print(analysis['fallback_summary'])
                return analysis
            
            print("\n✅ AI 분석 완료!")
            print("\n" + "-"*60)
            
            # 분석 결과 표시
            print("\n📊 AI 분석 결과:\n")
            
            # 핵심 트렌드
            if analysis.get('core_trends'):
                print("🎯 핵심 트렌드:")
                for i, trend in enumerate(analysis['core_trends'], 1):
                    print(f"  {i}. {trend}")
                print()
            
            # 토너먼트
            if analysis.get('tournaments'):
                print("🏆 주요 토너먼트:")
                for tournament in analysis['tournaments']:
                    print(f"  • {tournament}")
                print()
            
            # 주목할 선수
            if analysis.get('notable_players'):
                print("🌟 주목할 선수:")
                for player in analysis['notable_players']:
                    print(f"  • {player}")
                print()
            
            # 시장 동향
            if analysis.get('market_trends'):
                print("💼 시장 동향:")
                for trend in analysis['market_trends']:
                    print(f"  • {trend}")
                print()
            
            # 향후 전망
            if analysis.get('future_outlook'):
                print("🔮 향후 전망:")
                for outlook in analysis['future_outlook']:
                    print(f"  • {outlook}")
                print()
            
            # 콘텐츠 아이디어
            if analysis.get('content_ideas'):
                print("💡 콘텐츠 아이디어:")
                for i, idea in enumerate(analysis['content_ideas'], 1):
                    print(f"  {i}. {idea}")
                print()
            
            # 요약
            if analysis.get('summary'):
                print("📝 한 줄 요약:")
                print(f"  {analysis['summary']}")
                print()
            
            return analysis
            
        except Exception as e:
            print(f"\n❌ AI 분석 중 오류 발생: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def preview_slack_message(self, analysis: Dict, articles: List[Dict]) -> Dict:
        """Slack 메시지 미리보기"""
        print("\n" + "="*60)
        print("💬 Slack 메시지 미리보기")
        print("="*60)
        
        from pokernews_slack_reporter import PokerNewsSlackReporter
        
        try:
            # 임시 Webhook URL로 리포터 생성 (실제 전송하지 않음)
            reporter = PokerNewsSlackReporter(slack_webhook_url="http://preview.webhook.url")
            
            # Slack 메시지 생성
            message = reporter._create_slack_message(analysis, articles[:10])
            
            print("\n📱 Slack 메시지 구조:")
            print(f"  • 블록 수: {len(message.get('blocks', []))}")
            print(f"  • 메시지 타입: Block Kit (리치 포맷)")
            
            print("\n" + "-"*60)
            print("\n📄 메시지 내용 미리보기:\n")
            
            # 블록별 내용 표시
            for block in message.get('blocks', []):
                if block.get('type') == 'header':
                    header_text = block.get('text', {}).get('text', '')
                    print(f"\n{header_text}")
                    print("="*len(header_text))
                    
                elif block.get('type') == 'context':
                    elements = block.get('elements', [])
                    for elem in elements:
                        if elem.get('type') == 'mrkdwn':
                            context_text = elem.get('text', '')
                            # Slack 마크다운 제거
                            context_text = context_text.replace('*', '')
                            print(f"\n{context_text}")
                            
                elif block.get('type') == 'section':
                    text_obj = block.get('text', {})
                    if text_obj.get('type') == 'mrkdwn':
                        section_text = text_obj.get('text', '')
                        # Slack 마크다운 간단히 변환
                        section_text = section_text.replace('*', '')
                        print(f"\n{section_text}")
                        
                elif block.get('type') == 'divider':
                    print("-"*40)
            
            # JSON 파일로 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            preview_file = f"preview_slack_message_{timestamp}.json"
            
            with open(preview_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'preview_date': datetime.now().isoformat(),
                    'message': message,
                    'articles_count': len(articles),
                    'analysis_status': analysis.get('status', 'unknown')
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 전체 메시지가 '{preview_file}'에 저장되었습니다.")
            
            return {
                'status': 'success',
                'message': message,
                'preview_file': preview_file
            }
            
        except Exception as e:
            print(f"\n❌ Slack 메시지 생성 실패: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_full_preview(self, max_articles: int = 10, skip_ai: bool = False) -> Dict:
        """전체 미리보기 실행"""
        print("\n" + "="*60)
        print("\n=== PokerNews 시스템 전체 미리보기 ===")
        print("\n" + "="*60)
        
        start_time = time.time()
        
        # 1. 데이터 수집
        collection_result = self.preview_data_collection(max_articles)
        
        if collection_result['status'] != 'success':
            print("\n⚠️ 데이터 수집 실패로 미리보기를 종료합니다.")
            return collection_result
        
        articles = collection_result['articles']
        
        # 2. AI 분석 (선택적)
        if skip_ai:
            print("\n⏭️ AI 분석을 건너뜁니다.")
            analysis = {
                'status': 'skipped',
                'core_trends': ['AI 분석 건너뜀'],
                'summary': 'AI 분석이 실행되지 않았습니다.'
            }
        else:
            analysis = self.preview_ai_analysis(articles)
        
        # 3. Slack 메시지 미리보기
        slack_result = self.preview_slack_message(analysis, articles)
        
        # 실행 시간
        elapsed_time = time.time() - start_time
        
        # 최종 요약
        print("\n" + "="*60)
        print("📊 미리보기 완료 요약")
        print("="*60)
        
        print(f"\n✅ 전체 실행 시간: {elapsed_time:.2f}초")
        print(f"📰 수집된 기사: {len(articles)}개")
        print(f"📅 오늘/어제 기사: {len(collection_result.get('today_articles', []))}개")
        
        if not skip_ai and analysis.get('status') != 'error':
            print(f"🤖 AI 분석: 완료")
        else:
            print(f"🤖 AI 분석: 건너뜀 또는 실패")
        
        print(f"💬 Slack 메시지: {'준비 완료' if slack_result.get('status') == 'success' else '실패'}")
        
        if slack_result.get('preview_file'):
            print(f"\n📁 미리보기 파일: {slack_result['preview_file']}")
        
        print("\n" + "="*60)
        
        # 사용자 확인
        print("\n❓ Slack으로 전송하시겠습니까?")
        print("   (이 미리보기 스크립트는 전송하지 않습니다)")
        print("   실제 전송: python pokernews_slack_reporter.py")
        
        return {
            'status': 'preview_complete',
            'collection': collection_result,
            'analysis': analysis,
            'slack': slack_result,
            'elapsed_time': elapsed_time
        }


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PokerNews 미리보기')
    parser.add_argument('--articles', type=int, default=10, help='수집할 기사 수 (기본: 10)')
    parser.add_argument('--skip-ai', action='store_true', help='AI 분석 건너뛰기')
    parser.add_argument('--collection-only', action='store_true', help='수집만 실행')
    
    args = parser.parse_args()
    
    preview = PokerNewsPreview()
    
    if args.collection_only:
        # 수집만 실행
        result = preview.preview_data_collection(args.articles)
    else:
        # 전체 미리보기
        result = preview.run_full_preview(
            max_articles=args.articles,
            skip_ai=args.skip_ai
        )
    
    # 결과를 JSON 파일로 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f"preview_result_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        # datetime 객체를 문자열로 변환
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        json.dump(result, f, ensure_ascii=False, indent=2, default=json_serial)
    
    print(f"\n💾 전체 결과가 '{result_file}'에 저장되었습니다.")
    
    return result


if __name__ == "__main__":
    main()