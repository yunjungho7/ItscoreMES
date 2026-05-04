#!/bin/bash
set -e

PROJECT_DIR="/home/itscore/ItscoreMES"
cd "$PROJECT_DIR"

echo "=== [0/3] 포트 충돌 및 기존 프로세스 정리 ==="
# 80번 포트를 사용하는 node 프로세스(proxy-server.js 등) 종료
sudo lsof -t -i:80 | xargs sudo kill -9 2>/dev/null || true
# 기존 백엔드 프로세스 종료
pkill -f "gunicorn.*main:app" || true
pkill -f "uvicorn main:app" || true
sleep 2

echo "=== [1/3] 최신 코드 pull ==="
git pull origin master

echo "=== [2/3] 백엔드 재배포 ==="
cd backend
source venv/bin/activate
# 종속성 설치 (필요시)
pip install -r requirements.txt --quiet
# Gunicorn으로 백엔드 재시작 (4워커, 포트 8000)
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
echo "백엔드 재시작 완료 (포트 8000)"

echo "=== [3/3] 프론트엔드 재배포 ==="
cd ../frontend
npm install --silent
npm run build
echo "프론트엔드 빌드 완료 (dist/ 디렉토리)"

# Nginx 상태 확인 및 재시작 (reload보다 restart가 포트 확보에 확실함)
echo "itscore1!" | sudo -S systemctl restart nginx
echo "nginx 재시작 완료"

echo "=== 배포 완료 ==="
date
