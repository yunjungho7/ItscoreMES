"""불량코드 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.failcode import FailcodeCreate, FailcodeUpdate
from services.master.failcode import failcode_service

router = APIRouter(tags=["불량코드"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"불량코드 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/failcode", summary="불량코드 목록 조회")
def get_failcodes(search: Optional[str] = None, page: int = 1, size: int = 50):
    result = failcode_service.get_all(search=search, page=page, size=size)

    return {"data": result}


@router.get("/failcode/{fail_cd}", summary="불량코드 상세 조회")
def get_failcode(fail_cd: str):
    result = failcode_service.get_by_id({"FAILCD": fail_cd})
    if not result:
        _not_found(fail_cd)
    return result


@router.post("/failcode", summary="불량코드 등록", status_code=201)
def create_failcode(body: FailcodeCreate):
    return failcode_service.create(body.model_dump())


@router.put("/failcode/{fail_cd}", summary="불량코드 수정")
def update_failcode(fail_cd: str, body: FailcodeUpdate):
    result = failcode_service.update({"FAILCD": fail_cd}, body.model_dump())
    if not result:
        _not_found(fail_cd)
    return result


@router.delete("/failcode/{fail_cd}", summary="불량코드 삭제")
def delete_failcode(fail_cd: str):
    if not failcode_service.delete({"FAILCD": fail_cd}):
        _not_found(fail_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
