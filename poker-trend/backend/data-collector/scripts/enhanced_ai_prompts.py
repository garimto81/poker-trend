#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쇼츠 제작용 고도화된 AI 인사이트 프롬프트
"""

def get_enhanced_analysis_prompt(videos_data, report_type="daily"):
    """향상된 AI 분석 프롬프트 생성"""
    
    # 데이터 요약
    total_videos = len(videos_data)
    top_videos = sorted(videos_data, key=lambda x: x.get('view_count', 0), reverse=True)[:10]
    
    # 제목 패턴 분석용 데이터
    titles = [v.get('title', '') for v in top_videos]
    durations = [v.get('duration', '') for v in top_videos]
    
    prompt = f"""
당신은 YouTube 쇼츠 콘텐츠 전략 전문가입니다. 다음 포커 관련 영상 데이터를 분석하여 실제 쇼츠 제작에 활용할 수 있는 구체적이고 실행 가능한 인사이트를 제공해주세요.

## 📊 분석 데이터 ({report_type})
- 총 영상 수: {total_videos}개
- 상위 10개 영상 분석 대상

### TOP 영상들의 제목:
{chr(10).join([f"{i+1}. {title}" for i, title in enumerate(titles[:5])])}

### 영상 길이 분포:
{chr(10).join([f"- {duration}" for duration in durations[:5]])}

## 🎯 요청하는 분석 내용:

### 1. 바이럴 제목 패턴 분석
- 가장 효과적인 제목 구조 3가지
- 필수 포함 키워드/이모지
- 클릭을 유도하는 감정적 트리거

### 2. 최적 영상 길이 전략
- 현재 트렌드의 이상적 길이
- 길이별 장단점 분석

### 3. 콘텐츠 아이디어 도출
다음 형식으로 구체적인 쇼츠 아이디어 3개 제시:
```
아이디어 1: [제목]
- 내용: [30초 이내 스토리라인]
- 핵심 요소: [시각적/감정적 포인트]
- 예상 해시태그: [5개]
```

### 4. 썸네일 최적화 가이드
- 효과적인 표정/제스처
- 색상 조합 추천
- 텍스트 오버레이 전략

### 5. 업로드 타이밍 전략
- 최적 업로드 시간대
- 요일별 성과 예측

### 6. 경쟁 우위 전략
- 현재 시장 gap 분석
- 차별화 포인트 3가지

## 💡 답변 형식:
각 섹션을 명확히 구분하여 실무진이 바로 활용할 수 있도록 구체적이고 실행 가능한 가이드로 작성해주세요.
특히 '오늘 당장 만들 수 있는 쇼츠 아이디어'에 중점을 두고 분석해주세요.
"""
    
    return prompt

def get_trend_prediction_prompt(historical_data, current_data):
    """트렌드 예측 프롬프트"""
    
    prompt = f"""
포커 콘텐츠 트렌드 예측 전문가로서, 향후 7일간의 콘텐츠 전략을 수립해주세요.

## 📈 현재 데이터 기반 예측

### 다음 주 예상 트렌드:
1. **급상승 예상 키워드 3개**
2. **피해야 할 포화 상태 키워드 2개**
3. **틈새 기회 영역 1개**

### 일주일 콘텐츠 캘린더:
각 날짜별로 최적 콘텐츠 타입과 예상 성과를 제시해주세요.

월요일: [콘텐츠 타입] - [예상 조회수 범위]
화요일: [콘텐츠 타입] - [예상 조회수 범위]
...

### 실행 우선순위:
1순위 (즉시 제작): [구체적 아이디어]
2순위 (이번 주 내): [구체적 아이디어]  
3순위 (다음 주): [구체적 아이디어]
"""
    
    return prompt

def get_shorts_creation_prompt(viral_videos):
    """쇼츠 제작 전용 프롬프트"""
    
    prompt = f"""
YouTube 쇼츠 크리에이터를 위한 즉시 실행 가능한 제작 가이드를 제공해주세요.

## 🎬 즉시 제작 가능한 쇼츠 시나리오 5개

각 시나리오는 다음 형식으로:

### 시나리오 1: [매력적인 제목]
**스토리라인 (30초)**:
- 0-5초: [오프닝 훅]
- 5-20초: [메인 콘텐츠]
- 20-30초: [마무리/CTA]

**촬영 팁**:
- 카메라 각도: [구체적 지시]
- 조명: [권장 설정]
- 음향: [BGM/효과음 가이드]

**편집 포인트**:
- 필수 컷: [타이밍]
- 텍스트 오버레이: [내용과 위치]
- 전환 효과: [추천 효과]

**해시태그 세트**: [10개]

**예상 성과**: [조회수 범위와 근거]

---

이런 식으로 5개 시나리오를 제공하되, 각각 다른 포커 상황 (블러프, 빅핸드, 초보자 실수, 프로 플레이, 재미있는 순간)을 다뤄주세요.
"""
    
    return prompt

if __name__ == "__main__":
    print("Enhanced AI Prompts for Shorts Creation")
    print("=" * 50)
    
    # 예제 사용법
    sample_videos = [
        {"title": "he actually went for it 🤯 #poker #shorts", "view_count": 113517, "duration": "PT47S"},
        {"title": "most players miss this SECRET 🤫", "view_count": 49811, "duration": "PT57S"}
    ]
    
    enhanced_prompt = get_enhanced_analysis_prompt(sample_videos)
    print("Enhanced Analysis Prompt:")
    print(enhanced_prompt[:200] + "...")