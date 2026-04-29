"""거래처관리 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.master.company import CompanyCreate, CompanyUpdate
from services.master.company import company_service

router = APIRouter(tags=["거래처관리"])


def _not_found(key: str):
    raise HTTPException(status_code=404, detail={
        "statusCode": 404, "message": f"거래처 '{key}' 을(를) 찾을 수 없습니다."
    })


@router.get("/company", summary="거래처 목록 조회")
def get_companies(search: Optional[str] = None, company_type: Optional[str] = None, is_customer: Optional[int] = None, is_supplier: Optional[int] = None, plant_cd: Optional[str] = None, page: int = 1, size: int = 50):
    return company_service.get_all(search=search, company_type=company_type, is_customer=is_customer, is_supplier=is_supplier, plant_cd=plant_cd, page=page, size=size)


@router.get("/company/{company_cd}", summary="거래처 상세 조회")
def get_company(company_cd: str):
    result = company_service.get_by_id({"COMPANYCD": company_cd})
    if not result:
        _not_found(company_cd)
    return result


@router.post("/company", summary="거래처 등록", status_code=201)
def create_company(body: CompanyCreate):
    return company_service.create(body.model_dump())


@router.put("/company/{company_cd}", summary="거래처 수정")
def update_company(company_cd: str, body: CompanyUpdate):
    result = company_service.update({"COMPANYCD": company_cd}, body.model_dump())
    if not result:
        _not_found(company_cd)
    return result


@router.delete("/company/{company_cd}", summary="거래처 삭제")
def delete_company(company_cd: str):
    if not company_service.delete({"COMPANYCD": company_cd}):
        _not_found(company_cd)
    return {"statusCode": 200, "message": "삭제되었습니다."}
