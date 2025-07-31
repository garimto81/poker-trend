#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최소 테스트: 'poker' 키워드로 상위 10개 비디오만 수집 및 분석
API 할당량 절약을 위한 경량 버전
"""

import os
import json
import asyncio
from datetime import datetime
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv

# UTF-8 인코딩 설정
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class MinimalPokerTrendAnalyzer:
    def __init__(self):
        load_dotenv()
        
        # API 키 로드
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.youtube_api_key or not self.gemini_api_key:
            raise ValueError("API keys not found in .env file")
        
        # YouTube API 클라이언트 초기화
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        
        # Gemini AI 초기화
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        self.collected_videos = []
    
    async def collect_poker_videos(self):
        """'poker' 키워드로 상위 10개 비디오 수집"""
        print("\n[1/4] YouTube에서 'poker' 비디오 검색 중...")
        
        try:
            # YouTube 검색 실행
            search_response = self.youtube.search().list(
                q='poker',
                part='id,snippet',
                maxResults=10,
                order='relevance',
                type='video',
                regionCode='US',
                relevanceLanguage='en'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # 비디오 상세 정보 가져오기
            videos_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # 데이터 추출
            for video in videos_response['items']:
                video_data = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'][:500],  # 처음 500자만
                    'channel': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0)),
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                
                # 참여율 계산
                if video_data['view_count'] > 0:
                    video_data['engagement_rate'] = (
                        (video_data['like_count'] + video_data['comment_count']) 
                        / video_data['view_count']
                    ) * 100
                else:
                    video_data['engagement_rate'] = 0
                
                self.collected_videos.append(video_data)
            
            print(f"✅ {len(self.collected_videos)}개 비디오 수집 완료")
            
        except Exception as e:
            print(f"❌ 비디오 수집 중 오류: {str(e)}")
            raise
    
    def display_collected_data(self):
        """수집된 데이터 표시"""
        print("\n[2/4] 수집된 비디오 데이터:")
        print("=" * 80)
        
        for i, video in enumerate(self.collected_videos, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   채널: {video['channel']}")
            print(f"   조회수: {video['view_count']:,}")
            print(f"   좋아요: {video['like_count']:,}")
            print(f"   댓글: {video['comment_count']:,}")
            print(f"   참여율: {video['engagement_rate']:.2f}%")
            print(f"   URL: {video['url']}")
            
            # 설명 일부 표시
            desc_preview = video['description'][:100] + "..." if len(video['description']) > 100 else video['description']
            print(f"   설명: {desc_preview}")
    
    async def analyze_trends_with_gemini(self):
        """Gemini AI로 트렌드 분석"""
        print("\n[3/4] Gemini AI로 트렌드 분석 중...")
        
        # 분석용 프롬프트 준비
        video_summaries = []
        for video in self.collected_videos:
            summary = f"""
제목: {video['title']}
조회수: {video['view_count']:,}
참여율: {video['engagement_rate']:.2f}%
설명: {video['description'][:200]}
"""
            video_summaries.append(summary)
        
        prompt = f"""
다음은 YouTube에서 'poker'로 검색한 상위 10개 비디오 데이터입니다:

{''.join(video_summaries)}

이 데이터를 바탕으로 현재 포커 콘텐츠의 주요 트렌드를 분석해주세요.

다음 형식으로 답변해주세요:

1. **주요 트렌드 (1-3개)**
   - 트렌드명: 설명

2. **인기 콘텐츠 유형**
   - 어떤 유형의 포커 콘텐츠가 인기인지

3. **시청자 관심사**
   - 현재 포커 커뮤니티가 관심있어 하는 주제

4. **콘텐츠 제작 추천**
   - 이 트렌드를 바탕으로 만들면 좋을 콘텐츠 아이디어 2-3개
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            self.trend_analysis = response.text
            print("✅ 트렌드 분석 완료")
            return self.trend_analysis
        except Exception as e:
            print(f"❌ Gemini AI 분석 중 오류: {str(e)}")
            return None
    
    def save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"minimal_poker_test_{timestamp}.json"
        
        results = {
            'analysis_time': datetime.now().isoformat(),
            'search_keyword': 'poker',
            'total_videos': len(self.collected_videos),
            'videos': self.collected_videos,
            'trend_analysis': self.trend_analysis if hasattr(self, 'trend_analysis') else None
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n[4/4] 결과가 {filename}에 저장되었습니다.")
        return filename

async def main():
    print("=" * 80)
    print("포커 트렌드 최소 테스트 (상위 10개 비디오)")
    print("=" * 80)
    
    analyzer = MinimalPokerTrendAnalyzer()
    
    # 1. 비디오 수집
    await analyzer.collect_poker_videos()
    
    # 2. 수집된 데이터 표시
    analyzer.display_collected_data()
    
    # 3. 트렌드 분석
    trend_analysis = await analyzer.analyze_trends_with_gemini()
    
    if trend_analysis:
        print("\n" + "=" * 80)
        print("📊 트렌드 분석 결과")
        print("=" * 80)
        print(trend_analysis)
    
    # 4. 결과 저장
    analyzer.save_results()
    
    # 통계 요약
    print("\n" + "=" * 80)
    print("📈 전체 통계 요약")
    print("=" * 80)
    
    total_views = sum(v['view_count'] for v in analyzer.collected_videos)
    total_likes = sum(v['like_count'] for v in analyzer.collected_videos)
    total_comments = sum(v['comment_count'] for v in analyzer.collected_videos)
    avg_engagement = sum(v['engagement_rate'] for v in analyzer.collected_videos) / len(analyzer.collected_videos)
    
    print(f"총 조회수: {total_views:,}")
    print(f"총 좋아요: {total_likes:,}")
    print(f"총 댓글: {total_comments:,}")
    print(f"평균 참여율: {avg_engagement:.2f}%")
    
    # 가장 인기있는 비디오
    most_viewed = max(analyzer.collected_videos, key=lambda x: x['view_count'])
    print(f"\n🏆 최다 조회 비디오:")
    print(f"   {most_viewed['title']}")
    print(f"   조회수: {most_viewed['view_count']:,}")
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())