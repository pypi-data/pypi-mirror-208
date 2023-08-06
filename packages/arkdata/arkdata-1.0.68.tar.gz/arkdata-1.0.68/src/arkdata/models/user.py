from __future__ import annotations
from sqlalchemy import Column, String
from ..database.cursor import sqlalchemy
from ..database.table import Table
from .. import models
import bcrypt
from secrets import token_urlsafe


def temporary_xuid():
    return f"temporary_xuid_{token_urlsafe(32)}"


class User(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)
    gamertag = Column(String(100))
    password_digest = Column(String(100))

    @classmethod
    def create_user(cls, gamertag: str, password: str) -> models.Session | Table | None:
        """Returns the session token"""
        user = User.find_by(gamertag=gamertag.lower())
        password_digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        if user is None:  # user doesn't exist
            xuid = temporary_xuid()
            cls(xuid=xuid, gamertag=gamertag.lower(), password_digest=password_digest).create()
            models.Account(xuid=xuid).create()
            session = models.Session(xuid=xuid).create()
        else:
            session = user.session()
            if session.authenticated:  # user exists but is authenticated
                return
            # user exists but is not authenticated
            user(password_digest=password_digest)
            session.new_session_token()
        return session

    @classmethod
    def login(cls, gamertag: str, password: str) -> models.Session | Table | None:
        """Returns the session token"""
        user = models.User.find_by(gamertag=gamertag.lower())
        if user is None:
            return
        session = user.session()
        if not session.authenticated:
            return
        is_password_valid = bcrypt.checkpw(password.encode(), user.password_digest.encode())
        if not is_password_valid:
            return
        session.new_session_token()
        return session

    def __init__(self, xuid: str = None, gamertag: str = None, password_digest: str = None):
        self.xuid: str = xuid
        self.gamertag: str = gamertag and gamertag.lower()
        self.password_digest: str = password_digest

    def change_password(self, password: str) -> bool:
        if not isinstance(password, str):
            return False
        password_digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self(password_digest=password_digest)
        return True

    def session(self) -> models.Session | Table:
        return models.Session.find_by(xuid=self.xuid)

    def account(self) -> models.Account | Table:
        return models.Account.find_by(xuid=self.xuid)

    def cart_items(self) -> list[models.CartItem | Table]:
        return models.CartItem.find_all_by(xuid=self.xuid)

