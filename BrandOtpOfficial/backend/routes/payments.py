from fastapi import APIRouter
from .pay0_order import router as pay0_order_router
from .pay0_webhook import router as pay0_webhook_router

router = APIRouter()
router.include_router(pay0_order_router, prefix="/pay0", tags=["Pay0"])
router.include_router(pay0_webhook_router, prefix="/pay0", tags=["Pay0"])
# इस कोड को अपनी payments.py या pay0_order.py फाइल में जोड़ें

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import requests
import os
from dotenv import load_dotenv

# अपने प्रोजेक्ट के सही लोकेशन से इम्पोर्ट करें
from backend.utils.auth_utils import get_current_user
from backend.utils.wallet_utils import credit_user_wallet
from backend.db import wallets_collection, users_collection
from bson import ObjectId

# सुनिश्चित करें कि आपका राउटर पहले से बना हुआ है
# अगर यह payments.py है, तो यह लाइन पहले से होगी:
# router = APIRouter()
# अगर आप pay0_order.py में जोड़ रहे हैं, तो सुनिश्चित करें कि आप उसी के राउटर का उपयोग कर रहे हैं।

# .env फाइल से PAY0 की सीक्रेट key लोड करें (सुरक्षा के लिए)
load_dotenv()
PAY0_USER_TOKEN = os.getenv("PAY0_API_KEY") # यह आपकी Pay0 API Key है

@router.post("/check-status/{order_id}")
async def check_payment_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    फ्रंटएंड से ऑर्डर आईडी लेता है, Pay0 से स्टेटस की पुष्टि करता है, और वॉलेट अपडेट करता है।
    """
    try:
        # 1. जाँचें कि यह ट्रांजेक्शन पहले से सफल तो नहीं हो चुका
        existing_transaction = wallets_collection.find_one({
            "order_id": order_id,
            "status": "completed"
        })
        if existing_transaction:
            return JSONResponse(
                status_code=200, 
                content={"success": True, "message": "Payment already confirmed and wallet updated."}
            )

        # 2. Pay0 API से पेमेंट का स्टेटस पूछें
        pay0_url = "https://pay0.shop/api/check-order-status"
        payload = {
            "user_token": PAY0_USER_TOKEN, # अपनी Pay0 API Key का उपयोग करें
            "order_id": order_id
        }
        
        response = requests.post(pay0_url, data=payload)
        response.raise_for_status()  # HTTP एरर होने पर एक्सेप्शन उठाएगा

        data = response.json()

        # 3. स्टेटस के आधार पर एक्शन लें
        if data.get("status") == "SUCCESS":
            payment_amount = float(data.get("amount", 0.0))
            if payment_amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid payment amount received from gateway.")

            # 4. यूजर का वॉलेट क्रेडिट करें
            credit_result = credit_user_wallet(
                user_id=current_user["id"],
                amount=payment_amount,
                reason=f"Add Money - Pay0 (Order: {order_id})"
            )

            if credit_result.get("success"):
                # ट्रांजेक्शन में order_id को अपडेट करें ताकि दोबारा क्रेडिट न हो
                wallets_collection.update_one(
                    {"_id": ObjectId(credit_result["transaction_id"])},
                    {"$set": {"order_id": order_id}}
                )
                return JSONResponse(status_code=200, content={"success": True, "message": "Payment successful! Your wallet has been credited."})
            else:
                # अगर वॉलेट क्रेडिट फेल होता है
                raise HTTPException(status_code=500, detail=credit_result.get("error", "Failed to update wallet balance."))

        elif data.get("status") == "PENDING":
            return JSONResponse(status_code=202, content={"success": False, "detail": "Payment is still pending. Please wait."})
        
        else: # FAILED, CANCELLED, etc.
            return JSONResponse(status_code=400, content={"success": False, "detail": f"Payment status: {data.get('status', 'Failed')}"})

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to payment gateway: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

