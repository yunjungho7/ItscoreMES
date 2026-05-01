"""
생산 모듈 통합 라우터
- 생산계획 (/api/production/plan)
- 작업지시 (/api/production/workorder)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

from services.production.plan_service import plan_service
from services.production.workorder_service import workorder_service
from services.production.status_service import status_service
from services.production.input_material_service import input_material_service
from services.production.lot_service import lot_service
from services.production.daily_report_service import daily_report_service
from services.production.fail_lot_service import fail_lot_service
from services.production.field_service import field_service

router = APIRouter(tags=["생산"])


# ── Models ──
class PlanUpsert(BaseModel):
    PRODUCEDT: date
    PLANTCD: str
    PARTNO: str
    ORDERNUM: str = ''
    ORDERSEQ: int = 1
    PRODUCEQTY: int = 0
    REGUSERID: int = 1
    EDITUSERID: int = 1

class WorkOrderCreate(BaseModel):
    PLANTCD: str
    PARTNO: str
    ORDDATE: str
    ORDQTY: Optional[Decimal] = 0
    PROCESSCD: Optional[str] = None
    LINECD: Optional[str] = None
    SHIFT: Optional[str] = None
    ORDTYPE: Optional[str] = None
    ORDpriority: Optional[int] = 1
    PAR_WORKORDNO: Optional[str] = None
    REMARK: Optional[str] = None

class WorkOrderBatchCreate(BaseModel):
    header: WorkOrderCreate
    items: List[WorkOrderCreate]

class WorkOrderUpdate(BaseModel):
    ORDQTY: Optional[Decimal] = None
    PROCESSCD: Optional[str] = None
    LINECD: Optional[str] = None
    SHIFT: Optional[str] = None
    ORDTYPE: Optional[str] = None
    ORDpriority: Optional[int] = None
    ORDSTATE: Optional[str] = None
    REMARK: Optional[str] = None

class StatusChangeRequest(BaseModel):
    WORKORDNO: str
    STATUS: str  # SETTING, STARTED, INSPECTING, DONE

class ResultSaveRequest(BaseModel):
    WORKORDNO: str
    PROD_QTY: Decimal
    FAIL_QTY: Decimal

class InputMaterialRequest(BaseModel):
    WORKORDNO: str
    MAT_LOTNO: str
    INPUT_QTY: Decimal
    REMARK: Optional[str] = ''


# ════════════════════════════════════════
# 생산계획
# ════════════════════════════════════════

@router.get("/production/plan", summary="생산계획 조회 (월별 피벗)")
def get_plan(plant_cd: Optional[str] = None, base_date: Optional[str] = None,
             search: Optional[str] = None):
    return plan_service.get_plan_list(plant_cd=plant_cd, base_date=base_date, search=search)

@router.post("/production/plan", summary="생산계획 등록/수정", status_code=201)
def upsert_plan(body: PlanUpsert):
    plan_service.upsert(body.model_dump())
    return {"statusCode": 201, "message": "저장되었습니다."}

@router.post("/production/plan/batch", summary="생산계획 일괄 저장", status_code=201)
def batch_upsert_plan(body: List[PlanUpsert]):
    for item in body:
        plan_service.upsert(item.model_dump())
    return {"statusCode": 201, "message": f"{len(body)}건 저장되었습니다."}


# ════════════════════════════════════════
# 작업지시
# ════════════════════════════════════════

@router.get("/production/workorder", summary="작업지시 목록 조회")
def get_workorders(start_date: Optional[str] = None, end_date: Optional[str] = None,
                   plant_cd: Optional[str] = None, shift: Optional[str] = None,
                   ord_state: Optional[str] = None, search: Optional[str] = None,
                   parent_only: Optional[bool] = None,
                   page: int = 1, size: int = 50):
    return workorder_service.get_all(start_date=start_date, end_date=end_date,
                                      plant_cd=plant_cd, shift=shift,
                                      ord_state=ord_state, search=search,
                                      parent_only=parent_only,
                                      page=page, size=size)

@router.get("/production/workorder/{workordno}/children", summary="하위 작업지시")
def get_workorder_children(workordno: str):
    return workorder_service.get_children(workordno)

@router.post("/production/workorder", summary="작업지시 등록", status_code=201)
def create_workorder(body: WorkOrderCreate):
    return workorder_service.create(body.model_dump())

@router.post("/production/workorder/batch", summary="작업지시 일괄 등록 (상하위)", status_code=201)
def create_workorder_batch(body: WorkOrderBatchCreate):
    return workorder_service.create_batch(body.header.model_dump(), [item.model_dump() for item in body.items])

@router.put("/production/workorder/{workordno}", summary="작업지시 수정")
def update_workorder(workordno: str, body: WorkOrderUpdate):
    return workorder_service.update(workordno, body.model_dump())

@router.delete("/production/workorder/{workordno}", summary="작업지시 삭제")
def delete_workorder(workordno: str):
    if not workorder_service.delete(workordno):
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "삭제되었습니다."}

# ════════════════════════════════════════
# 생산현황 (작업실적)
# ════════════════════════════════════════

@router.get("/production/status/result/{workordno}", summary="작업실적 목록 조회")
def get_production_results(workordno: str):
    return status_service.get_results(workordno)

@router.delete("/production/status/result/{lotno}", summary="작업실적 취소")
def cancel_production_result(lotno: str):
    if not status_service.cancel_result(lotno):
        raise HTTPException(status_code=404, detail="작업실적을 찾을 수 없거나 이미 취소되었습니다.")
    return {"statusCode": 200, "message": "작업실적이 취소되었습니다."}

# ════════════════════════════════════════
# 투입자재
# ════════════════════════════════════════

@router.get("/production/input-material/{workordno}", summary="투입자재 목록 조회")
def get_input_materials(workordno: str):
    return input_material_service.get_input_materials(workordno)

@router.post("/production/field/input-material", summary="현장 자재 투입 저장")
def save_input_material(body: InputMaterialRequest):
    if not input_material_service.save_input(body.model_dump()):
        raise HTTPException(status_code=400, detail="자재 투입 저장에 실패했습니다.")
    return {"statusCode": 200, "message": "자재가 투입되었습니다."}

# ════════════════════════════════════════
# LOT 관리
# ════════════════════════════════════════

class LotCreate(BaseModel):
    PARTNO: str
    LOTQTY: Decimal
    UNIT: str
    WAREHOUSECODE: Optional[str] = None
    LOCATIONCODE: Optional[str] = None
    LOTCREATIONDAY: str
    LOTTYPE: Optional[str] = '일반'
    REMARK: Optional[str] = ''
    WORKORDNO: Optional[str] = None
    PROCESSCD: Optional[str] = None
    LINECD: Optional[str] = None
    SHIFT: Optional[str] = None

@router.get("/production/lot", summary="LOT 목록 조회")
def get_lots(start_date: Optional[str] = None, end_date: Optional[str] = None,
             lot_no: Optional[str] = None, part_no: Optional[str] = None,
             page: int = 1, size: int = 50):
    return lot_service.get_all(start_date, end_date, lot_no, part_no, page, size)

@router.post("/production/lot", summary="LOT 생성", status_code=201)
def create_lot(body: LotCreate):
    return lot_service.create(body.model_dump())

@router.get("/production/lot/tracking/{lotno}", summary="LOT 추적")
def track_lot(lotno: str):
    return lot_service.get_tracking(lotno)

# ════════════════════════════════════════
# 작업일보
# ════════════════════════════════════════

@router.get("/production/daily-report", summary="작업일보 목록 조회")
def get_daily_report(start_date: Optional[str] = None, end_date: Optional[str] = None,
                     plant_cd: Optional[str] = None, process_cd: Optional[str] = None,
                     shift: Optional[str] = None, page: int = 1, size: int = 50):
    return daily_report_service.get_all(start_date, end_date, plant_cd, process_cd, shift, page, size)

# ════════════════════════════════════════
# 불량 관리
# ════════════════════════════════════════

@router.get("/production/fail-lot", summary="불량 LOT 목록 조회")
def get_fail_lots(start_date: Optional[str] = None, end_date: Optional[str] = None,
                  plant_cd: Optional[str] = None, lot_no: Optional[str] = None,
                  fail_gubuns: Optional[str] = None, page: int = 1, size: int = 50):
    return fail_lot_service.get_all(start_date, end_date, plant_cd, lot_no, fail_gubuns, page, size)

@router.post("/production/fail-lot/{action}", summary="불량 LOT 양품/폐기 처리")
def process_fail_lots(action: str, items: List[dict]):
    if action not in ['recover', 'scrap']:
        raise HTTPException(status_code=400, detail="Invalid action")
    try:
        fail_lot_service.process_fail_qty(items, action)
        return {"statusCode": 200, "message": f"{action} 처리가 완료되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════
# 현장 생산관리
# ════════════════════════════════════════

@router.get("/production/field/workorders", summary="현장 작업지시 목록 조회")
def get_field_workorders(start_date: Optional[str] = None, end_date: Optional[str] = None,
                         shift: Optional[str] = None, ord_state: Optional[str] = None,
                         line_cd: Optional[str] = None, process_cd: Optional[str] = None,
                         workord_no: Optional[str] = None, search: Optional[str] = None,
                         include_done: bool = False,
                         page: int = 1, size: int = 50):
    return field_service.get_workorders(start_date=start_date, end_date=end_date,
                                         shift=shift, ord_state=ord_state,
                                         line_cd=line_cd, process_cd=process_cd,
                                         workord_no=workord_no, search=search,
                                         include_done=include_done,
                                         page=page, size=size)

@router.get("/production/field/summary/{workordno}", summary="현장 생산실적 집계")
def get_field_summary(workordno: str):
    return field_service.get_summary(workordno)

@router.get("/production/field/result/{workordno}", summary="현장 생산실적 LOT 상세")
def get_field_result(workordno: str):
    return field_service.get_result(workordno)

@router.get("/production/field/history/{workordno}", summary="현장 생산이력")
def get_field_history(workordno: str):
    return field_service.get_history(workordno)

@router.get("/production/field/defect/{workordno}", summary="현장 불량이력")
def get_field_defect(workordno: str):
    return field_service.get_defect(workordno)

@router.post("/production/field/status-change", summary="현장 작업 상태 변경")
def change_field_status(body: StatusChangeRequest):
    if body.STATUS not in ['SETTING', 'STARTED', 'INSPECTING', 'DONE']:
        raise HTTPException(status_code=400, detail="유효하지 않은 상태값입니다.")
    if not field_service.change_status(body.WORKORDNO, body.STATUS):
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": f"상태가 {body.STATUS}로 변경되었습니다."}

@router.post("/production/field/result-save", summary="현장 중간 생산실적 저장")
def save_field_result(body: ResultSaveRequest):
    if not field_service.save_result(body.model_dump()):
        raise HTTPException(status_code=400, detail="실적 저장에 실패했습니다.")
    return {"statusCode": 200, "message": "실적이 저장되었습니다."}

@router.post("/production/field/cancel-production", summary="현장 생산 취소")
def cancel_field_production(body: dict):
    workordno = body.get('WORKORDNO')
    if not workordno:
        raise HTTPException(status_code=400, detail="작업지시번호가 필요합니다.")
    if not field_service.cancel_production(workordno):
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "생산이 취소되고 실적이 초기화되었습니다."}
