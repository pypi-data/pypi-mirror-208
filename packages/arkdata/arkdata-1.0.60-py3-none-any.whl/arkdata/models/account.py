from __future__ import annotations
from ..database.cursor import sqlalchemy
from ..database.table import Table
from sqlalchemy import Column, String, Integer, Boolean
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import base64
from datetime import datetime


class Account(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)
    developer = Column(Boolean, default=False)
    nitrado_api_key = Column(String(500), nullable=True)
    subscription_start = Column(String(100), nullable=True)
    subscription_end = Column(String(100), nullable=True)

    @classmethod
    def cipher(cls, password: str) -> Fernet:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(hkdf.derive(password.encode()))
        return Fernet(key)

    @classmethod
    def encrypt(cls, content: str, password: str) -> str:
        cipher = cls.cipher(password)
        return cipher.encrypt(content.encode()).decode()

    @classmethod
    def decrypt(cls, content: str, password: str) -> str:
        cipher = cls.cipher(password)
        return cipher.decrypt(content.encode()).decode()

    def __init__(
            self,
            xuid: str = None,
            nitrado_api_key: str = None,
            subscription_start: str = None,
            subscription_end: str = None,
            developer: bool = False
    ):
        self.xuid = xuid
        self.subscription_start = subscription_start
        self.subscription_end = subscription_end
        self.nitrado_api_key = nitrado_api_key
        self.developer = developer

    def update_subscription_start(self, month: int, day: int, year: int) -> None:
        self(subscription_start=str(datetime(year=year, month=month, day=day)))

    def update_subscription_end(self, month: int, day: int, year: int) -> None:
        self(subscription_end=str(datetime(year=year, month=month, day=day)))

    def update_subscription(self, start: datetime, end: datetime) -> None:
        if not isinstance(start, datetime):
            raise Exception(f"Update subscription must have a 'start' parameter of type datetime: {start}")
        if not isinstance(end, datetime):
            raise Exception(f"Update subscription must have an 'end' parameter of type datetime: {end}")
        self(subscription_start=str(start), subscription_end=str(end))

    def has_active_subscription(self) -> bool:
        if self.developer:
            return True
        if self.subscription_start is None or self.subscription_end is None:
            return False
        start = datetime.fromisoformat(self.subscription_start)
        end = datetime.fromisoformat(self.subscription_end)
        if start >= end:
            return False
        return start <= datetime.now() < end