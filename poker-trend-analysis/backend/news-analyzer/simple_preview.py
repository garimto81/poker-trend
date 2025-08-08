#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 포커 뉴스 미리보기
"""

import json
from datetime import datetime
from pokernews_rss_collector import PokerNewsRSSCollector

def main():
    print("\n" + "="*60)
    print("포커 뉴스 미리보기")
    print("="*60)
    
    # RSS 수집기 초기화
    collector = PokerNewsRSSCollector()
    
    # 뉴스 수집
    print("\n[1] 뉴스 수집 중...")
    articles = collector.collect_from_rss(max_articles=10)
    
    if not articles:
        print("RSS 수집 실패. 모의 데이터 사용...")
        articles = collector.collect_mock_news()
    
    print(f"=> {len(articles)}개 기사 수집 완료\n")
    
    # 수집된 기사 표시
    print("-"*60)
    print("수집된 뉴스 목록:")
    print("-"*60)
    
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}] {article.get('title', 'No title')}")
        print(f"    출처: {article.get('source', 'Unknown')}")
        print(f"    날짜: {article.get('published_date', 'Unknown')}")
        
        if article.get('summary'):
            summary = article['summary'][:100]
            if len(article['summary']) > 100:
                summary += "..."
            print(f"    요약: {summary}")
        
        print(f"    URL: {article.get('url', 'No URL')[:80]}...")
    
    # Slack 메시지 미리보기
    print("\n" + "="*60)
    print("Slack 메시지 미리보기")
    print("="*60)
    
    print("\n[헤더]")
    print("포커 뉴스 일일 트렌드 분석")
    print(f"{datetime.now().strftime('%Y년 %m월 %d일')} | 분석 기사: {len(articles)}개")
    
    print("\n[주요 뉴스]")
    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', 'No title')
        if len(title) > 60:
            title = title[:60] + "..."
        print(f"{i}. {title}")
    
    print("\n[AI 분석 섹션]")
    print("=> AI 분석을 건너뛰었습니다 (--skip-ai 옵션)")
    print("=> 실제 실행 시 Gemini AI가 트렌드를 분석합니다")
    
    # JSON 파일 저장
    preview_data = {
        'preview_date': datetime.now().isoformat(),
        'articles_count': len(articles),
        'articles': articles[:5]  # 상위 5개만 저장
    }
    
    filename = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(preview_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[저장됨] {filename}")
    print("\n" + "="*60)
    print("미리보기 완료!")
    print("실제 Slack 전송: python pokernews_slack_reporter.py")
    print("="*60)

if __name__ == "__main__":
    main()