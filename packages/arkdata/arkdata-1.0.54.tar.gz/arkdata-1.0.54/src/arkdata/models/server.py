from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Integer
from .. import models


class Server(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), unique=False, nullable=False)
    service_id = Column(Integer, unique=False, nullable=True, default=None)

    @classmethod
    def server_by_service_id(cls, service_id: int):
        return cls.find_by(service_id=service_id)

    def __int__(self, xuid: str = None, service_id: str = None):
        self.xuid = xuid
        self.service_id = service_id

    def commands(self) -> list:
        return models.Command.find_all_by(server_id=self.id)

