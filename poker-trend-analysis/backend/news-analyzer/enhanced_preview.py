#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 포커 뉴스 미리보기 - 3줄 요약 및 하이퍼링크 포함
"""

import json
import os
from datetime import datetime
from pokernews_rss_collector import PokerNewsRSSCollector
from pokernews_ai_analyzer import PokerNewsAIAnalyzer
from dotenv import load_dotenv

load_dotenv()

def create_article_summary(article):
    """기사를 3줄로 요약"""
    title = article.get('title', '제목 없음')
    summary = article.get('summary', '')
    source = article.get('source', 'Unknown')
    date = article.get('published_date', 'Unknown')
    
    # 제목에서 주요 내용 추출
    lines = []
    
    # 1줄: 핵심 내용
    if 'WSOP' in title:
        lines.append("🏆 WSOP 관련 소식")
    elif 'WPT' in title:
        lines.append("🎯 WPT 토너먼트 소식")
    elif 'Hellmuth' in title or 'Negreanu' in title or 'Ivey' in title:
        lines.append("🌟 유명 프로 선수 관련")
    elif 'million' in title.lower() or '$' in title:
        lines.append("💰 대규모 상금 이벤트")
    elif 'online' in title.lower() or 'GGPoker' in title:
        lines.append("🌐 온라인 포커 소식")
    else:
        lines.append("📰 포커 업계 뉴스")
    
    # 2줄: 구체적 내용 (제목 기반)
    if len(title) > 80:
        lines.append(f"📋 {title[:80]}...")
    else:
        lines.append(f"📋 {title}")
    
    # 3줄: 출처와 날짜
    lines.append(f"📅 {date} | 출처: {source}")
    
    return lines

def generate_ai_summary(articles):
    """AI를 사용한 심화 요약 (Gemini API 필요)"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    
    try:
        analyzer = PokerNewsAIAnalyzer()
        # 간단한 요약만 요청
        prompt_articles = []
        for article in articles[:5]:
            prompt_articles.append({
                'title': article.get('title', ''),
                'summary': article.get('summary', '')[:200] if article.get('summary') else '',
                'published_date': article.get('published_date', '')
            })
        
        # AI 분석 실행
        analysis = analyzer.analyze_news_trends(prompt_articles)
        return analysis
    except Exception as e:
        print(f"AI 분석 실패: {e}")
        return None

def format_slack_preview(articles):
    """Slack 메시지 포맷 미리보기"""
    message = []
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 헤더
    message.append("="*60)
    message.append("📰 포커 뉴스 일일 트렌드 분석")
    message.append(f"📅 {current_date} | 🔍 분석 기사: {len(articles)}개")
    message.append("="*60)
    
    # 주요 기사 with 3줄 요약
    message.append("\n🎯 주요 기사 (3줄 요약)")
    message.append("-"*60)
    
    for i, article in enumerate(articles[:5], 1):
        message.append(f"\n[{i}] 기사")
        
        # 3줄 요약
        summary_lines = create_article_summary(article)
        for line in summary_lines:
            message.append(f"   {line}")
        
        # 하이퍼링크
        url = article.get('url', '#')
        if url and url != '#':
            # Slack 형식: <URL|표시 텍스트>
            if len(url) > 100:
                display_url = url[:50] + "..."
            else:
                display_url = url
            message.append(f"   🔗 <{url}|자세히 보기>")
        message.append("")
    
    return "\n".join(message)

def create_html_preview(articles):
    """HTML 형식 미리보기 생성"""
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>포커 뉴스 미리보기</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .article {{
            background-color: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .article-number {{
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            margin-right: 10px;
        }}
        .summary-line {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .article-link:hover {{
            background-color: #2980b9;
        }}
        .date {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 포커 뉴스 일일 트렌드 분석</h1>
        <p>📅 {datetime.now().strftime("%Y년 %m월 %d일")} | 🔍 분석 기사: {len(articles)}개</p>
    </div>
"""
    
    for i, article in enumerate(articles[:10], 1):
        summary_lines = create_article_summary(article)
        url = article.get('url', '#')
        
        html += f"""
    <div class="article">
        <h3><span class="article-number">{i}</span>{article.get('title', '제목 없음')}</h3>
        <div class="summary">
"""
        
        for line in summary_lines:
            html += f'            <div class="summary-line">{line}</div>\n'
        
        if url and url != '#':
            html += f'        <a href="{url}" target="_blank" class="article-link">🔗 원문 보기</a>\n'
        
        html += """        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    return html

def main():
    print("\n" + "="*60)
    print("향상된 포커 뉴스 미리보기")
    print("="*60)
    
    # RSS 수집기 초기화
    collector = PokerNewsRSSCollector()
    
    # 뉴스 수집
    print("\n📡 뉴스 수집 중...")
    articles = collector.collect_from_rss(max_articles=10)
    
    if not articles:
        print("📋 모의 데이터 사용...")
        articles = collector.collect_mock_news()
    
    print(f"✅ {len(articles)}개 기사 수집 완료\n")
    
    # Slack 형식 미리보기
    slack_preview = format_slack_preview(articles)
    print(slack_preview)
    
    # AI 요약 시도 (옵션)
    if os.getenv('GEMINI_API_KEY'):
        print("\n" + "="*60)
        print("🤖 AI 분석 중...")
        print("="*60)
        ai_analysis = generate_ai_summary(articles)
        if ai_analysis and ai_analysis.get('core_trends'):
            print("\n📊 AI가 분석한 핵심 트렌드:")
            for i, trend in enumerate(ai_analysis['core_trends'][:3], 1):
                print(f"  {i}. {trend}")
        if ai_analysis and ai_analysis.get('summary'):
            print(f"\n📝 한 줄 요약: {ai_analysis['summary']}")
    else:
        print("\n💡 팁: GEMINI_API_KEY를 설정하면 AI 분석도 볼 수 있습니다.")
    
    # HTML 미리보기 생성
    html_content = create_html_preview(articles)
    html_filename = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # JSON 데이터 저장
    preview_data = {
        'preview_date': datetime.now().isoformat(),
        'articles_count': len(articles),
        'articles_with_summary': []
    }
    
    for article in articles[:10]:
        article_data = article.copy()
        article_data['three_line_summary'] = create_article_summary(article)
        preview_data['articles_with_summary'].append(article_data)
    
    json_filename = f"preview_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(preview_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("📁 저장된 파일:")
    print(f"  - HTML 미리보기: {html_filename}")
    print(f"  - JSON 데이터: {json_filename}")
    print("\n💡 HTML 파일을 브라우저에서 열어 더 보기 좋은 형식으로 확인하세요!")
    print("\n🚀 실제 Slack 전송: python pokernews_slack_reporter.py")
    print("="*60)

if __name__ == "__main__":
    main()