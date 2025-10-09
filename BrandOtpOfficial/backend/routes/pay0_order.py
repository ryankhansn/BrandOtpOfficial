from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import time

# अपने प्रोजेक्ट के सही लोकेशन से इम्पोर्ट करें
from backend.utils.pay0_client import create_order
from backend.utils.auth_utils import get_current_user
from backend.config import config  # मान लिया कि आपकी Pay0 सेटिंग्स यहाँ हैं

router = APIRouter()

# ✅ Pydantic मॉडल को अपडेट किया गया
class OrderBody(BaseModel):
    amount: float = Field(gt=49, lt=5001, description="Amount must be between 50 and 5000")
    customer_mobile: str # फ्रंटएंड से मोबाइल नंबर यहाँ आएगा

@router.post("/create-order")
async def create_pay0_order(order: OrderBody, current_user: dict = Depends(get_current_user)):
    """
    Creates a Pay0 order with a dynamic redirect URL containing the order_id.
    """
    try:
        user_id = current_user.get("id")
        timestamp = int(time.time())
        order_id = f"BRANDOTP_{user_id[:4]}_{timestamp}"

        # अपने Netlify/Render URL का उपयोग करें
        redirect_url = f"https://brandotpofficial.onrender.com/payment-status.html?orderid={order_id}"

        # ✅ create_order फंक्शन को फ्रंटएंड से मिले मोबाइल नंबर के साथ कॉल करें
        payment_resp = create_order(
            customer_mobile=order.customer_mobile, # पेलोड से लिया गया
            user_token=settings.PAY0_USER_TOKEN, # आपकी config/settings से
            amount=order.amount,
            order_id=order_id,
            redirect_url=redirect_url,
            remark1=user_id,
            remark2="WalletTopup"
        )
        
        # Pay0 से मिले पेमेंट लिंक को निकालें
        pay0_link = payment_resp.get("payment_url")
        if not pay0_link:
             raise Exception("payment_url missing in Pay0 API response")

        return {
            "success": True,
            "order_id": order_id,
            "payment_url": pay0_link,
            "message": "Order created successfully."
        }
    except Exception as e:
        print(f"Error creating order: {e}") # लॉगिंग के लिए
        raise HTTPException(status_code=500, detail=str(e))


