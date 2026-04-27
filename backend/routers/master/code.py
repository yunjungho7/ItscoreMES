"""공통코드 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.code import CodeCreate, CodeUpdate
from services.master.code import code_service

router = APIRouter(tags=["공통코드"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"공통코드 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/code", summary="공통코드 목록 조회")
def get_codes(search: Optional[str] = None, par_codecd: Optional[str] = None,
              page: int = 1, size: int = 50):
    return code_service.get_all(search=search, page=page, size=size, par_codecd=par_codecd)


@router.get("/code/{code_cd}", summary="공통코드 상세 조회")
def get_code(code_cd: str):
    result = code_service.get_by_id({"CODECD": code_cd})
    if not result:
        _not_found(code_cd)
    return result


@router.post("/code", summary="공통코드 등록", status_code=201)
def create_code(body: CodeCreate):
    return code_service.create(body.model_dump())


@router.put("/code/{code_cd}", summary="공통코드 수정")
def update_code(code_cd: str, body: CodeUpdate):
    result = code_service.update({"CODECD": code_cd}, body.model_dump())
    if not result:
        _not_found(code_cd)
    return result


@router.delete("/code/{code_cd}", summary="공통코드 삭제")
def delete_code(code_cd: str):
    if not code_service.delete({"CODECD": code_cd}):
        _not_found(code_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
