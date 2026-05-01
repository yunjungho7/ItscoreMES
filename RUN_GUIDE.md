# 프로젝트 실행 가이드

## 백엔드 (FastAPI)

```powershell
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 활성화 및 서버 실행 (Windows)
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **API 문서**: http://localhost:8000/docs
- **API 서버**: http://localhost:8000

## 프론트엔드 (Vite)

```powershell
# 프론트엔드 디렉토리로 이동
cd frontend

# 개발 서버 실행
npm run dev
```

- **접속 URL**: http://localhost:5173/
