from __future__ import annotations
from sqlalchemy import Column, String
from ..database.cursor import sqlalchemy
from ..database.table import Table
from .. import models


class Developer(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)

    def __init__(
            self,
            xuid: str = None,
    ):
        self.xuid: str = xuid


