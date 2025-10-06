# backend/routes/pay0_order.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Annotated
import time

# अपने प्रोजेक्ट के सही लोकेशन से इम्पोर्ट करें
from backend.utils.pay0_client import create_order
from backend.utils.auth_utils import get_current_user

router = APIRouter()

class OrderBody(BaseModel):
    # मोबाइल नंबर की अब आवश्यकता नहीं होगी क्योंकि हम इसे लॉग-इन यूजर से लेंगे
    amount: float = Field(gt=49, lt=5001, description="Amount must be between 50 and 5000")

@router.post("/create-order")
async def create_pay0_order(order: OrderBody, current_user: dict = Depends(get_current_user)):
    """
    Creates a Pay0 order with a dynamic redirect URL containing the order_id.
    """
    try:
        # यूजर की जानकारी लॉग-इन क्रेडेंशियल्स से प्राप्त करें
        user_id = current_user.get("id")
        user_mobile = current_user.get("mobile", "9999999999") # अगर मोबाइल नंबर नहीं है तो एक डिफॉल्ट नंबर दें

        # एक यूनिक और बेहतर ऑर्डर आईडी बनाएँ
        timestamp = int(time.time())
        order_id = f"BRANDOTP_{user_id[:4]}_{timestamp}"

        # --- ✅ मुख्य बदलाव: डायनामिक redirect_url ---
        # यह यूजर को पेमेंट के बाद हमारे नए payment-status.html पेज पर भेजेगा
        redirect_url = f"https://brandotpofficial.netlify.app/payment-status.html?orderid={order_id}"
        # -------------------------------------------

        # create_order फंक्शन को कॉल करें
        payment_resp = create_order(
            customer_mobile=user_mobile,
            amount=order.amount,
            order_id=order_id, # सुनिश्चित करें कि आपका create_order फंक्शन order_id लेता है
            redirect_url=redirect_url,
            remark1=user_id, # remark1 में यूजर आईडी भेजना एक अच्छा अभ्यास है
            remark2="WalletTopup"
        )
        
        # Pay0 से मिले पेमेंट लिंक को निकालें
        pay0_link = None
        if isinstance(payment_resp, dict):
            pay0_link = (
                payment_resp.get("result", {}).get("paymenturl") or
                payment_resp.get("result", {}).get("payment_url") or
                payment_resp.get("paymenturl") or
                payment_resp.get("payment_url")
            )

        if not pay0_link or not isinstance(pay0_link, str):
            raise Exception("paymenturl missing or invalid in Pay0 API response")

        return {
            "success": True,
            "order_id": order_id,
            "amount": order.amount,
            "payment_url": pay0_link,
            "message": "Order created successfully. Redirecting to payment page."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

