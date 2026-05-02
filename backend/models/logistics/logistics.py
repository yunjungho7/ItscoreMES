"""수주관리 Pydantic Models"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal


class OrderBase(BaseModel):
    PLANTCD: Optional[str] = None
    COMPANYCD: Optional[str] = None
    ADOFREQDT: Optional[date] = None
    ORDERDT: Optional[date] = None
    ORDERSTATE: Optional[str] = None
    REMARK: Optional[str] = None

class OrderCreate(OrderBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1
    details: List['OrderDetailCreate'] = []

class OrderUpdate(OrderBase):
    EDITUSERID: int = 1
    details: List['OrderDetailCreate'] = []

class OrderDetailCreate(BaseModel):
    PARTNO: str
    SEQ: int = 1
    ADOFREQDT: Optional[date] = None
    REQQTY: Optional[Decimal] = 0
    UNIT_PRICE: Optional[Decimal] = 0
    REMARK: Optional[str] = None


"""발주관리 Pydantic Models"""

class ProducePlanCreate(BaseModel):
    PRODUCEDT: date
    PLANTCD: str
    PARTNO: str
    ORDERNUM: str
    ORDERSEQ: int = 1
    PRODUCEQTY: int = 0
    REGUSERID: int = 1

class PurchaseOrderCreate(BaseModel):
    PLANTCD: str
    COMPANYCD: Optional[str] = None
    ADOFREQDT: date
    REMARK: Optional[str] = None
    details: List['PurchaseItemCreate'] = []

class PurchaseItemCreate(BaseModel):
    PARTNO: str
    COMPANYCD: Optional[str] = None
    ORDERQTY: Decimal = 0
    UNIT_PRICE: Optional[Decimal] = 0
    ADOFREQDT: Optional[date] = None
    REMARK: Optional[str] = None


"""입고관리 Pydantic Models"""

class ReceiveCreate(BaseModel):
    PLANTCD: str
    ORDERNUM: Optional[str] = None
    COMPANYCD: Optional[str] = None
    INGUBUN: Optional[str] = None
    INDAY: Optional[date] = None
    REGUSERID: str = '1'
    details: List['ReceiveDetailCreate'] = []

class ReceiveDetailCreate(BaseModel):
    PARTNO: str
    LOTNO: Optional[str] = None
    INLOTQTY: Optional[Decimal] = 0
    LOCATIONCODE: Optional[str] = None
    UNIT_PRICE: Optional[Decimal] = 0


"""재고관리 Pydantic Models"""

class StockUpdateQty(BaseModel):
    LOTNO: str
    LOCATIONCODE: str
    STOCKQTY: Decimal
    REMARK: Optional[str] = None
    REGUSERID: int = 1


"""출하관리 Pydantic Models"""

class ShipmentCreate(BaseModel):
    PLANTCD: str
    COMPANYCD: str
    SHIPMENTGUBUN: Optional[str] = None
    SHIPMENTPLANDAY: Optional[date] = None
    ORDERNO: Optional[str] = None
    REMARK: Optional[str] = None
    details: List['ShipmentDetailCreate'] = []

class ShipmentDetailCreate(BaseModel):
    PARTNO: str
    ORDERNO: Optional[str] = None
    SHIPMENTINDICATIONQTY: Optional[Decimal] = 0
    ADOFREQDT: Optional[date] = None
    UNIT_PRICE: Optional[Decimal] = 0
    REMARK: Optional[str] = None

class ShipmentLot(BaseModel):
    part_no: str
    lot_no: str
    qty: Decimal

class ShipmentRegisterRequest(BaseModel):
    shipment_indication_no: str
    company_cd: str
    plant_cd: str
    unit: str
    user_id: int
    lots: List[ShipmentLot]
