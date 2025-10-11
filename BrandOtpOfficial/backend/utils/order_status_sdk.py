import requests

class OrderStatusSDK:
    def __init__(self, base_url="https://pay0.shop"):
        self.base_url = base_url
    
    def check_order_status(self, user_token, order_id):
        """Check order status from Pay0 API"""
        url = f"{self.base_url}/api/check-order-status"
        payload = {
            "user_token": user_token,
            "order_id": order_id
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Pay0 Status Response: {data}")
                return data
            else:
                return {"status": False, "message": "API request failed"}
        except Exception as e:
            print(f"❌ Order status check error: {e}")
            return {"status": False, "message": str(e)}
