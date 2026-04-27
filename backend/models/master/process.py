"""공정 (TBL_COM_PROCESS) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProcessBase(BaseModel):
    PROCESSCD: str
    LINECD: Optional[str] = None
    FACTORYCD: Optional[str] = None
    PROCESSNM: str
    CONTENTS: Optional[str] = None
    USEYN: Optional[bool] = True
    MOLDYN: Optional[bool] = False
    OEMYN: Optional[bool] = False
    EXTERNALBARCODEYN: Optional[bool] = False
    MANUALGENERATEYN: Optional[bool] = False
    INSPECT_CREATEREPORTYN: Optional[bool] = False
    INSPECT_APPLYFAILYN: Optional[bool] = False

class ProcessCreate(ProcessBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class ProcessUpdate(ProcessBase):
    EDITUSERID: int = 1

class ProcessResponse(ProcessBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
