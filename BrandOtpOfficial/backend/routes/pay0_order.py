import os
import httpx

PAY0_API_URL = "https://pay0.shop/api/create-order"
PAY0_USER_TOKEN = os.getenv("PAY0_USER_TOKEN")  # apni env me rakho

async def create_pay0_order_request(mobile, name, amount, order_id, redirect_url):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "customermobile": mobile,
        "customername": name,
        "usertoken": PAY0_USER_TOKEN,
        "amount": amount,
        "orderid": order_id,
        "redirecturl": redirect_url,
        "remark1": "Wallet Topup",
        "remark2": ""
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(PAY0_API_URL, data=data, headers=headers)
        result = resp.json()
        if not result.get("status"):
            raise Exception(f"Pay0 error: {result.get('message')}")
        return result["result"]["paymenturl"]  # payment page URL

# FastAPI route me use karo:
@router.post("/create-order")
async def create_pay0_order(order: OrderBody):
    try:
        payment_url = await create_pay0_order_request(
            order.mobile,
            "User",  # yahan name chaho to user se lo
            order.amount,
            f"ORD_{order.mobile}_{int(order.amount)}",
            "https://yourdomain.com/payment-success"
        )
        return {
            "success": True,
            "order_id": f"ORD_{order.mobile}_{int(order.amount)}",
            "amount": order.amount,
            "mobile": order.mobile,
            "payment_url": payment_url,
            "message": "Order created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
