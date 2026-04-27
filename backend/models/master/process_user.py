"""공정별작업자 (TBL_COM_PROCESS_USER) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional


class ProcessUserBase(BaseModel):
    USER_ID: str
    PROCESS_ID: str
    GRANTED_FUNCS: Optional[str] = None
    EXCEPTED_FUNCS: Optional[str] = None

class ProcessUserCreate(ProcessUserBase):
    pass

class ProcessUserUpdate(ProcessUserBase):
    pass

class ProcessUserResponse(ProcessUserBase):
    class Config:
        from_attributes = True
