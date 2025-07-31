"""
포커 트렌드 분석기 - 특정 키워드 기반 YouTube 분석
사용자 지정 키워드: Holdem, WSOP, Cashgame, PokerStars, GGPoker, GTO, WPT
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 필수 라이브러리
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import google.generativeai as genai
    import pandas as pd
    import logging
except ImportError as e:
    print(f"필수 라이브러리를 설치해주세요: {e}")
    print("pip install google-api-python-client google-generativeai pandas")
    exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('poker_trend_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VideoData:
    """비디오 데이터 구조"""
    video_id: str
    title: str
    description: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    channel_title: str
    duration: str
    keyword_matched: str
    relevance_score: float = 0.0

@dataclass
class TrendInsight:
    """트렌드 인사이트 구조"""
    trend_title: str
    trend_description: str
    confidence_score: float
    supporting_videos: List[str]
    trend_category: str  # 'emerging', 'stable', 'declining'
    keywords: List[str]
    impact_level: str  # 'nano', 'micro', 'meso', 'macro'

class SpecificKeywordTrendAnalyzer:
    """특정 키워드 기반 포커 트렌드 분석기"""
    
    def __init__(self, youtube_api_key: str, gemini_api_key: str):
        """
        초기화
        
        Args:
            youtube_api_key: YouTube Data API v3 키
            gemini_api_key: Gemini AI API 키
        """
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 사용자 지정 키워드
        self.target_keywords = [
            "Holdem", "WSOP", "Cashgame", "PokerStars", 
            "GGPoker", "GTO", "WPT"
        ]
        
        # 키워드별 검색 쿼리 확장
        self.keyword_queries = {
            "Holdem": ["Texas Holdem", "Hold'em poker", "Holdem strategy"],
            "WSOP": ["World Series of Poker", "WSOP 2024", "WSOP bracelet"],
            "Cashgame": ["Cash game poker", "Live cash game", "Online cash"],
            "PokerStars": ["PokerStars tournament", "PokerStars live", "PS poker"],
            "GGPoker": ["GG Poker online", "GGPoker tournament", "GG network"],
            "GTO": ["GTO poker", "Game theory optimal", "GTO solver"],
            "WPT": ["World Poker Tour", "WPT tournament", "WPT final table"]
        }
        
        self.collected_videos: List[VideoData] = []
        
    async def collect_videos_for_keyword(self, keyword: str, max_results: int = 50) -> List[VideoData]:
        """
        특정 키워드에 대해 YouTube 비디오 수집
        
        Args:
            keyword: 검색할 키워드
            max_results: 수집할 최대 비디오 수
            
        Returns:
            수집된 비디오 데이터 리스트
        """
        videos = []
        queries = self.keyword_queries.get(keyword, [keyword])
        
        for query in queries:
            try:
                logger.info(f"키워드 '{query}' 검색 시작...")
                
                # 최신 1개월 내 비디오 검색
                published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                
                search_response = self.youtube.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=min(20, max_results // len(queries)),
                    order='relevance',
                    type='video',
                    publishedAfter=published_after,
                    regionCode='US',
                    relevanceLanguage='en'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                if video_ids:
                    # 비디오 상세 정보 수집
                    video_details = self.youtube.videos().list(
                        part='statistics,snippet,contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for item in video_details['items']:
                        try:
                            stats = item['statistics']
                            snippet = item['snippet']
                            
                            video = VideoData(
                                video_id=item['id'],
                                title=snippet['title'],
                                description=snippet.get('description', ''),
                                published_at=snippet['publishedAt'],
                                view_count=int(stats.get('viewCount', 0)),
                                like_count=int(stats.get('likeCount', 0)),
                                comment_count=int(stats.get('commentCount', 0)),
                                channel_title=snippet['channelTitle'],
                                duration=item['contentDetails']['duration'],
                                keyword_matched=keyword,
                                relevance_score=self._calculate_relevance_score(
                                    snippet['title'] + ' ' + snippet.get('description', ''),
                                    keyword
                                )
                            )
                            videos.append(video)
                            
                        except (KeyError, ValueError) as e:
                            logger.warning(f"비디오 파싱 오류: {e}")
                            continue
                
                # API 제한 고려 대기
                await asyncio.sleep(0.1)
                
            except HttpError as e:
                logger.error(f"YouTube API 오류 (키워드: {query}): {e}")
                continue
        
        # 관련성 점수로 정렬
        videos.sort(key=lambda x: x.relevance_score, reverse=True)
        return videos[:max_results]
    
    def _calculate_relevance_score(self, text: str, keyword: str) -> float:
        """
        텍스트와 키워드의 관련성 점수 계산
        
        Args:
            text: 분석할 텍스트
            keyword: 기준 키워드
            
        Returns:
            관련성 점수 (0.0-1.0)
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # 기본 점수: 키워드 포함 여부
        base_score = 0.5 if keyword_lower in text_lower else 0.0
        
        # 추가 점수 요인들
        poker_terms = [
            'poker', 'tournament', 'cash', 'game', 'strategy', 'bluff',
            'fold', 'bet', 'raise', 'call', 'all-in', 'final table'
        ]
        
        bonus_score = sum(0.05 for term in poker_terms if term in text_lower)
        
        # 제목에 키워드 포함 시 추가 점수
        title_bonus = 0.3 if keyword_lower in text_lower[:100] else 0.0
        
        return min(1.0, base_score + bonus_score + title_bonus)
    
    async def collect_all_videos(self) -> List[VideoData]:
        """
        모든 키워드에 대해 비디오 수집
        
        Returns:
            전체 수집된 비디오 리스트
        """
        logger.info("전체 키워드 비디오 수집 시작...")
        
        all_videos = []
        tasks = []
        
        # 비동기로 모든 키워드 검색
        for keyword in self.target_keywords:
            task = self.collect_videos_for_keyword(keyword, 50)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"키워드 '{self.target_keywords[i]}' 수집 실패: {result}")
            else:
                all_videos.extend(result)
                logger.info(f"키워드 '{self.target_keywords[i]}': {len(result)}개 비디오 수집")
        
        # 중복 제거 (video_id 기준)
        unique_videos = {}
        for video in all_videos:
            if video.video_id not in unique_videos:
                unique_videos[video.video_id] = video
        
        self.collected_videos = list(unique_videos.values())
        logger.info(f"총 {len(self.collected_videos)}개 고유 비디오 수집 완료")
        
        # 상위 50개만 선택 (관련성 점수 기준)
        self.collected_videos.sort(key=lambda x: x.relevance_score, reverse=True)
        self.collected_videos = self.collected_videos[:50]
        
        return self.collected_videos
    
    def prepare_gemini_prompt(self, videos: List[VideoData]) -> str:
        """
        Gemini AI 분석을 위한 프롬프트 준비
        
        Args:
            videos: 분석할 비디오 데이터 리스트
            
        Returns:
            Gemini AI 프롬프트
        """
        # 비디오 데이터를 텍스트로 변환
        video_texts = []
        for i, video in enumerate(videos, 1):
            video_text = f"""
비디오 #{i}:
- 제목: {video.title}
- 설명: {video.description[:300]}...
- 채널: {video.channel_title}
- 조회수: {video.view_count:,}
- 좋아요: {video.like_count:,}
- 키워드: {video.keyword_matched}
- 게시일: {video.published_at}
"""
            video_texts.append(video_text)
        
        videos_content = "\n".join(video_texts)
        
        prompt = f"""
당신은 포커 업계의 전문 트렌드 분석가입니다. 다음 50개 YouTube 비디오의 제목과 설명을 분석하여 현재 포커 커뮤니티의 트렌드를 추론해주세요.

분석 대상 키워드: {', '.join(self.target_keywords)}

YouTube 비디오 데이터:
{videos_content}

다음 기준으로 분석해주세요:

1. **트렌드 식별**: 1-3개의 주요 트렌드를 식별
2. **트렌드 분류**: 각 트렌드를 다음 중 하나로 분류
   - Nano (바이럴, 수시간-수일)
   - Micro (전략/기술, 가변적)
   - Meso (토너먼트/인물, 수일-수주)
   - Macro (산업 변화, 6-24개월)

3. **분석 결과 JSON 형식**:
```json
{{
  "analysis_date": "{datetime.now().isoformat()}",
  "total_videos_analyzed": {len(videos)},
  "trends": [
    {{
      "trend_title": "트렌드 제목",
      "trend_description": "트렌드 상세 설명 (2-3문장)",
      "confidence_score": 0.85,
      "supporting_videos": ["video_id1", "video_id2"],
      "trend_category": "emerging/stable/declining",
      "keywords": ["관련키워드1", "관련키워드2"],
      "impact_level": "nano/micro/meso/macro",
      "content_potential": "높음/중간/낮음",
      "recommended_action": "콘텐츠 제작 권장사항"
    }}
  ],
  "keyword_insights": {{
    "most_trending": "가장 트렌딩한 키워드",
    "emerging_themes": ["새로 떠오르는 주제들"],
    "declining_themes": ["줄어드는 주제들"]
  }},
  "content_recommendations": [
    "즉시 제작 가능한 콘텐츠 아이디어 3-5개"
  ]
}}
```

특히 다음 사항에 주의하여 분석해주세요:
- 조회수와 좋아요 수가 높은 비디오의 공통점
- 최근 게시된 비디오들의 주제 변화
- 각 키워드별 콘텐츠의 성향과 트렌드
- 포커 커뮤니티의 관심사 변화
- 콘텐츠 제작자들이 주목하는 이슈

분석 결과를 위의 JSON 형식으로만 제공해주세요.
"""
        return prompt
    
    async def analyze_with_gemini(self, videos: List[VideoData]) -> Dict[str, Any]:
        """
        Gemini AI를 사용한 트렌드 분석
        
        Args:
            videos: 분석할 비디오 데이터
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info("Gemini AI 트렌드 분석 시작...")
        
        prompt = self.prepare_gemini_prompt(videos)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            
            # JSON 응답 파싱
            response_text = response.text
            
            # JSON 부분만 추출 (```json ... ``` 제거)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            analysis_result = json.loads(json_text)
            
            logger.info(f"트렌드 분석 완료: {len(analysis_result.get('trends', []))}개 트렌드 식별")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Gemini AI 분석 오류: {e}")
            
            # 폴백: 기본 분석 결과
            return {
                "analysis_date": datetime.now().isoformat(),
                "total_videos_analyzed": len(videos),
                "trends": [
                    {
                        "trend_title": "분석 오류 발생",
                        "trend_description": f"Gemini AI 분석 중 오류가 발생했습니다: {str(e)}",
                        "confidence_score": 0.0,
                        "supporting_videos": [],
                        "trend_category": "error",
                        "keywords": self.target_keywords,
                        "impact_level": "unknown",
                        "content_potential": "낮음",
                        "recommended_action": "수동 분석 필요"
                    }
                ],
                "keyword_insights": {
                    "most_trending": "분석 불가",
                    "emerging_themes": [],
                    "declining_themes": []
                },
                "content_recommendations": ["오류 해결 후 재분석 필요"]
            }
    
    def save_results(self, videos: List[VideoData], analysis: Dict[str, Any], 
                    filename_prefix: str = "poker_trend_analysis") -> str:
        """
        분석 결과 저장
        
        Args:
            videos: 수집된 비디오 데이터
            analysis: Gemini AI 분석 결과
            filename_prefix: 파일명 접두사
            
        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        
        # 비디오 데이터를 딕셔너리로 변환
        videos_dict = []
        for video in videos:
            videos_dict.append({
                'video_id': video.video_id,
                'title': video.title,
                'description': video.description,
                'published_at': video.published_at,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'channel_title': video.channel_title,
                'duration': video.duration,
                'keyword_matched': video.keyword_matched,
                'relevance_score': video.relevance_score,
                'url': f"https://www.youtube.com/watch?v={video.video_id}"
            })
        
        result = {
            'metadata': {
                'analysis_time': datetime.now().isoformat(),
                'target_keywords': self.target_keywords,
                'total_videos_collected': len(videos),
                'analyzer_version': '1.0.0'
            },
            'videos': videos_dict,
            'gemini_analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"분석 결과 저장 완료: {filename}")
        return filename
    
    def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """
        분석 결과 요약 리포트 생성
        
        Args:
            analysis: Gemini AI 분석 결과
            
        Returns:
            요약 리포트 텍스트
        """
        report = f"""
🎯 포커 트렌드 분석 리포트
분석 일시: {analysis.get('analysis_date', 'Unknown')}
분석 비디오 수: {analysis.get('total_videos_analyzed', 0)}개

📈 식별된 트렌드:
"""
        
        trends = analysis.get('trends', [])
        for i, trend in enumerate(trends, 1):
            report += f"""
{i}. {trend.get('trend_title', 'Unknown')}
   - 카테고리: {trend.get('trend_category', 'unknown')} ({trend.get('impact_level', 'unknown')} 레벨)
   - 신뢰도: {trend.get('confidence_score', 0):.2f}
   - 설명: {trend.get('trend_description', 'No description')}
   - 콘텐츠 잠재력: {trend.get('content_potential', 'unknown')}
   - 추천 액션: {trend.get('recommended_action', 'No action')}
"""
        
        keyword_insights = analysis.get('keyword_insights', {})
        report += f"""
🔥 키워드 인사이트:
- 가장 트렌딩: {keyword_insights.get('most_trending', 'Unknown')}
- 떠오르는 주제: {', '.join(keyword_insights.get('emerging_themes', []))}
- 줄어드는 주제: {', '.join(keyword_insights.get('declining_themes', []))}

💡 콘텐츠 제작 권장사항:
"""
        
        recommendations = analysis.get('content_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report

async def main():
    """메인 실행 함수"""
    
    # 환경 변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # API 키 설정 (환경 변수에서 가져오기)
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not youtube_api_key or not gemini_api_key or \
       youtube_api_key == 'your_youtube_api_key_here' or \
       gemini_api_key == 'your_gemini_api_key_here':
        print("API 키를 설정해주세요:")
        print("1. .env 파일을 편집하세요")
        print("2. YOUTUBE_API_KEY와 GEMINI_API_KEY에 실제 키를 입력하세요")
        print("\nAPI 키 생성 방법:")
        print("YouTube API: https://console.developers.google.com/")
        print("Gemini AI: https://makersuite.google.com/app/apikey")
        return
    
    # 분석기 초기화
    analyzer = SpecificKeywordTrendAnalyzer(youtube_api_key, gemini_api_key)
    
    try:
        # 1. 비디오 수집
        print("🔍 키워드별 YouTube 비디오 수집 중...")
        videos = await analyzer.collect_all_videos()
        
        print(f"✅ 총 {len(videos)}개 비디오 수집 완료")
        
        # 2. Gemini AI 분석
        print("🤖 Gemini AI 트렌드 분석 중...")
        analysis = await analyzer.analyze_with_gemini(videos)
        
        # 3. 결과 저장
        print("💾 분석 결과 저장 중...")
        saved_file = analyzer.save_results(videos, analysis)
        
        # 4. 요약 리포트 출력
        print("📊 분석 결과 요약:")
        print("=" * 60)
        summary = analyzer.generate_summary_report(analysis)
        print(summary)
        
        print(f"\n📁 상세 결과는 {saved_file} 파일을 확인하세요.")
        
    except Exception as e:
        logger.error(f"분석 프로세스 오류: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())