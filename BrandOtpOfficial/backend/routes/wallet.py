# backend/routes/pay0_webhook.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from bson import ObjectId

# Import dependencies from your project
from backend.db import get_db, users_collection, wallets_collection  # Use wallets_collection for consistency
from backend.routes.wallet import credit_user_wallet # Re-use the logic from wallet.py

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
        # Step 1: Parse form data correctly from the request body
        form_data = await request.form()
        
        # Log all received data for debugging
        logger.info(f"Webhook Data Received: {dict(form_data)}")

        status = form_data.get("status")
        order_id = form_data.get("order_id")
        amount_str = form_data.get("amount")
        
        # The user_id is passed in 'remark1' when creating the order
        user_id_str = form_data.get("remark1") 

    except Exception as e:
        logger.error(f"Error parsing webhook form data: {e}")
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid form data"})

    # Step 2: Check if essential data is present
    if not all([status, order_id, amount_str, user_id_str]):
        logger.warning(f"Webhook missing essential data. Received: status={status}, order_id={order_id}, amount={amount_str}, user_id={user_id_str}")
        return JSONResponse(status_code=400, content={"success": False, "message": "Missing essential data in webhook."})

    # Step 3: Process based on payment status
    if status.upper() == "SUCCESS":
        try:
            payment_amount = float(amount_str)
            
            # Check if this transaction has already been processed to prevent double-crediting
            existing_transaction = wallets_collection.find_one({"order_id": order_id})
            if existing_transaction:
                logger.warning(f"Duplicate webhook call for order_id: {order_id}. Ignoring.")
                return JSONResponse(status_code=200, content={"success": True, "message": "Duplicate webhook. Already processed."})

            # Credit the user's wallet using the function from wallet.py
            # This centralizes the wallet logic
            credit_result = credit_user_wallet(
                user_id=user_id_str, 
                amount=payment_amount, 
                reason=f"Add Money - Pay0 (Order: {order_id})"
            )

            if credit_result.get("success"):
                # Additionally, save the order_id in the transaction log for tracking
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
        # Here you could potentially log the failed transaction if needed
        return JSONResponse(status_code=200, content={"success": True, "message": f"Payment {status.lower()} acknowledged."})

    else:
        logger.warning(f"Received unhandled status: {status} for order_id: {order_id}")
        return JSONResponse(status_code=200, content={"success": True, "message": "Unhandled status."})


@router.get("/webhook")
def webhook_test_get():
    """A simple GET endpoint to confirm the webhook URL is reachable."""
    return {"message": "Webhook endpoint is active. Use POST for actual data."}
