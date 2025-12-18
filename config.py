import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """Centralized configuration management"""

    # URLs
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

    # Database config
    SQL_DATABASE_URL = os.getenv("SQL_DATABASE_URL")

    # Secret Keys
    JWT_SECRET_KEY = os.getenv("SECRET_KEY")
