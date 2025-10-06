# backend/utils/wallet_utils.py

from datetime import datetime
from bson import ObjectId
from backend.db import users_collection, wallets_collection
import logging

logger = logging.getLogger(__name__)

def credit_user_wallet(user_id: str, amount: float, reason: str = "Credit") -> dict:
    """
    Credits a specified amount to a user's wallet.
    This is a centralized utility function.
    """
    try:
        # Validate user_id format before querying
        if not ObjectId.is_valid(user_id):
            logger.error(f"Invalid ObjectId format for user_id: {user_id}")
            return {"success": False, "error": "Invalid user ID format"}

        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            logger.warning(f"Credit failed: User not found for ID {user_id}")
            return {"success": False, "error": "User not found"}
        
        current_balance = float(user.get("balance", 0.0))
        new_balance = current_balance + amount
        
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"balance": new_balance}}
        )
        
        if result.modified_count > 0:
            transaction = {
                "user_id": user_id,
                "type": "credit",
                "amount": amount,
                "previous_balance": current_balance,
                "new_balance": new_balance,
                "reason": reason,
                "status": "completed",
                "created_at": datetime.utcnow()
            }
            # Use wallets_collection consistently
            tx_result = wallets_collection.insert_one(transaction)
            
            logger.info(f"Successfully credited {amount} to user {user_id}. New balance: {new_balance}")
            return {
                "success": True,
                "new_balance": new_balance,
                "transaction_id": str(tx_result.inserted_id)
            }
        else:
            logger.warning(f"Failed to update balance for user {user_id}, though user was found.")
            return {"success": False, "error": "Failed to update balance"}
            
    except Exception as e:
        logger.error(f"Critical error in credit_user_wallet for user {user_id}: {e}")
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

def debit_user_wallet(user_id: str, amount: float, reason: str = "Debit") -> dict:
    # (The debit function remains the same, but it's good practice to keep it here)
    try:
        if not ObjectId.is_valid(user_id):
            return {"success": False, "error": "Invalid user ID format"}
            
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "error": "User not found"}
        
        current_balance = float(user.get("balance", 0.0))
        
        if current_balance < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        new_balance = current_balance - amount
        
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"balance": new_balance}}
        )
        
        # ... (rest of the debit logic)
        return {"success": True, "new_balance": new_balance}

    except Exception as e:
        return {"success": False, "error": str(e)}

