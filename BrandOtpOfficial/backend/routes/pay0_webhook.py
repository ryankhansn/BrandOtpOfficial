"""
FastAPI Pay0 Webhook Handler
Handles payment success notifications from Pay0 gateway
SYNC VERSION - Compatible with PyMongo
"""

from fastapi import APIRouter, Request, Form
from typing import Optional
import json
from datetime import datetime
import logging

# ===== FIX: Add parent directory to Python path =====
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Now database import will work
from database import users_collection, transactions_collection

# Setup logger
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook")
def pay0_webhook(  # REMOVED async
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
    Pay0 Webhook Endpoint (SYNC)
    Receives payment status updates from Pay0 gateway
    
    Expected Form Data:
    - status: SUCCESS/FAILED
    - order_id: Order ID
    - remark1: User ID (stored during order creation)
    - remark2: Custom data
    - amount: Payment amount
    - customer_mobile: Customer phone number
    """
    
    try:
        # Log incoming webhook
        logger.info("=" * 60)
        logger.info("🔔 PAY0 WEBHOOK RECEIVED")
        logger.info("=" * 60)
        logger.info(f"📊 Status: {status}")
        logger.info(f"📊 Order ID: {order_id}")
        logger.info(f"📊 Amount: {amount}")
        logger.info(f"📊 Mobile: {customer_mobile}")
        logger.info(f"📊 Remark1 (User ID): {remark1}")
        logger.info(f"📊 Remark2: {remark2}")
        logger.info("=" * 60)
        
        # Check if payment successful
        if status and status.upper() == "SUCCESS":
            logger.info(f"✅ Payment SUCCESS for order {order_id}")
            
            # Convert amount to float
            payment_amount = float(amount) if amount else 0.0
            
            # Get user ID from remark1 (stored during order creation)
            user_id = remark1
            
            if user_id and users_collection:
                # Find user in database (REMOVED await)
                user = users_collection.find_one({"_id": user_id})
                
                if user:
                    # Update user balance
                    current_balance = float(user.get("balance", 0))
                    new_balance = current_balance + payment_amount
                    
                    # REMOVED await
                    users_collection.update_one(
                        {"_id": user_id},
                        {"$set": {"balance": new_balance}}
                    )
                    
                    logger.info(f"✅ Balance updated: ₹{current_balance} → ₹{new_balance}")
                    
                    # Create transaction record
                    transaction = {
                        "user_id": user_id,
                        "type": "credit",
                        "amount": payment_amount,
                        "reason": f"Add Money - Pay0 (Order: {order_id})",
                        "order_id": order_id,
                        "transaction_id": order_id,
                        "status": "completed",
                        "payment_method": "Pay0",
                        "created_at": datetime.utcnow()
                    }
                    
                    if transactions_collection:
                        # REMOVED await
                        transactions_collection.insert_one(transaction)
                        logger.info(f"✅ Transaction recorded: {order_id}")
                    
                    return {
                        "success": True,
                        "message": "Webhook received successfully",
                        "order_id": order_id,
                        "amount": payment_amount,
                        "new_balance": new_balance
                    }
                else:
                    logger.warning(f"⚠️ User not found: {user_id}")
                    return {
                        "success": False,
                        "message": "User not found",
                        "order_id": order_id
                    }
            else:
                logger.warning(f"⚠️ No user ID in webhook data or database unavailable")
                return {
                    "success": False,
                    "message": "User ID missing or database unavailable",
                    "order_id": order_id
                }
        
        elif status and status.upper() in ["FAILED", "CANCELLED"]:
            logger.error(f"❌ Payment FAILED/CANCELLED: {status}")
            return {
                "success": False,
                "message": f"Payment {status}",
                "order_id": order_id
            }
        
        else:
            logger.warning(f"⏳ Unknown payment status: {status}")
            return {
                "success": False,
                "message": f"Invalid status: {status}",
                "order_id": order_id
            }
    
    except Exception as e:
        logger.error(f"❌ WEBHOOK ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return 200 OK to prevent Pay0 from retrying
        return {
            "success": False,
            "message": "Webhook received with error",
            "error": str(e)
        }


@router.get("/webhook")
def webhook_test():  # REMOVED async
    """
    Test endpoint - Pay0 sometimes sends GET request to verify webhook URL
    """
    logger.info("🔍 Webhook test endpoint accessed")
    return {
        "success": True,
        "message": "Webhook endpoint is active",
        "status": "ready",
        "method": "POST required for actual webhooks",
        "endpoint": "/api/payments/pay0/webhook"
    }
