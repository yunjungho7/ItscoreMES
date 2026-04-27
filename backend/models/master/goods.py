"""품목 (TBL_COM_GOODS) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class GoodsBase(BaseModel):
    PARTNO: str
    PLANTCD: Optional[str] = ''
    PARTNM: Optional[str] = ''
    CARTYPE: Optional[str] = None
    PARTTYPE: Optional[str] = ''
    LOTSTDQTY: Optional[int] = 0
    INTESTYN: Optional[bool] = False
    SAFETYSTOCK: Optional[int] = 0
    OPTIMUMSTOCK: Optional[int] = 0
    UNIT: Optional[str] = None
    WEIGHT: Optional[Decimal] = None
    TEXTURE: Optional[str] = None
    WIDTH: Optional[Decimal] = None
    LENGTH: Optional[Decimal] = None
    THICK: Optional[Decimal] = None
    DIAMETER: Optional[Decimal] = None
    STANDARD: Optional[str] = ''
    UNITWEIGHT: Optional[Decimal] = None
    LEADTIME: Optional[int] = 0
    PALLETSTDINFO: Optional[str] = None
    IMPORTPARTYN: Optional[bool] = True
    WORKSTDPATH: Optional[str] = None
    CUSTOMPARTNO: Optional[str] = ''
    PROCESSCD: Optional[str] = None
    USEYN: Optional[bool] = True
    UNIT_PRICE: Optional[Decimal] = 0
    LOCATIONCD: Optional[str] = None
    LOCATIONCD_PROD: Optional[str] = None
    QTYPERBOX: Optional[Decimal] = 0
    COMPANYCD: Optional[str] = ''
    TESTYN: Optional[str] = '0'
    MOLDLOCATION: Optional[str] = None
    INWEIGHT: Optional[Decimal] = None
    QTYPERBONG: Optional[int] = None
    WASTELENGTH: Optional[Decimal] = None
    IRONSHEETPARTNO: Optional[str] = None
    SENSEBASE: Optional[Decimal] = None

class GoodsCreate(GoodsBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class GoodsUpdate(GoodsBase):
    EDITUSERID: int = 1

class GoodsResponse(GoodsBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
