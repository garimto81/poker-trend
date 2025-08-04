@echo off
REM Claude Code 별칭 - 항상 모든 권한으로 실행

claude --dangerously-skip-permissions --permission-mode bypassPermissions --allowedTools "*" %*