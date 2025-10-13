# backend/utils/smsman_client.py - COMPLETE FIXED WITH DEBUG LOGS
import httpx
import os
import json
import asyncio
from typing import List, Dict, Any, Optional

# Load API key from environment
SMSMAN_API_KEY = os.getenv("SMSMAN_API_KEY")
SMSMAN_BASE_URL = "https://api.sms-man.com/control"

# Pricing configuration
PROFIT_MARGIN = 1.70  # 70% markup

print(f"🔑 SMSMan API Key: {SMSMAN_API_KEY[:10] if SMSMAN_API_KEY else 'NOT FOUND'}...")
print(f"🌐 Using SMSMan API v2.0: {SMSMAN_BASE_URL}")

# ===== CACHE SYSTEM =====
_country_pricing_cache = {}  # {country_id: {service_id: pricing_data}}

async def get_countries() -> List[Dict[str, Any]]:
    """Fetch ALL countries from SMSMan API v2.0"""
    
    if not SMSMAN_API_KEY:
        return []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SMSMAN_BASE_URL}/countries",
                params={"token": SMSMAN_API_KEY}
            )
            
            if response.status_code == 200:
                data = response.json()
                countries = []
                
                if isinstance(data, dict):
                    for country_id, country_info in data.items():
                        try:
                            clean_id = int(str(country_id).strip())
                            
                            if isinstance(country_info, dict):
                                clean_name = str(country_info.get('title', country_info.get('name', ''))).strip()
                            elif isinstance(country_info, str):
                                clean_name = str(country_info).strip()
                            else:
                                continue
                            
                            if clean_name and len(clean_name) > 1:
                                countries.append({
                                    "id": clean_id,
                                    "title": clean_name,
                                    "code": generate_country_code(clean_name)
                                })
                                
                        except Exception:
                            continue
                
                if countries:
                    countries.sort(key=lambda x: x['title'])
                    return countries
                        
    except Exception as e:
        print(f"❌ Countries error: {e}")
    
    return []

async def get_services() -> List[Dict[str, Any]]:
    """Fetch services with INDIA/RUSSIA fallback pricing"""
    
    if not SMSMAN_API_KEY:
        return []
    
    try:
        print("📱 Fetching default services...")
        
        # Try India first, then Russia
        services = await get_services_by_country(91)
        if not services:
            print("⚠️ India failed, trying Russia...")
            services = await get_services_by_country(7)
        
        return services
                    
    except Exception as e:
        print(f"❌ Services error: {e}")
    
    return []

async def get_services_by_country(country_id: int) -> List[Dict[str, Any]]:
    """
    Fetch services with country-specific pricing
    ✅ IMPROVED LIST/DICT PARSING WITH DEBUG LOGS
    """
    
    if not SMSMAN_API_KEY:
        print(f"❌ No API key for country {country_id}")
        return []
    
    try:
        print(f"📱 Fetching services for country {country_id}...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Get all services
            services_response = await client.get(
                f"{SMSMAN_BASE_URL}/applications",
                params={"token": SMSMAN_API_KEY}
            )
            
            if services_response.status_code != 200:
                print(f"❌ Services API failed for country {country_id}")
                return []
            
            services_data = services_response.json()
            print(f"📋 Got {len(services_data)} services for country {country_id}")
            
            # Step 2: Get country-specific pricing
            print(f"💰 Fetching LIVE pricing for country {country_id}...")
            
            pricing_response = await client.get(
                f"{SMSMAN_BASE_URL}/get-prices",
                params={
                    "token": SMSMAN_API_KEY,
                    "country_id": country_id
                }
            )
            
            print(f"💰 Country {country_id} pricing status: {pricing_response.status_code}")
            
            if pricing_response.status_code != 200:
                print(f"❌ Pricing API failed for country {country_id}")
                return []
            
            try:
                pricing_raw = pricing_response.json()
                print(f"📊 Country {country_id} pricing type: {type(pricing_raw)}")
                
                # ✅ DEBUG: Print sample to understand format
                if isinstance(pricing_raw, list):
                    if len(pricing_raw) > 0:
                        print(f"📊 Sample LIST item [0]: {str(pricing_raw[0])[:200]}")
                        if len(pricing_raw) > 1:
                            print(f"📊 Sample LIST item [1]: {str(pricing_raw[1])[:200]}")
                elif isinstance(pricing_raw, dict):
                    keys = list(pricing_raw.keys())[:3]
                    for key in keys:
                        print(f"📊 Sample DICT key '{key}': {str(pricing_raw[key])[:200]}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Country {country_id} pricing JSON error: {e}")
                return []
            
            # Step 3: Parse pricing - IMPROVED LOGIC
            country_pricing = {}
            
            try:
                # ✅ FORMAT 1: LIST (Most common)
                if isinstance(pricing_raw, list):
                    print(f"🔄 Processing LIST format for country {country_id}...")
                    
                    for idx, item in enumerate(pricing_raw):
                        if not isinstance(item, dict):
                            continue
                        
                        try:
                            # Try different field name combinations
                            service_id = None
                            cost = None
                            count = 0
                            
                            # Service ID variations
                            for field in ['application_id', 'app_id', 'id', 'service_id']:
                                if field in item:
                                    try:
                                        service_id = int(str(item[field]).strip())
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            # Cost variations
                            for field in ['cost', 'price', 'amount']:
                                if field in item:
                                    try:
                                        cost = float(str(item[field]).strip())
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            # Count variations
                            for field in ['count', 'quantity', 'available']:
                                if field in item:
                                    try:
                                        count = int(str(item[field]).strip())
                                        break
                                    except (ValueError, TypeError):
                                        continue
                            
                            if service_id and service_id > 0 and cost and cost > 0:
                                country_pricing[service_id] = {
                                    'original': cost,
                                    'user_price': cost * PROFIT_MARGIN,
                                    'count': count
                                }
                                
                                # Debug first 5 items
                                if idx < 5:
                                    print(f"✅ LIST[{idx}] - Service {service_id}: ₹{cost} → ₹{cost * PROFIT_MARGIN:.2f}")
                                
                        except Exception as e:
                            if idx < 5:
                                print(f"⚠️ Parse error LIST[{idx}]: {e}")
                            continue
                
                # ✅ FORMAT 2: DICT (Nested)
                elif isinstance(pricing_raw, dict):
                    print(f"🔄 Processing DICT format for country {country_id}...")
                    
                    parsed_count = 0
                    
                    # Try multiple nesting levels
                    for key1, value1 in pricing_raw.items():
                        if not isinstance(value1, dict):
                            continue
                        
                        # Level 1: Direct service IDs {"123": {"cost": "15"}}
                        if 'cost' in value1 or 'price' in value1:
                            try:
                                service_id = int(str(key1).strip())
                                cost = float(value1.get('cost', value1.get('price', 0)))
                                
                                if service_id > 0 and cost > 0:
                                    country_pricing[service_id] = {
                                        'original': cost,
                                        'user_price': cost * PROFIT_MARGIN,
                                        'count': int(value1.get('count', 0))
                                    }
                                    
                                    if parsed_count < 5:
                                        print(f"✅ DICT Level1 - Service {service_id}: ₹{cost} → ₹{cost * PROFIT_MARGIN:.2f}")
                                    parsed_count += 1
                            except (ValueError, TypeError):
                                pass
                        
                        # Level 2: Nested service IDs {"0": {"123": {"cost": "15"}}}
                        else:
                            for key2, value2 in value1.items():
                                if not isinstance(value2, dict):
                                    continue
                                
                                try:
                                    service_id = int(str(key2).strip())
                                    cost = float(value2.get('cost', value2.get('price', 0)))
                                    
                                    if service_id > 0 and cost > 0:
                                        country_pricing[service_id] = {
                                            'original': cost,
                                            'user_price': cost * PROFIT_MARGIN,
                                            'count': int(value2.get('count', 0))
                                        }
                                        
                                        if parsed_count < 5:
                                            print(f"✅ DICT Level2 - Service {service_id}: ₹{cost} → ₹{cost * PROFIT_MARGIN:.2f}")
                                        parsed_count += 1
                                except (ValueError, TypeError):
                                    continue
                
                print(f"✅ Country {country_id}: Parsed pricing for {len(country_pricing)} services")
                
                # ✅ CACHE THE PRICING
                if country_pricing:
                    _country_pricing_cache[country_id] = country_pricing
                else:
                    print(f"⚠️ No services parsed! Check debug logs above for format issues.")
                
            except Exception as e:
                print(f"❌ Country {country_id} pricing parsing error: {e}")
                import traceback
                traceback.print_exc()
                return []
            
            # If no pricing, return empty
            if not country_pricing:
                print(f"❌ No pricing data for country {country_id}")
                return []
            
            # Step 4: Build services list
            services = []
            
            if isinstance(services_data, dict):
                for service_id, service_info in services_data.items():
                    try:
                        clean_id = int(str(service_id).strip())
                        
                        if isinstance(service_info, dict):
                            clean_name = str(service_info.get('title', service_info.get('name', ''))).strip()
                        elif isinstance(service_info, str):
                            clean_name = str(service_info).strip()
                        else:
                            continue
                        
                        if clean_name and len(clean_name) > 1:
                            # ONLY ADD IF PRICING EXISTS
                            if clean_id in country_pricing:
                                pricing_info = country_pricing[clean_id]
                                user_price = pricing_info['user_price']
                                original_price = pricing_info['original']
                                
                                services.append({
                                    "id": clean_id,
                                    "name": clean_name,
                                    "display_price": f"₹{user_price:.2f}",
                                    "pricing": {
                                        "user_price": round(user_price, 2),
                                        "original_price": round(original_price, 2),
                                        "profit_amount": round(user_price - original_price, 2),
                                        "margin_percent": 70,
                                        "live_api": True,
                                        "availability": pricing_info['count'],
                                        "country_id": country_id
                                    }
                                })
                                
                    except Exception:
                        continue
                
                services.sort(key=lambda x: x['name'].lower())
                
                print(f"🎯 Country {country_id} RESULT: {len(services)} services with live pricing")
                
                if services:
                    samples = [(s['name'], s['display_price']) for s in services[:5]]
                    print(f"🌟 Country {country_id} samples: {samples}")
                    
                return services
                    
    except Exception as e:
        print(f"❌ Country {country_id} services error: {e}")
        import traceback
        traceback.print_exc()
    
    return []

async def get_service_price(application_id: int, country_id: int = 91) -> Dict[str, Any]:
    """
    Get LIVE price for specific service
    ✅ FIX: Uses cached pricing from get_services_by_country()
    """
    
    try:
        if not SMSMAN_API_KEY:
            return {"error": "No API key available", "live_api": False}
        
        print(f"💰 Getting price: Service {application_id}, Country {country_id}")
        
        # ✅ CHECK CACHE FIRST
        if country_id in _country_pricing_cache:
            country_pricing = _country_pricing_cache[country_id]
            
            if application_id in country_pricing:
                pricing_info = country_pricing[application_id]
                user_price = pricing_info['user_price']
                original_price = pricing_info['original']
                
                print(f"✅ Using cached price: ₹{user_price:.2f}")
                
                return {
                    "user_price": round(user_price, 2),
                    "original_price": round(original_price, 2),
                    "profit_amount": round(user_price - original_price, 2),
                    "display_price": f"₹{user_price:.2f}",
                    "live_api": True,
                    "availability": pricing_info['count']
                }
        
        # ✅ IF NOT IN CACHE, FETCH FRESH
        print(f"⚠️ Not in cache, fetching fresh pricing for country {country_id}...")
        
        services = await get_services_by_country(country_id)
        
        # Find service in list
        for service in services:
            if service["id"] == application_id:
                pricing_data = service.get("pricing", {})
                
                return {
                    "user_price": pricing_data.get("user_price", 0),
                    "original_price": pricing_data.get("original_price", 0),
                    "profit_amount": pricing_data.get("profit_amount", 0),
                    "display_price": service.get("display_price", "N/A"),
                    "live_api": True,
                    "availability": pricing_data.get("availability", 0)
                }
        
        return {"error": "No live pricing available", "live_api": False}
        
    except Exception as e:
        print(f"❌ Price error: {e}")
        return {"error": str(e), "live_api": False}

async def buy_number(application_id: int, country_id: int = 91) -> Dict[str, Any]:
    """Buy number from SMSMan API v2.0"""
    
    try:
        if not SMSMAN_API_KEY:
            return {"error": "No API key available", "status": "error"}
            
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{SMSMAN_BASE_URL}/get-number",
                params={
                    "token": SMSMAN_API_KEY,
                    "application_id": application_id,
                    "country_id": country_id
                }
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, dict):
                        if "number" in data and "request_id" in data:
                            return {
                                "number": data["number"],
                                "request_id": data["request_id"],
                                "status": "success",
                                "live_purchase": True
                            }
                        elif "error_msg" in data:
                            return {
                                "error": data["error_msg"],
                                "status": "api_error",
                                "live_purchase": False
                            }
                            
                except json.JSONDecodeError:
                    pass
        
        return {"error": "Purchase failed", "status": "error"}
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

async def get_sms(request_id: str) -> Dict[str, Any]:
    """
    Get SMS for a request ID
    ✅ API DOCS: Returns {"sms_code": "1243"} or {"error_code": "wait_sms"}
    """
    
    try:
        if not SMSMAN_API_KEY:
            return {"error": "No API key available", "status": "error"}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{SMSMAN_BASE_URL}/get-sms",
                params={
                    "token": SMSMAN_API_KEY,
                    "request_id": request_id
                }
            )
            
            print(f"📨 SMS API response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, dict):
                        # ✅ SMS RECEIVED
                        if "sms_code" in data and data["sms_code"]:
                            return {
                                "sms_code": data["sms_code"],
                                "sms_text": f"Your code: {data['sms_code']}",
                                "sender": "Service",
                                "status": "received"
                            }
                        # ⏳ WAITING FOR SMS
                        elif "error_code" in data and data["error_code"] == "wait_sms":
                            return {
                                "status": "waiting",
                                "message": data.get("error_msg", "Waiting for SMS...")
                            }
                        else:
                            return {"status": "waiting", "message": "No SMS yet"}
                            
                except json.JSONDecodeError:
                    pass
        
        return {"status": "waiting", "message": "Waiting for SMS"}
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

def generate_country_code(country_name: str) -> str:
    """Generate country code from country name"""
    name = country_name.lower().strip()
    
    mappings = {
        "russia": "RU", "india": "IN", "ukraine": "UA", "china": "CN",
        "kazakhstan": "KZ", "usa": "US", "uk": "GB", "germany": "DE",
        "france": "FR", "italy": "IT", "japan": "JP", "brazil": "BR",
        "costa rica": "CR", "kenya": "KE", "indonesia": "ID", "congo": "CO"
    }
    
    if name in mappings:
        return mappings[name]
    
    words = name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    elif len(name) >= 2:
        return name[:2].upper()
    else:
        return "XX"
