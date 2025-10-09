from fastapi import APIRouter, Depends, HTTPException
import sqlite3
import time

# अपने प्रोजेक्ट के सही लोकेशन से इम्पोर्ट करें
from backend.utils.auth_utils import get_current_user
from backend.utils.order_status_sdk import OrderStatusSDK
from backend.config import config

router = APIRouter()

@router.get("/verify-payment/{order_id}")
async def verify_payment_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Checks the payment status with Pay0 and updates the user's balance if successful.
    """
    try:
        user_id = current_user.get("id")

        # 1. सुरक्षा जाँच: क्या यह ऑर्डर पहले ही प्रोसेस हो चुका है?
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM wallet_transactions WHERE transaction_id = ?", (order_id,))
        transaction = cursor.fetchone()

        if transaction and transaction[0] == 'completed':
            conn.close()
            return {"success": True, "message": "Payment already verified."}

        # 2. Pay0 से असली स्टेटस पता करें
        status_sdk = OrderStatusSDK()
        status_response = status_sdk.check_order_status(
            user_token=config.PAY0_USER_TOKEN,
            order_id=order_id
        )

        if not status_response or status_response.get("status") != "SUCCESS":
            conn.close()
            raise HTTPException(status_code=400, detail="Payment not successful or is still pending.")

        # 3. अगर पेमेंट सफल है, तो बैलेंस अपडेट करें
        amount_to_add = float(status_response.get("amount", 0))

        # यूजर का बैलेंस बढ़ाएँ
        cursor.execute("UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE id = ?", (amount_to_add, user_id))

        # ट्रांजैक्शन को 'completed' मार्क करें
        cursor.execute("UPDATE wallet_transactions SET status = 'completed' WHERE transaction_id = ?", (order_id,))
        
        conn.commit()
        conn.close()

        print(f"✅ Balance updated for user {user_id} by {amount_to_add} for order {order_id}")
        return {"success": True, "message": "Payment verified and wallet has been updated!"}

    except Exception as e:
        print(f"❌ Error verifying payment: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
