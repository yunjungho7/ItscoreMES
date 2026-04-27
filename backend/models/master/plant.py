"""사업장 (TBL_COM_PLANT) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlantBase(BaseModel):
    PLANTCD: str
    PAR_PLANTCD: Optional[str] = None
    PLANTNM: Optional[str] = None
    PLANTTYPE: Optional[str] = None
    ZIPCD: Optional[str] = None
    ADDR1: Optional[str] = None
    ADDR2: Optional[str] = None
    TEL: Optional[str] = None
    FAX: Optional[str] = None
    BUSINESSNO: Optional[str] = None
    BOSSNM: Optional[str] = None
    PERSON_CHARGE: Optional[str] = None
    BOSSTEL: Optional[str] = None
    USEYN: Optional[bool] = True
    INFAILLOCCD: Optional[str] = None
    PRODFAILLOCCD: Optional[str] = None
    OUTFAILLOCCD: Optional[str] = None

class PlantCreate(PlantBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class PlantUpdate(PlantBase):
    EDITUSERID: int = 1

class PlantResponse(PlantBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
