import os

from dotenv import load_dotenv

load_dotenv()

VALID_CATEGORIES = (
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
)
VALID_ORDER_STATUS = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
DISCOUNT_TIERS = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)
MIN_PRODUCT_NAME = 2
MAX_PRODUCT_NAME = 200


def _secret_key():
    configured = os.getenv("SECRET_KEY")
    if configured:
        return configured
    return os.urandom(24).hex()


class Settings:
    secret_key = _secret_key()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    db_path = os.getenv("DB_PATH", "loja.db")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))


settings = Settings()
