from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Integer, Boolean
from .. import models


class Player(sqlalchemy.db.Model, Table):
    service_id = Column(String(100))
    gamertag = Column(String(100))
    player_id = Column(String(200))
    tribe_id = Column(String(100))
    tribe = Column(String(100))
    online = Column(Boolean, default=False)
    last_online = Column(String(100))

    def __int__(
            self,
            service_id: str = None,
            gamertag: str = None,
            player_id: str = None,
            tribe_id: str = None,
            tribe: str = None,
            online: bool = False,
            last_online: str = None,
    ):
        self.service_id = service_id
        self.gamertag = gamertag
        self.player_id = player_id
        self.player_id_type = player_id_type
        self.online = online
        self.last_online = last_online


    def tribe_players(self) -> list:
        pass