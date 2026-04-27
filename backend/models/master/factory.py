"""공장 (TBL_COM_FACTORY) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FactoryBase(BaseModel):
    FACTORYCD: str
    PLANTCD: Optional[str] = None
    FACTORYNM: Optional[str] = None
    USEYN: Optional[bool] = True

class FactoryCreate(FactoryBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class FactoryUpdate(FactoryBase):
    EDITUSERID: int = 1

class FactoryResponse(FactoryBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
