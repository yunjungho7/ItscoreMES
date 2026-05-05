from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from core.logging import setup_logging
from routers.master import router as master_router
from routers.logistics import router as logistics_router
from routers.production import router as production_router
from routers.status import router as status_router
from routers.inspection import router as inspection_router
from routers.system import router as system_router
from routers.auth import router as auth_router
from core.auth_dependency import get_current_user

# Setup logging before FastAPI initialization
setup_logging()

app = FastAPI(
    title="PFMES API",
    description="PFMES Manufacturing Execution System API",
    version="1.0.0"
)

# Correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 전역 에러 핸들러 ──
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"statusCode": exc.status_code, "message": str(detail)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"statusCode": 500, "message": str(exc)}
    )

# ── API 라우터 등록 (모두 /api prefix 사용) ──
# 인증 없이 접근 가능한 라우터
app.include_router(auth_router, prefix="/api")

# 인증이 필요한 라우터들 (dependencies 추가)
protected_dependency = [Depends(get_current_user)]

app.include_router(master_router, prefix="/api", dependencies=protected_dependency)
app.include_router(logistics_router, prefix="/api", dependencies=protected_dependency)
app.include_router(production_router, prefix="/api", dependencies=protected_dependency)
app.include_router(status_router, prefix="/api", dependencies=protected_dependency)
app.include_router(inspection_router, prefix="/api", dependencies=protected_dependency)
app.include_router(system_router, prefix="/api", dependencies=protected_dependency)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "PFMES API"}
