"""공정별작업자 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.process_user import ProcessUserCreate, ProcessUserUpdate
from services.master.process_user import process_user_service

router = APIRouter(tags=["공정별작업자"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"공정별작업자 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/process-user", summary="공정별작업자 목록 조회")
def get_process_users(search: Optional[str] = None, page: int = 1, size: int = 50):
    result = process_user_service.get_all(search=search, page=page, size=size)

    return {"data": result}


@router.get("/process-user/{user_id}/{process_id}", summary="공정별작업자 상세 조회")
def get_process_user(user_id: str, process_id: str):
    result = process_user_service.get_by_id({"USER_ID": user_id, "PROCESS_ID": process_id})
    if not result:
        _not_found(f"{user_id}/{process_id}")
    return result


@router.post("/process-user", summary="공정별작업자 등록", status_code=201)
def create_process_user(body: ProcessUserCreate):
    return process_user_service.create(body.model_dump())


@router.put("/process-user/{user_id}/{process_id}", summary="공정별작업자 수정")
def update_process_user(user_id: str, process_id: str, body: ProcessUserUpdate):
    result = process_user_service.update(
        {"USER_ID": user_id, "PROCESS_ID": process_id},
        body.model_dump()
    )
    if not result:
        _not_found(f"{user_id}/{process_id}")
    return result


@router.delete("/process-user/{user_id}/{process_id}", summary="공정별작업자 삭제")
def delete_process_user(user_id: str, process_id: str):
    if not process_user_service.delete({"USER_ID": user_id, "PROCESS_ID": process_id}):
        _not_found(f"{user_id}/{process_id}")
    return {"statusCode": 200, "message": "삭제되었습니다."}
