#!/bin/bash
# PFMES Production Deployment Script
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ENV="production"
PORT="80"
BACKEND_PORT="8000"
SERVICE_NAME="mes-backend-prod"
DIST_DIR="dist-prod"
PROJECT_DIR="/home/itscore/ItscoreMES"
SUDO_PASS="itscore1!"

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   PFMES [PRODUCTION] 배포 프로세스 시작${NC}"
echo -e "${GREEN}==========================================${NC}"

cd "$PROJECT_DIR"

# 1. 소스 업데이트
echo -e "${YELLOW}Step 1: 소스 최신화...${NC}"
# git pull origin master

# 2. 백엔드 배포
echo -e "${YELLOW}Step 2: 백엔드(FastAPI) 설정 및 재시작...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "기존 서비스($SERVICE_NAME) 재시작..."
echo "$SUDO_PASS" | sudo -S systemctl restart $SERVICE_NAME

# 백엔드 헬스 체크
sleep 3
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null; then
    echo -e "${GREEN}✔ 백엔드가 포트 $BACKEND_PORT에서 정상 작동 중입니다.${NC}"
else
    echo -e "${RED}✘ 백엔드 시작 확인 실패.${NC}"
    echo -e "${YELLOW}최근 백엔드 로그(backend/logs/backend_prod.log):${NC}"
    tail -n 20 backend/logs/backend_prod.log || true
    echo -e "${YELLOW}시스템 서비스 로그(journalctl -u $SERVICE_NAME):${NC}"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

# 3. 프론트엔드 배포
echo -e "${YELLOW}Step 3: 프론트엔드(Vite) 빌드 및 배치...${NC}"
cd ../frontend

npm install --silent
echo "Vite 빌드 실행 (Mode: production)..."
npm run build -- --mode production

echo "결과물 이동: dist -> $DIST_DIR"
rm -rf $DIST_DIR
mv dist $DIST_DIR

# 4. Nginx 설정 적용
echo -e "${YELLOW}Step 4: Nginx 설정 업데이트...${NC}"
sudo systemctl restart nginx || sudo systemctl start nginx

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   운영 환경 배포 완료!${NC}"
echo -e "${GREEN}   - 접속 URL: http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
echo -e "${GREEN}==========================================${NC}"
