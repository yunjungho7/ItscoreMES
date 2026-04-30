from fastapi import APIRouter, Depends
from typing import List
from models.system.menu import MenuCreate, MenuUpdate
from services.system.menu import MenuService

router = APIRouter(
    prefix="/system/menus",
    tags=["System - Menus"]
)

def get_menu_service():
    return MenuService()

@router.get("", response_model=dict)
def get_menus(
    service: MenuService = Depends(get_menu_service)
):
    result = service.get_menus()
    return {"data": result}

@router.post("", response_model=dict)
def create_menu(
    menu: MenuCreate,
    service: MenuService = Depends(get_menu_service)
):
    service.create_menu(menu)
    return {"message": "메뉴가 등록되었습니다."}

@router.put("/{menucd}", response_model=dict)
def update_menu(
    menucd: str,
    menu: MenuUpdate,
    service: MenuService = Depends(get_menu_service)
):
    service.update_menu(menucd, menu)
    return {"message": "메뉴 정보가 수정되었습니다."}

@router.delete("/{menucd}", response_model=dict)
def delete_menu(
    menucd: str,
    service: MenuService = Depends(get_menu_service)
):
    service.delete_menu(menucd)
    return {"message": "메뉴가 삭제되었습니다."}
