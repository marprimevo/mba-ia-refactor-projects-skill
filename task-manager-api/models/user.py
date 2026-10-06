import hashlib
import hmac
import os

from database import db
from utils.helpers import utc_now

_ITERATIONS = 100_000


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, pwd):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt, _ITERATIONS)
        self.password = salt.hex() + "$" + digest.hex()

    def check_password(self, pwd):
        try:
            salt_hex, digest_hex = self.password.split("$", 1)
            salt = bytes.fromhex(salt_hex)
        except (AttributeError, ValueError):
            return False
        digest = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt, _ITERATIONS)
        return hmac.compare_digest(digest.hex(), digest_hex)

    def is_admin(self):
        return self.role == "admin"
