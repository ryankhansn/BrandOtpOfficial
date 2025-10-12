from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
import time

from backend.db import users_collection, payments_collection

router = APIRouter()

@router.post("/webhook")
async def pay0_webhook(request: Request):
    """
    Pay0 webhook handler
    """
    try:
        data = await request.form()
        status = data.get("status")
        order_id = data.get("order_id")
        user_id_str = data.get("remark1")  # User ID as string
        amount = float(data.get("amount", 0))
        
        print(f"📩 Webhook received: Order {order_id}, Status {status}")
        
        if status != "SUCCESS":
            return JSONResponse(content={"success": False, "message": "Status not SUCCESS"})
        
        # ✅ FIX: Validate and convert user_id to ObjectId
        try:
            # Check if it's already a valid ObjectId hex string (24 chars)
            if len(user_id_str) == 24:
                user_object_id = ObjectId(user_id_str)
            else:
                # If not valid ObjectId, find user by other means or skip
                print(f"⚠️ Invalid ObjectId format: {user_id_str}")
                # For now, use the string as-is and update by string ID
                user_object_id = user_id_str
        except Exception as e:
            print(f"❌ ObjectId conversion error: {e}")
            user_object_id = user_id_str
        
        # Check if already processed
        existing_payment = payments_collection.find_one({"order_id": order_id})
        if existing_payment and existing_payment.get("status") == "SUCCESS":
            print(f"⚠️ Already processed: {order_id}")
            return JSONResponse(content={"success": True, "message": "Already processed"})
        
        # Update user wallet
        try:
            if isinstance(user_object_id, ObjectId):
                update_result = users_collection.update_one(
                    {"_id": user_object_id},
                    {"$inc": {"balance": amount}}
                )
            else:
                # Fallback: try updating by string ID field
                update_result = users_collection.update_one(
                    {"user_id": user_object_id},
                    {"$inc": {"balance": amount}}
                )
            
            print(f"✅ Wallet update result: {update_result.modified_count} document(s) updated")
        except Exception as e:
            print(f"❌ Wallet update error: {e}")
        
        # Save payment record
        payment_data = {
            "order_id": order_id,
            "user_id": user_id_str,  # Store as string
            "amount": amount,
            "status": "SUCCESS",
            "type": "credit",
            "reason": "Wallet Top-up via Pay0 Webhook",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        if existing_payment:
            payments_collection.update_one(
                {"order_id": order_id},
                {"$set": payment_data}
            )
        else:
            payments_collection.insert_one(payment_data)
        
        print(f"✅ [WEBHOOK] Wallet updated: User {user_id_str}, Amount +₹{amount}")
        
        return JSONResponse(content={"success": True, "message": "Wallet updated"})
        
    except Exception as e:
        print(f"❌ [WEBHOOK] Error: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
