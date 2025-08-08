#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews RSS 피드 수집기
RSS를 활용한 안정적인 뉴스 수집
"""

import os
import sys
import json
import logging
import requests
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from bs4 import BeautifulSoup

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerNewsRSSCollector:
    """PokerNews RSS 수집기"""
    
    def __init__(self):
        # 일반적인 포커 뉴스 사이트 RSS 피드
        self.rss_feeds = [
            # PokerNews RSS (있을 경우)
            "https://www.pokernews.com/rss.xml",
            "https://www.pokernews.com/news/rss",
            
            # 대체 포커 뉴스 소스
            "https://www.cardplayer.com/rss",
            "https://www.pokerstrategy.com/rss/",
            
            # Google News 포커 검색
            "https://news.google.com/rss/search?q=poker+tournament+WSOP+when:1d&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=poker+news+latest&hl=en-US&gl=US&ceid=US:en"
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def collect_from_rss(self, max_articles: int = 20) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        all_articles = []
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"RSS 피드 시도: {feed_url}")
                
                # RSS 피드 파싱
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"RSS 파싱 경고: {feed_url}")
                    continue
                
                # 엔트리가 있는지 확인
                if not feed.entries:
                    logger.info(f"엔트리 없음: {feed_url}")
                    continue
                
                logger.info(f"발견된 엔트리: {len(feed.entries)}개")
                
                # 각 엔트리 처리
                for entry in feed.entries[:10]:  # 각 피드에서 최대 10개
                    article = self._parse_rss_entry(entry, feed_url)
                    if article:
                        all_articles.append(article)
                
                time.sleep(0.5)  # 서버 부하 방지
                
            except Exception as e:
                logger.error(f"RSS 피드 처리 실패 {feed_url}: {e}")
                continue
        
        # 중복 제거
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 날짜순 정렬
        unique_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
        
        logger.info(f"총 {len(unique_articles)}개의 고유한 기사 수집")
        return unique_articles[:max_articles]
    
    def _parse_rss_entry(self, entry, feed_url: str) -> Optional[Dict]:
        """RSS 엔트리 파싱"""
        try:
            article = {
                'source': self._get_source_name(feed_url),
                'collected_at': datetime.now().isoformat()
            }
            
            # 제목
            article['title'] = entry.get('title', '').strip()
            if not article['title']:
                return None
            
            # URL
            article['url'] = entry.get('link', '')
            if not article['url']:
                return None
            
            # 요약/설명
            if hasattr(entry, 'summary'):
                # HTML 태그 제거
                soup = BeautifulSoup(entry.summary, 'html.parser')
                article['summary'] = soup.get_text(strip=True)[:500]
            elif hasattr(entry, 'description'):
                soup = BeautifulSoup(entry.description, 'html.parser')
                article['summary'] = soup.get_text(strip=True)[:500]
            
            # 날짜
            if hasattr(entry, 'published_parsed'):
                article['published_timestamp'] = time.mktime(entry.published_parsed)
                article['published_date'] = datetime.fromtimestamp(
                    article['published_timestamp']
                ).strftime('%Y-%m-%d %H:%M')
            elif hasattr(entry, 'updated_parsed'):
                article['published_timestamp'] = time.mktime(entry.updated_parsed)
                article['published_date'] = datetime.fromtimestamp(
                    article['published_timestamp']
                ).strftime('%Y-%m-%d %H:%M')
            else:
                article['published_timestamp'] = time.time()
                article['published_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # 카테고리/태그
            tags = []
            if hasattr(entry, 'tags'):
                for tag in entry.tags:
                    if hasattr(tag, 'term'):
                        tags.append(tag.term)
            if tags:
                article['tags'] = tags
            
            # 저자
            if hasattr(entry, 'author'):
                article['author'] = entry.author
            
            # 포커 관련 여부 확인
            if not self._is_poker_related(article):
                return None
            
            return article
            
        except Exception as e:
            logger.debug(f"엔트리 파싱 실패: {e}")
            return None
    
    def _get_source_name(self, feed_url: str) -> str:
        """피드 URL에서 소스 이름 추출"""
        if 'pokernews' in feed_url.lower():
            return 'PokerNews'
        elif 'cardplayer' in feed_url.lower():
            return 'CardPlayer'
        elif 'pokerstrategy' in feed_url.lower():
            return 'PokerStrategy'
        elif 'google' in feed_url.lower():
            return 'Google News'
        else:
            return 'Unknown'
    
    def _is_poker_related(self, article: Dict) -> bool:
        """포커 관련 기사인지 확인"""
        poker_keywords = [
            'poker', 'wsop', 'wpt', 'ept', 'tournament',
            'holdem', "hold'em", 'omaha', 'stud',
            'pokerstars', 'ggpoker', 'partypoker',
            'bluff', 'all-in', 'fold', 'raise',
            'bracelet', 'final table', 'main event'
        ]
        
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # 포커 키워드가 있는지 확인
        for keyword in poker_keywords:
            if keyword in text:
                return True
        
        return False
    
    def collect_mock_news(self) -> List[Dict]:
        """테스트용 모의 뉴스 데이터"""
        mock_articles = [
            {
                'title': 'Daniel Negreanu Wins WSOP Online Bracelet Event',
                'url': 'https://example.com/negreanu-wsop-win',
                'summary': 'Daniel Negreanu captured his 7th WSOP bracelet in the $1,500 Online event, defeating a field of 2,483 players.',
                'source': 'Mock News',
                'published_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tags': ['WSOP', 'Daniel Negreanu', 'Online Poker']
            },
            {
                'title': 'GGPoker Announces $100 Million GTD Super MILLION$ Week',
                'url': 'https://example.com/ggpoker-super-millions',
                'summary': 'GGPoker revealed details of their biggest online tournament series with $100 million in guarantees.',
                'source': 'Mock News',
                'published_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tags': ['GGPoker', 'Tournament', 'Online']
            },
            {
                'title': 'Phil Ivey Returns to High Stakes Cash Games',
                'url': 'https://example.com/ivey-cash-games',
                'summary': 'Poker legend Phil Ivey has been spotted playing high stakes cash games in Las Vegas.',
                'source': 'Mock News',
                'published_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                'tags': ['Phil Ivey', 'Cash Games', 'Las Vegas']
            },
            {
                'title': 'Poker Strategy: Understanding GTO vs Exploitative Play',
                'url': 'https://example.com/gto-vs-exploitative',
                'summary': 'A deep dive into when to use Game Theory Optimal (GTO) strategy versus exploitative play.',
                'source': 'Mock News',
                'published_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tags': ['Strategy', 'GTO', 'Education']
            },
            {
                'title': 'EPT Barcelona Schedule Released with Record Prize Pools',
                'url': 'https://example.com/ept-barcelona',
                'summary': 'The European Poker Tour returns to Barcelona with the biggest guarantees in EPT history.',
                'source': 'Mock News',
                'published_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tags': ['EPT', 'Barcelona', 'Tournament']
            }
        ]
        
        for article in mock_articles:
            article['collected_at'] = datetime.now().isoformat()
            article['published_timestamp'] = time.time()
        
        return mock_articles


def main():
    """테스트 실행"""
    collector = PokerNewsRSSCollector()
    
    print("RSS 피드에서 뉴스 수집 시도...")
    articles = collector.collect_from_rss(max_articles=20)
    
    # RSS가 실패하면 모의 데이터 사용
    if not articles:
        print("\nRSS 수집 실패. 모의 데이터 사용...")
        articles = collector.collect_mock_news()
    
    # 결과 출력
    print(f"\n수집된 뉴스: {len(articles)}개\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article.get('source', 'Unknown')}] {article.get('title', 'No title')}")
        print(f"   URL: {article.get('url', 'No URL')}")
        print(f"   날짜: {article.get('published_date', 'Unknown')}")
        if article.get('summary'):
            print(f"   요약: {article['summary'][:100]}...")
        if article.get('tags'):
            print(f"   태그: {', '.join(article['tags'][:5])}")
        print()
    
    # JSON 파일로 저장
    output_file = f"pokernews_rss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()