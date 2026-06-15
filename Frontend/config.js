import os

# API Configuration - detects environment automatically
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Use the production domain/URL from environment or set it when deploying
    API_BASE = os.getenv("API_URL", "https://your-app-name.onrender.com")
else:
    # Local development
    API_BASE = "http://localhost:8000"

export const API_CONFIG = {
    API_BASE: API_BASE
};
