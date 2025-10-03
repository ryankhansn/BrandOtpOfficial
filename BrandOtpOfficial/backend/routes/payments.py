from fastapi import APIRouter

# Pay0 sub-routers
from .pay0_order import router as pay0_order_router
from .pay0_webhook import router as pay0_webhook_router

router = APIRouter()

# Register Pay0 routes
router.include_router(pay0_order_router, prefix="/pay0", tags=["Pay0"])
router.include_router(pay0_webhook_router, prefix="/pay0", tags=["Pay0"])
