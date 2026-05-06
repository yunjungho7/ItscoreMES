#!/bin/bash
set -e

# 사용법: ./deploy.sh [prod|dev|staging]
ENV="${1:-prod}"  # 기본값: prod

echo "🚀 PFMES 배포 시작 (환경: $ENV): $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"

# 환경별 설정
if [ "$ENV" = "prod" ]; then
    BACKEND_PORT=8000
    FRONTEND_PORT=80
    BACKEND_DIR="/home/itscore/ItscoreMES/backend"
    FRONTEND_DIR="/home/itscore/ItscoreMES/frontend"
    echo "📦 운영 환경(Production) 배포"
elif [ "$ENV" = "dev" ]; then
    BACKEND_PORT=8001
    FRONTEND_PORT=3000
    BACKEND_DIR="/home/itscore/ItscoreMES/backend"
    FRONTEND_DIR="/home/itscore/ItscoreMES/frontend"
    echo "🔧 개발 환경(Development) 배포"
else
    echo "❌ 알 수 없는 환경: $ENV"
    echo "사용법: ./deploy.sh [prod|dev]"
    exit 1
fi

# ============================================
# 1. 백엔드 재시작 (Gunicorn)
# ============================================
echo "📦 백엔드 재시작 중 (포트 $BACKEND_PORT)..."

cd "$BACKEND_DIR"
source venv/bin/activate

# 기존 프로세스 종료
pkill -f "gunicorn.*main:app" 2>/dev/null || true
sleep 2

# 백엔드 시작
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$BACKEND_PORT main:app > /home/itscore/backend.log 2>&1 &
sleep 3

# 헬스 체크
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1 || curl -s http://localhost:$BACKEND_PORT/ > /dev/null 2>&1; then
    echo "✅ 백엔드 재시작 성공 (포트 $BACKEND_PORT)"
else
    echo "⚠️ 백엔드 응답 확인 필요 (포트 $BACKEND_PORT)"
fi

# ============================================
# 2. 프론트엔드 재시작 (Vue.js)
# ============================================
echo "🎨 프론트엔드 재시작 중 (포트 $FRONTEND_PORT)..."

if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    cd "$FRONTEND_DIR"
    
    # 기존 프로세스 종료
    pkill -f "serve -s dist" 2>/dev/null || true
    sleep 2
    
    # 빌드 (필요시)
    if [ -f "package.json" ]; then
        echo "📦 프론트엔드 빌드 중..."
        npm run build 2>&1 | tail -20
        
        # 빌드 결과 서빙
        if [ -d "dist" ]; then
            # 포트 사용 중인 프로세스 확인 및 종료
            sudo lsof -ti:$FRONTEND_PORT | xargs sudo kill -9 2>/dev/null || true
            sleep 1
            
            # 서빙 (node에 cap_net_bind_service 권한 있음)
            nohup serve -s dist -l $FRONTEND_PORT > /home/itscore/frontend.log 2>&1 &
            sleep 2
            
            # 확인
            if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
                echo "✅ 프론트엔드 서빙 시작 (포트 $FRONTEND_PORT)"
            else
                echo "⚠️ 프론트엔드 포트 $FRONTEND_PORT 확인 필요"
            fi
        fi
    fi
else
    echo "ℹ️ 프론트엔드 폴더 없음, 건너뜀"
fi

echo "🎉 배포 완료 (환경: $ENV): $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"
