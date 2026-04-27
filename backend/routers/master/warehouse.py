"""창고관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.warehouse import WarehouseCreate, WarehouseUpdate
from services.master.warehouse import warehouse_service

router = APIRouter(tags=["창고관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"창고 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/warehouse", summary="창고 목록 조회")
def get_warehouses(search: Optional[str] = None, page: int = 1, size: int = 50):
    return warehouse_service.get_all(search=search, page=page, size=size)


@router.get("/warehouse/{warehouse_cd}", summary="창고 상세 조회")
def get_warehouse(warehouse_cd: str):
    result = warehouse_service.get_by_id({"WAREHOUSECODE": warehouse_cd})
    if not result:
        _not_found(warehouse_cd)
    return result


@router.post("/warehouse", summary="창고 등록", status_code=201)
def create_warehouse(body: WarehouseCreate):
    return warehouse_service.create(body.model_dump())


@router.put("/warehouse/{warehouse_cd}", summary="창고 수정")
def update_warehouse(warehouse_cd: str, body: WarehouseUpdate):
    result = warehouse_service.update({"WAREHOUSECODE": warehouse_cd}, body.model_dump())
    if not result:
        _not_found(warehouse_cd)
    return result


@router.delete("/warehouse/{warehouse_cd}", summary="창고 삭제")
def delete_warehouse(warehouse_cd: str):
    if not warehouse_service.delete({"WAREHOUSECODE": warehouse_cd}):
        _not_found(warehouse_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
