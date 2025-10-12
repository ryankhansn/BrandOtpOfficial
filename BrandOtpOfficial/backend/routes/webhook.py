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
        user_id_str = data.get("remark1")  # User ID from Pay0
        amount_str = data.get("amount", "0")  # ✅ Get amount from webhook
        
        print(f"📩 Webhook received: Order {order_id}, Status {status}")
        print(f"📋 Raw webhook data: status={status}, order_id={order_id}, user_id={user_id_str}, amount={amount_str}")
        
        # ✅ FIX 1: Handle manual status update (no remark1)
        if not user_id_str or user_id_str == "Manually Status Changed":
            print(f"⚠️ Manual update detected. Fetching user from payment record...")
            
            # Try to find existing payment record
            existing_payment = payments_collection.find_one({"order_id": order_id})
            if existing_payment and existing_payment.get("user_id"):
                user_id_str = existing_payment.get("user_id")
                print(f"✅ Found user_id from payment record: {user_id_str}")
            else:
                print(f"❌ No user_id found for order {order_id}")
                return JSONResponse(content={"success": False, "message": "User ID not found"})
        
        # ✅ FIX 2: Parse amount properly
        try:
            amount = float(amount_str)
            print(f"💰 Amount parsed: ₹{amount}")
        except (ValueError, TypeError):
            print(f"❌ Invalid amount: {amount_str}")
            return JSONResponse(content={"success": False, "message": "Invalid amount"})
        
        if status != "SUCCESS":
            print(f"⚠️ Status not SUCCESS: {status}")
            return JSONResponse(content={"success": False, "message": "Status not SUCCESS"})
        
        # Check if already processed
        existing_payment = payments_collection.find_one({"order_id": order_id})
        if existing_payment and existing_payment.get("status") == "SUCCESS":
            print(f"⚠️ Already processed: {order_id}")
            return JSONResponse(content={"success": True, "message": "Already processed"})
        
        # ✅ FIX 3: Validate and convert user_id to ObjectId
        try:
            if len(user_id_str) == 24:
                user_object_id = ObjectId(user_id_str)
                print(f"✅ Valid ObjectId: {user_object_id}")
            else:
                print(f"⚠️ Invalid ObjectId format: {user_id_str}")
                user_object_id = user_id_str  # Use as string
        except Exception as e:
            print(f"❌ ObjectId conversion error: {e}")
            user_object_id = user_id_str
        
        # ✅ FIX 4: Update user wallet in MongoDB
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
            
            if update_result.modified_count == 0:
                print(f"⚠️ No document updated! User might not exist: {user_id_str}")
        except Exception as e:
            print(f"❌ Wallet update error: {e}")
        
        # ✅ FIX 5: Save/update payment record
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
            print(f"✅ Payment record updated")
        else:
            payments_collection.insert_one(payment_data)
            print(f"✅ Payment record created")
        
        print(f"✅ [WEBHOOK] Wallet updated: User {user_id_str}, Amount +₹{amount}")
        
        return JSONResponse(content={"success": True, "message": "Wallet updated successfully"})
        
    except Exception as e:
        print(f"❌ [WEBHOOK] Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
