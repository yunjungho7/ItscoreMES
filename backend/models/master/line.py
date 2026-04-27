"""라인 (TBL_COM_LINE) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LineBase(BaseModel):
    LINECD: str
    PAR_LINECD: Optional[str] = None
    FACTORYCD: Optional[str] = None
    LINENM: str
    LINEDIV: Optional[str] = None
    USEYN: Optional[str] = 'Y'

class LineCreate(LineBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class LineUpdate(LineBase):
    EDITUSERID: int = 1

class LineResponse(LineBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
