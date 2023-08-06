from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Integer
from .. import models


class GameServer(sqlalchemy.db.Model, Table):
    service_id = Column(String(100))
    status = Column(String(100))
    ip = Column(String(100))
    port = Column(String(100))
    memory_mb = Column(String(100))
    game = Column(String(100))
    game_human = Column(String(100))
    slots = Column(Integer)
    location = Column(String(100))

    def __int__(
            self,
            service_id: str = None,
            status: str = None,
            ip: str = None,
            port: str = None,
            memory_mb: str = None,
            game: str = None,
            game_human: str = None,
            slots: str = None,
            location: str = None,
    ):
        self.service_id = service_id
        self.status = status
        self.ip = ip
        self.port = port
        self.memory_mb = memory_mb
        self.game = game
        self.game_human = game_human
        self.slots = slots
        self.location = location


