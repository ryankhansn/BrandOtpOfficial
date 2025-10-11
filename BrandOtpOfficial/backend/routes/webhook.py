from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
import time

from backend.db import users_collection, payments_collection

router = APIRouter()

@router.post("/webhook")
async def pay0_webhook(request: Request):
    """
    Optional webhook handler for Pay0.
    This is backup - main flow uses manual status check.
    """
    try:
        data = await request.form()
        status = data.get("status")
        order_id = data.get("order_id")
        user_id = data.get("remark1")  # We passed user_id in remark1
        amount = float(data.get("amount", 0))
        
        print(f"📩 Webhook received: Order {order_id}, Status {status}")
        
        if status != "SUCCESS":
            return JSONResponse(content={"success": False, "message": "Status not SUCCESS"})
        
        # Check if already processed
        existing_payment = payments_collection.find_one({"order_id": order_id})
        if existing_payment and existing_payment.get("status") == "SUCCESS":
            return JSONResponse(content={"success": True, "message": "Already processed"})
        
        # Update user wallet
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"balance": amount}}
        )
        
        # Save payment record
        payment_data = {
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
            "status": "SUCCESS",
            "type": "credit",
            "reason": "Wallet Top-up via Pay0 Webhook",
            "updated_at": time.time()
        }
        
        if existing_payment:
            payments_collection.update_one(
                {"order_id": order_id},
                {"$set": payment_data}
            )
        else:
            payment_data["created_at"] = time.time()
            payments_collection.insert_one(payment_data)
        
        print(f"✅ [WEBHOOK] Wallet updated: User {user_id}, Amount +₹{amount}")
        
        return JSONResponse(content={"success": True, "message": "Wallet updated"})
        
    except Exception as e:
        print(f"❌ [WEBHOOK] Error: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
