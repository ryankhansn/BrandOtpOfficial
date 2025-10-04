from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated

router = APIRouter()

# Pydantic v2 model for order
class OrderBody(BaseModel):
    # Mobile must be 10 digits, only numbers allowed by pattern, min/max_length=10
    mobile: Annotated[
        str,
        StringConstraints(min_length=10, max_length=10, pattern=r"^\d{10}$")
    ]
    # Amount between 50 and 5000 (both ends exclusive)
    amount: Annotated[
        float,
        StringConstraints(gt=49, lt=5001)
    ]
    upi_id: Optional[str] = None  # Optional UPI id

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    """Create Pay0 order"""
    try:
        # No need for .isdigit() check, pattern does it automatically!
        return {
            "success": True,
            "order_id": f"ORD_{order.mobile}_{int(order.amount)}",
            "amount": order.amount,
            "mobile": order.mobile,
            "payment_url": "https://pay0.in/demo-payment-page",
            "message": "Order created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

@router.get("/order-status/{order_id}")
async def get_order_status(order_id: str):
    """Get Pay0 order status"""
    try:
        return {
            "success": True,
            "order_id": order_id,
            "status": "pending",
            "message": "Order status retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
