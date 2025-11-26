__all__ = ("router", )

from fastapi import APIRouter
from .clients import router as client_router

router = APIRouter(prefix='/v1')

router.include_router(router=client_router)