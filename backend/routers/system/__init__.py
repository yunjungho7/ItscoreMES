from fastapi import APIRouter
from .user import router as user_router
from .menu import router as menu_router

router = APIRouter()
router.include_router(user_router)
router.include_router(menu_router)
