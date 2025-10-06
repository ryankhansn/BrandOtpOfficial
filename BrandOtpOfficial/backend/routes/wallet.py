# backend/routes/wallet.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Dict, Any
import logging
from bson import ObjectId

# Import dependencies
from backend.db import get_db, users_collection, wallets_collection
from backend.utils.auth_utils import get_current_user

# --- ✅ STEP 1: IMPORT FROM THE NEW UTILS FILE ---
from backend.utils.wallet_utils import credit_user_wallet, debit_user_wallet
# ------------------------------------------------

# ✅ CREATE ROUTER INSTANCE
router = APIRouter()

# --- ✅ STEP 2: The local credit_user_wallet and debit_user_wallet functions have been REMOVED from this file. ---


# ✅ ROUTE HANDLERS
@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user)):
    """Get user wallet balance"""
    try:
        if "balance" not in current_user or current_user["balance"] is None:
            users_collection.update_one(
                {"_id": ObjectId(current_user["id"])},
                {"$set": {"balance": 0.0}}
            )
            current_user["balance"] = 0.0
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "balance": float(current_user.get("balance", 0.0)),
                "user": {
                    "username": current_user.get("username", "User"),
                    "email": current_user.get("email", "")
                }
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": f"Failed to get balance: {str(e)}"})

@router.post("/add-money")
async def add_money(
    request: Request,
    current_user: dict = Depends(get_current_user),
    amount: float = Form(...),
    payment_method: str = Form("manual"),
):
    """Add money to user wallet (manual/admin usage)"""
    try:
        if amount <= 0:
            return JSONResponse(status_code=400, content={"success": False, "detail": "Amount must be positive."})
            
        # --- ✅ STEP 3: THIS NOW USES THE IMPORTED FUNCTION ---
        result = credit_user_wallet(
            user_id=current_user["id"],
            amount=amount,
            reason=f"Money added via {payment_method}"
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"₹{amount} added successfully to your wallet",
                    "balance": result["new_balance"]
                }
            )
        else:
            return JSONResponse(status_code=500, content={"success": False, "detail": result.get("error", "Failed to add money")})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": f"Failed to add money: {str(e)}"})

@router.get("/transactions")
async def get_transactions(
    current_user: dict = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0
):
    """Get user wallet transactions"""
    try:
        transactions = list(
            wallets_collection
            .find({"user_id": current_user["id"]})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
            if "created_at" in transaction:
                transaction["created_at"] = transaction["created_at"].isoformat()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "transactions": transactions,
                "current_balance": float(current_user.get("balance", 0.0))
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": f"Failed to get transactions: {str(e)}"})

