# Claude Code 작업 규칙 및 가이드라인

## 📌 기본 규칙

### 1. Subagents와 MCP 적극 활용
- 복잡한 작업은 항상 적절한 subagent에게 위임
- 단순 작업도 MCP를 통해 자동화 고려
- 작업 시작 전 사용 가능한 도구 확인

### 2. 언어 설정
- **모든 응답은 한글로 작성**
- 코드 주석도 가능한 한글로 작성
- 기술 용어는 한글(영문) 형식 사용

### 3. 프로젝트 관리 원칙
- 프로젝트 간 충돌 방지를 위해 독립적 환경 유지
- 공통 모듈 수정 시 영향도 분석 필수
- 각 프로젝트별 README 최신 상태 유지
- **수정할때마다 항상 버전 업데이트를 처리할 것**
- **수정할때마다 항상 테스트를 완벽하게 수행하여 문제가 없는 상황을 만들 것**
- **수정할때마다 항상 README.md 파일을 업데이트 할 것**

### 4. 단계적 사고 프로세스
- 복잡한 작업은 하위 작업으로 분해
- TodoWrite로 작업 계획 수립
- 각 단계별 적절한 subagent 할당

### 5. MCP 선택 가이드
- 작업 특성 분석 후 최적 MCP 선택
- 여러 MCP 조합 활용 고려
- 효율성과 정확성 균형 유지

## 🚀 주요 Subagents 활용 가이드

### 백엔드 개발
- `backend-architect`: API 설계, 데이터베이스 스키마
- `python-pro`: 고급 Python 기능 구현
- `deployment-engineer`: 배포 및 CI/CD 설정

### 프론트엔드 개발
- `frontend-developer`: Next.js/React 개발
- `typescript-expert`: TypeScript 타입 시스템
- `graphql-architect`: GraphQL 스키마 설계

### 데이터 및 AI
- `data-scientist`: 데이터 분석 및 SQL
- `ml-engineer`: ML 파이프라인 구축
- `ai-engineer`: LLM 통합 및 RAG 시스템

### 인프라 및 운영
- `cloud-architect`: 클라우드 인프라 설계
- `devops-troubleshooter`: 운영 이슈 해결
- `database-optimizer`: DB 성능 최적화

### 품질 관리
- `test-automator`: 테스트 코드 작성
- `security-auditor`: 보안 검토
- `code-reviewer`: 코드 품질 검토

## 📁 프로젝트별 주의사항

### Archive-MAM
- OpenCV 버전 호환성 확인
- 대용량 비디오 처리 시 메모리 관리
- Docker 환경에서 GUI 관련 이슈 주의

### poker-trend
- YouTube API 할당량 관리
- Gemini API 키 보안
- 일일 스케줄러 충돌 방지

### slack-report-automation
- Slack 권한 스코프 확인
- 타임존 설정 주의
- GitHub Actions 시크릿 관리

### superclaude
- 설치 경로 충돌 방지
- 플러그인 의존성 관리
- 버전 호환성 확인

## 🛠️ 자주 사용하는 명령어

```bash
# 테스트 실행
python aiden_test_advanced.py

# Docker 컨테이너 관리
docker-compose up -d
docker-compose logs -f

# 가상환경 활성화
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
npm install
```

## 🔌 유용한 MCP 목록

### Supabase MCP
- 프로젝트 관리: `list_projects`, `get_project`
- 데이터베이스: `execute_sql`, `apply_migration`
- 보안 검사: `get_advisors`

### Context7 MCP
- 라이브러리 문서: `resolve-library-id`, `get-library-docs`
- 최신 버전 확인 및 마이그레이션 가이드

### Exa MCP
- 웹 검색: `web_search_exa`
- 기업 리서치: `company_research_exa`
- 심층 분석: `deep_researcher_start`

### GitHub MCP
- 저장소 검색: `search_repositories`
- 이슈 관리: `create_issue`, `update_issue`
- PR 생성: `create_pull_request`

## 📋 작업 흐름 예시

### 새 기능 개발 시
1. TodoWrite로 작업 계획 수립
2. `backend-architect`로 API 설계
3. `test-automator`로 테스트 작성
4. 구현 후 `code-reviewer`로 검토
5. `deployment-engineer`로 배포 설정

### 버그 수정 시
1. `devops-troubleshooter`로 원인 분석
2. `debugger`로 상세 디버깅
3. 수정 후 `test-automator`로 테스트
4. `security-auditor`로 보안 검토

### 성능 최적화 시
1. `performance-engineer`로 병목 지점 분석
2. `database-optimizer`로 쿼리 최적화
3. `python-pro` 또는 `typescript-expert`로 코드 개선
4. 테스트 및 모니터링 설정

## 🔄 정기 점검 사항

### 일일
- [ ] 모든 테스트 통과 확인
- [ ] API 할당량 확인
- [ ] 로그 이상 징후 점검

### 주간
- [ ] 의존성 업데이트 확인
- [ ] 보안 취약점 스캔
- [ ] 백업 상태 확인

### 월간
- [ ] 전체 프로젝트 문서 업데이트
- [ ] 성능 지표 분석
- [ ] 비용 최적화 검토

## 💡 팁과 모범 사례

1. **병렬 처리**: 여러 도구를 동시에 호출하여 작업 시간 단축
2. **컨텍스트 관리**: 큰 파일은 부분적으로 읽어 토큰 절약
3. **에러 처리**: 항상 예외 상황 고려하여 안정적인 코드 작성
4. **문서화**: 코드 작성과 동시에 문서 업데이트
5. **테스트 우선**: TDD 접근 방식으로 품질 보장

## 📞 도움말 및 참고 자료

- Claude Code 문서: https://docs.anthropic.com/en/docs/claude-code
- 피드백 제출: https://github.com/anthropics/claude-code/issues
- 프로젝트 마스터 플랜: [PROJECT_MASTER_PLAN.md](./PROJECT_MASTER_PLAN.md)

---

이 문서는 지속적으로 업데이트됩니다.
최종 수정일: 2025-09-08