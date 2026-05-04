"""품목 (TBL_COM_GOODS) Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class GoodsBase(BaseModel):
    PARTNO: str = Field(..., min_length=1, description="품번")
    PLANTCD: Optional[str] = Field('', min_length=1, description="사업장코드")
    PARTNM: Optional[str] = Field('', min_length=1, description="품명")
    CARTYPE: Optional[str] = None
    PARTTYPE: Optional[str] = Field('', min_length=1, description="품목구분")
    LOTSTDQTY: Optional[int] = Field(0, ge=0)
    INTESTYN: Optional[bool] = False
    SAFETYSTOCK: Optional[int] = Field(0, ge=0)
    OPTIMUMSTOCK: Optional[int] = Field(0, ge=0)
    UNIT: Optional[str] = None
    WEIGHT: Optional[Decimal] = Field(None, ge=0)
    TEXTURE: Optional[str] = None
    WIDTH: Optional[Decimal] = Field(None, ge=0)
    LENGTH: Optional[Decimal] = Field(None, ge=0)
    THICK: Optional[Decimal] = Field(None, ge=0)
    DIAMETER: Optional[Decimal] = Field(None, ge=0)
    STANDARD: Optional[str] = ''
    UNITWEIGHT: Optional[Decimal] = Field(None, ge=0)
    LEADTIME: Optional[int] = Field(0, ge=0)
    PALLETSTDINFO: Optional[str] = None
    IMPORTPARTYN: Optional[bool] = True
    WORKSTDPATH: Optional[str] = None
    CUSTOMPARTNO: Optional[str] = ''
    PROCESSCD: Optional[str] = None
    USEYN: Optional[bool] = True
    UNIT_PRICE: Optional[Decimal] = Field(0, ge=0)
    LOCATIONCD: Optional[str] = None
    LOCATIONCD_PROD: Optional[str] = None
    QTYPERBOX: Optional[Decimal] = Field(0, ge=0)
    COMPANYCD: Optional[str] = ''
    TESTYN: Optional[str] = '0'
    MOLDLOCATION: Optional[str] = None
    INWEIGHT: Optional[Decimal] = Field(None, ge=0)
    QTYPERBONG: Optional[int] = Field(None, ge=0)
    WASTELENGTH: Optional[Decimal] = Field(None, ge=0)
    IRONSHEETPARTNO: Optional[str] = None
    SENSEBASE: Optional[Decimal] = Field(None, ge=0)

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
