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
    is_developer = Column(Boolean, default=False)
    subscription_start = Column(String(100), nullable=True)
    subscription_stop = Column(String(100), nullable=True)
    nitrado_api_key = Column(String(500), nullable=True)

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
            subscription_stop: str = None,
            is_developer: bool = False
    ):
        self.xuid = xuid
        self.subscription_start = subscription_start
        self.subscription_stop = subscription_stop
        self.nitrado_api_key = nitrado_api_key
        self.is_developer = is_developer

    def update_subscription_start(self, month: int, day: int, year: int) -> None:
        self(subscription_start=str(datetime(year=year, month=month, day=day)))

    def update_subscription_stop(self, month: int, day: int, year: int) -> None:
        self(subscription_stop=str(datetime(year=year, month=month, day=day)))

    def update_subscription(self, start: datetime, stop: datetime) -> None:
        if not isinstance(start, datetime):
            raise Exception(f"Update subscription must have a 'start' parameter of type datetime: {start}")
        if not isinstance(stop, datetime):
            raise Exception(f"Update subscription must have an 'stop' parameter of type datetime: {stop}")
        self(subscription_start=str(start), subscription_stop=str(stop))

    def has_active_subscription(self) -> bool:
        if self.is_developer:
            return True
        if self.subscription_start is None or self.subscription_stop is None:
            return False
        start = datetime.fromisoformat(self.subscription_start)
        stop = datetime.fromisoformat(self.subscription_stop)
        return start <= datetime.now() < stop
