from fastapi import APIRouter

from app.modules.system.handlers import router as system_router
from app.modules.rmq_module.handlers import router as rmq_router
from app.modules.base_diagnostic_module.handlers import router as diagnostic_router
from app.modules.default_diagnostic_module.handlers import router as default_diagnostic_router
from app.modules.file_module.handlers import router as file_router
from app.modules.invisible_diagnostic_module.handlers import (
    router as invisible_diagnostic_router,
)
from app.modules.telegram_module.handlers import router as telegram_router

router = APIRouter(prefix="/api")

# Built-in infrastructure and feature routers live here.
router.include_router(system_router)
router.include_router(rmq_router)

router.include_router(diagnostic_router)
router.include_router(default_diagnostic_router)
router.include_router(invisible_diagnostic_router)
router.include_router(file_router)
router.include_router(telegram_router)
