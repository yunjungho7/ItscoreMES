#!/bin/bash
set -e

echo "🚀 배포 시작: $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"

# ============================================
# 1. 백엔드 재시작 (Gunicorn - 포트 8000)
# ============================================
echo "📦 백엔드 재시작 중 (포트 8000)..."

cd /home/itscore/ItscoreMES/backend
source venv/bin/activate

# 기존 프로세스 종료
pkill -f "gunicorn.*main:app" 2>/dev/null || true
sleep 2

# 백엔드 시작
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app > /home/itscore/backend.log 2>&1 &
sleep 3

# 헬스 체크
if curl -s http://localhost:8000/health > /dev/null 2>&1 || curl -s http://localhost:8000/ > /dev/null 2>&1; then
  echo "✅ 백엔드 재시작 성공 (포트 8000)"
else
  echo "⚠️ 백엔드 응답 확인 필요"
fi

# ============================================
# 2. 프론트엔드 재시작 (Vue.js - 포트 80)
# ============================================
echo "🎨 프론트엔드 재시작 중 (포트 80)..."

FRONTEND_PATH="/home/itscore/ItscoreMES/frontend"

if [ -d "$FRONTEND_PATH" ] && [ -f "$FRONTEND_PATH/package.json" ]; then
  cd "$FRONTEND_PATH"
  
  # 기존 프로세스 종료
  pkill -f "serve -s dist" 2>/dev/null || true
  sleep 2
  
  # 빌드 (필요시)
  if [ -f "package.json" ]; then
    echo "📦 프론트엔드 빌드 중..."
    npm run build 2>&1 | tail -20
    
    # 빌드 결과 서빙 (포트 80)
    if [ -d "dist" ]; then
      # 포트 80 사용 중인 프로세스 확인 및 종료
      sudo lsof -ti:80 | xargs sudo kill -9 2>/dev/null || true
      sleep 1
      
      # sudo 없이 서빙 (node에 cap_net_bind_service 권한 있음)
      nohup serve -s dist -l 80 > /home/itscore/frontend.log 2>&1 &
      sleep 2
      
      # 확인
      if curl -s http://localhost:80 > /dev/null 2>&1; then
        echo "✅ 프론트엔드 서빙 시작 (포트 80)"
      else
        echo "⚠️ 프론트엔드 포트 80 확인 필요"
      fi
    fi
  fi
else
  echo "ℹ️ 프론트엔드 폴더 없음, 건너뜀"
fi

echo "🎉 배포 완료: $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST')"
