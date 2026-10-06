import os

from dotenv import load_dotenv

load_dotenv()


def _secret_key():
    configured = os.getenv("SECRET_KEY")
    if configured:
        return configured
    return os.urandom(24).hex()


class Settings:
    secret_key = _secret_key()
    database_uri = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")


settings = Settings()
