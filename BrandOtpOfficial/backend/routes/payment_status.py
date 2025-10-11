from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
import time

from backend.db import users_collection, payments_collection
from backend.utils.auth_utils import get_current_user
from backend.utils.order_status_sdk import OrderStatusSDK
from backend.config import config

router = APIRouter()

@router.get("/check-status")
async def check_payment_status(
    order_id: str = Query(..., description="Order ID to check"),
    current_user: dict = Depends(get_current_user)
):
    """
    Check payment status from Pay0 and update user wallet if successful.
    This is called from payment-status.html page.
    """
    try:
        user_id = current_user.get("id")
        
        # 1. Check if payment already processed
        existing_payment = payments_collection.find_one({"order_id": order_id})
        
        if existing_payment and existing_payment.get("status") == "SUCCESS":
            return {
                "success": True,
                "status": "SUCCESS",
                "message": "Payment already verified and wallet updated",
                "already_processed": True
            }
        
        # 2. Check status with Pay0 API
        status_sdk = OrderStatusSDK()
        pay0_response = status_sdk.check_order_status(
            user_token=config.PAY0_USER_TOKEN,
            order_id=order_id
        )
        
        if not pay0_response or not pay0_response.get("status"):
            return {
                "success": False,
                "status": "PENDING",
                "message": "Payment is still pending. Please wait 10-20 minutes.",
                "pay0_response": pay0_response
            }
        
        # 3. Extract status from Pay0 response
        result = pay0_response.get("result", {})
        txn_status = result.get("txnStatus", "PENDING")
        
        if txn_status == "SUCCESS":
            # 4. Update user wallet
            amount = float(result.get("amount", 0))
            
            # Update user balance in MongoDB
            update_result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"balance": amount}}
            )
            
            # 5. Save/Update payment record
            payment_data = {
                "order_id": order_id,
                "user_id": user_id,
                "amount": amount,
                "status": "SUCCESS",
                "txn_status": txn_status,
                "utr": result.get("utr", ""),
                "date": result.get("date", ""),
                "updated_at": time.time(),
                "type": "credit",
                "reason": "Wallet Top-up via Pay0"
            }
            
            if existing_payment:
                payments_collection.update_one(
                    {"order_id": order_id},
                    {"$set": payment_data}
                )
            else:
                payment_data["created_at"] = time.time()
                payments_collection.insert_one(payment_data)
            
            print(f"✅ Wallet updated: User {user_id}, Amount +₹{amount}, Order {order_id}")
            
            return {
                "success": True,
                "status": "SUCCESS",
                "message": f"Payment successful! ₹{amount} added to your wallet.",
                "amount": amount,
                "utr": result.get("utr", "")
            }
        
        elif txn_status == "PENDING":
            return {
                "success": False,
                "status": "PENDING",
                "message": "Payment is still pending. Please wait 10-20 minutes and refresh."
            }
        
        else:  # FAILED
            # Save failed payment record
            if existing_payment:
                payments_collection.update_one(
                    {"order_id": order_id},
                    {"$set": {"status": "FAILED", "updated_at": time.time()}}
                )
            
            return {
                "success": False,
                "status": "FAILED",
                "message": "Payment failed. Please try again or contact support."
            }
        
    except Exception as e:
        print(f"❌ Payment status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking payment status: {str(e)}")
