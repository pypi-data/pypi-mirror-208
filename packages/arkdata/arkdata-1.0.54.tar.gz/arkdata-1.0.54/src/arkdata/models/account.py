from ..database.cursor import sqlalchemy
from ..database.table import Table
from sqlalchemy import Column, String, Integer
from pathlib import Path
import os
import arkdata


class Account(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False, unique=True)
    player_name = Column(String(100), nullable=True, default=None)
    ark_player_id = Column(Integer, nullable=True, default=None)
    berry_bush_seeds = Column(Integer, nullable=False, default=0)

    def __init__(self, xuid=None, player_name=None, ark_player_id=None, berry_bush_seeds=0):
        self.xuid = xuid
        self.player_name = player_name
        self.ark_player_id = ark_player_id
        self.berry_bush_seeds = berry_bush_seeds


    