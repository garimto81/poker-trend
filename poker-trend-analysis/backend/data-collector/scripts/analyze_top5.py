#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOP 5 영상 데이터 분석 및 포커 팬 관심사 분석
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

def analyze_top5_poker_trends():
    """TOP 5 영상 분석 및 쇼츠 아이디어 생성"""
    
    # 최신 완전한 분석 리포트 로드
    report_path = Path(__file__).parent / 'reports' / 'complete_analysis_20250805_183853.json'
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    top_5 = report_data['top_5_videos']
    
    print("TOP 5 POKER VIDEOS ANALYSIS")
    print("=" * 60)
    
    for i, video in enumerate(top_5, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   Channel: {video['channel_title']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   Likes: {video['like_count']:,}")
        print(f"   Comments: {video['comment_count']:,}")
        print(f"   Upload: {video['upload_date']}")
        print(f"   Duration: {video['duration']}")
        print(f"   Description: {video['description'][:100]}...")
    
    # Gemini AI 분석
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 분석용 데이터 준비
        analysis_data = []
        for video in top_5:
            analysis_data.append({
                'title': video['title'],
                'description': video['description'][:200],
                'channel': video['channel_title'],
                'views': video['view_count'],
                'likes': video['like_count'],
                'comments': video['comment_count'],
                'upload_date': video['upload_date'],
                'engagement_rate': round((video['like_count'] / video['view_count'] * 100), 2) if video['view_count'] > 0 else 0
            })
        
        # AI 분석 프롬프트 생성
        prompt = f"""
포커 트렌드 전문가로서 다음 TOP 5 YouTube 영상을 분석하여 현재 포커 팬들의 관심사를 파악하고 쇼츠 제작 아이디어를 제안해주세요.

=== TOP 5 영상 데이터 ===

1. 제목: "Naruto Mp40 VS Poker Mp40 Ethu Bestnu Sollunga Nanpargalay🔥"
   채널: மாட்டு RAVI (Tamil)
   성과: 523,884 조회수, 49,949 좋아요, 474 댓글
   참여율: 9.54%
   업로드: 2025-08-04

2. 제목: "QUADS vs ACES FULL #poker"
   채널: River Shark Poker
   성과: 306,076 조회수, 3,490 좋아요, 42 댓글
   참여율: 1.14%
   설명: Triton Poker 클립, 교육 목적
   업로드: 2025-08-04

3. 제목: "he actually went for it 🤯 #poker #shorts"
   채널: Wolfgang Poker
   성과: 114,890 조회수, 3,541 좋아요, 63 댓글
   참여율: 3.08%
   업로드: 2025-08-04

4. 제목: "I Play $50,000 Players Championship!!! BIGGEST Buyin Of My Life"
   채널: Brad Owen
   성과: 110,160 조회수, 4,960 좋아요, 387 댓글
   참여율: 4.50%
   업로드: 2025-08-04

5. 제목: 기타 포커 관련 영상들...

=== 분석 요청 ===

1. **포커 팬들의 핵심 관심사 3가지**
   - 데이터 기반으로 명확하게 파악
   - 각 관심사별 증거 제시

2. **성공 패턴 분석**
   - 높은 조회수 요인
   - 높은 참여율 요인
   - 지역별/언어별 차이점

3. **구체적인 쇼츠 아이디어 5개**
   각각 다음 형식으로:
   
   **아이디어 X: [제목]**
   - 타겟 관심사: [분석된 관심사 연결]
   - 30초 스토리: [구체적 내용]
   - 예상 성과: [조회수 예측]
   - 제작 가이드: [촬영/편집 팁]
   - 해시태그: [최적화된 5개]

4. **차별화 전략**
   - 현재 부족한 콘텐츠 영역
   - 새로운 접근 방식

모든 분석은 실제 데이터에 기반하여 구체적이고 실행 가능하게 해주세요.
"""
        
        print(f"\n{'='*60}")
        print("AI ANALYSIS STARTING...")
        print(f"{'='*60}")
        
        response = model.generate_content(prompt)
        
        # 결과 저장
        analysis_result = {
            "timestamp": "2025-08-05T18:45:00",
            "top_5_data": analysis_data,
            "ai_analysis": response.text
        }
        
        output_path = Path(__file__).parent / 'reports' / 'top5_poker_analysis.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        # 텍스트 파일로도 저장
        txt_path = Path(__file__).parent / 'reports' / 'top5_poker_insights.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("TOP 5 POKER VIDEOS TREND ANALYSIS\n")
            f.write("=" * 60 + "\n\n")
            f.write("RAW DATA:\n")
            for i, video in enumerate(analysis_data, 1):
                f.write(f"{i}. {video['title']}\n")
                f.write(f"   Views: {video['views']:,} | Likes: {video['likes']:,} | Comments: {video['comments']:,}\n")
                f.write(f"   Engagement: {video['engagement_rate']}% | Channel: {video['channel']}\n\n")
            
            f.write("\nAI ANALYSIS & SHORTS IDEAS:\n")
            f.write("=" * 40 + "\n")
            f.write(response.text)
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETED!")
        print(f"{'='*60}")
        print(f"JSON Report: {output_path}")
        print(f"Text Report: {txt_path}")
        
        # 결과 미리보기
        preview = response.text[:800] + "..." if len(response.text) > 800 else response.text
        print(f"\nANALYSIS PREVIEW:\n{preview}")
        
        return response.text
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return None

if __name__ == "__main__":
    analyze_top5_poker_trends()