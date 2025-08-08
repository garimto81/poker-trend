#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 TOP 5 포커 트렌드 분석 및 쇼츠 아이디어 생성
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

def final_poker_analysis():
    """최종 포커 트렌드 분석"""
    
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # TOP 5 영상 데이터 (인코딩 안전한 형태)
        top5_data = [
            {
                "rank": 1,
                "title": "Naruto Mp40 VS Poker Mp40 (Tamil Gaming Video)",
                "views": 523884,
                "likes": 49949,
                "comments": 474,
                "channel": "Tamil Gaming Channel",
                "engagement_rate": 9.54,
                "type": "gaming_comparison"
            },
            {
                "rank": 2,
                "title": "QUADS vs ACES FULL #poker",
                "views": 306076,
                "likes": 3490,
                "comments": 42,
                "channel": "River Shark Poker",
                "engagement_rate": 1.14,
                "type": "hand_analysis"
            },
            {
                "rank": 3,
                "title": "he actually went for it (poker shorts)",
                "views": 114890,
                "likes": 3541,
                "comments": 63,
                "channel": "Wolfgang Poker",
                "engagement_rate": 3.08,
                "type": "dramatic_moment"
            },
            {
                "rank": 4,
                "title": "I Play $50,000 Players Championship - BIGGEST Buyin",
                "views": 110160,
                "likes": 4960,
                "comments": 387,
                "channel": "Brad Owen",
                "engagement_rate": 4.50,
                "type": "high_stakes"
            }
        ]
        
        prompt = f"""
포커 트렌드 분석 전문가로서 다음 TOP 4 YouTube 영상을 분석하여 현재 포커 팬들의 관심사를 파악하고 실제 제작 가능한 쇼츠 아이디어를 제안해주세요.

=== 핵심 데이터 분석 ===

🏆 1위: Tamil Gaming + Poker 비교 영상
- 523,884 조회수, 참여율 9.54% (매우 높음)
- 게임과 포커를 비교하는 독특한 접근

🏆 2위: QUADS vs ACES 핸드 분석
- 306,076 조회수, 참여율 1.14%
- 클래식한 핸드 분석 콘텐츠

🏆 3위: 극적인 순간 쇼츠
- 114,890 조회수, 참여율 3.08%
- 짧고 임팩트 있는 순간 포착

🏆 4위: 고액 토너먼트 참가기
- 110,160 조회수, 참여율 4.50%
- $50,000 바이인의 거액 토너먼트

=== 분석 및 제안 요청 ===

1. **포커 팬들의 핵심 관심사 TOP 3**
   - 데이터 기반 명확한 파악
   - 각 관심사가 성공한 이유

2. **성공 패턴 분석**
   - 왜 Tamil 콘텐츠가 1위인가?
   - 참여율이 높은 콘텐츠의 특징
   - 제목과 성과의 상관관계

3. **즉시 제작 가능한 쇼츠 아이디어 5개**
   
   **아이디어 1: [제목]**
   - 관심사 연결: [분석된 팬 관심사]
   - 스토리라인: [30초 구성]
   - 예상 조회수: [근거 포함]
   - 제작 가이드: [구체적 방법]
   - 해시태그: [5개]
   
   (이런 식으로 5개 모두)

4. **차별화 전략**
   - 현재 놓치고 있는 기회
   - 새로운 각도나 접근법

5. **실행 우선순위**
   - 가장 먼저 만들어야 할 콘텐츠
   - 시급성과 성공 가능성 기준

모든 제안은 실제 데이터에 기반하여 오늘 당장 실행 가능하게 해주세요.
"""
        
        print("Generating final poker trend analysis...")
        
        response = model.generate_content(prompt)
        
        # 결과 저장
        final_result = {
            "timestamp": "2025-08-05T18:50:00",
            "analysis_type": "final_poker_trend_shorts_ideas",
            "top_videos_data": top5_data,
            "ai_analysis": response.text
        }
        
        # JSON 저장
        json_path = Path(__file__).parent / 'reports' / 'final_poker_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        
        # 텍스트 저장
        txt_path = Path(__file__).parent / 'reports' / 'FINAL_POKER_SHORTS_IDEAS.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("FINAL POKER TREND ANALYSIS & SHORTS IDEAS\n")
            f.write("=" * 80 + "\n\n")
            f.write("TOP PERFORMING VIDEOS:\n")
            f.write("-" * 40 + "\n")
            for video in top5_data:
                f.write(f"{video['rank']}. {video['title']}\n")
                f.write(f"   {video['views']:,} views | {video['likes']:,} likes | {video['engagement_rate']}% engagement\n")
                f.write(f"   Type: {video['type']} | Channel: {video['channel']}\n\n")
            
            f.write("\nAI ANALYSIS & ACTIONABLE INSIGHTS:\n")
            f.write("=" * 80 + "\n")
            f.write(response.text)
        
        print("Analysis completed successfully!")
        print(f"JSON Report: {json_path}")
        print(f"Text Report: {txt_path}")
        
        # 성공 요약
        print("\nKEY FINDINGS SUMMARY:")
        print("- Tamil gaming crossover content dominated (523k views)")
        print("- Hand analysis content remains popular (306k views)")
        print("- High engagement rates in personal/dramatic content")
        print("- High-stakes tournament content generates strong engagement")
        
        return response.text
        
    except Exception as e:
        print(f"Error in final analysis: {e}")
        return None

if __name__ == "__main__":
    final_poker_analysis()