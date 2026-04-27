from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from models.system.user import UserCreate, UserUpdate, UserResponse
from services.system.user import UserService

router = APIRouter(
    prefix="/api/system/users",
    tags=["System - Users"]
)

def get_user_service():
    return UserService()

@router.get("", response_model=List[dict])
def get_users(
    plant: Optional[str] = Query(None, description="사업장"),
    name: Optional[str] = Query(None, description="이름"),
    deptcd: Optional[str] = Query(None, description="부서"),
    showyn: Optional[bool] = Query(None, description="사용여부"),
    service: UserService = Depends(get_user_service)
):
    return service.get_users(plant, name, deptcd, showyn)

@router.post("", response_model=dict)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    service.create_user(user)
    return {"message": "사용자가 등록되었습니다."}

@router.put("/{empid}", response_model=dict)
def update_user(
    empid: str,
    user: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    service.update_user(empid, user)
    return {"message": "사용자 정보가 수정되었습니다."}

@router.delete("/{empid}", response_model=dict)
def delete_user(
    empid: str,
    service: UserService = Depends(get_user_service)
):
    service.delete_user(empid)
    return {"message": "사용자가 삭제되었습니다."}
