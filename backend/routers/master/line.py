"""라인관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.line import LineCreate, LineUpdate
from services.master.line import line_service

router = APIRouter(tags=["라인관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"라인 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/line", summary="라인 목록 조회")
def get_lines(search: Optional[str] = None, page: int = 1, size: int = 50):
    return line_service.get_all(search=search, page=page, size=size)


@router.get("/line/{line_cd}", summary="라인 상세 조회")
def get_line(line_cd: str):
    result = line_service.get_by_id({"LINECD": line_cd})
    if not result:
        _not_found(line_cd)
    return result


@router.post("/line", summary="라인 등록", status_code=201)
def create_line(body: LineCreate):
    return line_service.create(body.model_dump())


@router.put("/line/{line_cd}", summary="라인 수정")
def update_line(line_cd: str, body: LineUpdate):
    result = line_service.update({"LINECD": line_cd}, body.model_dump())
    if not result:
        _not_found(line_cd)
    return result


@router.delete("/line/{line_cd}", summary="라인 삭제")
def delete_line(line_cd: str):
    if not line_service.delete({"LINECD": line_cd}):
        _not_found(line_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
