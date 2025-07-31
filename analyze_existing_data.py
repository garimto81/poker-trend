#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 데이터에서 상위 10개 비디오 추출 및 트렌드 분석
"""

import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_top_10_videos():
    # 최신 분석 데이터 로드
    with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 바이럴 점수 기준 상위 10개 비디오 추출
    all_videos = data['videos']
    top_10_videos = sorted(all_videos, key=lambda x: x['viral_score'], reverse=True)[:10]
    
    print("=" * 80)
    print("포커 트렌드 분석 - 상위 10개 비디오")
    print("=" * 80)
    print("\n[수집된 데이터]")
    
    total_views = 0
    total_likes = 0
    total_comments = 0
    
    for i, video in enumerate(top_10_videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   키워드: {video['keyword_matched']}")
        print(f"   조회수: {video['view_count']:,}")
        print(f"   좋아요: {video['like_count']:,}")
        print(f"   댓글: {video.get('comment_count', 0):,}")
        print(f"   참여율: {video['engagement_rate']*100:.2f}%")
        print(f"   바이럴 점수: {video['viral_score']:.2f}")
        
        # 설명 일부 표시
        desc = video.get('description', '')[:150] + "..." if len(video.get('description', '')) > 150 else video.get('description', '')
        print(f"   설명: {desc}")
        
        total_views += video['view_count']
        total_likes += video['like_count']
        total_comments += video.get('comment_count', 0)
    
    # 전체 통계
    print("\n" + "=" * 80)
    print("전체 통계 (상위 10개 비디오)")
    print("=" * 80)
    print(f"총 조회수: {total_views:,}")
    print(f"총 좋아요: {total_likes:,}")
    print(f"총 댓글: {total_comments:,}")
    print(f"평균 참여율: {sum(v['engagement_rate'] for v in top_10_videos)/10*100:.2f}%")
    
    # Gemini AI로 트렌드 분석
    load_dotenv()
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if gemini_api_key:
        print("\n" + "=" * 80)
        print("Gemini AI 트렌드 분석")
        print("=" * 80)
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 분석 프롬프트 준비
        video_data = ""
        for i, video in enumerate(top_10_videos, 1):
            video_data += f"""
{i}. {video['title']}
   키워드: {video['keyword_matched']}
   조회수: {video['view_count']:,}
   참여율: {video['engagement_rate']*100:.2f}%
   설명: {video.get('description', '')[:200]}
"""
        
        prompt = f"""
다음은 포커 관련 YouTube 비디오 중 바이럴 점수가 가장 높은 상위 10개입니다:

{video_data}

이 데이터를 바탕으로 현재 포커 콘텐츠의 주요 트렌드를 분석해주세요.

다음 형식으로 답변해주세요:

1. **핵심 트렌드 3가지**
   - 각 트렌드에 대한 구체적 설명

2. **인기 콘텐츠 특징**
   - 높은 참여율을 보이는 콘텐츠의 공통점

3. **키워드별 인사이트**
   - 어떤 키워드가 가장 효과적인지와 그 이유

4. **콘텐츠 제작 추천사항**
   - 이 분석을 바탕으로 한 구체적인 콘텐츠 아이디어 3개
"""
        
        try:
            response = model.generate_content(prompt)
            print(response.text)
        except Exception as e:
            print(f"Gemini AI 분석 중 오류: {str(e)}")
    
    # 키워드별 분포
    print("\n" + "=" * 80)
    print("키워드별 분포 (상위 10개 중)")
    print("=" * 80)
    keyword_count = {}
    for video in top_10_videos:
        keyword = video['keyword_matched']
        keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    for keyword, count in sorted(keyword_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{keyword}: {count}개")

if __name__ == "__main__":
    analyze_top_10_videos()