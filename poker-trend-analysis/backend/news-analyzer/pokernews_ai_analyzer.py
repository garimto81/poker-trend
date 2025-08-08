#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerNews AI 분석기
Gemini AI를 활용하여 포커 뉴스를 분석하고 트렌드를 추출하는 모듈
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokerNewsAIAnalyzer:
    """포커 뉴스 AI 분석기"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            gemini_api_key: Gemini API 키
        """
        self.api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 필요합니다")
        
        # Gemini 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        logger.info("Gemini AI 분석기 초기화 완료")
    
    def analyze_news_trends(self, articles: List[Dict]) -> Dict:
        """
        뉴스 기사들을 분석하여 트렌드 추출
        
        Args:
            articles: 뉴스 기사 리스트
            
        Returns:
            분석 결과
        """
        if not articles:
            logger.warning("분석할 기사가 없습니다")
            return {
                'status': 'no_articles',
                'message': '분석할 기사가 없습니다'
            }
        
        logger.info(f"{len(articles)}개 기사 AI 분석 시작")
        
        # 기사 내용 준비
        news_content = self._prepare_news_content(articles)
        
        # AI 프롬프트 생성
        prompt = self._create_analysis_prompt(news_content)
        
        try:
            # Gemini AI 분석 실행
            response = self.model.generate_content(prompt)
            
            # 응답 파싱
            analysis_result = self._parse_ai_response(response.text)
            
            # 메타데이터 추가
            analysis_result['meta'] = {
                'analyzed_articles': len(articles),
                'analysis_date': datetime.now().isoformat(),
                'source': 'PokerNews'
            }
            
            logger.info("AI 분석 완료")
            return analysis_result
            
        except Exception as e:
            logger.error(f"AI 분석 실패: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'fallback_summary': self._create_fallback_summary(articles)
            }
    
    def _prepare_news_content(self, articles: List[Dict]) -> str:
        """뉴스 컨텐츠를 AI 분석용으로 준비"""
        content_parts = []
        
        for i, article in enumerate(articles[:15], 1):  # 최대 15개 기사만
            part = f"[기사 {i}]\n"
            part += f"제목: {article.get('title', 'No title')}\n"
            
            if article.get('summary'):
                part += f"요약: {article['summary']}\n"
            
            if article.get('section'):
                part += f"섹션: {article['section']}\n"
            
            if article.get('tags'):
                part += f"태그: {', '.join(article['tags'])}\n"
            
            if article.get('published_date'):
                part += f"날짜: {article['published_date']}\n"
            
            content_parts.append(part)
        
        return "\n---\n".join(content_parts)
    
    def _create_analysis_prompt(self, news_content: str) -> str:
        """AI 분석 프롬프트 생성"""
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        prompt = f"""당신은 전문 포커 산업 분석가입니다. 
다음 PokerNews 기사들을 분석하여 {current_date} 기준 포커 업계의 주요 트렌드와 인사이트를 추출해주세요.

[뉴스 기사들]
{news_content}

다음 형식으로 분석 결과를 작성해주세요:

## 🎯 오늘의 핵심 트렌드 (3-5개)
- 가장 중요한 트렌드를 불릿 포인트로 작성
- 각 트렌드는 구체적이고 실행 가능한 인사이트 포함

## 📊 주요 이벤트 및 토너먼트
- 진행 중이거나 예정된 주요 토너먼트
- 중요한 결과나 우승 소식

## 🌟 주목할 선수/인물
- 뉴스에 자주 언급된 포커 프로들
- 특별한 성과나 이슈가 있는 인물

## 💡 시장 동향 및 비즈니스
- 온라인 포커 플랫폼 관련 소식
- 규제, 법률, 시장 변화
- 새로운 제품이나 서비스 출시

## 🔮 향후 전망
- 단기(1주일) 및 중기(1개월) 전망
- 주목해야 할 upcoming 이벤트

## 🎬 콘텐츠 아이디어
- YouTube나 소셜 미디어 콘텐츠로 활용할 수 있는 주제 3개
- 각 아이디어에 대한 간단한 설명

## 📝 한 줄 요약
- 오늘 포커 업계를 한 문장으로 요약

모든 내용은 한국어로 작성하고, 구체적이고 실용적인 정보를 제공해주세요.
숫자나 통계가 있다면 포함시켜주세요."""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """AI 응답 파싱"""
        try:
            sections = {
                'core_trends': [],
                'tournaments': [],
                'notable_players': [],
                'market_trends': [],
                'future_outlook': [],
                'content_ideas': [],
                'summary': '',
                'raw_response': response_text
            }
            
            current_section = None
            current_content = []
            
            for line in response_text.split('\n'):
                line = line.strip()
                
                # 섹션 헤더 감지
                if '핵심 트렌드' in line:
                    current_section = 'core_trends'
                    current_content = []
                elif '이벤트' in line or '토너먼트' in line:
                    current_section = 'tournaments'
                    current_content = []
                elif '주목할 선수' in line or '인물' in line:
                    current_section = 'notable_players'
                    current_content = []
                elif '시장 동향' in line or '비즈니스' in line:
                    current_section = 'market_trends'
                    current_content = []
                elif '향후 전망' in line or '전망' in line:
                    current_section = 'future_outlook'
                    current_content = []
                elif '콘텐츠 아이디어' in line:
                    current_section = 'content_ideas'
                    current_content = []
                elif '한 줄 요약' in line:
                    current_section = 'summary'
                    current_content = []
                elif line.startswith('-') or line.startswith('•'):
                    # 불릿 포인트 내용
                    if current_section and current_section != 'summary':
                        content = line.lstrip('-•').strip()
                        if content:
                            current_content.append(content)
                            if current_section in sections and isinstance(sections[current_section], list):
                                sections[current_section].append(content)
                elif current_section == 'summary' and line:
                    # 요약 내용
                    sections['summary'] += line + ' '
            
            # 요약 정리
            sections['summary'] = sections['summary'].strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"응답 파싱 실패: {e}")
            return {
                'error': 'parsing_failed',
                'raw_response': response_text
            }
    
    def _create_fallback_summary(self, articles: List[Dict]) -> str:
        """AI 분석 실패 시 대체 요약 생성"""
        summary_parts = [
            f"📰 오늘의 포커 뉴스 요약 ({len(articles)}개 기사)",
            ""
        ]
        
        # 섹션별 기사 분류
        sections = {}
        for article in articles:
            section = article.get('section', 'general')
            if section not in sections:
                sections[section] = []
            sections[section].append(article.get('title', 'No title'))
        
        # 섹션별 요약
        for section, titles in sections.items():
            summary_parts.append(f"【{section.upper()}】")
            for title in titles[:3]:  # 각 섹션당 최대 3개
                summary_parts.append(f"• {title}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def generate_content_recommendations(self, analysis: Dict) -> List[Dict]:
        """
        분석 결과를 기반으로 콘텐츠 추천 생성
        
        Args:
            analysis: AI 분석 결과
            
        Returns:
            콘텐츠 추천 리스트
        """
        recommendations = []
        
        # 핵심 트렌드 기반 추천
        for trend in analysis.get('core_trends', [])[:3]:
            recommendations.append({
                'type': 'trend_analysis',
                'title': f"트렌드 분석: {trend[:50]}",
                'description': f"최신 트렌드 '{trend}'에 대한 심층 분석 콘텐츠",
                'priority': 'high',
                'format': ['video', 'article']
            })
        
        # 토너먼트 기반 추천
        for tournament in analysis.get('tournaments', [])[:2]:
            recommendations.append({
                'type': 'tournament_coverage',
                'title': f"토너먼트 하이라이트: {tournament[:50]}",
                'description': f"주요 핸드와 전략 분석",
                'priority': 'medium',
                'format': ['video', 'live_stream']
            })
        
        # 선수 기반 추천
        for player in analysis.get('notable_players', [])[:2]:
            recommendations.append({
                'type': 'player_spotlight',
                'title': f"플레이어 스포트라이트: {player[:50]}",
                'description': f"플레이 스타일과 최근 성과 분석",
                'priority': 'medium',
                'format': ['video', 'interview']
            })
        
        return recommendations


def main():
    """테스트 실행"""
    # 테스트용 기사 데이터
    test_articles = [
        {
            'title': 'Daniel Negreanu Wins WSOP Bracelet #7',
            'summary': 'Daniel Negreanu finally wins his 7th WSOP bracelet after years of trying.',
            'section': 'tours',
            'tags': ['WSOP', 'Daniel Negreanu'],
            'published_date': datetime.now().isoformat()
        },
        {
            'title': 'GGPoker Launches New Tournament Series',
            'summary': 'GGPoker announces a new $50 million guaranteed tournament series.',
            'section': 'online-poker',
            'tags': ['GGPoker', 'Online Tournament'],
            'published_date': datetime.now().isoformat()
        },
        {
            'title': 'Poker Strategy: Understanding Range Advantages',
            'summary': 'Deep dive into range advantages and how to exploit them.',
            'section': 'strategy',
            'tags': ['Strategy', 'Education'],
            'published_date': datetime.now().isoformat()
        }
    ]
    
    # 분석기 초기화 및 실행
    analyzer = PokerNewsAIAnalyzer()
    result = analyzer.analyze_news_trends(test_articles)
    
    # 결과 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 콘텐츠 추천 생성
    recommendations = analyzer.generate_content_recommendations(result)
    print("\n콘텐츠 추천:")
    for rec in recommendations:
        print(f"- {rec['title']}: {rec['description']}")


if __name__ == "__main__":
    main()