"""거래처 (TBL_COM_COMPANY) Pydantic Models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    COMPANYCD: str
    PLANTCD: str
    COMPANYTYPE: Optional[str] = None
    COMPANYNM: Optional[str] = None
    COMPANYNM2: Optional[str] = None
    BSNO: Optional[str] = None
    OPENYEAR: Optional[str] = None
    BSSECTORS: Optional[str] = None
    ZIPCD: Optional[str] = None
    ADDR1: Optional[str] = None
    ADDR2: Optional[str] = None
    CEONM: Optional[str] = None
    MANAGER: Optional[str] = None
    EMAIL: Optional[str] = None
    TEL: Optional[str] = None
    FAX: Optional[str] = None
    MOBILE: Optional[str] = None
    HOMEURL: Optional[str] = None
    CLAIMYN: Optional[str] = None
    PURCHASEYN: Optional[str] = None
    TRADSTDATE: Optional[str] = None
    TRADENDATE: Optional[str] = None
    GRADE: Optional[str] = None
    SQCERT: Optional[str] = None
    SQGRADE: Optional[str] = None
    SQSPONSOR: Optional[str] = None
    TSISOYN: Optional[str] = None
    REMARK: Optional[str] = None
    USEYN: Optional[bool] = True
    ITEMSHEETTYPE: Optional[str] = None

class CompanyCreate(CompanyBase):
    REGUSERID: int = 1
    EDITUSERID: int = 1

class CompanyUpdate(CompanyBase):
    EDITUSERID: int = 1

class CompanyResponse(CompanyBase):
    REGUSERID: Optional[int] = None
    REGDTM: Optional[datetime] = None
    EDITUSERID: Optional[int] = None
    EDITDTM: Optional[datetime] = None
    class Config:
        from_attributes = True
