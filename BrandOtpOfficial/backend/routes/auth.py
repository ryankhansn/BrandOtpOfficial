from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated
import bcrypt
from datetime import datetime, timedelta
from bson import ObjectId
import os
import jwt

# Import database and auth utilities
from backend.db import users_collection
from backend.utils.auth_utils import get_current_user

router = APIRouter()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "brandotpsecretkey2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Pydantic Models
class UserSignup(BaseModel):
    username: Annotated[str, StringConstraints(min_length=4)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=4)]

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=4)]

# Password utilities
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_password.decode('utf-8')
    except Exception as e:
        print(f"❌ Hash password error: {e}")
        raise HTTPException(status_code=500, detail="Password hashing failed")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        if not plain_password or not hashed_password:
            return False
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        result = bcrypt.checkpw(pwd_bytes, hashed_bytes)
        return result
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        return False

def create_access_token(data: dict):
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"❌ JWT creation error: {e}")
        raise HTTPException(status_code=500, detail="Token creation failed")

@router.post("/signup")
async def signup(user_data: UserSignup):
    """User registration"""
    try:
        print(f"🚀 SIGNUP: {user_data.email}")

        # Check existing users
        if users_collection.find_one({"email": user_data.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        if users_collection.find_one({"username": user_data.username}):
            raise HTTPException(status_code=400, detail="Username already taken")

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "balance": 0.0,
            "is_active": True,
            "created_at": datetime.utcnow()
        }

        # Insert user
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)

        print(f"✅ SIGNUP: User created {user_id}")

        # Create token
        access_token = create_access_token(data={"user_id": user_id, "email": user_data.email})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "balance": 0.0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ SIGNUP ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(user_credentials: UserLogin):
    """User login"""
    try:
        print(f"🚀 LOGIN: {user_credentials.email}")

        # Find user
        user = users_collection.find_one({"email": user_credentials.email})
        if not user:
            print(f"❌ LOGIN: User not found")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        print(f"👤 LOGIN: User found - {user.get('username', 'N/A')}")

        # Check password
        if 'password' not in user or not user['password']:
            raise HTTPException(status_code=401, detail="Account setup incomplete")

        # Verify password
        if not verify_password(user_credentials.password, user['password']):
            print(f"❌ LOGIN: Invalid password")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        print(f"✅ LOGIN: Password verified")

        # Check if active
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Account deactivated")

        # Create token
        user_id = str(user["_id"])
        access_token = create_access_token(data={"user_id": user_id, "email": user["email"]})

        user_response = {
            "id": user_id,
            "username": user["username"],
            "email": user["email"],
            "balance": float(user.get("balance", 0.0)),
            "is_active": user.get("is_active", True)
        }

        print(f"✅ LOGIN: Success for {user['username']}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ LOGIN ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# ✅ FIXED: Real JWT-based /me endpoint
@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    try:
        print(f"✅ /me endpoint: User {current_user.get('username')}")
        
        return {
            "success": True,
            "user": current_user
        }
    except Exception as e:
        print(f"❌ Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@router.get("/test")
async def test_auth():
    """Test endpoint"""
    try:
        user_count = users_collection.count_documents({})
        return {
            "message": "Auth working!",
            "status": "success",
            "users_in_db": user_count
        }
    except Exception as e:
        return {"error": str(e)}
