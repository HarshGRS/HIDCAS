import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin1234@localhost:5432/hidcas"
)

# API Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
API_PORT = int(os.getenv("API_PORT", 8000))
API_URL = os.getenv("API_URL", "http://localhost:8000")

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5500",
]

# Add production URLs when deployed
if ENVIRONMENT == "production":
    ALLOWED_ORIGINS.extend([
        os.getenv("FRONTEND_URL", ""),
        os.getenv("API_URL", ""),
    ])
    ALLOWED_ORIGINS = [url for url in ALLOWED_ORIGINS if url]  # Remove empty strings

# Security
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
