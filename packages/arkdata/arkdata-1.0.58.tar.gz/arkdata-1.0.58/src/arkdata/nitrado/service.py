from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Integer
from .. import models


class Service(sqlalchemy.db.Model, Table):
    service_id = Column(String(100))
    location_id = Column(Integer)
    user_id = Column(String(100))
    type = Column(String(100))
    username = Column(String(100))

    def __int__(
            self,
            service_id: str = None,
            location_id: int = None,
            user_id: str = None,
            type: str = None,
            username: str = None,
    ):
        self.service_id = service_id
        self.location_id = location_id
        self.user_id = user_id
        self.type = type
        self.username = username


