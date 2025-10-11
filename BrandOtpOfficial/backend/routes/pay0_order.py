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

        redirect_url = f"https://brandotpofficials.netlify.app/payment-status.html?orderid={order_id}"

        # Create order
        payment_resp = create_order(
            order.customer_mobile,
            order.amount,
            redirect_url,
            user_id,
            "WalletTopup"
        )
        
        # ✅ FIXED: Extract payment_url from nested 'result' object
        if payment_resp.get("status") and payment_resp.get("result"):
            pay0_link = payment_resp["result"].get("payment_url") or payment_resp["result"].get("paymenturl")
        else:
            pay0_link = None
        
        if not pay0_link:
            print(f"❌ Pay0 API Response: {payment_resp}")
            raise Exception(f"payment_url missing in response: {payment_resp}")

        return {
            "success": True,
            "order_id": order_id,
            "payment_url": pay0_link,  # Frontend expects payment_url
            "message": "Order created successfully."
        }
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
