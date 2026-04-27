"""
물류 모듈 통합 라우터
- 수주관리 (/api/order)
- 발주관리 (/api/purchase)
- 입고관리 (/api/receive)
- 재고관리 (/api/inventory)
- 출하관리 (/api/shipment)
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from models.logistics.logistics import (
    OrderCreate, OrderUpdate,
    ProducePlanCreate, PurchaseOrderCreate,
    ReceiveCreate,
    StockUpdateQty,
    ShipmentCreate,
)
from services.logistics.order_service import order_service
from services.logistics.purchase_service import purchase_service
from services.logistics.receive_service import receive_service
from services.logistics.inventory_service import inventory_service
from services.logistics.shipment_service import shipment_service

router = APIRouter(tags=["물류"])

# ════════════════════════════════════════
# 수주관리
# ════════════════════════════════════════

@router.get("/api/order/list", summary="수주 목록 조회")
def get_orders(start_date: Optional[str] = None, end_date: Optional[str] = None,
               plant_cd: Optional[str] = None, company_cd: Optional[str] = None,
               search: Optional[str] = None, page: int = 1, size: int = 50):
    return order_service.get_all(start_date=start_date, end_date=end_date,
                                 plant_cd=plant_cd, company_cd=company_cd,
                                 search=search, page=page, size=size)

@router.get("/api/order/detail/{order_no}", summary="수주 상세 조회")
def get_order(order_no: int):
    result = order_service.get_by_id(order_no)
    if not result:
        raise HTTPException(status_code=404, detail="수주를 찾을 수 없습니다.")
    return result

@router.get("/api/order/detail/{order_no}/items", summary="수주 품목 목록")
def get_order_details(order_no: int):
    return order_service.get_details(order_no)

@router.post("/api/order/create", summary="수주 등록", status_code=201)
def create_order(body: OrderCreate):
    return order_service.create(body.model_dump())

@router.put("/api/order/update/{order_no}", summary="수주 수정")
def update_order(order_no: int, body: OrderUpdate):
    return order_service.update(order_no, body.model_dump())

@router.delete("/api/order/delete/{order_no}", summary="수주 삭제")
def delete_order(order_no: int):
    if not order_service.delete(order_no):
        raise HTTPException(status_code=404, detail="수주를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "삭제되었습니다."}


# ════════════════════════════════════════
# 발주관리
# ════════════════════════════════════════

@router.get("/api/purchase/plan", summary="생산계획(발주대상) 목록 조회")
def get_plan_list(plant_cd: Optional[str] = None, start_date: Optional[str] = None,
                  end_date: Optional[str] = None, search: Optional[str] = None):
    return purchase_service.get_plan_list(plant_cd=plant_cd, start_date=start_date,
                                           end_date=end_date, search=search)

@router.post("/api/purchase/plan", summary="생산계획 등록", status_code=201)
def create_plan(body: ProducePlanCreate):
    purchase_service.create_plan(body.model_dump())
    return {"statusCode": 201, "message": "등록되었습니다."}

@router.get("/api/purchase/bom/{par_partno}", summary="BOM 자재 전개")
def get_bom_children(par_partno: str):
    return purchase_service.get_bom_children(par_partno)

@router.post("/api/purchase/order", summary="발주 등록 (BOM 기반)", status_code=201)
def create_purchase_order(body: PurchaseOrderCreate):
    return {"statusCode": 201, "message": "발주가 등록되었습니다."}


# ════════════════════════════════════════
# 입고관리
# ════════════════════════════════════════

@router.get("/api/receive/list", summary="입고 목록 조회")
def get_receives(start_date: Optional[str] = None, end_date: Optional[str] = None,
                 plant_cd: Optional[str] = None, company_cd: Optional[str] = None,
                 order_num: Optional[str] = None, search: Optional[str] = None,
                 page: int = 1, size: int = 50):
    return receive_service.get_all(start_date=start_date, end_date=end_date,
                                    plant_cd=plant_cd, company_cd=company_cd,
                                    order_num=order_num, search=search,
                                    page=page, size=size)

@router.get("/api/receive/summary", summary="입고 현황 요약 통계")
def get_receive_summary():
    return receive_service.get_summary()

@router.get("/api/receive/detail/{warehouse_num}/items", summary="입고 상세 품목")
def get_receive_details(warehouse_num: str):
    return receive_service.get_details(warehouse_num)

@router.post("/api/receive/create", summary="입고 등록", status_code=201)
def create_receive(body: ReceiveCreate):
    return receive_service.create(body.model_dump())

@router.delete("/api/receive/delete/{warehouse_num}", summary="입고 삭제(취소)")
def delete_receive(warehouse_num: str):
    if not receive_service.delete(warehouse_num):
        raise HTTPException(status_code=404, detail="입고를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "입고가 취소되었습니다."}


# ════════════════════════════════════════
# 재고관리
# ════════════════════════════════════════

@router.get("/api/inventory/list", summary="재고 현황 조회")
def get_inventory(plant_cd: Optional[str] = None, warehouse_cd: Optional[str] = None,
                  line_cd: Optional[str] = None, process_cd: Optional[str] = None,
                  part_type: Optional[str] = None, lot_no: Optional[str] = None,
                  location_cd: Optional[str] = None, search: Optional[str] = None,
                  page: int = 1, size: int = 50):
    return inventory_service.get_all(plant_cd=plant_cd, warehouse_cd=warehouse_cd,
                                      line_cd=line_cd, process_cd=process_cd,
                                      part_type=part_type, lot_no=lot_no,
                                      location_cd=location_cd, search=search,
                                      page=page, size=size)

@router.get("/api/inventory/summary", summary="재고 현황 요약 통계")
def get_inventory_summary():
    return inventory_service.get_summary()

@router.get("/api/inventory/detail/{partno}", summary="품목별 LOT 재고 상세")
def get_inventory_detail(partno: str):
    return inventory_service.get_detail(partno)

@router.put("/api/inventory/update-qty", summary="재고수량 수정")
def update_stock_qty(body: StockUpdateQty):
    inventory_service.update_stock_qty(body.model_dump())
    return {"statusCode": 200, "message": "재고수량이 수정되었습니다."}


# ════════════════════════════════════════
# 출하관리
# ════════════════════════════════════════

@router.get("/api/shipment/list", summary="출하지시 목록 조회")
def get_shipments(start_date: Optional[str] = None, end_date: Optional[str] = None,
                  plant_cd: Optional[str] = None, company_cd: Optional[str] = None,
                  order_no: Optional[str] = None, search: Optional[str] = None,
                  include_done: Optional[str] = None, page: int = 1, size: int = 50):
    return shipment_service.get_all(start_date=start_date, end_date=end_date,
                                    plant_cd=plant_cd, company_cd=company_cd,
                                    order_no=order_no, search=search,
                                    include_done=include_done, page=page, size=size)

@router.get("/api/shipment/summary", summary="출하 현황 요약 통계")
def get_shipment_summary():
    return shipment_service.get_summary()

@router.get("/api/shipment/detail/{shipment_no}/items", summary="출하지시 상세 품목")
def get_shipment_details(shipment_no: str):
    return shipment_service.get_details(shipment_no)

@router.get("/api/shipment/order-items", summary="수주 품목 조회 (출하등록용)")
def get_order_items_for_shipment(company_cd: Optional[str] = None, plant_cd: Optional[str] = None,
                                  start_date: Optional[str] = None, end_date: Optional[str] = None):
    return shipment_service.get_order_items(company_cd=company_cd, plant_cd=plant_cd,
                                             start_date=start_date, end_date=end_date)

@router.post("/api/shipment/create", summary="출하지시 등록", status_code=201)
def create_shipment(body: ShipmentCreate):
    return shipment_service.create(body.model_dump())

@router.put("/api/shipment/complete/{shipment_no}", summary="출하완료")
def complete_shipment(shipment_no: str):
    if not shipment_service.complete(shipment_no):
        raise HTTPException(status_code=404, detail="출하지시를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "출하완료 처리되었습니다."}

@router.delete("/api/shipment/delete/{shipment_no}", summary="출하지시 삭제")
def delete_shipment(shipment_no: str):
    if not shipment_service.delete(shipment_no):
        raise HTTPException(status_code=404, detail="출하지시를 찾을 수 없습니다.")
    return {"statusCode": 200, "message": "삭제되었습니다."}
