"""사업장관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.plant import PlantCreate, PlantUpdate
from services.master.plant import plant_service

router = APIRouter(tags=["사업장관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"사업장 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/plant", summary="사업장 목록 조회")
def get_plants(search: Optional[str] = None, page: int = 1, size: int = 50):
    result = plant_service.get_all(search=search, page=page, size=size)

    return {"data": result}


@router.get("/plant/{plant_cd}", summary="사업장 상세 조회")
def get_plant(plant_cd: str):
    result = plant_service.get_by_id({"PLANTCD": plant_cd})
    if not result:
        _not_found(plant_cd)
    return result


@router.post("/plant", summary="사업장 등록", status_code=201)
def create_plant(body: PlantCreate):
    return plant_service.create(body.model_dump())


@router.put("/plant/{plant_cd}", summary="사업장 수정")
def update_plant(plant_cd: str, body: PlantUpdate):
    result = plant_service.update({"PLANTCD": plant_cd}, body.model_dump())
    if not result:
        _not_found(plant_cd)
    return result


@router.delete("/plant/{plant_cd}", summary="사업장 삭제")
def delete_plant(plant_cd: str):
    if not plant_service.delete({"PLANTCD": plant_cd}):
        _not_found(plant_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
