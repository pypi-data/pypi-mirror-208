from __future__ import annotations
from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from pathlib import Path
import os
import arkdata


class Command(sqlalchemy.db.Model, Table):
    admin_gamertag = Column(String(100), unique=False, nullable=True)
    player_gamertag = Column(String(100), unique=False, nullable=True)
    code = Column(String(500), unique=False, nullable=False)
    executed = Column(Boolean, unique=False, nullable=False, default=False)
    service_id = Column(String(100), unique=False, nullable=True, default=None)
    server_name = Column(String(200), unique=False, nullable=True)
    executed_at = Column(String(100), nullable=True)

    @classmethod
    def queued(cls, admin_gamertag: str = None, player_gamertag: str = None, service_id: str = None, server_name: str = None) -> list[Command | Table]:
        params = {}
        if service_id:
            params['service_id'] = service_id
        if server_name:
            params['server_name'] = server_name
        if admin_gamertag:
            params['admin_gamertag'] = admin_gamertag
        if player_gamertag:
            params['player_gamertag'] = player_gamertag
        return cls.find_all_by(**params, executed=False)

    @classmethod
    def completed(cls, admin_gamertag: str = None, player_gamertag: str = None, service_id: str = None, server_name: str = None) -> list[Command | Table]:
        params = {}
        if service_id:
            params['service_id'] = service_id
        if server_name:
            params['server_name'] = server_name
        if admin_gamertag:
            params['admin_gamertag'] = admin_gamertag
        if player_gamertag:
            params['player_gamertag'] = player_gamertag
        return cls.find_all_by(**params, executed=True)

    @classmethod
    def find_by_player(cls, gamertag: str) -> list[Command | Table]:
        return cls.find_all_by(player_gamertag=gamertag)

    @classmethod
    def find_by_admin(cls, gamertag: str) -> list[Command | Table]:
        return cls.find_all_by(admin_gamertag=gamertag)

    def __init__(
            self,
            admin_gamertag: str = None,
            player_gamertag: str = None,
            code: str = None,
            executed: bool = False,
            service_id: str = None,
            server_name: str = None,
            executed_at: str = None,
    ):
        self.admin_gamertag = admin_gamertag    # Admin who executed the code
        self.player_gamertag = player_gamertag  # Player who requested the code
        self.code = code
        self.executed = executed
        self.service_id = service_id
        self.server_name = server_name
        self.executed_at = executed and not executed_at and str(datetime.now()) or executed_at
