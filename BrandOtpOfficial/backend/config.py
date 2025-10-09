# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Pricing Configuration
    MARKUP_PERCENTAGE = float(os.getenv('MARKUP_PERCENTAGE', 1.70))
    
    # SMSMan Configuration  
    SMSMAN_API_KEY = os.getenv('SMSMAN_API_KEY')
    SMSMAN_BASE_URL = "https://api.smsman.com"
    
    # ✅ Pay0 Configuration - यह लाइन अब सही जगह पर है
    PAY0_USER_TOKEN = os.getenv('PAY0_USER_TOKEN')
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def get_user_price(smsman_price):
        """Convert SMSMan price to user price with markup"""
        return float(smsman_price) * Config.MARKUP_PERCENTAGE

# ✅ सबसे महत्वपूर्ण लाइन: क्लास का एक ऑब्जेक्ट बनाएँ
config = Config()
