from fastapi import APIRouter
from .views import router as quest_router
from .websocket import router as ws_router

router = APIRouter()
router.include_router(quest_router, prefix="/api")
router.include_router(ws_router, prefix="/api")
