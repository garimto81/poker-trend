#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 PokerNews 스크래핑 테스트
"""

import sys
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup

def test_pokernews_access():
    """PokerNews 접근 테스트"""
    
    url = "https://www.pokernews.com/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Accessing: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Successfully connected to PokerNews")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 확인
            title = soup.find('title')
            if title:
                print(f"Page Title: {title.text}")
            
            # 다양한 선택자로 기사 찾기 시도
            selectors = [
                'article',
                'div.article',
                'div.news-article',
                'a[href*="/news/"]',
                'h2',
                'h3',
                '.content-item',
                '.news-item',
                '.post'
            ]
            
            print("\n기사 요소 검색:")
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  {selector}: {len(elements)}개 발견")
                    
                    # 첫 번째 요소의 텍스트 샘플
                    if len(elements) > 0:
                        sample_text = elements[0].get_text(strip=True)[:100]
                        print(f"    샘플: {sample_text}...")
            
            # 모든 링크 중 뉴스 링크 찾기
            news_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/news/' in href and '/20' in href:  # 연도가 포함된 뉴스 링크
                    news_links.append(href)
            
            print(f"\n뉴스 링크 발견: {len(news_links)}개")
            if news_links:
                print("샘플 링크:")
                for link in news_links[:5]:
                    print(f"  - {link}")
            
            # HTML 일부 저장 (디버깅용)
            with open('pokernews_sample.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:10000])
            print("\nHTML 샘플이 'pokernews_sample.html'에 저장되었습니다.")
            
        else:
            print(f"✗ Failed to access PokerNews: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"✗ Request failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_pokernews_access()