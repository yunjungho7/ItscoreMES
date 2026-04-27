"""Location (TBL_COM_LOCATION) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LocationBase(BaseModel):
    LOCATIONCODE: str
    WAREHOUSECODE: Optional[str] = None
    LOCATIONNAME: Optional[str] = None
    RACKCODE: Optional[str] = None
    ROW: Optional[str] = None
    FLOOR: Optional[str] = None
    USEYN: Optional[bool] = True
    PAR_LOCATIONCD: Optional[str] = None
    FAILLOCYN: Optional[bool] = False

class LocationCreate(LocationBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class LocationUpdate(LocationBase):
    EDITUSERID: int = 1

class LocationResponse(LocationBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
