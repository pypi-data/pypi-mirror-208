from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Integer, Boolean, Text
from .. import models


class Log(sqlalchemy.db.Model, Table):
    service_id = Column(String(100))
    log = Column(Text)

    @classmethod
    def exists(cls, service_id: str, log: str):
        return Log.find_by(service_id=service_id, log=log) is not None

    @classmethod
    def insert(cls, service_id: str, log: str) -> bool:
        if cls.exists(service_id, log):
            return False
        cls(service_id=service_id, log=log).create()
        return True

    def __int__(
            self,
            service_id: str = None,
            log: str = None,
    ):
        self.service_id = service_id
        self.log = log

