import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Instagram DM Automation"
    PROJECT_VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    
    # APIs
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Database (for development, we'll use JSON files)
    ACCOUNTS_DB_PATH = "data/accounts.json"
    TEMPLATES_DB_PATH = "data/templates.json"
    
    # Instagram
    IG_DEVICE_SETTINGS = {
        "app_version": "269.0.0.18.75",
        "android_version": "28",
        "android_release": "9.0",
        "device_name": "OnePlus6T",
        "manufacturer": "OnePlus"
    }
    
    # Rate Limiting
    DM_DELAY_SECONDS = 30  # Delay between DMs to avoid rate limiting
    MAX_RETRIES = 3  # Maximum number of retries for failed operations
    
    # Auto Reply
    AUTO_REPLY_CHECK_INTERVAL = 60  # Check for new DMs every 60 seconds

settings = Settings()
