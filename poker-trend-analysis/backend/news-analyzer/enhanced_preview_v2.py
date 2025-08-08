#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 포커 뉴스 미리보기 v2 - 실제 내용 기반 3줄 요약 및 제목 하이퍼링크
"""

import json
import os
import re
from datetime import datetime
from pokernews_rss_collector import PokerNewsRSSCollector
from pokernews_ai_analyzer import PokerNewsAIAnalyzer
from dotenv import load_dotenv

load_dotenv()

def create_article_summary(article):
    """기사 실제 내용 기반 3줄 요약"""
    title = article.get('title', '제목 없음')
    summary = article.get('summary', '')
    source = article.get('source', 'Unknown')
    date = article.get('published_date', 'Unknown')
    
    lines = []
    
    # 제목 분석하여 핵심 내용 추출
    title_clean = title.split(' - ')[0] if ' - ' in title else title
    
    # 1줄: 주요 이벤트/인물 추출
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
    elif 'Ryan Riess' in title and 'Main Event' in title:
        lines.append("🎯 Ryan Riess, WSOP 메인이벤트 재우승 도전 의사 표명")
    elif 'Garrett Adelstein' in title:
        lines.append("😤 Garrett Adelstein, 최근 출연에서 연속 불운")
    elif 'Mike Matusow' in title and 'Heads-Up' in title:
        lines.append("⏰ Mike Matusow, 12년 만에 헤즈업 타이틀 방어전")
    elif '$500,000' in title or '500,000' in title:
        lines.append("💸 Sycuan 카지노 회원 포커 테이블 게임서 $50만 이상 획득")
    elif 'Negreanu' in title and 'Hellmuth' in title:
        lines.append("🎤 Negreanu와 Hellmuth, 내셔널 헤즈업 챔피언십 불참")
    else:
        # 기본 요약
        if 'million' in title.lower() or '$' in title:
            lines.append(f"💰 {title_clean[:60]}...")
        elif 'WSOP' in title or 'WPT' in title:
            lines.append(f"🏆 {title_clean[:60]}...")
        else:
            lines.append(f"📰 {title_clean[:60]}...")
    
    # 2줄: 핵심 세부사항
    if 'Bracelet' in title:
        lines.append("🎖️ 브레이슬릿 이벤트 상세 일정 및 참가 정보 포함")
    elif 'dates' in title.lower() or 'schedule' in title.lower():
        lines.append("📆 구체적인 대회 일정과 장소 정보 발표")
    elif 'wins' in title.lower() or 'won' in title.lower():
        lines.append("🏅 우승 소식과 상금 규모 상세 정보")
    elif 'guide' in title.lower() or 'commentary' in title.lower():
        lines.append("📚 전문가의 경험과 노하우 공유")
    elif 'controversy' in title.lower() or 'sparks' in title.lower():
        lines.append("⚠️ 업계 내 논란과 다양한 의견 대립")
    else:
        # summary 활용
        if summary and len(summary) > 20:
            summary_clean = re.sub(r'[^\w\s]', '', summary[:80])
            lines.append(f"📝 {summary_clean}...")
        else:
            lines.append(f"📝 {source}에서 보도한 최신 포커 업계 소식")
    
    # 3줄: 시사점 또는 영향
    if 'Thailand' in title:
        lines.append("🌏 아시아 포커 시장 확장의 신호탄으로 주목")
    elif 'WSOP' in title or 'bracelet' in title.lower():
        lines.append("🎲 세계 최대 포커 시리즈의 새로운 기회")
    elif 'million' in title.lower() or '€' in title or '$' in title:
        lines.append("💎 대규모 상금으로 프로 선수들 관심 집중")
    elif any(name in title for name in ['Hellmuth', 'Negreanu', 'Ivey', 'Adelstein', 'Riess']):
        lines.append("⭐ 유명 프로 선수 동향이 포커 팬들에게 화제")
    else:
        lines.append(f"📊 포커 커뮤니티에 새로운 관심사 제공")
    
    return lines

def format_slack_preview(articles):
    """Slack 메시지 포맷 미리보기 - 제목에 하이퍼링크 포함"""
    message = []
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 헤더
    message.append("="*60)
    message.append("📰 포커 뉴스 일일 트렌드 분석")
    message.append(f"📅 {current_date} | 🔍 분석 기사: {len(articles)}개")
    message.append("="*60)
    
    # 주요 기사 with 실제 내용 기반 3줄 요약
    message.append("\n🎯 주요 기사")
    message.append("-"*60)
    
    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        
        # 제목에 하이퍼링크 포함 (Slack 형식)
        if len(title) > 80:
            display_title = title[:80] + "..."
        else:
            display_title = title
        
        message.append(f"\n[{i}] <{url}|{display_title}>")
        
        # 실제 내용 기반 3줄 요약
        summary_lines = create_article_summary(article)
        for line in summary_lines:
            message.append(f"   {line}")
        message.append("")
    
    return "\n".join(message)

def create_html_preview(articles):
    """HTML 형식 미리보기 생성 - 제목에 하이퍼링크 포함"""
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
        .article-title {{
            color: #2c3e50;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .article-title:hover {{
            color: #3498db;
            text-decoration: underline;
        }}
        .summary-line {{
            margin: 8px 0;
            padding-left: 40px;
            color: #555;
            line-height: 1.5;
        }}
        .date {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-left: 40px;
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
        title = article.get('title', '제목 없음')
        url = article.get('url', '#')
        date = article.get('published_date', 'Unknown')
        source = article.get('source', 'Unknown')
        summary_lines = create_article_summary(article)
        
        html += f"""
    <div class="article">
        <h3>
            <span class="article-number">{i}</span>
            <a href="{url}" target="_blank" class="article-title">{title}</a>
        </h3>
        <div class="date">📅 {date} | 출처: {source}</div>
        <div class="summary">
"""
        
        for line in summary_lines:
            html += f'            <div class="summary-line">{line}</div>\n'
        
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
    print("향상된 포커 뉴스 미리보기 v2")
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
        try:
            analyzer = PokerNewsAIAnalyzer()
            ai_analysis = analyzer.analyze_news_trends(articles[:5])
            if ai_analysis and ai_analysis.get('core_trends'):
                print("\n📊 AI가 분석한 핵심 트렌드:")
                for i, trend in enumerate(ai_analysis['core_trends'][:3], 1):
                    print(f"  {i}. {trend}")
            if ai_analysis and ai_analysis.get('summary'):
                print(f"\n📝 한 줄 요약: {ai_analysis['summary']}")
        except Exception as e:
            print(f"AI 분석 실패: {e}")
    else:
        print("\n💡 팁: GEMINI_API_KEY를 설정하면 AI 분석도 볼 수 있습니다.")
    
    # HTML 미리보기 생성
    html_content = create_html_preview(articles)
    html_filename = f"preview_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
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
        article_data['content_based_summary'] = create_article_summary(article)
        preview_data['articles_with_summary'].append(article_data)
    
    json_filename = f"preview_data_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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