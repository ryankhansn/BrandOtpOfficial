# backend/utils/pay0_client.py
import os
import requests
import uuid
import typing as t

BASE_URL = "https://pay0.shop/api"
USER_TOKEN = os.getenv("PAY0_USER_TOKEN")  # Make sure this is set in .env

def _post(endpoint: str, data: dict) -> dict:
    """Helper function to make POST requests to Pay0 API"""
    try:
        resp = requests.post(
            f"{BASE_URL}{endpoint}",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        return resp.json() if resp.content else {"status": False, "message": "Empty response"}
    except Exception as e:
        return {"status": False, "message": str(e)}

def create_order(mobile: str, amount: float, redirect: str,
                 remark1: str = "", remark2: str = "") -> dict:
    """
    Create Pay0 order with 5 parameters:
    - mobile: Customer mobile number
    - amount: Payment amount
    - redirect: Redirect URL after payment
    - remark1: Optional remark (e.g., user_id)
    - remark2: Optional remark (e.g., payment type)
    """
    payload = {
        "customer_mobile": mobile,
        "customer_name": "BrandOtp User",
        "user_token": USER_TOKEN,
        "amount": f"{amount:.2f}",
        "order_id": f"ORD_{uuid.uuid4().hex[:12]}",
        "redirect_url": redirect,
        "remark1": remark1,
        "remark2": remark2
    }
    return _post("/create-order", payload)

def check_status(order_id: str) -> dict:
    """Check Pay0 order status"""
    return _post("/check-order-status",
                 {"user_token": USER_TOKEN, "order_id": order_id})
