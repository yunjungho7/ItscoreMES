"""품목관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.goods import GoodsCreate, GoodsUpdate
from services.master.goods import goods_service

router = APIRouter(tags=["품목관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"품목 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/goods", summary="품목 목록 조회")
def get_goods_list(search: Optional[str] = None, parttype: Optional[str] = None,
                   page: int = 1, size: int = 50):
    return goods_service.get_all(search=search, page=page, size=size, parttype=parttype)


@router.get("/goods/{part_no}", summary="품목 상세 조회")
def get_goods(part_no: str):
    result = goods_service.get_by_id({"PARTNO": part_no})
    if not result:
        _not_found(part_no)
    return result


@router.post("/goods", summary="품목 등록", status_code=201)
def create_goods(body: GoodsCreate):
    return goods_service.create(body.model_dump())


@router.put("/goods/{part_no}", summary="품목 수정")
def update_goods(part_no: str, body: GoodsUpdate):
    result = goods_service.update({"PARTNO": part_no}, body.model_dump())
    if not result:
        _not_found(part_no)
    return result


@router.delete("/goods/{part_no}", summary="품목 삭제")
def delete_goods(part_no: str):
    if not goods_service.delete({"PARTNO": part_no}):
        _not_found(part_no)
    return {"statusCode": 200, "message": "삭제되었습니다."}
