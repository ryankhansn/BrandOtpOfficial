# backend/routes/pay0_webhook.py

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from bson import ObjectId

# Import dependencies from your project
from backend.db import wallets_collection

# --- ✅ STEP 1: CHANGE THIS IMPORT ---
# Import from the new utils file to prevent circular dependency
from backend.utils.wallet_utils import credit_user_wallet 
# ------------------------------------

# Setup logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
async def pay0_webhook(request: Request):
    """
    Handles incoming webhooks from Pay0 to process payment status.
    """
    logger.info("🔔 PAY0 WEBHOOK RECEIVED")
    
    try:
        form_data = await request.form()
        logger.info(f"Webhook Data Received: {dict(form_data)}")

        status = form_data.get("status")
        order_id = form_data.get("order_id")
        amount_str = form_data.get("amount")
        user_id_str = form_data.get("remark1") # User ID passed during order creation

    except Exception as e:
        logger.error(f"Error parsing webhook form data: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid form data"})

    if not all([status, order_id, amount_str, user_id_str]):
        logger.warning(f"Webhook missing essential data. Received: status={status}, order_id={order_id}, amount={amount_str}, user_id={user_id_str}")
        return JSONResponse(status_code=400, content={"success": False, "message": "Missing essential data in webhook."})

    if status.upper() == "SUCCESS":
        try:
            payment_amount = float(amount_str)
            
            existing_transaction = wallets_collection.find_one({"order_id": order_id})
            if existing_transaction:
                logger.warning(f"Duplicate webhook call for order_id: {order_id}. Ignoring.")
                return JSONResponse(status_code=200, content={"success": True, "message": "Duplicate webhook. Already processed."})

            # --- ✅ STEP 2: THIS NOW USES THE CORRECTLY IMPORTED FUNCTION ---
            credit_result = credit_user_wallet(
                user_id=user_id_str, 
                amount=payment_amount, 
                reason=f"Add Money - Pay0 (Order: {order_id})"
            )

            if credit_result.get("success"):
                wallets_collection.update_one(
                    {"_id": ObjectId(credit_result["transaction_id"])},
                    {"$set": {"order_id": order_id}}
                )
                logger.info(f"✅ Successfully processed webhook for order {order_id}. User {user_id_str} credited with {payment_amount}.")
                return JSONResponse(status_code=200, content={"success": True, "message": "Webhook processed successfully."})
            else:
                logger.error(f"Failed to credit wallet for user {user_id_str}. Reason: {credit_result.get('error')}")
                return JSONResponse(status_code=500, content={"success": False, "message": "Wallet credit failed."})

        except ValueError:
            logger.error(f"Invalid amount format in webhook: {amount_str}")
            return JSONResponse(status_code=400, content={"success": False, "message": "Invalid amount format."})
        except Exception as e:
            logger.error(f"Webhook SUCCESS processing error: {e}")
            return JSONResponse(status_code=500, content={"success": False, "message": "Internal server error."})

    elif status.upper() in ["FAILED", "CANCELLED"]:
        logger.info(f"Payment {status.lower()} for order_id: {order_id}.")
        return JSONResponse(status_code=200, content={"success": True, "message": f"Payment {status.lower()} acknowledged."})

    else:
        logger.warning(f"Received unhandled status: {status} for order_id: {order_id}")
        return JSONResponse(status_code=200, content={"success": True, "message": "Unhandled status."})


@router.get("/webhook")
def webhook_test_get():
    """A simple GET endpoint to confirm the webhook URL is reachable."""
    return {"message": "Webhook endpoint is active. Use POST for actual data."}
