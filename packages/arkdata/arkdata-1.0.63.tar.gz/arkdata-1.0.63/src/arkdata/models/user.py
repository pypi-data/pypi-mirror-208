from __future__ import annotations
from sqlalchemy import Column, String
from ..database.cursor import sqlalchemy
from ..database.table import Table
from .. import models
import bcrypt


def random_xuid():
    from random import randint
    return f"temporary_xuid_{randint(1, 10000)}"


class User(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)
    gamertag = Column(String(100))
    password_digest = Column(String(100))

    @classmethod
    def create_user(cls, gamertag: str, password: str) -> models.Session | Table | None:
        """Returns the session token"""
        if User.find_by(gamertag=gamertag.lower()) is not None:
            return
        xuid = random_xuid()
        password_digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cls(xuid=xuid, gamertag=gamertag, password_digest=password_digest).create()
        models.Account(xuid=xuid).create()
        session = models.Session(xuid=xuid).create()
        session.new_session_token()
        return session

    @classmethod
    def login(cls, gamertag: str, password: str) -> models.Session | Table | None:
        """Returns the session token"""
        user = models.User.find_by(gamertag=gamertag)
        if user is None:
            return
        is_password_valid = bcrypt.checkpw(password.encode(), user.password_digest.encode())
        if not is_password_valid:
            return
        session = user.session()
        session.new_session_token()
        return session

    def __init__(self, xuid=None, gamertag=None, password_digest=None):
        self.xuid: str = xuid
        self.gamertag: str = gamertag
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

