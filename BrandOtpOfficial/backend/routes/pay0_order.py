from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from backend.utils.pay0_client import create_order

router = APIRouter()

class OrderBody(BaseModel):
    mobile: Annotated[str, Field(min_length=10, max_length=10)]
    amount: float = Field(gt=49, lt=5001)
    upi_id: Optional[str] = None

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    try:
        name = "User"
        order_id = f"ORD_{order.mobile}_{int(order.amount)}"
        redirect_url = "https://brandotpofficial.netlify.app/payment-success"
        # Get Pay0 raw response (object/dict)
        payment_resp = create_order(
            order.mobile,
            order.amount,
            redirect_url,
            remark1="Wallet Topup",
            remark2=""
        )

        # 🟢 IMPORTANT: Extract the real paymenturl string from nested dict
        pay0_link = None
        if isinstance(payment_resp, dict):
            pay0_link = (
                payment_resp.get("result", {}).get("paymenturl")
                or payment_resp.get("result", {}).get("payment_url")
                or payment_resp.get("paymenturl")
                or payment_resp.get("payment_url")
            )
        else:
            pay0_link = payment_resp  # string/direct fallback

        if not pay0_link or not isinstance(pay0_link, str):
            raise Exception("paymenturl missing from Pay0 API response")

        return {
            "success": True,
            "order_id": order_id,
            "amount": order.amount,
            "mobile": order.mobile,
            "payment_url": pay0_link,  # STRING ONLY!
            "message": "Order created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
