from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter()

@router.post("/webhook")
async def pay0_webhook(request: Request):
    """
    This is a backup webhook called by Pay0.
    It updates the user's balance if the main verification fails for some reason.
    """
    try:
        data = await request.form()
        status = data.get("status")
        order_id = data.get("order_id")
        user_id = data.get("remark1")

        if status != "SUCCESS":
            return JSONResponse(content={"success": False, "message": "Status is not SUCCESS"}, status_code=400)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # सुरक्षा जाँच: क्या यह ऑर्डर पहले ही प्रोसेस हो चुका है?
        cursor.execute("SELECT status FROM wallet_transactions WHERE transaction_id = ?", (order_id,))
        transaction = cursor.fetchone()
        if transaction and transaction[0] == 'completed':
            conn.close()
            return JSONResponse(content={"success": True, "message": "Already processed"})

        # ट्रांजैक्शन की रकम निकालें
        cursor.execute("SELECT amount FROM wallet_transactions WHERE transaction_id = ?", (order_id,))
        amount_result = cursor.fetchone()
        if not amount_result:
            raise Exception("Transaction amount not found.")
        
        amount_to_add = amount_result[0]

        # यूजर का बैलेंस अपडेट करें
        cursor.execute("UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE id = ?", (amount_to_add, user_id))
        # ट्रांजैक्शन को 'completed' मार्क करें
        cursor.execute("UPDATE wallet_transactions SET status = 'completed' WHERE transaction_id = ?", (order_id,))
        
        conn.commit()
        conn.close()

        print(f"✅ [WEBHOOK] Balance updated for user {user_id} for order {order_id}")
        return JSONResponse(content={"success": True})

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        print(f"❌ [WEBHOOK] Error: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
