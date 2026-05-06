#!/bin/bash
set -e

# PFMES Production Deployment Script
ENV="prod"
PROJECT_DIR="/home/itscore/ItscoreMES"
SERVICE_NAME="mes-backend-prod"
PORT=8000
DIST_DIR="dist-prod"

cd "$PROJECT_DIR"

echo "=== [1/4] 최신 코드 pull (PFMES_V3) ==="
git pull origin PFMES_V3

echo "=== [2/4] 백엔드 운영 서버 재배포 ==="
cd backend
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "시스템 서비스 ($SERVICE_NAME) 재시작..."
sudo systemctl restart $SERVICE_NAME

echo "백엔드 운영 서버 재시작 완료 (포트 $PORT)"

echo "=== [3/4] 프론트엔드 운영 빌드 ==="
cd ../frontend
npm install --silent
npm run build -- --mode production

rm -rf $DIST_DIR
mv dist $DIST_DIR

echo "프론트엔드 운영 빌드 완료 ($DIST_DIR)"

echo "=== [4/4] Nginx 설정 반영 ==="
sudo systemctl reload nginx
echo "nginx reload 완료"

echo "=== 운영 환경 배포 완료 ==="
date
