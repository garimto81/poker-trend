#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews 뉴스 수집기
PokerNews.com에서 최신 뉴스를 수집하는 모듈
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerNewsCollector:
    """PokerNews 뉴스 수집기"""
    
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
        """
        최신 뉴스 수집
        
        Args:
            max_articles: 수집할 최대 기사 수
            
        Returns:
            뉴스 기사 리스트
        """
        logger.info(f"PokerNews에서 최신 뉴스 {max_articles}개 수집 시작")
        
        articles = []
        
        # 메인 뉴스 페이지 수집
        news_sections = [
            "/news/",  # 메인 뉴스
            "/strategy/",  # 전략 기사
            "/tours/",  # 토너먼트 뉴스
            "/online-poker/",  # 온라인 포커
            "/live-reporting/"  # 라이브 리포팅
        ]
        
        for section in news_sections:
            try:
                section_articles = self._collect_section_news(section, max_articles // len(news_sections))
                articles.extend(section_articles)
                
                # API 부하 방지를 위한 지연
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"섹션 {section} 수집 실패: {e}")
                continue
        
        # 중복 제거 및 정렬
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 날짜순 정렬 (최신순)
        unique_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        logger.info(f"총 {len(unique_articles)}개의 고유한 뉴스 기사 수집 완료")
        
        return unique_articles[:max_articles]
    
    def _collect_section_news(self, section_path: str, limit: int = 5) -> List[Dict]:
        """특정 섹션의 뉴스 수집"""
        url = urljoin(self.base_url, section_path)
        logger.info(f"섹션 수집: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # PokerNews 기사 요소 선택자 (사이트 구조에 따라 조정 필요)
            article_selectors = [
                'article.article-preview',  # 일반적인 기사 프리뷰
                'div.article-item',  # 대체 선택자
                'div.news-article',  # 또 다른 대체
                'div.post-item',
                'article.post'
            ]
            
            article_elements = []
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    article_elements = elements
                    logger.info(f"선택자 {selector}로 {len(elements)}개 요소 발견")
                    break
            
            # 기사 요소가 없으면 링크 기반으로 수집
            if not article_elements:
                logger.info("기사 요소를 찾지 못함, 링크 기반 수집 시도")
                article_elements = self._find_article_links(soup)
            
            for element in article_elements[:limit]:
                article = self._parse_article_element(element, section_path)
                if article:
                    articles.append(article)
            
            return articles
            
        except requests.RequestException as e:
            logger.error(f"섹션 {section_path} 요청 실패: {e}")
            return []
        except Exception as e:
            logger.error(f"섹션 {section_path} 파싱 실패: {e}")
            return []
    
    def _find_article_links(self, soup: BeautifulSoup) -> List:
        """링크 기반으로 기사 찾기"""
        article_links = []
        
        # 뉴스 관련 링크 패턴
        news_patterns = ['/news/', '/strategy/', '/tours/', '/online-poker/']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # 뉴스 패턴과 일치하고 연도가 포함된 링크 (보통 뉴스 URL 형식)
            if any(pattern in href for pattern in news_patterns) and '/20' in href:
                # 부모 요소를 기사 컨테이너로 사용
                parent = link.find_parent(['div', 'article', 'li'])
                if parent and parent not in article_links:
                    article_links.append(parent)
        
        return article_links[:10]  # 최대 10개만
    
    def _parse_article_element(self, element, section: str) -> Optional[Dict]:
        """기사 요소 파싱"""
        try:
            article = {
                'source': 'PokerNews',
                'section': section.strip('/'),
                'collected_at': datetime.now().isoformat()
            }
            
            # 제목 추출
            title_element = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if title_element:
                article['title'] = title_element.get_text(strip=True)
            else:
                # 링크 텍스트를 제목으로 사용
                link = element.find('a')
                if link:
                    article['title'] = link.get_text(strip=True)
            
            # URL 추출
            link_element = element.find('a', href=True)
            if link_element:
                article['url'] = urljoin(self.base_url, link_element['href'])
            
            # 요약/설명 추출
            desc_selectors = ['p', '.excerpt', '.summary', '.description']
            for selector in desc_selectors:
                desc = element.find(selector)
                if desc:
                    article['summary'] = desc.get_text(strip=True)[:500]  # 최대 500자
                    break
            
            # 날짜 추출
            date_selectors = ['time', '.date', '.published', '.post-date']
            for selector in date_selectors:
                date_elem = element.find(selector)
                if date_elem:
                    # datetime 속성 확인
                    if date_elem.get('datetime'):
                        article['published_date'] = date_elem['datetime']
                    else:
                        article['published_date'] = date_elem.get_text(strip=True)
                    break
            
            # 이미지 URL 추출
            img_element = element.find('img')
            if img_element:
                img_src = img_element.get('src') or img_element.get('data-src')
                if img_src:
                    article['image_url'] = urljoin(self.base_url, img_src)
            
            # 저자 추출
            author_selectors = ['.author', '.by-author', '.post-author']
            for selector in author_selectors:
                author = element.find(selector)
                if author:
                    article['author'] = author.get_text(strip=True)
                    break
            
            # 태그 추출
            tags = []
            tag_elements = element.find_all(['a', 'span'], class_=['tag', 'category', 'label'])
            for tag in tag_elements:
                tag_text = tag.get_text(strip=True)
                if tag_text and len(tag_text) < 30:  # 너무 긴 텍스트는 태그가 아닐 가능성
                    tags.append(tag_text)
            if tags:
                article['tags'] = tags
            
            # 필수 필드 확인
            if 'title' in article and 'url' in article:
                return article
            else:
                return None
                
        except Exception as e:
            logger.error(f"기사 파싱 실패: {e}")
            return None
    
    def get_article_content(self, article_url: str) -> Optional[str]:
        """
        기사 본문 내용 가져오기
        
        Args:
            article_url: 기사 URL
            
        Returns:
            기사 본문 텍스트
        """
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 본문 컨테이너 선택자
            content_selectors = [
                'div.article-content',
                'div.post-content',
                'article.content',
                'div.entry-content',
                'div.article-body',
                'main article'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 불필요한 요소 제거
                    for unwanted in content_elem.find_all(['script', 'style', 'aside', 'nav']):
                        unwanted.decompose()
                    
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            if not content:
                # 폴백: 모든 p 태그 수집
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            return content[:5000] if content else None  # 최대 5000자
            
        except Exception as e:
            logger.error(f"기사 내용 가져오기 실패 {article_url}: {e}")
            return None
    
    def filter_today_news(self, articles: List[Dict]) -> List[Dict]:
        """오늘 날짜의 뉴스만 필터링"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        filtered = []
        for article in articles:
            try:
                # 날짜 파싱 시도
                date_str = article.get('published_date', '')
                if not date_str:
                    continue
                
                # ISO 형식 날짜 파싱
                if 'T' in date_str:
                    article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                else:
                    # 다양한 날짜 형식 시도
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%B %d, %Y']:
                        try:
                            article_date = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                    else:
                        continue
                
                # 오늘 또는 어제 기사만 포함 (시차 고려)
                if article_date == today or article_date == yesterday:
                    filtered.append(article)
                    
            except Exception as e:
                logger.debug(f"날짜 파싱 실패: {article.get('title', 'Unknown')}: {e}")
                # 날짜를 파싱할 수 없으면 포함 (최신 기사일 가능성)
                filtered.append(article)
        
        logger.info(f"오늘/어제 날짜 기사: {len(filtered)}개")
        return filtered


def main():
    """테스트 실행"""
    collector = PokerNewsCollector()
    
    # 최신 뉴스 수집
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
    
    # JSON 파일로 저장
    output_file = f"pokernews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f"결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()