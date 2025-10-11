from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import time

from backend.utils.pay0_client import create_order
from backend.utils.auth_utils import get_current_user

router = APIRouter()

class OrderBody(BaseModel):
    amount: float = Field(gt=49, lt=5001, description="Amount must be between 50 and 5000")
    customer_mobile: str

@router.post("/pay0/create-order")
async def create_pay0_order(order: OrderBody, current_user: dict = Depends(get_current_user)):
    """
    Creates a Pay0 order with a dynamic redirect URL containing the order_id.
    """
    try:
        user_id = current_user.get("id")
        timestamp = int(time.time())
        order_id = f"BRANDOTP_{user_id[:4]}_{timestamp}"

        # Redirect URL with order_id parameter
        redirect_url = f"https://brandotpofficials.netlify.app/payment-status.html?orderid={order_id}"

        # ✅ FIXED: Pass only 5 arguments
        payment_resp = create_order(
            order.customer_mobile,    # mobile: str
            order.amount,             # amount: float
            redirect_url,             # redirect: str
            user_id,                  # remark1: str
            "WalletTopup"            # remark2: str
        )
        
        # ✅ FIXED: Check for 'paymenturl' first (Pay0 uses this key)
        pay0_link = payment_resp.get("paymenturl")
        
        if not pay0_link:
            print(f"❌ Pay0 API Response: {payment_resp}")
            raise Exception(f"paymenturl missing in Pay0 API response: {payment_resp}")

        return {
            "success": True,
            "order_id": order_id,
            "paymenturl": pay0_link,  # ✅ Changed key name
            "message": "Order created successfully."
        }
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
