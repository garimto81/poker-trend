# Workflow 수동 실행 방법

새로운 workflow "YouTube Trend Daily Analysis"를 실행하려면:

1. 브라우저에서 https://github.com/garimto81/poker-trend/actions 접속
2. 좌측 사이드바에서 "YouTube Trend Daily Analysis" 클릭
3. "Run workflow" 버튼 클릭
4. Branch: master 선택
5. Debug mode: true 선택 (상세 로그 확인용)
6. "Run workflow" 클릭

또는 GitHub CLI를 사용한 방법:
```bash
gh workflow run "YouTube Trend Daily Analysis" --repo garimto81/poker-trend
```