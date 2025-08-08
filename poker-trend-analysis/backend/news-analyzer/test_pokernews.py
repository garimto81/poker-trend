#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews 시스템 테스트
각 모듈의 기능을 테스트하는 스크립트
"""

import os
import sys
import json
import logging
from datetime import datetime

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pokernews_collector import PokerNewsCollector
from pokernews_ai_analyzer import PokerNewsAIAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_collector():
    """뉴스 수집기 테스트"""
    print("\n" + "="*50)
    print("1. PokerNews 수집기 테스트")
    print("="*50)
    
    collector = PokerNewsCollector()
    
    # 최신 뉴스 5개 수집
    articles = collector.collect_latest_news(max_articles=5)
    
    if articles:
        print(f"✅ 수집 성공: {len(articles)}개 기사")
        for i, article in enumerate(articles, 1):
            print(f"\n[기사 {i}]")
            print(f"제목: {article.get('title', 'No title')}")
            print(f"URL: {article.get('url', 'No URL')}")
            print(f"섹션: {article.get('section', 'Unknown')}")
            print(f"날짜: {article.get('published_date', 'Unknown')}")
            if article.get('summary'):
                print(f"요약: {article['summary'][:100]}...")
    else:
        print("❌ 수집 실패: 기사를 가져올 수 없습니다")
        return False
    
    # 오늘 날짜 필터링 테스트
    today_articles = collector.filter_today_news(articles)
    print(f"\n오늘/어제 날짜 기사: {len(today_articles)}개")
    
    return True

def test_ai_analyzer():
    """AI 분석기 테스트"""
    print("\n" + "="*50)
    print("2. Gemini AI 분석기 테스트")
    print("="*50)
    
    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다")
        print("   .env 파일에 GEMINI_API_KEY를 추가하세요")
        return False
    
    # 테스트용 기사 데이터
    test_articles = [
        {
            'title': 'Phil Ivey Wins Major Tournament at Triton Series',
            'summary': 'Phil Ivey takes down the $100k buy-in event for $2.5 million.',
            'section': 'tours',
            'tags': ['Triton', 'Phil Ivey', 'High Roller'],
            'published_date': datetime.now().isoformat()
        },
        {
            'title': 'New Online Poker Regulations in Michigan',
            'summary': 'Michigan approves new online poker regulations allowing interstate play.',
            'section': 'online-poker',
            'tags': ['Regulation', 'Michigan', 'Online Poker'],
            'published_date': datetime.now().isoformat()
        },
        {
            'title': 'Strategy: Exploiting Weak Players in Small Stakes',
            'summary': 'Learn how to maximize profit against recreational players.',
            'section': 'strategy',
            'tags': ['Strategy', 'Cash Game'],
            'published_date': datetime.now().isoformat()
        }
    ]
    
    try:
        analyzer = PokerNewsAIAnalyzer()
        result = analyzer.analyze_news_trends(test_articles)
        
        if result.get('status') == 'error':
            print(f"❌ AI 분석 실패: {result.get('error')}")
            return False
        
        print("✅ AI 분석 성공!")
        print("\n[분석 결과]")
        
        if result.get('core_trends'):
            print("\n🎯 핵심 트렌드:")
            for trend in result['core_trends'][:3]:
                print(f"  • {trend}")
        
        if result.get('summary'):
            print(f"\n📝 요약: {result['summary']}")
        
        # 콘텐츠 추천 테스트
        recommendations = analyzer.generate_content_recommendations(result)
        if recommendations:
            print("\n💡 콘텐츠 추천:")
            for rec in recommendations[:3]:
                print(f"  • {rec['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI 분석 오류: {e}")
        return False

def test_integration():
    """통합 테스트 (수집 → 분석)"""
    print("\n" + "="*50)
    print("3. 통합 테스트 (수집 → AI 분석)")
    print("="*50)
    
    try:
        # 1. 뉴스 수집
        print("\n뉴스 수집 중...")
        collector = PokerNewsCollector()
        articles = collector.collect_latest_news(max_articles=10)
        
        if not articles:
            print("❌ 수집된 뉴스가 없습니다")
            return False
        
        print(f"✅ {len(articles)}개 기사 수집 완료")
        
        # 2. AI 분석
        print("\nAI 분석 중...")
        analyzer = PokerNewsAIAnalyzer()
        analysis = analyzer.analyze_news_trends(articles[:5])  # 상위 5개만 분석
        
        if analysis.get('status') == 'error':
            print(f"❌ 분석 실패: {analysis.get('error')}")
            return False
        
        print("✅ AI 분석 완료")
        
        # 3. 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"test_integration_{timestamp}.json"
        
        result = {
            'test_date': datetime.now().isoformat(),
            'articles_collected': len(articles),
            'articles_analyzed': min(5, len(articles)),
            'analysis': analysis,
            'sample_articles': articles[:3]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 통합 테스트 성공!")
        print(f"   결과 저장: {output_file}")
        
        # 주요 결과 출력
        if analysis.get('core_trends'):
            print("\n[주요 트렌드]")
            for i, trend in enumerate(analysis['core_trends'][:3], 1):
                print(f"{i}. {trend}")
        
        return True
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        return False

def test_slack_message():
    """Slack 메시지 포맷 테스트 (실제 전송 없음)"""
    print("\n" + "="*50)
    print("4. Slack 메시지 포맷 테스트")
    print("="*50)
    
    from pokernews_slack_reporter import PokerNewsSlackReporter
    
    # 테스트 데이터
    test_analysis = {
        'core_trends': [
            'Phil Ivey가 Triton Series에서 우승하며 복귀 신호',
            '미시간 주 온라인 포커 규제 완화로 시장 확대 예상',
            '소액 스테이크 전략 콘텐츠 수요 증가'
        ],
        'tournaments': [
            'Triton Series Montenegro 진행 중',
            'WSOP Online 예선 시작'
        ],
        'notable_players': [
            'Phil Ivey - Triton 우승',
            'Daniel Negreanu - 새로운 마스터클래스 출시'
        ],
        'market_trends': [
            '미국 온라인 포커 시장 성장세',
            'GGPoker 아시아 확장'
        ],
        'content_ideas': [
            'Phil Ivey 플레이 스타일 분석',
            '미시간 온라인 포커 가이드',
            '소액 스테이크 수익 극대화 전략'
        ],
        'summary': '하이롤러 토너먼트 활성화와 미국 온라인 포커 규제 완화가 주요 트렌드'
    }
    
    test_articles = [
        {
            'title': 'Test Article 1',
            'url': 'https://pokernews.com/test1',
            'section': 'news'
        },
        {
            'title': 'Test Article 2',
            'url': 'https://pokernews.com/test2',
            'section': 'strategy'
        }
    ]
    
    try:
        # Slack 메시지 생성 (전송하지 않음)
        reporter = PokerNewsSlackReporter(slack_webhook_url="http://test.webhook.url")
        message = reporter._create_slack_message(test_analysis, test_articles)
        
        print("✅ Slack 메시지 포맷 생성 성공")
        print("\n[메시지 구조]")
        print(f"블록 수: {len(message.get('blocks', []))}")
        
        # 메시지 내용 미리보기
        for block in message.get('blocks', [])[:3]:
            if block.get('type') == 'header':
                print(f"헤더: {block.get('text', {}).get('text', '')}")
            elif block.get('type') == 'section':
                text = block.get('text', {}).get('text', '')
                if text:
                    print(f"섹션: {text[:50]}...")
        
        # JSON 파일로 저장
        with open('test_slack_message.json', 'w', encoding='utf-8') as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        print("\nSlack 메시지 포맷이 test_slack_message.json에 저장되었습니다")
        
        return True
        
    except Exception as e:
        print(f"❌ Slack 메시지 포맷 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("PokerNews 시스템 테스트 시작")
    print("="*60)
    
    # 테스트 실행
    tests = [
        ("수집기", test_collector),
        ("AI 분석", test_ai_analyzer),
        ("통합", test_integration),
        ("Slack 포맷", test_slack_message)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} 테스트 실행 중 오류: {e}")
            results[name] = False
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    for name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    # 전체 결과
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패. 로그를 확인하세요.")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)