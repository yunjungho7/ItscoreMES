"""
기준정보 Routers 패키지
- 13개 화면별 라우터를 하나의 router에 통합 등록
- main.py에서 from routers.master import router 로 사용
"""
from fastapi import APIRouter

from routers.master.plant import router as plant_router
from routers.master.factory import router as factory_router
from routers.master.dept import router as dept_router
from routers.master.company import router as company_router
from routers.master.warehouse import router as warehouse_router
from routers.master.location import router as location_router
from routers.master.line import router as line_router
from routers.master.process import router as process_router
from routers.master.goods import router as goods_router
from routers.master.bom import router as bom_router
from routers.master.process_user import router as process_user_router
from routers.master.code import router as code_router
from routers.master.failcode import router as failcode_router

router = APIRouter(prefix="/api/master", tags=["기준정보"])

router.include_router(plant_router)
router.include_router(factory_router)
router.include_router(dept_router)
router.include_router(company_router)
router.include_router(warehouse_router)
router.include_router(location_router)
router.include_router(line_router)
router.include_router(process_router)
router.include_router(goods_router)
router.include_router(bom_router)
router.include_router(process_user_router)
router.include_router(code_router)
router.include_router(failcode_router)
