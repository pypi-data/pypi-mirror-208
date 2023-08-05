from __future__ import annotations
from sqlalchemy import Column, String, Boolean
from ..database.cursor import sqlalchemy
from ..database.table import Table
from .. import models
from secrets import token_urlsafe
from pathlib import Path
import arkdata
import os


class Session(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)
    session_token = Column(String(100), default=token_urlsafe)
    security_token = Column(String(100), default=token_urlsafe)
    api_token = Column(String(200), default=token_urlsafe)
    driver_token = Column(String(200), default=token_urlsafe)
    nitrado_code = Column(String(200), default=token_urlsafe)
    nitrado_state = Column(String(200), default=token_urlsafe)
    nitrado_refresh_token = Column(String(200), default=token_urlsafe)
    authenticated = Column(Boolean, default=False)

    @classmethod
    def user_by_session_token(cls, session_token: str) -> models.User | Table:
        session = cls.find_by(session_token=session_token)
        if session is not None:
            return session.user()

    @classmethod
    def user_by_driver_token(cls, driver_token: str) -> models.User | Table:
        session = cls.find_by(driver_token=driver_token)
        if session is not None:
            return session.user()

    @classmethod
    def user_by_security_token(cls, security_token: str) -> models.User | Table:
        session = cls.find_by(security_token=security_token)
        if session is not None:
            return session.user()

    @classmethod
    def user_by_api_token(cls, api_token: str) -> models.User | Table:
        session = cls.find_by(api_token=api_token)
        if session is not None:
            return session.user()

    def __init__(
            self,
            xuid=None,
            session_token=None,
            security_token=None,
            api_token=None,
            authenticated=False,
            driver_token=None,
            nitrado_code=None,
            nitrado_state=None,
            nitrado_refresh_token=None,
    ):
        self.xuid = xuid
        self.session_token = session_token
        self.security_token = security_token
        self.api_token = api_token
        self.driver_token = driver_token
        self.authenticated = authenticated
        self.nitrado_code = nitrado_code
        self.nitrado_state = nitrado_state
        self.nitrado_refresh_token = nitrado_refresh_token

    def account(self) -> models.Account | Table:
        return models.Account.find_by(xuid=self.xuid)

    def admin(self) -> models.Admin | Table:
        return models.Admin.find_by(xuid=self.xuid)

    def cart_items(self) -> list[models.CartItem | Table]:
        return models.CartItem.find_all_by(xuid=self.xuid)

    def user(self) -> models.User | Table:
        return models.User.find_by(xuid=self.xuid)

    def logout(self) -> None:
        with sqlalchemy.app_context():
            self.session_token = token_urlsafe(64)
            sqlalchemy.db.session.commit()

    def new_session_token(self) -> str:
        self(session_token=token_urlsafe(64))
        return self.session_token

    def new_security_token(self) -> str:
        self(security_token=token_urlsafe(64))
        return self.security_token
        # TODO: Send token to xbox account

    def new_api_token(self) -> str:
        self(api_token=token_urlsafe(64))
        return self.api_token

    def new_driver_token(self) -> str:
        self(driver_token=token_urlsafe(64))
        return self.driver_token

    def new_nitrado_state(self) -> str:
        self(nitrado_state=token_urlsafe(64))
        return self.nitrado_state

