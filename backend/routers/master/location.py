"""Location관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.location import LocationCreate, LocationUpdate
from services.master.location import location_service

router = APIRouter(tags=["Location관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"Location '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/location", summary="Location 목록 조회")
def get_locations(search: Optional[str] = None, page: int = 1, size: int = 50):
    return location_service.get_all(search=search, page=page, size=size)


@router.get("/location/{location_cd}", summary="Location 상세 조회")
def get_location(location_cd: str):
    result = location_service.get_by_id({"LOCATIONCODE": location_cd})
    if not result:
        _not_found(location_cd)
    return result


@router.post("/location", summary="Location 등록", status_code=201)
def create_location(body: LocationCreate):
    return location_service.create(body.model_dump())


@router.put("/location/{location_cd}", summary="Location 수정")
def update_location(location_cd: str, body: LocationUpdate):
    result = location_service.update({"LOCATIONCODE": location_cd}, body.model_dump())
    if not result:
        _not_found(location_cd)
    return result


@router.delete("/location/{location_cd}", summary="Location 삭제")
def delete_location(location_cd: str):
    if not location_service.delete({"LOCATIONCODE": location_cd}):
        _not_found(location_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
