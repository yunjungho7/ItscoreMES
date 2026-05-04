"""BOM (TBL_COM_BOM) Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class BomBase(BaseModel):
    PAR_PARTNO: str = Field(..., min_length=1)
    CHILD_PARTNO: str = Field(..., min_length=1)
    REQQTY: Decimal = Field(..., gt=0)
    ORD: Optional[int] = Field(None, ge=1)
    USEYN: Optional[bool] = True

class BomCreate(BomBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class BomDetailCreate(BaseModel):
    CHILD_PARTNO: str
    REQQTY: Decimal
    ORD: Optional[int] = 1

class BomBatchCreate(BaseModel):
    PAR_PARTNO: str
    REGUSERID: int = 1
    details: List[BomDetailCreate]

class BomUpdate(BomBase):
    EDITUSERID: int = 1

class BomResponse(BomBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
