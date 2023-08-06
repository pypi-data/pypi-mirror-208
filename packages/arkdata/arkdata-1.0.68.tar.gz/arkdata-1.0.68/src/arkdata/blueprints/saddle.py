from ..database.cursor import sqlalchemy
from ..database.table import Table
from sqlalchemy import Column, String, Integer, Text
import os
import arkdata
from pathlib import Path


class Saddle(sqlalchemy.db.Model, Table):

    name = Column(String(100), unique=True, nullable=False)
    creature_name_tag = Column(String(100), unique=False, nullable=False)
    type = Column(String(100), nullable=False, default='OTHER')
    stack_size = Column(Integer, nullable=True, default=None)
    class_name = Column(String(100), nullable=True, default=None)
    blueprint = Column(String(200), nullable=True, default=None)
    description = Column(Text, nullable=True, default=None)
    image_url = Column(String(500), nullable=True, default=None)
    summary = Column(Text, default=None)
    url = Column(String(500), nullable=True, default=None)

    def __init__(self, id=None, name=None, creature_name_tag=None, type=None, stack_size=None, class_name=None, blueprint=None, description=None, image_url=None, summary=None, url=None):
        self.id = id
        self.name = name
        self.creature_name_tag = creature_name_tag
        self.type = type
        self.stack_size = stack_size
        self.class_name = class_name
        self.blueprint = blueprint
        self.description = description
        self.image_url = image_url
        self.summary = summary
        self.url = url


