# backend/routes/smsman_numbers.py - FIXED FOR ALL COUNTRIES
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import time
from bson import ObjectId

# Import SMSMan client functions
from backend.utils.smsman_client import (
    get_services, 
    get_services_by_country,  # ✅ NEW IMPORT
    get_countries, 
    get_service_price, 
    buy_number as smsman_buy_number,
    get_sms as smsman_get_sms
)

# Import database and auth
from backend.db import users_collection, smsman_purchases_collection, payments_collection
from backend.utils.auth_utils import get_current_user

router = APIRouter()

# ===== MODELS =====
class BuyNumberRequest(BaseModel):
    application_id: int
    country_id: int

class CancelNumberRequest(BaseModel):
    request_id: int

# ===== FIX 1: COUNTRY CODE HELPER =====
def get_country_code_prefix(country_id: int) -> str:
    """Get country dial code from country ID"""
    country_codes = {
        1: "+1",      # USA
        7: "+7",      # Russia/Kazakhstan
        14: "+254",   # Kenya  ✅ ADDED
        16: "+63",    # Philippines
        44: "+44",    # UK
        49: "+49",    # Germany
        86: "+86",    # China
        91: "+91",    # India
        254: "+254",  # Kenya (alternative ID)
    }
    return country_codes.get(country_id, f"+{country_id}")

# ===== ENDPOINT 1: GET SERVICES (UPDATED FOR ALL COUNTRIES) =====
@router.get("/services")
async def get_services_endpoint(country_id: Optional[int] = None):
    """
    Get services with 70% markup
    - If country_id provided: Return country-specific pricing
    - If no country_id: Return default pricing (India/Russia fallback)
    """
    try:
        if country_id:
            # ✅ Get country-specific services with live pricing
            print(f"🔄 Loading services for country {country_id}...")
            services = await get_services_by_country(country_id)
            
            if not services:
                print(f"⚠️ No services for country {country_id}, trying default...")
                services = await get_services()
            
            print(f"✅ Loaded {len(services)} services for country {country_id}")
        else:
            # Get default services (India/Russia)
            print("🔄 Loading default services...")
            services = await get_services()
            print(f"✅ Loaded {len(services)} default services")
        
        return {
            "success": True,
            "services": services,
            "count": len(services),
            "country_id": country_id
        }
    except Exception as e:
        print(f"❌ Services Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
