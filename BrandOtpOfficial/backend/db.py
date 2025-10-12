import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables (.env handling for local/dev)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

print(f"✅ python-dotenv loaded successfully from: {env_path}")

# Get MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    # Fallback connection string
    MONGO_URI = "mongodb+srv://ryankhann703_db_user:Bs6DNplkZwqY5ppN@brandotpofficial.mbrslgk.mongodb.net/brandotp?retryWrites=true&w=majority&appName=BrandOtpOfficial"
    print("⚠️ Using fallback MONGO_URI")
else:
    print(f"✅ MONGO_URI loaded from .env: {MONGO_URI[:50]}...")

# Database name
DB_NAME = "brandotp"

try:
    print("🔄 Connecting to MongoDB Atlas...")
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsAllowInvalidHostnames=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    client.admin.command('ping')
    print("✅ MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"❌ TLS connection failed: {e}")
    print("🔄 Trying basic connection...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ MongoDB Atlas connected with basic settings!")
    except Exception as e2:
        print(f"❌ All connection attempts failed: {e2}")
        raise

# Database setup
db = client[DB_NAME]

# Collections (Add all you use)
users_collection = db["users"]
transactions_collection = db["transactions"]
services_collection = db["services"]
orders_collection = db["orders"]
otp_requests_collection = db["otp_requests"]
wallets_collection = db["wallets"]
payments_collection = db["payments"]
numbers_collection = db["numbers"]      # If number-related used anywhere
smsman_purchases_collection = db["smsman_purchases"]
# Helpers / quick accessor
def get_db():
    return db

print("🎉 Database setup completed successfully!")
