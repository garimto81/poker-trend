# -*- coding: utf-8 -*-
"""
포커 트렌드 분석기 - 조회수 중심 강화 버전
조회수, 좋아요, 댓글 수를 종합적으로 분석하여 트렌드 추론
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import statistics

from dotenv import load_dotenv
load_dotenv()

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai

@dataclass
class EnhancedVideoData:
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
    engagement_score: float = 0.0
    viral_potential: str = "low"
    performance_tier: str = "unknown"

class EnhancedPokerTrendAnalyzer:
    def __init__(self, youtube_api_key: str, gemini_api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.target_keywords = [
            "Holdem", "WSOP", "Cashgame", "PokerStars", 
            "GGPoker", "GTO", "WPT"
        ]
        
        self.keyword_queries = {
            "Holdem": ["Texas Holdem", "Hold'em poker", "Holdem strategy"],
            "WSOP": ["World Series of Poker", "WSOP 2025", "WSOP bracelet"],
            "Cashgame": ["Cash game poker", "Live cash game", "Online cash"],
            "PokerStars": ["PokerStars tournament", "PokerStars live", "PS poker"],
            "GGPoker": ["GG Poker online", "GGPoker tournament", "GG network"],
            "GTO": ["GTO poker", "Game theory optimal", "GTO solver"],
            "WPT": ["World Poker Tour", "WPT tournament", "WPT final table"]
        }
        
        self.collected_videos: List[EnhancedVideoData] = []
    
    def _calculate_engagement_score(self, video: EnhancedVideoData) -> float:
        """참여도 점수 계산 (조회수 대비 좋아요, 댓글 비율)"""
        if video.view_count == 0:
            return 0.0
        
        # 좋아요 비율 (0-1)
        like_ratio = min(video.like_count / video.view_count, 0.1) * 10  # 최대 10% 가정
        
        # 댓글 비율 (0-1)
        comment_ratio = min(video.comment_count / video.view_count, 0.05) * 20  # 최대 5% 가정
        
        # 종합 참여도 점수 (0-1)
        engagement = (like_ratio * 0.7 + comment_ratio * 0.3)
        return min(engagement, 1.0)
    
    def _determine_performance_tier(self, view_count: int) -> str:
        """조회수 기반 성과 등급 분류"""
        if view_count >= 1000000:
            return "viral"  # 100만 이상
        elif view_count >= 100000:
            return "high"   # 10만 이상
        elif view_count >= 10000:
            return "medium" # 1만 이상
        elif view_count >= 1000:
            return "low"    # 1천 이상
        else:
            return "minimal" # 1천 미만
    
    def _determine_viral_potential(self, video: EnhancedVideoData) -> str:
        """바이럴 잠재력 평가"""
        # 조회수와 참여도를 종합 평가
        if video.view_count >= 500000 and video.engagement_score >= 0.05:
            return "very_high"
        elif video.view_count >= 100000 and video.engagement_score >= 0.03:
            return "high"
        elif video.view_count >= 50000 and video.engagement_score >= 0.02:
            return "medium"
        elif video.view_count >= 10000 and video.engagement_score >= 0.01:
            return "low"
        else:
            return "minimal"
    
    def _calculate_relevance_score(self, text: str, keyword: str) -> float:
        """관련성 점수 계산 (기존 로직 유지)"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        base_score = 0.5 if keyword_lower in text_lower else 0.0
        
        poker_terms = [
            'poker', 'tournament', 'cash', 'game', 'strategy', 'bluff',
            'fold', 'bet', 'raise', 'call', 'all-in', 'final table',
            'bracelet', 'wsop', 'wpt', 'high roller', 'live', 'online'
        ]
        
        bonus_score = sum(0.05 for term in poker_terms if term in text_lower)
        title_bonus = 0.3 if keyword_lower in text_lower[:100] else 0.0
        
        return min(1.0, base_score + bonus_score + title_bonus)

    async def collect_videos_for_keyword(self, keyword: str, max_results: int = 50) -> List[EnhancedVideoData]:
        """키워드별 비디오 수집 (조회수 데이터 강화)"""
        videos = []
        queries = self.keyword_queries.get(keyword, [keyword])
        
        print(f"키워드 '{keyword}' 검색 중...")
        
        for query in queries:
            try:
                # 최근 60일 내 비디오로 확장 (더 많은 데이터)
                published_after = (datetime.now() - timedelta(days=60)).isoformat() + 'Z'
                
                search_response = self.youtube.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=min(25, max_results // len(queries)),  # 더 많은 결과
                    order='relevance',  # 관련성 우선
                    type='video',
                    publishedAfter=published_after,
                    regionCode='US',
                    relevanceLanguage='en'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                if video_ids:
                    video_details = self.youtube.videos().list(
                        part='statistics,snippet,contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for item in video_details['items']:
                        try:
                            stats = item['statistics']
                            snippet = item['snippet']
                            
                            video = EnhancedVideoData(
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
                                relevance_score=0.0,
                                engagement_score=0.0,
                                viral_potential="low",
                                performance_tier="unknown"
                            )
                            
                            # 점수 계산
                            video.relevance_score = self._calculate_relevance_score(
                                video.title + ' ' + video.description, keyword
                            )
                            video.engagement_score = self._calculate_engagement_score(video)
                            video.performance_tier = self._determine_performance_tier(video.view_count)
                            video.viral_potential = self._determine_viral_potential(video)
                            
                            videos.append(video)
                            
                        except (KeyError, ValueError) as e:
                            continue
                
                await asyncio.sleep(0.1)
                
            except HttpError as e:
                print(f"YouTube API 오류 (키워드: {query}): {e}")
                continue
        
        # 조회수와 관련성을 결합한 정렬
        videos.sort(key=lambda x: (x.view_count * x.relevance_score), reverse=True)
        return videos[:max_results]

    async def collect_all_videos(self) -> List[EnhancedVideoData]:
        """전체 키워드 비디오 수집"""
        print("전체 키워드 비디오 수집 시작...")
        
        all_videos = []
        tasks = []
        
        for keyword in self.target_keywords:
            task = self.collect_videos_for_keyword(keyword, 15)  # 키워드당 15개
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"키워드 '{self.target_keywords[i]}' 수집 실패: {result}")
            else:
                all_videos.extend(result)
                print(f"키워드 '{self.target_keywords[i]}': {len(result)}개 비디오 수집")
        
        # 중복 제거
        unique_videos = {}
        for video in all_videos:
            if video.video_id not in unique_videos:
                unique_videos[video.video_id] = video
        
        self.collected_videos = list(unique_videos.values())
        
        # 조회수 * 관련성 점수로 최종 정렬
        self.collected_videos.sort(
            key=lambda x: (x.view_count * x.relevance_score * (1 + x.engagement_score)), 
            reverse=True
        )
        self.collected_videos = self.collected_videos[:50]
        
        print(f"총 {len(self.collected_videos)}개 고유 비디오 수집 완료")
        return self.collected_videos

    def analyze_viewcount_patterns(self, videos: List[EnhancedVideoData]) -> Dict[str, Any]:
        """조회수 패턴 분석"""
        if not videos:
            return {}
        
        view_counts = [v.view_count for v in videos]
        engagement_scores = [v.engagement_score for v in videos]
        
        # 키워드별 조회수 분석
        keyword_stats = {}
        for keyword in self.target_keywords:
            keyword_videos = [v for v in videos if v.keyword_matched == keyword]
            if keyword_videos:
                keyword_views = [v.view_count for v in keyword_videos]
                keyword_stats[keyword] = {
                    'count': len(keyword_videos),
                    'avg_views': statistics.mean(keyword_views),
                    'max_views': max(keyword_views),
                    'total_views': sum(keyword_views),
                    'top_video': max(keyword_videos, key=lambda x: x.view_count).title
                }
        
        # 성과 등급별 분포
        tier_distribution = {}
        for video in videos:
            tier = video.performance_tier
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            'total_videos': len(videos),
            'total_views': sum(view_counts),
            'avg_views': statistics.mean(view_counts),
            'median_views': statistics.median(view_counts),
            'max_views': max(view_counts),
            'min_views': min(view_counts),
            'avg_engagement': statistics.mean(engagement_scores),
            'keyword_performance': keyword_stats,
            'performance_distribution': tier_distribution,
            'top_performers': [
                {
                    'title': v.title,
                    'views': v.view_count,
                    'keyword': v.keyword_matched,
                    'engagement': round(v.engagement_score, 4),
                    'viral_potential': v.viral_potential
                }
                for v in sorted(videos, key=lambda x: x.view_count, reverse=True)[:10]
            ]
        }

    def prepare_enhanced_gemini_prompt(self, videos: List[EnhancedVideoData], viewcount_analysis: Dict[str, Any]) -> str:
        """조회수 분석을 포함한 강화된 Gemini 프롬프트"""
        
        # 상위 20개 비디오만 상세 분석 (토큰 제한 고려)
        top_videos = videos[:20]
        
        video_texts = []
        for i, video in enumerate(top_videos, 1):
            video_text = f"""
비디오 #{i}:
- 제목: {video.title}
- 설명: {video.description[:200]}...
- 채널: {video.channel_title}
- 조회수: {video.view_count:,}
- 좋아요: {video.like_count:,}
- 댓글: {video.comment_count:,}
- 키워드: {video.keyword_matched}
- 게시일: {video.published_at}
- 참여도 점수: {video.engagement_score:.4f}
- 성과 등급: {video.performance_tier}
- 바이럴 잠재력: {video.viral_potential}
"""
            video_texts.append(video_text)
        
        videos_content = "\n".join(video_texts)
        
        # 조회수 분석 요약
        viewcount_summary = f"""
조회수 분석 요약:
- 총 비디오 수: {viewcount_analysis.get('total_videos', 0)}개
- 총 조회수: {viewcount_analysis.get('total_views', 0):,}
- 평균 조회수: {viewcount_analysis.get('avg_views', 0):,.0f}
- 최고 조회수: {viewcount_analysis.get('max_views', 0):,}
- 평균 참여도: {viewcount_analysis.get('avg_engagement', 0):.4f}

키워드별 성과:
"""
        
        for keyword, stats in viewcount_analysis.get('keyword_performance', {}).items():
            viewcount_summary += f"- {keyword}: 평균 {stats['avg_views']:,.0f} 조회수, 최고 {stats['max_views']:,}\n"

        prompt = f"""
당신은 포커 업계의 전문 트렌드 분석가입니다. YouTube 비디오의 조회수, 참여도, 키워드 성과를 종합 분석하여 포커 커뮤니티의 트렌드를 추론해주세요.

{viewcount_summary}

상위 {len(top_videos)}개 비디오 상세 데이터:
{videos_content}

다음 기준으로 분석해주세요:

1. **조회수 기반 트렌드 식별**: 높은 조회수를 기록한 콘텐츠의 공통점 분석
2. **참여도 패턴**: 좋아요, 댓글 비율이 높은 콘텐츠의 특징
3. **키워드별 성과**: 어떤 키워드가 가장 많은 관심을 받고 있는지
4. **바이럴 잠재력**: 높은 성과를 보인 콘텐츠의 바이럴 요소

분석 결과를 다음 JSON 형식으로 제공:
{{
  "analysis_date": "{datetime.now().isoformat()}",
  "total_videos_analyzed": {len(videos)},
  "viewcount_insights": {{
    "total_views": {viewcount_analysis.get('total_views', 0)},
    "avg_views": {viewcount_analysis.get('avg_views', 0)},
    "top_performing_keyword": "가장 성과가 좋은 키워드",
    "engagement_leaders": ["높은 참여도를 보인 콘텐츠 유형들"],
    "viral_factors": ["바이럴 성공 요인들"]
  }},
  "trends": [
    {{
      "trend_title": "트렌드 제목",
      "trend_description": "조회수와 참여도 데이터를 바탕으로 한 트렌드 설명",
      "confidence_score": 0.85,
      "supporting_videos": ["고조회수 비디오 ID들"],
      "viewcount_evidence": "조회수 데이터로 뒷받침되는 근거",
      "trend_category": "emerging/stable/declining",
      "keywords": ["관련키워드들"],
      "impact_level": "nano/micro/meso/macro",
      "content_potential": "높음/중간/낮음",
      "recommended_action": "조회수 향상을 위한 구체적 액션"
    }}
  ],
  "keyword_insights": {{
    "most_trending": "최고 조회수 키워드",
    "highest_engagement": "최고 참여도 키워드",
    "emerging_themes": ["새로 떠오르는 주제들"],
    "declining_themes": ["줄어드는 주제들"]
  }},
  "content_recommendations": [
    "조회수 최적화된 콘텐츠 아이디어 5개"
  ]
}}

조회수, 참여도, 성과 데이터를 중심으로 분석 결과를 JSON 형식으로만 제공해주세요.
"""
        return prompt

    async def analyze_with_gemini(self, videos: List[EnhancedVideoData]) -> Dict[str, Any]:
        """조회수 분석을 포함한 Gemini AI 트렌드 분석"""
        print("조회수 패턴 분석 중...")
        viewcount_analysis = self.analyze_viewcount_patterns(videos)
        
        print("Gemini AI 강화 트렌드 분석 시작...")
        
        prompt = self.prepare_enhanced_gemini_prompt(videos, viewcount_analysis)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            
            # JSON 부분 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            analysis_result = json.loads(json_text)
            
            # 조회수 분석 데이터 추가
            analysis_result['detailed_viewcount_analysis'] = viewcount_analysis
            
            print(f"강화 트렌드 분석 완료: {len(analysis_result.get('trends', []))}개 트렌드 식별")
            return analysis_result
            
        except Exception as e:
            print(f"Gemini AI 분석 오류: {e}")
            
            # 조회수 기반 폴백 분석
            return {
                "analysis_date": datetime.now().isoformat(),
                "total_videos_analyzed": len(videos),
                "viewcount_insights": {
                    "total_views": viewcount_analysis.get('total_views', 0),
                    "avg_views": viewcount_analysis.get('avg_views', 0),
                    "top_performing_keyword": max(viewcount_analysis.get('keyword_performance', {}).keys(), 
                                                key=lambda k: viewcount_analysis['keyword_performance'][k]['avg_views']) if viewcount_analysis.get('keyword_performance') else "unknown",
                    "engagement_leaders": ["분석 실패로 확인 불가"],
                    "viral_factors": ["분석 실패로 확인 불가"]
                },
                "trends": [
                    {
                        "trend_title": f"분석 오류 발생: {str(e)[:100]}",
                        "trend_description": "조회수 데이터는 수집되었으나 AI 분석 중 오류가 발생했습니다.",
                        "confidence_score": 0.0,
                        "supporting_videos": [],
                        "viewcount_evidence": f"총 {viewcount_analysis.get('total_views', 0):,} 조회수 데이터 수집됨",
                        "trend_category": "error",
                        "keywords": self.target_keywords,
                        "impact_level": "unknown",
                        "content_potential": "낮음",
                        "recommended_action": "오류 해결 후 재분석 필요"
                    }
                ],
                "detailed_viewcount_analysis": viewcount_analysis,
                "keyword_insights": {
                    "most_trending": "분석 불가",
                    "highest_engagement": "분석 불가",
                    "emerging_themes": [],
                    "declining_themes": []
                },
                "content_recommendations": ["오류 해결 후 재분석 필요"]
            }

    def save_enhanced_results(self, videos: List[EnhancedVideoData], analysis: Dict[str, Any]) -> str:
        """강화된 결과 저장 (조회수 상세 정보 포함)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_poker_trend_analysis_{timestamp}.json"
        
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
                'engagement_score': video.engagement_score,
                'performance_tier': video.performance_tier,
                'viral_potential': video.viral_potential,
                'url': f"https://www.youtube.com/watch?v={video.video_id}"
            })
        
        result = {
            'metadata': {
                'analysis_time': datetime.now().isoformat(),
                'target_keywords': self.target_keywords,
                'total_videos_collected': len(videos),
                'analyzer_version': '2.0.0-enhanced',
                'features': ['viewcount_analysis', 'engagement_scoring', 'viral_potential', 'performance_tiers']
            },
            'videos': videos_dict,
            'gemini_analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"강화된 분석 결과 저장 완료: {filename}")
        return filename

    def generate_enhanced_summary_report(self, analysis: Dict[str, Any]) -> str:
        """조회수 중심 강화된 요약 리포트"""
        viewcount_insights = analysis.get('viewcount_insights', {})
        detailed_analysis = analysis.get('detailed_viewcount_analysis', {})
        
        report = f"""
포커 트렌드 분석 리포트 (조회수 강화 버전)
분석 일시: {analysis.get('analysis_date', 'Unknown')}
분석 비디오 수: {analysis.get('total_videos_analyzed', 0)}개

조회수 인사이트:
- 총 조회수: {viewcount_insights.get('total_views', 0):,}
- 평균 조회수: {viewcount_insights.get('avg_views', 0):,.0f}
- 최고 성과 키워드: {viewcount_insights.get('top_performing_keyword', 'Unknown')}
- 평균 참여도: {detailed_analysis.get('avg_engagement', 0):.4f}

성과 등급별 분포:
"""
        
        for tier, count in detailed_analysis.get('performance_distribution', {}).items():
            report += f"- {tier}: {count}개\n"
        
        report += "\n키워드별 성과:\n"
        for keyword, stats in detailed_analysis.get('keyword_performance', {}).items():
            report += f"- {keyword}: 평균 {stats['avg_views']:,.0f} 조회수 ({stats['count']}개 비디오)\n"
        
        report += "\n상위 성과 비디오:\n"
        for i, video in enumerate(detailed_analysis.get('top_performers', [])[:5], 1):
            report += f"{i}. {video['title'][:50]}... ({video['views']:,} 조회수, {video['keyword']})\n"
        
        report += "\n식별된 트렌드:\n"
        trends = analysis.get('trends', [])
        for i, trend in enumerate(trends, 1):
            report += f"""
{i}. {trend.get('trend_title', 'Unknown')}
   - 카테고리: {trend.get('trend_category', 'unknown')} ({trend.get('impact_level', 'unknown')} 레벨)
   - 신뢰도: {trend.get('confidence_score', 0):.2f}
   - 설명: {trend.get('trend_description', 'No description')}
   - 조회수 근거: {trend.get('viewcount_evidence', 'No evidence')}
   - 콘텐츠 잠재력: {trend.get('content_potential', 'unknown')}
   - 추천 액션: {trend.get('recommended_action', 'No action')}
"""
        
        keyword_insights = analysis.get('keyword_insights', {})
        report += f"""
키워드 인사이트:
- 최고 조회수: {keyword_insights.get('most_trending', 'Unknown')}
- 최고 참여도: {keyword_insights.get('highest_engagement', 'Unknown')}
- 떠오르는 주제: {', '.join(keyword_insights.get('emerging_themes', []))}
- 줄어드는 주제: {', '.join(keyword_insights.get('declining_themes', []))}

조회수 최적화 콘텐츠 추천:
"""
        
        recommendations = analysis.get('content_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report

async def main():
    """메인 실행 함수"""
    # API 키 확인
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not youtube_api_key or not gemini_api_key or \
       youtube_api_key == 'your_youtube_api_key_here' or \
       gemini_api_key == 'your_gemini_api_key_here':
        print("API 키를 설정해주세요:")
        print("1. .env 파일을 편집하세요")
        print("2. YOUTUBE_API_KEY와 GEMINI_API_KEY에 실제 키를 입력하세요")
        return
    
    try:
        # 강화된 분석기 초기화
        analyzer = EnhancedPokerTrendAnalyzer(youtube_api_key, gemini_api_key)
        
        # 1. 비디오 수집 (조회수 중심)
        print("조회수 중심 키워드별 YouTube 비디오 수집 중...")
        videos = await analyzer.collect_all_videos()
        
        if not videos:
            print("수집된 비디오가 없습니다.")
            return
        
        print(f"총 {len(videos)}개 비디오 수집 완료")
        print(f"총 조회수: {sum(v.view_count for v in videos):,}")
        print(f"평균 조회수: {sum(v.view_count for v in videos) // len(videos):,}")
        
        # 2. 강화된 Gemini AI 분석
        print("조회수 기반 강화 트렌드 분석 중...")
        analysis = await analyzer.analyze_with_gemini(videos)
        
        # 3. 강화된 결과 저장
        print("강화된 분석 결과 저장 중...")
        saved_file = analyzer.save_enhanced_results(videos, analysis)
        
        # 4. 강화된 요약 리포트 출력
        print("강화된 분석 결과 요약:")
        print("=" * 80)
        summary = analyzer.generate_enhanced_summary_report(analysis)
        print(summary)
        
        print(f"상세 결과는 {saved_file} 파일을 확인하세요.")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())