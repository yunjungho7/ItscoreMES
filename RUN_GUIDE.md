# 프로젝트 실행 및 배포 가이드

## 로컬 개발 환경

### 백엔드 (FastAPI)
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 프론트엔드 (Vite)
```bash
cd frontend
npm run dev
```

---

## 우분투 배포 (개발/운영 분리)

본 프로젝트는 우분투 환경에서 개발(Dev)과 운영(Prod) 환경을 분리하여 배포할 수 있도록 구성되어 있습니다.

### 1. 환경 설정 파일 준비
`backend/.env.development`, `backend/.env.production` 및 `frontend/.env.development`, `frontend/.env.production` 파일이 각 환경에 맞게 설정되어 있는지 확인합니다.

### 2. 시스템 서비스 등록 (최초 1회)
`deployment/systemd/` 폴더의 서비스 파일들을 `/etc/systemd/system/`으로 복사하고 등록합니다.

```bash
sudo cp deployment/systemd/mes-backend-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mes-backend-dev
sudo systemctl enable mes-backend-prod
```

### 3. Nginx 설정 등록 (최초 1회)
`deployment/nginx/` 폴더의 설정 파일들을 `/etc/nginx/sites-available/`로 복사하고 활성화합니다.

```bash
sudo cp deployment/nginx/mes-*.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/mes-dev.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/mes-prod.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 4. 배포 스크립트 실행
스크립트 실행 시 인자로 `dev` 또는 `prod`를 전달합니다.

```bash
# 개발 환경 배포 (Port: 8081)
./deploy.sh dev

# 운영 환경 배포 (Port: 80)
./deploy.sh prod
```

- **개발 환경 접속**: http://서버IP:8081
- **운영 환경 접속**: http://서버IP (80)
