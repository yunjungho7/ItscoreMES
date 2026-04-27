"""공통코드 (TBL_COM_CODE) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CodeBase(BaseModel):
    CODECD: str
    PAR_CODECD: Optional[str] = None
    CODENM: Optional[str] = None
    ORD: Optional[int] = 0
    TEXTVAL: Optional[str] = None
    NUMVAL: Optional[Decimal] = None
    USEYN: Optional[bool] = True
    SYS_CONST: Optional[bool] = False

class CodeCreate(CodeBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class CodeUpdate(CodeBase):
    EDITUSERID: int = 1

class CodeResponse(CodeBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
