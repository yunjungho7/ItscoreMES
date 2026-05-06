#!/bin/bash
# PFMES Development Deployment Script (Ultimate)
# 단일 소스로 개발 환경을 완벽히 분리 운영합니다.

set -e

# 색상 및 환경 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ENV="development"
PORT="8081"
BACKEND_PORT="8001"
SERVICE_NAME="mes-backend-dev"
DIST_DIR="dist-dev"
PROJECT_DIR="/home/itscore/ItscoreMES"

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   PFMES [DEVELOPMENT] 배포 프로세스 시작${NC}"
echo -e "${GREEN}==========================================${NC}"

cd "$PROJECT_DIR"

# 1. 소스 업데이트
echo -e "${YELLOW}Step 1: 소스 최신화 (Branch: master)...${NC}"
# git pull origin master

# 2. 백엔드 배포
echo -e "${YELLOW}Step 2: 백엔드(FastAPI) 설정 및 재시작...${NC}"
cd backend

# .env.development 파일 존재 확인
if [ ! -f ".env.development" ]; then
    echo -e "${RED}Error: .env.development 파일이 없습니다.${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "기존 서비스($SERVICE_NAME) 중지 및 대기..."
sudo systemctl stop $SERVICE_NAME || true
sleep 2

echo "시스템 데몬 리로드 및 서비스 시작..."
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME

# 백엔드 헬스 체크
sleep 3
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null; then
    echo -e "${GREEN}✔ 백엔드가 포트 $BACKEND_PORT에서 정상 작동 중입니다.${NC}"
else
    echo -e "${RED}✘ 백엔드 시작 확인 실패.${NC}"
    echo -e "${YELLOW}최근 백엔드 로그(backend/logs/backend.log):${NC}"
    tail -n 20 backend/logs/backend.log || true
    echo -e "${YELLOW}시스템 서비스 로그(journalctl -u $SERVICE_NAME):${NC}"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

# 3. 프론트엔드 배포
echo -e "${YELLOW}Step 3: 프론트엔드(Vite) 빌드 및 배치...${NC}"
cd ../frontend

# .env.development 파일 존재 확인
if [ ! -f ".env.development" ]; then
    echo -e "${RED}Error: frontend/.env.development 파일이 없습니다.${NC}"
    exit 1
fi

npm install --silent
echo "Vite 빌드 실행 (Mode: development)..."
npm run build -- --mode development

echo "결과물 이동: dist -> $DIST_DIR"
rm -rf $DIST_DIR
mv dist $DIST_DIR

# 4. Nginx 설정 적용
echo -e "${YELLOW}Step 4: Nginx 설정 업데이트...${NC}"
sudo systemctl reload nginx

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   개발 환경 배포 완료!${NC}"
echo -e "${GREEN}   - 접속 URL: http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
echo -e "${GREEN}   - API 포트: $BACKEND_PORT${NC}"
echo -e "${GREEN}   - 빌드 폴더: $DIST_DIR${NC}"
echo -e "${GREEN}==========================================${NC}"
