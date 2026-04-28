from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from backend.core.logging import setup_logging
from routers.master import router as master_router
from routers.logistics import router as logistics_router
from routers.production import router as production_router
from routers.status import router as status_router
from routers.inspection import router as inspection_router
from routers.system import router as system_router
from routers.auth import router as auth_router

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

# ── 라우터 등록 ──
app.include_router(master_router)
app.include_router(logistics_router)
app.include_router(production_router)
app.include_router(status_router)
app.include_router(inspection_router)
app.include_router(system_router)
app.include_router(auth_router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "PFMES API"}
