"""부서 (TBL_COM_DEPT) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeptBase(BaseModel):
    DEPTCD: str
    FACTORYCD: Optional[str] = None
    PAR_DEPTCD: Optional[str] = None
    DEPTNM: Optional[str] = None
    USEYN: Optional[bool] = True

class DeptCreate(DeptBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class DeptUpdate(DeptBase):
    EDITUSERID: int = 1

class DeptResponse(DeptBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
