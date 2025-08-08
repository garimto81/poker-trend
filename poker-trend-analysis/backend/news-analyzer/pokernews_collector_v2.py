#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews 뉴스 수집기 v2
개선된 스크래핑 로직
"""

import os
import sys
import json
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from urllib.parse import urljoin, urlparse
import re

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerNewsCollectorV2:
    """개선된 PokerNews 뉴스 수집기"""
    
    def __init__(self):
        self.base_url = "https://www.pokernews.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def collect_latest_news(self, max_articles: int = 20) -> List[Dict]:
        """최신 뉴스 수집 - 개선된 버전"""
        logger.info(f"PokerNews에서 최신 뉴스 {max_articles}개 수집 시작")
        
        articles = []
        
        # 메인 뉴스 페이지에서 직접 수집
        try:
            url = f"{self.base_url}/news/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 링크 찾기 (연도가 포함된 URL 패턴)
            news_pattern = re.compile(r'/news/\d{4}/\d{2}/')
            
            processed_urls = set()
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                
                # 뉴스 패턴 매칭
                if news_pattern.search(href):
                    # 전체 URL 생성
                    full_url = urljoin(self.base_url, href)
                    
                    # 중복 체크
                    if full_url in processed_urls:
                        continue
                    processed_urls.add(full_url)
                    
                    # 기사 정보 추출
                    article = self._extract_article_info(link, full_url, soup)
                    if article:
                        articles.append(article)
                        
                        if len(articles) >= max_articles:
                            break
            
            # 추가 섹션에서 수집
            if len(articles) < max_articles:
                sections = ['/strategy/', '/tours/', '/online-poker/']
                for section in sections:
                    remaining = max_articles - len(articles)
                    if remaining <= 0:
                        break
                        
                    section_articles = self._collect_section_articles(section, remaining)
                    articles.extend(section_articles)
                    time.sleep(0.5)  # 서버 부하 방지
            
        except Exception as e:
            logger.error(f"뉴스 수집 실패: {e}")
        
        # 날짜순 정렬
        articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        logger.info(f"총 {len(articles)}개의 뉴스 기사 수집 완료")
        return articles[:max_articles]
    
    def _extract_article_info(self, link_element, url: str, soup: BeautifulSoup) -> Optional[Dict]:
        """링크 요소에서 기사 정보 추출"""
        try:
            article = {
                'url': url,
                'source': 'PokerNews',
                'collected_at': datetime.now().isoformat()
            }
            
            # 제목 추출
            title_text = link_element.get_text(strip=True)
            if title_text and len(title_text) > 10:  # 너무 짧은 텍스트 제외
                article['title'] = title_text
            else:
                # 부모 요소에서 제목 찾기
                parent = link_element.find_parent(['div', 'article', 'li'])
                if parent:
                    h_tag = parent.find(['h1', 'h2', 'h3', 'h4'])
                    if h_tag:
                        article['title'] = h_tag.get_text(strip=True)
            
            if not article.get('title'):
                return None
            
            # URL에서 날짜 추출
            date_match = re.search(r'/(\d{4})/(\d{2})/', url)
            if date_match:
                year, month = date_match.groups()
                article['published_date'] = f"{year}-{month}"
            
            # 섹션 추출
            if '/strategy/' in url:
                article['section'] = 'strategy'
            elif '/tours/' in url:
                article['section'] = 'tours'
            elif '/online-poker/' in url:
                article['section'] = 'online-poker'
            else:
                article['section'] = 'news'
            
            # 부모 요소에서 추가 정보 추출
            parent = link_element.find_parent(['div', 'article', 'li'])
            if parent:
                # 요약 찾기
                p_tag = parent.find('p')
                if p_tag:
                    summary = p_tag.get_text(strip=True)
                    if summary and len(summary) > 20:
                        article['summary'] = summary[:500]
                
                # 이미지 찾기
                img = parent.find('img')
                if img:
                    img_src = img.get('src') or img.get('data-src')
                    if img_src:
                        article['image_url'] = urljoin(self.base_url, img_src)
            
            return article
            
        except Exception as e:
            logger.debug(f"기사 정보 추출 실패: {e}")
            return None
    
    def _collect_section_articles(self, section_path: str, limit: int = 5) -> List[Dict]:
        """특정 섹션의 기사 수집"""
        articles = []
        
        try:
            url = urljoin(self.base_url, section_path)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 링크 패턴
            news_pattern = re.compile(r'/\d{4}/\d{2}/')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                
                if news_pattern.search(href) and section_path.strip('/') in href:
                    full_url = urljoin(self.base_url, href)
                    article = self._extract_article_info(link, full_url, soup)
                    if article:
                        articles.append(article)
                        if len(articles) >= limit:
                            break
            
        except Exception as e:
            logger.error(f"섹션 {section_path} 수집 실패: {e}")
        
        return articles
    
    def get_article_content(self, article_url: str) -> Optional[str]:
        """기사 본문 가져오기"""
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 본문 찾기
            content_selectors = [
                'div.article-content',
                'div.article-body',
                'div.entry-content',
                'article',
                'main'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    # 불필요한 요소 제거
                    for unwanted in content.find_all(['script', 'style']):
                        unwanted.decompose()
                    
                    text = content.get_text(separator='\n', strip=True)
                    if len(text) > 100:
                        return text[:5000]
            
            return None
            
        except Exception as e:
            logger.error(f"기사 내용 가져오기 실패: {e}")
            return None
    
    def filter_recent_news(self, articles: List[Dict], days_back: int = 2) -> List[Dict]:
        """최근 뉴스만 필터링"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        filtered = []
        for article in articles:
            # URL에서 날짜 추출 시도
            url = article.get('url', '')
            date_match = re.search(r'/(\d{4})/(\d{2})/.*?-(\d{2})', url)
            
            if date_match:
                year, month, day = date_match.groups()
                try:
                    article_date = datetime(int(year), int(month), int(day))
                    if article_date >= cutoff_date:
                        article['published_date'] = article_date.strftime('%Y-%m-%d')
                        filtered.append(article)
                except:
                    # 날짜 파싱 실패 시 포함
                    filtered.append(article)
            else:
                # 날짜를 알 수 없으면 포함 (최신일 가능성)
                filtered.append(article)
        
        logger.info(f"최근 {days_back}일 기사: {len(filtered)}개")
        return filtered


def main():
    """테스트 실행"""
    collector = PokerNewsCollectorV2()
    
    # 최신 뉴스 수집
    print("뉴스 수집 중...")
    news = collector.collect_latest_news(max_articles=10)
    
    # 결과 출력
    print(f"\n수집된 뉴스: {len(news)}개\n")
    for i, article in enumerate(news, 1):
        print(f"{i}. {article.get('title', 'No title')}")
        print(f"   URL: {article.get('url', 'No URL')}")
        print(f"   섹션: {article.get('section', 'Unknown')}")
        print(f"   날짜: {article.get('published_date', 'Unknown')}")
        if article.get('summary'):
            print(f"   요약: {article['summary'][:100]}...")
        print()
    
    # 최근 뉴스 필터링
    recent = collector.filter_recent_news(news, days_back=7)
    print(f"\n최근 7일 기사: {len(recent)}개")
    
    # JSON 파일로 저장
    output_file = f"pokernews_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f"\n결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()