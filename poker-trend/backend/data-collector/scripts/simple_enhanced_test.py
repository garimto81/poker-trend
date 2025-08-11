#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 개선된 AI 인사이트 테스트
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def create_shorts_analysis_prompt(top_videos):
    """쇼츠 제작용 분석 프롬프트"""
    
    titles = [v.get('title', '') for v in top_videos[:5]]
    
    prompt = f"""
You are a YouTube Shorts content strategy expert. Analyze these top poker videos and provide actionable insights for creating viral shorts.

TOP 5 VIDEOS:
{chr(10).join([f"{i+1}. {title} - {v.get('view_count', 0):,} views" for i, (title, v) in enumerate(zip(titles, top_videos[:5]))])}

ANALYSIS REQUIRED:

1. VIRAL TITLE PATTERNS
- What makes these titles effective?
- Key emotional triggers used
- Essential keywords/phrases

2. OPTIMAL VIDEO LENGTH
- Current trend analysis
- Recommended duration for maximum engagement

3. CONCRETE SHORTS IDEAS (3 specific ideas)
Format each as:
IDEA: [Title]
CONCEPT: [30-second storyline]
HOOK: [First 3 seconds]
HASHTAGS: [5 relevant tags]

4. THUMBNAIL STRATEGY
- Effective facial expressions
- Color combinations
- Text overlay recommendations

5. CONTENT GAPS & OPPORTUNITIES
- Underserved topics in current trend
- Differentiation strategies

Provide practical, immediately actionable advice that a creator can implement today.
"""
    
    return prompt

def test_simple_enhanced_ai():
    """간단한 개선된 AI 테스트"""
    
    # 최신 리포트 데이터 로드
    report_path = Path(__file__).parent / 'reports' / 'daily_report_20250805_182310.json'
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    videos = report_data.get('videos', [])
    top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
    
    print("Simple Enhanced AI Test")
    print("=" * 50)
    print(f"Analyzing TOP 5 videos from {len(videos)} total")
    
    # TOP 5 요약
    print("\nTOP 5 VIDEOS:")
    for i, video in enumerate(top_videos, 1):
        title = video.get('title', '').encode('ascii', 'ignore').decode('ascii')[:50]
        views = video.get('view_count', 0)
        channel = video.get('channel_title', '').encode('ascii', 'ignore').decode('ascii')
        print(f"{i}. {title}... - {views:,} views ({channel})")
    
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = create_shorts_analysis_prompt(top_videos)
        
        print("\nRequesting AI analysis...")
        response = model.generate_content(prompt)
        
        # 응답을 파일로 저장 (인코딩 문제 방지)
        output_path = Path(__file__).parent / 'reports' / 'shorts_insights.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED AI INSIGHTS FOR SHORTS CREATION\n")
            f.write("=" * 60 + "\n\n")
            f.write(response.text)
        
        print(f"\nAI analysis completed!")
        print(f"Results saved to: {output_path}")
        
        # 첫 500자만 미리보기
        preview = response.text.replace('\n', ' ')[:500]
        print(f"\nPreview: {preview}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_enhanced_ai()