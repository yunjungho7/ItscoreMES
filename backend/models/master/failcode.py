"""불량코드 (TBL_COM_FAILCODE) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FailcodeBase(BaseModel):
    FAILCD: str
    PAR_FAILCD: Optional[str] = None
    FAILCDNM: Optional[str] = None
    FAILTYPE: Optional[str] = None
    USEYN: Optional[bool] = True
    REMARK: Optional[str] = None

class FailcodeCreate(FailcodeBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class FailcodeUpdate(FailcodeBase):
    EDITUSERID: int = 1

class FailcodeResponse(FailcodeBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
