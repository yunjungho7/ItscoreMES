"""BOM관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models.master.bom import BomCreate, BomUpdate, BomBatchCreate
from services.master.bom import bom_service

router = APIRouter(tags=["BOM관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"BOM '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/bom", summary="BOM 목록 조회")
def get_boms(search: Optional[str] = None, page: int = 1, size: int = 50):
    return bom_service.get_all(search=search, page=page, size=size)


@router.get("/bom/detail/{par_partno}", summary="BOM 자식 목록 조회")
def get_bom_details(par_partno: str):
    return bom_service.get_details(par_partno)


@router.get("/bom/{par_partno}/{child_partno}", summary="BOM 상세 조회")
def get_bom(par_partno: str, child_partno: str):
    result = bom_service.get_by_id({"PAR_PARTNO": par_partno, "CHILD_PARTNO": child_partno})
    if not result:
        _not_found(f"{par_partno}/{child_partno}")
    return result


@router.post("/bom", summary="BOM 일괄 등록", status_code=201)
def create_bom_batch(body: BomBatchCreate):
    return bom_service.upsert_batch(body.model_dump())


@router.post("/bom/single", summary="BOM 단건 등록", status_code=201)
def create_bom_single(body: BomCreate):
    return bom_service.create(body.model_dump())


@router.put("/bom/{par_partno}/{child_partno}", summary="BOM 수정")
def update_bom(par_partno: str, child_partno: str, body: BomUpdate):
    result = bom_service.update(
        {"PAR_PARTNO": par_partno, "CHILD_PARTNO": child_partno},
        body.model_dump()
    )
    if not result:
        _not_found(f"{par_partno}/{child_partno}")
    return result


@router.delete("/bom/{par_partno}/{child_partno}", summary="BOM 삭제")
def delete_bom(par_partno: str, child_partno: str):
    if not bom_service.delete({"PAR_PARTNO": par_partno, "CHILD_PARTNO": child_partno}):
        _not_found(f"{par_partno}/{child_partno}")
    return {"statusCode": 200, "message": "삭제되었습니다."}
