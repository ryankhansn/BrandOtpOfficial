from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from backend.utils.pay0_client import create_order  # ⬅️ yahan import karo

router = APIRouter()

class OrderBody(BaseModel):
    mobile: Annotated[str, Field(min_length=10, max_length=10)]
    amount: float = Field(gt=49, lt=5001)
    upi_id: Optional[str] = None

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    try:
        name = "User"  # fixed placeholder name
        order_id = f"ORD_{order.mobile}_{int(order.amount)}"
        redirect_url = "https://brandotpofficial.netlify.app/payment-success"
        payment_url = create_order(
            order.mobile,
            order.amount,
            redirect_url,
            remark1="Wallet Topup",
            remark2=""
        )
        return {
            "success": True,
            "order_id": order_id,
            "amount": order.amount,
            "mobile": order.mobile,
            "payment_url": payment_url,
            "message": "Order created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
