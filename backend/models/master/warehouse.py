"""창고 (TBL_COM_WAREHOUSE) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WarehouseBase(BaseModel):
    WAREHOUSECODE: str
    PLANTCD: Optional[str] = None
    WAREHOUSENAME: Optional[str] = None
    USEYN: Optional[bool] = True

class WarehouseCreate(WarehouseBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class WarehouseUpdate(WarehouseBase):
    EDITUSERID: int = 1

class WarehouseResponse(WarehouseBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
