from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.inspection.insp_item_service import insp_item_service

router = APIRouter(tags=["검사"])

class InspItemSaveRequest(BaseModel):
    CODE: Optional[str] = None
    PLANTCD: Optional[str] = 'P001'
    INSP_TP: Optional[str] = None
    ITEMGUBUN: Optional[str] = None
    TESTITEMGP: Optional[str] = None
    TESTITEM: Optional[str] = None
    GAUGE: Optional[str] = None
    STANDARD: Optional[str] = None
    USEYN: Optional[bool] = True
    FAILTYPE: Optional[str] = None
    FAILBREAKDOWN: Optional[str] = None

@router.get("/api/inspection/items", summary="검사항목 목록 조회")
def get_inspection_items(
    plant_cd: Optional[str] = None, insp_tp: Optional[str] = None,
    item_gubun: Optional[str] = None, test_item_gp: Optional[str] = None,
    test_item: Optional[str] = None, gauge: Optional[str] = None,
    use_yn: Optional[int] = None, page: int = 1, size: int = 50
):
    return insp_item_service.get_all(plant_cd, insp_tp, item_gubun, test_item_gp, test_item, gauge, use_yn, page, size)

@router.post("/api/inspection/items", summary="검사항목 저장 (신규/수정)")
def save_inspection_item(req: InspItemSaveRequest):
    try:
        result = insp_item_service.save(req.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from services.inspection.insp_standard_service import insp_standard_service

class InspStandardSaveRequest(BaseModel):
    master: dict
    items: List[dict]

@router.get("/api/inspection/standard", summary="기준서 마스터 목록 조회")
def get_inspection_standards(part_no_nm: Optional[str] = None, part_gubun: Optional[str] = None):
    return insp_standard_service.get_list(part_no_nm, part_gubun)

@router.get("/api/inspection/standard/{part_no}/history", summary="기준서 개정 이력 조회")
def get_inspection_standard_history(part_no: str, process_cd: str):
    return insp_standard_service.get_history(part_no, process_cd)

@router.get("/api/inspection/standard/detail/{code}", summary="기준서 단건(마스터+디테일) 조회")
def get_inspection_standard_detail(code: str):
    return insp_standard_service.get_details(code)

@router.post("/api/inspection/standard", summary="기준서 일괄 저장 (Master+Detail)")
def save_inspection_standard(req: InspStandardSaveRequest):
    try:
        result = insp_standard_service.save(req.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from services.inspection.testscore_service import testscore_service

@router.get("/api/inspection/testscore", summary="검사성적서 마스터 목록 조회")
def get_inspection_testscore_list(
    plant: Optional[str] = None, test_gubun: Optional[str] = None,
    prod_cd: Optional[str] = None, part_no_nm: Optional[str] = None,
    lot_no: Optional[str] = None, start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return testscore_service.get_list(plant, test_gubun, prod_cd, part_no_nm, lot_no, start_date, end_date)

@router.get("/api/inspection/testscore/{pcode}/details", summary="검사성적서 상세 (기준서 항목) 조회")
def get_inspection_testscore_details(pcode: str):
    return testscore_service.get_details(pcode)
