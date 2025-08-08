@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python pokernews_preview.py --skip-ai --articles 10
pause