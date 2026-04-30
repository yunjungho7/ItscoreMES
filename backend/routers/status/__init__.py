from fastapi import APIRouter, HTTPException
from typing import Optional, List
from services.status.defect_status_service import defect_status_service
from services.status.production_status_service import production_status_service

router = APIRouter(tags=["현황"])

@router.get("/status/production", summary="생산현황 목록 조회")
def get_production_status(start_date: Optional[str] = None, end_date: Optional[str] = None,
                          plant_cd: Optional[str] = None, lot_no: Optional[str] = None,
                          part_no: Optional[str] = None, search: Optional[str] = None,
                          page: int = 1, size: int = 50):
    return production_status_service.get_all(start_date, end_date, plant_cd, lot_no, part_no, search, page, size)

@router.get("/status/production/{lot_no}/defects", summary="생산실적 불량 상세 조회")
def get_production_defects(lot_no: str):
    return production_status_service.get_defects(lot_no)

@router.get("/status/defect", summary="불량현황 목록 조회")
def get_defect_status(start_date: Optional[str] = None, end_date: Optional[str] = None,
                      plant_cd: Optional[str] = None, lot_no: Optional[str] = None,
                      part_no: Optional[str] = None, process_status: Optional[str] = None,
                      page: int = 1, size: int = 50):
    return defect_status_service.get_all(start_date, end_date, plant_cd, lot_no, part_no, process_status, page, size)
