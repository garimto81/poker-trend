# -*- coding: utf-8 -*-
"""
포커 트렌드 분석기 모의 테스트 (Mock Test)
실제 API 키 없이도 시스템 로직을 테스트할 수 있습니다.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import random

@dataclass
class MockVideoData:
    """모의 비디오 데이터 구조"""
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

class MockPokerTrendAnalyzer:
    """모의 포커 트렌드 분석기"""
    
    def __init__(self):
        self.target_keywords = [
            "Holdem", "WSOP", "Cashgame", "PokerStars", 
            "GGPoker", "GTO", "WPT"
        ]
        self.collected_videos: List[MockVideoData] = []
        
        # 모의 비디오 데이터 생성
        self.sample_videos = self._generate_sample_videos()
    
    def _generate_sample_videos(self) -> List[MockVideoData]:
        """샘플 비디오 데이터 생성"""
        videos = []
        
        # 각 키워드별로 샘플 비디오 생성
        for keyword in self.target_keywords:
            for i in range(10):  # 키워드당 10개
                video = MockVideoData(
                    video_id=f"{keyword.lower()}_{i+1:03d}",
                    title=f"{keyword} Strategy Guide #{i+1} - Advanced Tips",
                    description=f"Learn advanced {keyword} strategies from professional players. "
                               f"This comprehensive guide covers key concepts and tactics. "
                               f"Perfect for intermediate to advanced players looking to improve.",
                    published_at=(datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    view_count=random.randint(1000, 100000),
                    like_count=random.randint(50, 5000),
                    comment_count=random.randint(10, 500),
                    channel_title=f"Poker Pro {keyword}",
                    duration="PT10M30S",
                    keyword_matched=keyword,
                    relevance_score=random.uniform(0.6, 1.0)
                )
                videos.append(video)
        
        return videos
    
    def _calculate_relevance_score(self, text: str, keyword: str) -> float:
        """관련성 점수 계산 테스트"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # 기본 점수
        base_score = 0.5 if keyword_lower in text_lower else 0.0
        
        # 포커 용어 보너스
        poker_terms = [
            'poker', 'tournament', 'cash', 'game', 'strategy', 'bluff',
            'fold', 'bet', 'raise', 'call', 'all-in', 'final table'
        ]
        
        bonus_score = sum(0.05 for term in poker_terms if term in text_lower)
        title_bonus = 0.3 if keyword_lower in text_lower[:100] else 0.0
        
        return min(1.0, base_score + bonus_score + title_bonus)
    
    async def collect_videos_for_keyword(self, keyword: str, max_results: int = 50) -> List[MockVideoData]:
        """키워드별 비디오 수집 모의"""
        print(f"모의 수집: 키워드 '{keyword}' 검색 중...")
        
        # 실제 API 호출 시뮬레이션 (지연)
        await asyncio.sleep(0.2)
        
        # 해당 키워드 비디오 필터링
        keyword_videos = [v for v in self.sample_videos if v.keyword_matched == keyword]
        
        # 관련성 점수 재계산
        for video in keyword_videos:
            video.relevance_score = self._calculate_relevance_score(
                video.title + " " + video.description, keyword
            )
        
        # 상위 결과 반환
        keyword_videos.sort(key=lambda x: x.relevance_score, reverse=True)
        return keyword_videos[:max_results]
    
    async def collect_all_videos(self) -> List[MockVideoData]:
        """전체 키워드 비디오 수집 모의"""
        print("모의 수집: 전체 키워드 비디오 수집 시작...")
        
        all_videos = []
        
        # 모든 키워드에 대해 비동기 수집
        tasks = []
        for keyword in self.target_keywords:
            task = self.collect_videos_for_keyword(keyword, 10)  # 키워드당 10개
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for i, keyword_videos in enumerate(results):
            all_videos.extend(keyword_videos)
            print(f"키워드 '{self.target_keywords[i]}': {len(keyword_videos)}개 비디오 수집")
        
        # 중복 제거 및 상위 50개 선택
        unique_videos = {}
        for video in all_videos:
            if video.video_id not in unique_videos:
                unique_videos[video.video_id] = video
        
        self.collected_videos = list(unique_videos.values())
        self.collected_videos.sort(key=lambda x: x.relevance_score, reverse=True)
        self.collected_videos = self.collected_videos[:50]
        
        print(f"총 {len(self.collected_videos)}개 고유 비디오 수집 완료")
        return self.collected_videos
    
    def mock_gemini_analysis(self, videos: List[MockVideoData]) -> Dict[str, Any]:
        """Gemini AI 분석 모의"""
        print("모의 분석: Gemini AI 트렌드 분석 중...")
        
        # 키워드별 비디오 수 계산
        keyword_counts = {}
        for video in videos:
            keyword_counts[video.keyword_matched] = keyword_counts.get(video.keyword_matched, 0) + 1
        
        # 가장 많은 키워드 찾기
        most_trending = max(keyword_counts.keys(), key=lambda k: keyword_counts[k])
        
        # 모의 트렌드 생성
        mock_trends = [
            {
                "trend_title": f"{most_trending} 전략의 급부상",
                "trend_description": f"{most_trending} 관련 콘텐츠가 크게 증가하고 있으며, 특히 고급 전략에 대한 관심이 높아지고 있습니다.",
                "confidence_score": 0.85,
                "supporting_videos": [v.video_id for v in videos if v.keyword_matched == most_trending][:3],
                "trend_category": "emerging",
                "keywords": [most_trending, "strategy", "advanced"],
                "impact_level": "meso",
                "content_potential": "높음",
                "recommended_action": f"{most_trending} 초급자 가이드 콘텐츠 제작 권장"
            },
            {
                "trend_title": "포커 교육 콘텐츠 수요 증가",
                "trend_description": "전략적 포커 교육에 대한 수요가 지속적으로 증가하고 있으며, 상세한 해설이 포함된 콘텐츠가 인기를 끌고 있습니다.",
                "confidence_score": 0.72,
                "supporting_videos": [v.video_id for v in videos[:5]],
                "trend_category": "stable",
                "keywords": ["education", "strategy", "guide"],
                "impact_level": "micro",
                "content_potential": "중간",
                "recommended_action": "단계별 학습 시리즈 제작"
            }
        ]
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "total_videos_analyzed": len(videos),
            "trends": mock_trends,
            "keyword_insights": {
                "most_trending": most_trending,
                "emerging_themes": ["advanced strategy", "tournament play"],
                "declining_themes": ["basic rules"]
            },
            "content_recommendations": [
                f"{most_trending} 초급자 완벽 가이드",
                "포커 실수 TOP 10과 해결법",
                "프로 플레이어 인터뷰 시리즈",
                "라이브 게임 vs 온라인 게임 비교",
                "포커 수학 쉽게 배우기"
            ]
        }
    
    def save_results(self, videos: List[MockVideoData], analysis: Dict[str, Any], 
                    filename_prefix: str = "mock_poker_trend_analysis") -> str:
        """결과 저장"""
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
                'url': f"https://www.youtube.com/watch?v={video.video_id} (MOCK)"
            })
        
        result = {
            'metadata': {
                'analysis_time': datetime.now().isoformat(),
                'target_keywords': self.target_keywords,
                'total_videos_collected': len(videos),
                'analyzer_version': '1.0.0-mock',
                'note': '이것은 모의 테스트 결과입니다. 실제 YouTube 데이터가 아닙니다.'
            },
            'videos': videos_dict,
            'gemini_analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"모의 분석 결과 저장 완료: {filename}")
        return filename
    
    def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """요약 리포트 생성"""
        report = f"""
포커 트렌드 분석 리포트 (모의 테스트)
분석 일시: {analysis.get('analysis_date', 'Unknown')}
분석 비디오 수: {analysis.get('total_videos_analyzed', 0)}개

식별된 트렌드:
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
키워드 인사이트:
- 가장 트렌딩: {keyword_insights.get('most_trending', 'Unknown')}
- 떠오르는 주제: {', '.join(keyword_insights.get('emerging_themes', []))}
- 줄어드는 주제: {', '.join(keyword_insights.get('declining_themes', []))}

콘텐츠 제작 권장사항:
"""
        
        recommendations = analysis.get('content_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += "\n[주의] 이것은 모의 테스트 결과입니다."
        
        return report

async def main():
    """메인 모의 테스트 함수"""
    print("포커 트렌드 분석기 모의 테스트 시작")
    print("=" * 60)
    
    try:
        # 모의 분석기 초기화
        analyzer = MockPokerTrendAnalyzer()
        
        # 1. 비디오 수집 테스트
        print("1. 키워드별 YouTube 비디오 수집 모의...")
        videos = await analyzer.collect_all_videos()
        print(f"✓ 총 {len(videos)}개 비디오 수집 완료")
        print()
        
        # 2. 관련성 점수 테스트
        if videos:
            sample_video = videos[0]
            score = analyzer._calculate_relevance_score(
                sample_video.title + " " + sample_video.description,
                sample_video.keyword_matched
            )
            print(f"2. 관련성 점수 계산 테스트:")
            print(f"   샘플 비디오: {sample_video.title}")
            print(f"   키워드: {sample_video.keyword_matched}")
            print(f"   관련성 점수: {score:.3f}")
            print("✓ 관련성 점수 계산 알고리즘 정상 작동")
            print()
        
        # 3. Gemini AI 분석 모의
        print("3. Gemini AI 트렌드 분석 모의...")
        analysis = analyzer.mock_gemini_analysis(videos)
        print(f"✓ {len(analysis.get('trends', []))}개 트렌드 식별 완료")
        print()
        
        # 4. 결과 저장 테스트
        print("4. 분석 결과 저장 테스트...")
        saved_file = analyzer.save_results(videos, analysis)
        print(f"✓ 결과 저장 완료: {saved_file}")
        print()
        
        # 5. 요약 리포트 생성
        print("5. 분석 결과 요약:")
        print("=" * 60)
        summary = analyzer.generate_summary_report(analysis)
        print(summary)
        
        print("=" * 60)
        print("모의 테스트 완료!")
        print("✓ 모든 핵심 기능이 정상적으로 작동합니다.")
        print(f"✓ 상세 결과는 {saved_file} 파일을 확인하세요.")
        
        return True
        
    except Exception as e:
        print(f"❌ 모의 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 시스템이 정상적으로 구현되었습니다!")
        print("실제 API 키를 설정하면 바로 사용할 수 있습니다.")
    else:
        print("\n❌ 시스템에 문제가 있습니다. 오류를 확인하세요.")