"""
FastAPI Pay0 Webhook Handler
Converted from Flask to FastAPI
Handles payment success notifications from Pay0
"""

from fastapi import APIRouter, Request, HTTPException, Form
from typing import Optional
import json
from datetime import datetime

# Database imports (adjust based on your setup)
from database import users_collection, transactions_collection

router = APIRouter()

@router.post("/webhook")
async def pay0_webhook(
    request: Request,
    status: Optional[str] = Form(None),
    order_id: Optional[str] = Form(None),
    remark1: Optional[str] = Form(None),
    remark2: Optional[str] = Form(None),
    amount: Optional[str] = Form(None),
    customer_mobile: Optional[str] = Form(None),
    user_token: Optional[str] = Form(None)
):
    """
    Pay0 Webhook Endpoint
    Receives payment status updates from Pay0 gateway
    
    Expected Form Data:
    - status: SUCCESS/FAILED
    - order_id: Order ID
    - remark1: Custom data 1
    - remark2: Custom data 2
    - amount: Payment amount
    - customer_mobile: Customer phone
    """
    
    try:
        # Log incoming webhook
        print("=" * 60)
        print("🔔 PAY0 WEBHOOK RECEIVED")
        print("=" * 60)
        print(f"Status: {status}")
        print(f"Order ID: {order_id}")
        print(f"Amount: {amount}")
        print(f"Mobile: {customer_mobile}")
        print(f"Remark1: {remark1}")
        print(f"Remark2: {remark2}")
        print("=" * 60)
        
        # Check if payment successful
        if status == "SUCCESS":
            print(f"✅ Payment SUCCESS for order {order_id}")
            
            # Convert amount to float
            payment_amount = float(amount) if amount else 0.0
            
            # Find user by mobile number or remark1 (user_id stored there)
            user_id = remark1  # Assuming you stored user_id in remark1
            
            if user_id:
                # Find user in database
                user = await users_collection.find_one({"_id": user_id})
                
                if user:
                    # Update user balance
                    current_balance = float(user.get("balance", 0))
                    new_balance = current_balance + payment_amount
                    
                    await users_collection.update_one(
                        {"_id": user_id},
                        {"$set": {"balance": new_balance}}
                    )
                    
                    print(f"✅ Balance updated: {current_balance} → {new_balance}")
                    
                    # Create transaction record
                    transaction = {
                        "user_id": user_id,
                        "type": "credit",
                        "amount": payment_amount,
                        "reason": f"Add Money - Pay0 (Order: {order_id})",
                        "order_id": order_id,
                        "status": "completed",
                        "payment_method": "Pay0",
                        "created_at": datetime.utcnow()
                    }
                    
                    await transactions_collection.insert_one(transaction)
                    print(f"✅ Transaction recorded: {order_id}")
                    
                    return {"message": "Webhook received successfully", "status": "success"}
                else:
                    print(f"⚠️ User not found: {user_id}")
                    return {"message": "User not found", "status": "error"}
            else:
                print(f"⚠️ No user ID in webhook data")
                return {"message": "User ID missing", "status": "error"}
        
        else:
            # Payment failed or pending
            print(f"❌ Payment status: {status}")
            return {"error": f"Invalid status: {status}"}, 400
    
    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return 200 OK to prevent Pay0 from retrying
        return {"message": "Webhook received with error", "error": str(e)}


# Optional: GET endpoint for testing
@router.get("/webhook")
async def webhook_test():
    """
    Test endpoint - Pay0 sometimes sends GET request to verify webhook URL
    """
    return {
        "message": "Webhook endpoint is active",
        "status": "ready",
        "method": "POST required for actual webhooks"
    }
