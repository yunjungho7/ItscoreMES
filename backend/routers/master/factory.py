"""공장관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.factory import FactoryCreate, FactoryUpdate
from services.master.factory import factory_service

router = APIRouter(tags=["공장관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"공장 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/factory", summary="공장 목록 조회")
def get_factories(search: Optional[str] = None, plant_cd: Optional[str] = None,
                  page: int = 1, size: int = 50):
    """사업장코드(plant_cd) 기준 필터링을 지원합니다."""
    result = factory_service.get_all(search=search, page=page, size=size, plant_cd=plant_cd)

    return {"data": result}


@router.get("/factory/next-code/{plant_cd}", summary="사업장별 다음 공장코드 채번")
def get_next_factory_code(plant_cd: str):
    """사업장코드 기반으로 다음 공장코드를 자동 생성합니다. (예: P01-F001, P01-F002 ...)"""
    next_code = factory_service.get_next_code(plant_cd)
    return {"nextCode": next_code}


@router.get("/factory/{factory_cd}", summary="공장 상세 조회")
def get_factory(factory_cd: str):
    result = factory_service.get_by_id({"FACTORYCD": factory_cd})
    if not result:
        _not_found(factory_cd)
    return result


@router.post("/factory", summary="공장 등록", status_code=201)
def create_factory(body: FactoryCreate):
    return factory_service.create(body.model_dump())


@router.put("/factory/{factory_cd}", summary="공장 수정")
def update_factory(factory_cd: str, body: FactoryUpdate):
    result = factory_service.update({"FACTORYCD": factory_cd}, body.model_dump())
    if not result:
        _not_found(factory_cd)
    return result


@router.delete("/factory/{factory_cd}", summary="공장 삭제")
def delete_factory(factory_cd: str):
    if not factory_service.delete({"FACTORYCD": factory_cd}):
        _not_found(factory_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
