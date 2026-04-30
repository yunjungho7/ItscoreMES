#!/bin/bash
cd /home/itscore/ItscoreMES/backend
source venv/bin/activate
# 기존 백엔드 프로세스 종료
pkill -f "gunicorn.*main:app" || true
pkill -f "uvicorn main:app" || true
sleep 2
# Gunicorn으로 백엔드 재시작 (4워커, 포트 8000)
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
echo "백엔드 재시작 완료 (포트 8000)"
