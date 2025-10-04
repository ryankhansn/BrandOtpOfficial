from fastapi import APIRouter, Request, Form
from typing import Optional
from database import users_collection, transactions_collection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
def pay0_webhook(
    request: Request,
    status: Optional[str] = Form(None),
    order_id: Optional[str] = Form(None),
    remark1: Optional[str] = Form(None),
    remark2: Optional[str] = Form(None),
    amount: Optional[str] = Form(None),
    customer_mobile: Optional[str] = Form(None),
    user_token: Optional[str] = Form(None)
):
    try:
        logger.info("🔔 PAY0 WEBHOOK RECEIVED")
        if status and status.upper() == "SUCCESS":
            payment_amount = float(amount) if amount else 0.0
            user_id = remark1
            if user_id and users_collection:
                user = users_collection.find_one({"_id": user_id})
                if user:
                    current_balance = float(user.get("balance", 0))
                    new_balance = current_balance + payment_amount
                    users_collection.update_one({"_id": user_id}, {"$set": {"balance": new_balance}})
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
                        transactions_collection.insert_one(transaction)
                    return {"success": True, "message": "Webhook received successfully", "order_id": order_id, "amount": payment_amount, "new_balance": new_balance}
                else:
                    return {"success": False, "message": "User not found", "order_id": order_id}
            else:
                return {"success": False, "message": "User ID missing or database unavailable", "order_id": order_id}
        elif status and status.upper() in ["FAILED", "CANCELLED"]:
            return {"success": False, "message": f"Payment {status}", "order_id": order_id}
        else:
            return {"success": False, "message": f"Invalid status: {status}", "order_id": order_id}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"success": False, "message": "Webhook received with error", "error": str(e)}

@router.get("/webhook")
def webhook_test():
    return {"success": True, "message": "Webhook endpoint active", "method": "POST required for actual webhooks"}
