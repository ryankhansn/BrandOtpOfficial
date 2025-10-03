from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

# Pydantic model for order
class OrderBody(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=10)  # Fixed: No constr
    amount: float = Field(gt=49, lt=5001)  # Fixed: Proper indentation
    upi_id: Optional[str] = None

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    """Create Pay0 order"""
    try:
        # Validate mobile number format
        if not order.mobile.isdigit():
            raise HTTPException(status_code=400, detail="Invalid mobile number")
        
        # For now, return demo response
        # TODO: Integrate actual Pay0 API
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
        # TODO: Implement Pay0 status check API
        return {
            "success": True,
            "order_id": order_id,
            "status": "pending",
            "message": "Order status retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
