#!/bin/bash
set -e

PROJECT_DIR="/home/itscore/ItscoreMES"
echo "🚀 배포 시작: $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"

cd "$PROJECT_DIR"

echo "=== [0/4] 기존 충돌 프로세스 정리 ==="
# 80번 포트를 점유하는 node(serve 등) 프로세스 강제 종료
sudo lsof -t -i:80 | xargs sudo kill -9 2>/dev/null || true
# 기존 백엔드 프로세스 종료
pkill -f "gunicorn.*main:app" || true
pkill -f "uvicorn main:app" || true
sleep 2

echo "=== [1/4] 최신 코드 pull ==="
git pull origin master

echo "=== [2/4] 백엔드 재배포 (Port 8000) ==="
cd backend
source venv/bin/activate
pip install -r requirements.txt --quiet
# Gunicorn 시작
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
echo "✅ 백엔드 재시작 완료"

echo "=== [3/4] 프론트엔드 빌드 ==="
cd ../frontend
npm install --silent
npm run build
echo "✅ 프론트엔드 빌드 완료"

echo "=== [4/4] Nginx 재시작 (Port 80) ==="
# Nginx 설정 파일이 sites-enabled에 있는지 확인 (없으면 복사)
if [ ! -f /etc/nginx/sites-enabled/itscore-mes ]; then
    echo "itscore1!" | sudo -S cp "$PROJECT_DIR/nginx/itscore-mes" /etc/nginx/sites-available/
    echo "itscore1!" | sudo -S ln -s /etc/nginx/sites-available/itscore-mes /etc/nginx/sites-enabled/ || true
fi

# Nginx 재시작
echo "itscore1!" | sudo -S systemctl restart nginx
echo "✅ Nginx 재시작 완료"

echo "🎉 모든 배포가 성공적으로 완료되었습니다: $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"
