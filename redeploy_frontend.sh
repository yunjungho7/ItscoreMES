#!/bin/bash
set -e
cd /home/itscore/ItscoreMES/frontend
echo "의존성 설치 중..."
npm install --silent
echo "프론트엔드 빌드 중..."
npm run build
echo "프론트엔드 빌드 완료 (dist/ 디렉토리)"
echo "itscore1!" | sudo -S systemctl reload nginx
echo "nginx reload 완료"
