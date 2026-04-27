from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    PLANT: str
    GUBUN: str
    NAME: str
    EMAIL: Optional[str] = None
    DEPTCD: Optional[str] = None
    JIKGUB: Optional[str] = None
    PASS: Optional[str] = None
    SECURE_GRADE: Optional[str] = None
    USEAREA: Optional[str] = None
    PARTNERSHOWYN: Optional[str] = "N"
    TEL: Optional[str] = None
    MOBILE: Optional[str] = None
    PASSYN: Optional[str] = "N"
    PASSWRITERID: Optional[str] = None
    SHOWYN: Optional[bool] = True
    LOGINYN: Optional[str] = "N"
    SESSIONTIME: Optional[int] = 1440
    OUTERACCESSYN: Optional[str] = "1"
    CHIEFYN: Optional[str] = "N"
    PASSWD: Optional[str] = None
    PLANTAREA: Optional[str] = None
    FROMTODAY: Optional[int] = 0
    PARTNERGUBUN: Optional[str] = None
    MANAGERYN: Optional[str] = "N"

class UserCreate(UserBase):
    EMPID: str

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    ID: int
    EMPID: str
    
    class Config:
        from_attributes = True
