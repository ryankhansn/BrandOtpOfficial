from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sqlite3
import time

# --- ✅ 1. अपने सभी राउटर्स को यहाँ इम्पोर्ट करें ---
from backend.routes.smsman_numbers import router as smsman_router
from backend.routes.pay0_order import router as pay0_router
from backend.routes.payment_status import router as payment_status_router
from backend.routes.webhook import router as webhook_router # वेबहुक राउटर (बैकअप के लिए)

# (आपके बाकी के इम्पोर्ट्स)
import hashlib
import secrets

# (आपके सभी फंक्शन्स)
def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta=None):
    return secrets.token_urlsafe(32)

# App Initialization
app = FastAPI(
    title="BrandOtp Official API",
    description="Complete OTP Service API with Authentication & Payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://brandotpofficial.shop",
        "https://www.brandotpofficial.shop",
        "https://brandotp.netlify.app",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ✅ 2. अपने सभी राउटर्स को यहाँ सही तरीके से जोड़ें ---
app.include_router(pay0_router, prefix="/api/payments", tags=["Payments"])
app.include_router(payment_status_router, prefix="/api/payments", tags=["Payments"])
app.include_router(webhook_router, prefix="/api/payments", tags=["Payments"]) # वेबहुक जोड़ा गया
app.include_router(smsman_router, prefix="/api/smsman", tags=["SMSMan API"])
# ---------------------------------------------------

# (यहाँ से आपका बाकी का main.py कोड शुरू होता है, जिसमें कोई बदलाव नहीं है)
# ... init_database() ...
# ... get_current_user() ...
# ... Exception Handlers ...
# ... /api/history/numbers ...
# ... @app.post("/api/buy-number") ...
# ... @app.post("/api/update-sms-status") ...
# ... @app.get("/api/wallet/balance") ...
# ... @app.get("/api/wallet/transactions") ...
# ... @app.get("/api/auth/me") ...

# --- ❌ ध्यान दें: पुराना @app.post("/api/wallet/add-money") वाला फंक्शन और register_all_routers(app) यहाँ से हटा दिए गए हैं ---

# ... (StaticFiles Mount और बाकी के Page Routes) ...
# ... (Health Check और Startup/Shutdown Events) ...
# ... (if __name__ == "__main__":) ...



# Database initialization
def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS number_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        service TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        country TEXT NOT NULL,
        amount REAL NOT NULL,
        sms_status TEXT DEFAULT 'waiting',
        order_status TEXT DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance REAL DEFAULT 0.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        transaction_id TEXT UNIQUE,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'completed',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables initialized")

# ✅ Helper function (NO async, simplified)
def get_current_user(request: Request):
    """Get current user from session/token - simplified for testing"""
    try:
        # Simplified - just return demo user for now
        # TODO: Implement proper token validation later
        return {"user_id": 1, "username": "demo_user", "email": "demo@example.com"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication required")

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": "Validation failed",
            "errors": [str(error) for error in exc.errors()]
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"❌ Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "Internal server error. Please try again later."
        }
    )

# ✅ HISTORY API ROUTES
@app.get("/api/history/numbers")
async def get_number_history(request: Request):
    """Get user's number purchase history"""
    try:
        current_user = get_current_user(request)
        user_id = current_user["user_id"]
        
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT order_id, service, phone_number, country, amount, 
                   sms_status, order_status, created_at 
            FROM number_orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        formatted_history = []
        for row in rows:
            formatted_history.append({
                'orderId': row['order_id'],
                'service': row['service'],
                'phoneNumber': row['phone_number'],
                'country': row['country'],
                'amount': f"₹{row['amount']:.2f}",
                'smsStatus': row['sms_status'],
                'orderStatus': row['order_status'],
                'dateTime': row['created_at']
            })
        
        return {"success": True, "history": formatted_history}
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Failed to fetch history"}
        )

@app.post("/api/buy-number")
async def buy_number_api(
    request: Request,
    service: str = Form(...),
    country: str = Form(...)
):
    """Buy a number and save to database"""
    try:
        current_user = get_current_user(request)
        user_id = current_user["user_id"]
        
        order_id = f"ORD{int(time.time())}"
        phone_number = "+91 98765 43210"
        amount = 25.00
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO number_orders 
            (order_id, user_id, service, phone_number, country, amount, sms_status, order_status)
            VALUES (?, ?, ?, ?, ?, ?, 'waiting', 'active')
        """, (order_id, user_id, service, phone_number, country, amount))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "order_id": order_id,
            "phone_number": phone_number,
            "amount": amount,
            "message": "Number purchased successfully!"
        }
        
    except Exception as e:
        print(f"Error buying number: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Failed to purchase number"}
        )

@app.post("/api/update-sms-status")
async def update_sms_status(
    request: Request,
    order_id: str = Form(...),
    status: str = Form(...)
):
    """Update SMS status when SMS is received"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        if status == 'received':
            order_status = 'completed'
        elif status == 'timeout':
            order_status = 'expired'
        elif status == 'cancelled':
            order_status = 'cancelled'
        else:
            order_status = 'active'
        
        cursor.execute("""
            UPDATE number_orders 
            SET sms_status = ?, order_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (status, order_status, order_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Status updated to {status}"}
        
    except Exception as e:
        print(f"Error updating SMS status: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Failed to update status"}
        )

# ✅ WALLET API ROUTES
@app.get("/api/wallet/balance")
async def get_wallet_balance(request: Request):
    """Get user wallet balance"""
    try:
        current_user = get_current_user(request)
        user_id = current_user["user_id"]
        
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        balance = float(result['balance']) if result and result['balance'] else 0.0
        conn.close()
        
        return {"success": True, "balance": balance}
        
    except Exception as e:
        print(f"❌ Balance API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "balance": 0.0}
        )

@app.get("/api/wallet/transactions")  
async def get_wallet_transactions(request: Request):
    """Get user wallet transactions"""
    try:
        current_user = get_current_user(request)
        user_id = current_user["user_id"]
        
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT type, amount, reason, status, created_at
            FROM wallet_transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'type': row['type'],
                'amount': float(row['amount']),
                'reason': row['reason'],
                'status': row['status'], 
                'created_at': row['created_at']
            })
        
        return {"success": True, "transactions": transactions}
        
    except Exception as e:
        print(f"❌ Transactions API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "transactions": []}
        )



@app.get("/api/auth/me")
async def get_current_user_info(request: Request):
    """Get current user info"""
    try:
        current_user = get_current_user(request)
        return {
            "success": True,
            "user": {
                "id": current_user["user_id"],
                "username": current_user.get("username", "User"),
                "email": current_user.get("email", "")
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Authentication required"}
        )



# ✅ ADD SMSMan routes
app.include_router(smsman_router, prefix="/api/smsman", tags=["SMSMan API"])

# Frontend Configuration
frontend_dir = "frontend"
assets_dir = os.path.join(frontend_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    print("✅ Static assets mounted at /assets")
else:
    print(f"⚠️ Assets directory not found at: {assets_dir}")

# Helper for HTML file serving
def serve_html_file(page: str, fallback_html: str):
    page_path = os.path.join(frontend_dir, f"{page}.html")
    if os.path.exists(page_path):
        return FileResponse(page_path, media_type='text/html')
    return HTMLResponse(content=fallback_html, status_code=200)

# Page Routes
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BrandOtp - Welcome</title>
        <style>body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; } .container { text-align: center; background: rgba(255,255,255,0.1); padding: 60px 40px; border-radius: 20px; backdrop-filter: blur(10px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); } h1 { font-size: 3rem; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); } p { font-size: 1.2rem; margin-bottom: 40px; opacity: 0.9; } .buttons { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; } .btn { padding: 15px 30px; border: none; border-radius: 25px; font-size: 1.1rem; font-weight: 600; text-decoration: none; cursor: pointer; transition: all 0.3s ease; display: inline-block; } .btn-primary { background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%); color: white; } .btn-secondary { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; } .btn:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }</style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 BrandOtp</h1>
            <p>Welcome to BrandOtp Official - Your OTP Service Platform with SMSMan Integration</p>
            <div class="buttons">
                <a href="/login" class="btn btn-primary">🔐 Login</a>
                <a href="/signup" class="btn btn-secondary">📝 Sign Up</a>
                <a href="/buy-number" class="btn btn-primary">📱 Buy Numbers</a>
                <a href="/history" class="btn btn-secondary">📊 History</a>
                <a href="/docs" class="btn btn-secondary">📖 API Docs</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/signup", response_class=HTMLResponse)
async def serve_signup():
    return serve_html_file("signup", "<h1>Signup - File not found</h1>")

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    return serve_html_file("login", "<h1>Login - File not found</h1>")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return serve_html_file("dashboard", "<h1>Dashboard - File not found</h1><p>Please create frontend/dashboard.html</p>")

@app.get("/wallet", response_class=HTMLResponse)
async def serve_wallet():
    return serve_html_file("wallet", "<h1>Wallet - File not found</h1>")

@app.get("/add-money", response_class=HTMLResponse)
async def serve_add_money():
    return serve_html_file("add_money", "<h1>Add Money - File not found</h1>")

@app.get("/buy-number", response_class=HTMLResponse)
async def serve_buy_number():
    return serve_html_file("buy_number", "<h1>Buy Number - File not found</h1>")

@app.get("/history", response_class=HTMLResponse)
async def serve_history():
    """Serve history page"""
    return serve_html_file("history", """
    <!DOCTYPE html>
    <html>
    <head>
        <title>History - BrandOtp</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #f5f5f5; 
                padding: 20px; 
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                text-align: center;
                max-width: 600px;
            }
            h1 { color: #6366f1; margin-bottom: 20px; }
            p { color: #6b7280; margin-bottom: 30px; }
            .btn { 
                display: inline-block;
                padding: 12px 24px; 
                background: #6366f1; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 5px;
                transition: background 0.3s;
            }
            .btn:hover { background: #4f46e5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 History Page</h1>
            <p>Please create <code>frontend/history.html</code> file with the history page template provided.</p>
            <a href="/" class="btn">← Go Home</a>
            <a href="/buy-number" class="btn">📱 Buy Numbers</a>
        </div>
    </body>
    </html>
    """)

# ✅ API Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "BrandOtp Official API",
        "version": "1.0.0",
        "features": ["Authentication", "Wallet", "SMSMan Integration", "History Tracking"]
    }

# ✅ API Root Check  
@app.get("/api")
async def api_root():
    return {
        "message": "BrandOtp API Working",
        "version": "1.0.0",
        "endpoints": {
            "smsman_services": "/api/smsman/services",
            "smsman_countries": "/api/smsman/countries", 
            "smsman_meta": "/api/smsman/meta",
            "history_numbers": "/api/history/numbers",
            "buy_number": "/api/buy-number",
            "update_sms_status": "/api/update-sms-status",
            "docs": "/docs"
        }
    }

@app.on_event("startup")
async def startup_event():
    print("🚀 BrandOtp API Starting...")
    init_database()
    print(f"📁 Frontend directory: {os.path.abspath(frontend_dir)}")
    print("🏠 Home: http://localhost:8000/")
    print("🔐 Login: http://localhost:8000/login")
    print("📝 Signup: http://localhost:8000/signup")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📱 Buy Numbers: http://localhost:8000/buy-number")
    print("📊 History: http://localhost:8000/history")
    print("🔗 SMSMan Services: http://localhost:8000/api/smsman/services")
    print("🌍 SMSMan Countries: http://localhost:8000/api/smsman/countries")
    print("📊 Number History API: http://localhost:8000/api/history/numbers")
    print("📖 API Docs: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 BrandOtp API Shutting down...")
    with suppress(asyncio.CancelledError):
        await asyncio.sleep(0.1)

@app.get("/{path:path}")
async def serve_spa(path: str):
    html_path = os.path.join(frontend_dir, f"{path}.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    file_path = os.path.join(frontend_dir, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return HTMLResponse(
        content="""
        <html>
        <head><title>404 - Page Not Found</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 100px;">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" style="color: #4361ee; text-decoration: none;">← Go Home</a>
        </body>
        </html>
        """,
        status_code=404
    )

if __name__ == "__main__":
    print("🚀 Starting BrandOtp API Server...")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔐 Login: http://localhost:8000/login")
    print("📝 Signup: http://localhost:8000/signup")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📱 SMSMan API: http://localhost:8000/api/smsman/services")
    print("📊 History API: http://localhost:8000/api/history/numbers")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )









