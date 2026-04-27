from pydantic import BaseModel
from typing import Optional

class MenuBase(BaseModel):
    PAR_MENUCD: Optional[str] = None
    MENUNM: Optional[str] = None
    CLASS_PATH: Optional[str] = None
    ORD: Optional[int] = 0
    SEARCH: Optional[bool] = False
    REGEDIT: Optional[bool] = False
    USE_YN: Optional[bool] = True

class MenuCreate(MenuBase):
    MENUCD: str

class MenuUpdate(MenuBase):
    pass

class MenuResponse(MenuBase):
    MENUCD: str
    
    class Config:
        from_attributes = True
