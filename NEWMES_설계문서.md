# NEWMES 시스템 설계 문서

> **프로젝트**: NEWMES (Manufacturing Execution System)  
> **작성일**: 2026-05-02  
> **버전**: 1.0.0  
> **기술 스택**: FastAPI (Backend) + Vue.js + TypeScript (Frontend)

---

## 1. 시스템 개요

### 1.1 프로젝트 목적
제조 실행 시스템(MES)으로 생산 현장의 실시간 모니터링, 생산 관리, 물류 관리, 품질 검사 등을 통합 관리하는 웹 기반 솔루션입니다.

### 1.2 주요 기능
- **생산 관리**: 생산 지시, 공정 관리, 실적 수집
- **물류 관리**: 입출고, 재고 관리, 이동 이력
- **품질 관리**: 검사 항목 관리, 불량 코드 관리, 검사 실적
- **마스터 데이터**: 부서, 거래처, 품목, BOM, 공장 정보
- **상태 모니터링**: 설비 상태, 생산 진행 현황
- **시스템 관리**: 사용자 인증, 시스템 설정

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue.js)                        │
│  - Vite + Vue 3 + TypeScript                              │
│  - Pinia (State Management)                                │
│  - Vue Router 5                                            │
│  - API 통신: Axios + OpenAPI 타입 생성 (@hey-api/openapi-ts)│
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ (CORS enabled)
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  - FastAPI Framework                                       │
│  - Uvicorn ASGI Server                                     │
│  - Correlation ID 추적 (asgi-correlation-id)               │
│  - 구조화된 로깅 (core/logging.py)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Database (SQL)                           │
│  - SQL 쿼리 파일로 관리 (backend/sql/)                     │
│  - 모델 정의 (backend/models/)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 디렉토리 구조

### 3.1 백엔드 (backend/)

```
backend/
├── main.py                 # FastAPI 애플리케이션 진입점
├── core/                   # 핵심 기능 (로깅 등)
│   └── logging.py         # 로깅 설정
├── models/                 # 데이터 모델 (Pydantic)
│   ├── master/            # 마스터 데이터 모델
│   ├── logistics/         # 물류 관련 모델
│   └── system/            # 시스템 모델
├── routers/                # API 라우터 (Controller)
│   ├── auth.py            # 인증 라우터
│   ├── master/            # 마스터 데이터 라우터
│   │   ├── bom.py         # BOM 관리
│   │   ├── code.py        # 코드 관리
│   │   ├── company.py     # 거래처 관리
│   │   ├── dept.py        # 부서 관리
│   │   ├── factory.py     # 공장 관리
│   │   ├── failcode.py    # 불량 코드 관리
│   │   └── goods.py       # 품목 관리
│   ├── logistics/         # 물류 라우터
│   ├── production/        # 생산 라우터
│   ├── status/            # 상태 모니터링 라우터
│   ├── inspection/        # 검사 라우터
│   └── system/            # 시스템 라우터
├── services/               # 비즈니스 로직 레이어
│   ├── master/
│   ├── logistics/
│   ├── production/
│   ├── status/
│   ├── inspection/
│   └── system/
├── sql/                    # SQL 쿼리 파일
│   ├── master/
│   ├── logistics/
│   ├── production/
│   ├── status/
│   ├── inspection/
│   └── system/
├── db/                     # 데이터베이스 연결 설정
├── scripts/                # 유틸리티 스크립트
│   └── extract_openapi.py # OpenAPI 스키마 추출
└── venv/                   # Python 가상환경
```

### 3.2 프론트엔드 (frontend/)

```
frontend/
├── src/
│   ├── api/               # API 통신 레이어 (OpenAPI 자동 생성)
│   ├── assets/            # 정적 자산 (이미지, 스타일)
│   ├── components/        # 재사용 컴포넌트
│   ├── composables/        # Vue 컴포저블 (로직 재사용)
│   ├── router/            # Vue Router 설정
│   ├── views/             # 페이지 컴포넌트
│   │   ├── Login.vue      # 로그인 페이지
│   │   ├── ModeSelect.vue # 모드 선택 페이지
│   │   ├── field/         # 현장 화면
│   │   ├── logistics/     # 물류 화면
│   │   └── management/    # 관리자 화면
│   ├── App.vue
│   └── main.ts
├── public/                 # 공용 정적 파일
├── dist/                   # 빌드 결과물
├── package.json           # 의존성 및 스크립트
└── vite.config.ts         # Vite 설정
```

---

## 4. API 설계

### 4.1 API 구조
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **문서**: `http://localhost:8000/docs` (Swagger UI)

### 4.2 라우터별 엔드포인트

| 모듈 | 라우터 위치 | 설명 |
|------|------------|------|
| **Auth** | `/api/auth` | 사용자 인증 (로그인, 토큰 발급) |
| **Master** | `/api/master` | 마스터 데이터 관리 |
| **Logistics** | `/api/logistics` | 물류 관리 (입출고, 재고) |
| **Production** | `/api/production` | 생산 관리 (지시, 실적) |
| **Status** | `/api/status` | 상태 모니터링 |
| **Inspection** | `/api/inspection` | 품질 검사 관리 |
| **System** | `/api/system` | 시스템 설정 |

### 4.3 에러 처리
- **HTTPException**: `statusCode`, `message` 형식으로 응답
- **Global Exception**: 500 에러 시 동일한 형식으로 응답
- **에러 응답 형식**:
```json
{
  "statusCode": 400,
  "message": "에러 메시지"
}
```

---

## 5. 데이터 모델

### 5.1 모델 디렉토리 구조
```
models/
├── master/              # 마스터 데이터 모델
│   ├── bom.py          # BOM (Bill of Materials)
│   ├── code.py         # 공통 코드
│   ├── company.py      # 거래처 (Customer/Supplier)
│   ├── dept.py         # 부서
│   ├── factory.py      # 공장/설비
│   ├── failcode.py     # 불량 코드
│   └── goods.py        # 품목/제품
├── logistics/          # 물류 데이터 모델
└── system/             # 시스템 모델 (사용자, 권한 등)
```

### 5.2 데이터 관리 방식
- **모델 정의**: Pydantic 모델로 요청/응답 스키마 정의
- **SQL 관리**: `backend/sql/` 디렉토리에 모듈별 SQL 파일 분리
- **쿼리 실행**: 서비스 레이어에서 SQL 파일 로드하여 실행

---

## 6. 프론트엔드 설계

### 6.1 기술 스택
- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite 8
- **State Management**: Pinia 3
- **Routing**: Vue Router 5
- **HTTP Client**: Axios
- **API Type Generation**: @hey-api/openapi-ts

### 6.2 주요 페이지 구성
1. **Login.vue** - 사용자 로그인
2. **ModeSelect.vue** - 사용자 모드 선택 (현장/관리자 등)
3. **field/** - 현장 작업 화면 (생산 실적 입력 등)
4. **logistics/** - 물류 관리 화면
5. **management/** - 관리자 화면 (마스터 데이터 관리 등)

### 6.3 API 연동 방식
```bash
# OpenAPI 스키마 추출 및 타입 생성
npm run generate-api
```
- `backend/scripts/extract_openapi.py`로 OpenAPI 스키마 추출
- `@hey-api/openapi-ts`로 TypeScript 타입 및 API 클라이언트 자동 생성

---

## 7. 배포 및 실행

### 7.1 백엔드 실행 (Windows)
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 프론트엔드 실행 (Windows)
```powershell
cd frontend
npm run dev
```
- 접속 URL: http://localhost:5173/

### 7.3 배포 (Linux)
```bash
./deploy.sh
```

---

## 8. 로깅 및 모니터링

### 8.1 Correlation ID
- 모든 요청에 고유 ID 부여 (`asgi-correlation-id`)
- 요청 추적 및 로그 연관성 확보

### 8.2 구조화된 로깅
- `core/logging.py`에서 로깅 설정
- JSON 형식 로그 출력 (운영 환경)

---

## 9. 데이터 삭제 정책

### 9.1 트랜잭션 데이터 삭제
- `delete_transaction_data.md` 문서 참조
- 주의: 마스터 데이터와 트랜잭션 데이터의 분리 관리 필요

---

## 10. 향후 개선 사항

1. **인증/인가**: JWT 토큰 기반 인증 강화
2. **실시간 통신**: WebSocket을 통한 실시간 상태 업데이트
3. **데이터베이스**: ORM 도입 검토 (SQLAlchemy 등)
4. **테스트**: 단위 테스트 및 통합 테스트 추가
5. **CI/CD**: GitHub Actions를 통한 자동화 (.github/ 디렉토리 존재)
6. **문서화**: API 문서 외 추가 문서화 필요

---

## 부록

### A. 주요 설정 파일
- `backend/main.py`: FastAPI 앱 설정, CORS, 미들웨어
- `frontend/package.json`: 프론트엔드 의존성
- `frontend/vite.config.ts`: Vite 설정

### B. 관련 문서
- `RUN_GUIDE.md`: 실행 가이드
- `.planning/`: 프로젝트 계획 및 연구 자료

---

*본 문서는 NEWMES 프로젝트의 소스 코드 분석을 통해 자동 생성되었습니다.*
