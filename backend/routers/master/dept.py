"""부서관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.dept import DeptCreate, DeptUpdate
from services.master.dept import dept_service

router = APIRouter(tags=["부서관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"부서 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/dept", summary="부서 목록 조회")
def get_depts(search: Optional[str] = None, plant_cd: Optional[str] = None,
              factory_cd: Optional[str] = None, page: int = 1, size: int = 50):
    result = dept_service.get_all(
        search=search, page=page, size=size,
        plant_cd=plant_cd, factory_cd=factory_cd
    )

    return {"data": result}


@router.get("/dept/{dept_cd}", summary="부서 상세 조회")
def get_dept(dept_cd: str):
    result = dept_service.get_by_id({"DEPTCD": dept_cd})
    if not result:
        _not_found(dept_cd)
    return result


@router.post("/dept", summary="부서 등록", status_code=201)
def create_dept(body: DeptCreate):
    return dept_service.create(body.model_dump())


@router.put("/dept/{dept_cd}", summary="부서 수정")
def update_dept(dept_cd: str, body: DeptUpdate):
    result = dept_service.update({"DEPTCD": dept_cd}, body.model_dump())
    if not result:
        _not_found(dept_cd)
    return result


@router.delete("/dept/{dept_cd}", summary="부서 삭제")
def delete_dept(dept_cd: str):
    if not dept_service.delete({"DEPTCD": dept_cd}):
        _not_found(dept_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
