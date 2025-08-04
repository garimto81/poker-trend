@echo off
echo Claude Code 환경 변수 설정 중...

REM Claude Code 기본 권한 설정을 위한 환경 변수
setx CLAUDE_PERMISSION_MODE "bypassPermissions"
setx CLAUDE_SKIP_PERMISSIONS "true"
setx CLAUDE_ALLOWED_TOOLS "*"
setx CLAUDE_AUTO_APPROVE "true"

echo.
echo 다음 환경 변수가 설정되었습니다:
echo - CLAUDE_PERMISSION_MODE=bypassPermissions
echo - CLAUDE_SKIP_PERMISSIONS=true  
echo - CLAUDE_ALLOWED_TOOLS=*
echo - CLAUDE_AUTO_APPROVE=true
echo.
echo 설정이 완료되었습니다. 새 터미널 창에서 적용됩니다.
echo.
pause