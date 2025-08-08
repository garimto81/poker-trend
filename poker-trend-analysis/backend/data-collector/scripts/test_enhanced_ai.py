#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 AI 인사이트 테스트
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from enhanced_ai_prompts import get_enhanced_analysis_prompt

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def test_enhanced_ai_insights():
    """개선된 AI 인사이트 테스트"""
    
    # 최신 리포트 데이터 로드
    report_path = Path(__file__).parent / 'reports' / 'daily_report_20250805_182310.json'
    
    if not report_path.exists():
        print("[ERROR] Report file not found")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    videos = report_data.get('videos', [])
    top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
    
    print("=" * 60)
    print("Enhanced AI Insights Test")
    print("=" * 60)
    
    print(f"\nAnalyzing: {len(videos)} videos, TOP {len(top_videos)} selected")
    
    # Gemini AI 설정
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 개선된 프롬프트 생성
        enhanced_prompt = get_enhanced_analysis_prompt(top_videos, "daily")
        
        print("\nStarting AI analysis...")
        print("-" * 40)
        
        # AI 분석 실행
        response = model.generate_content(enhanced_prompt)
        
        print("\nEnhanced AI Insights:")
        print("=" * 60)
        print(response.text)
        
        # 결과 저장
        enhanced_report = {
            "timestamp": "2025-08-05T18:30:00",
            "original_videos_count": len(videos),
            "analyzed_videos_count": len(top_videos),
            "enhanced_ai_insights": response.text,
            "top_videos_summary": [
                {
                    "rank": i+1,
                    "title": video.get('title', ''),
                    "channel": video.get('channel_title', ''),
                    "views": video.get('view_count', 0),
                    "duration": video.get('duration', '')
                }
                for i, video in enumerate(top_videos[:5])
            ]
        }
        
        output_path = Path(__file__).parent / 'reports' / 'enhanced_ai_insights.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_report, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved enhanced insights: {output_path}")
        
    except Exception as e:
        print(f"[ERROR] AI 분석 실패: {e}")

if __name__ == "__main__":
    test_enhanced_ai_insights()