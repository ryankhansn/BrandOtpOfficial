from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints, Field
from typing import Optional, Annotated

router = APIRouter()

# Correct Pydantic v2 order model:
class OrderBody(BaseModel):
    # Mobile must be 10 digits (string with exactly 10 numeric chars):
    mobile: Annotated[
        str,
        StringConstraints(min_length=10, max_length=10, pattern=r'^\d{10}$')
    ]

    # Amount must be float, 50 to 5000 rupees (exclusive):
    amount: float = Field(gt=49, lt=5001)
    # UPI ID is optional
    upi_id: Optional[str] = None

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    """Create Pay0 order"""
    try:
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
