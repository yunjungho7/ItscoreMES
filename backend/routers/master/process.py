"""공정관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.process import ProcessCreate, ProcessUpdate
from services.master.process import process_service

router = APIRouter(tags=["공정관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"공정 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/process", summary="공정 목록 조회")
def get_processes(search: Optional[str] = None, page: int = 1, size: int = 50):
    result = process_service.get_all(search=search, page=page, size=size)

    return {"data": result}


@router.get("/process/{process_cd}", summary="공정 상세 조회")
def get_process(process_cd: str):
    result = process_service.get_by_id({"PROCESSCD": process_cd})
    if not result:
        _not_found(process_cd)
    return result


@router.post("/process", summary="공정 등록", status_code=201)
def create_process(body: ProcessCreate):
    return process_service.create(body.model_dump())


@router.put("/process/{process_cd}", summary="공정 수정")
def update_process(process_cd: str, body: ProcessUpdate):
    result = process_service.update({"PROCESSCD": process_cd}, body.model_dump())
    if not result:
        _not_found(process_cd)
    return result


@router.delete("/process/{process_cd}", summary="공정 삭제")
def delete_process(process_cd: str):
    if not process_service.delete({"PROCESSCD": process_cd}):
        _not_found(process_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
