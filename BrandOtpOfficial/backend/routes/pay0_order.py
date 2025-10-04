import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints, Field
from typing import Optional, Annotated

router = APIRouter()  # Yeh line sabse UPPER me (isliye error aata agar nahi hota!)

PAY0_API_URL = "https://pay0.shop/api/create-order"
PAY0_USER_TOKEN = os.getenv("PAY0_USER_TOKEN")  # Render/Heroku/Local env vars me set kar lo

# Pydantic model
class OrderBody(BaseModel):
    mobile: Annotated[
        str,
        StringConstraints(min_length=10, max_length=10, pattern=r'^\d{10}$')
    ]
    amount: float = Field(gt=49, lt=5001)
    upi_id: Optional[str] = None  # Not required by Pay0 doc, lekin rakhna ho to

async def create_pay0_order_request(mobile, name, amount, order_id, redirect_url):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "customermobile": mobile,
        "customername": name,  # User ka name yahan chaho to frontend se lo
        "usertoken": PAY0_USER_TOKEN,
        "amount": amount,
        "orderid": order_id,
        "redirecturl": redirect_url,
        "remark1": "Wallet Topup",
        "remark2": ""
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(PAY0_API_URL, data=data, headers=headers)
        result = resp.json()
        if not result.get("status"):
            raise Exception(f"Pay0 error: {result.get('message')}")
        return result["result"]["paymenturl"]  # <- Pay0 ka real payment page URL

@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    try:
        # Yahan name har user ka alag bhejna ho to frontend/order me field add karo
        name = "User"  # Temporary, ya order.username
        order_id = f"ORD_{order.mobile}_{int(order.amount)}"
        redirect_url = "https://brandotpofficial.netlify.app//payment-success"  # Change karo as per production
        payment_url = await create_pay0_order_request(
            order.mobile, name, order.amount, order_id, redirect_url
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
