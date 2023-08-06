from ..database.cursor import sqlalchemy
from ..database.table import Table
from sqlalchemy import Column, String, Integer, Text
import os
import arkdata
from pathlib import Path


class Creature(sqlalchemy.db.Model, Table):

    name = Column(String(100), unique=True, nullable=False)
    name_tag = Column(String(100), nullable=True, default=None)
    category = Column(String(100), nullable=True, default=None)
    entity_id = Column(String(100), nullable=True, default=None)
    blueprint = Column(String(200), nullable=True, default=None)
    small_image_url = Column(String(200), nullable=True, default=None)
    large_image_url = Column(String(200), nullable=True, default=None)
    description = Column(Text, nullable=True, default=None)
    url = Column(String(200), nullable=True, default=None)
    color_id = Column(Integer, nullable=True, default=None)

    def __init__(self, id=None, name=None, name_tag=None, category=None, entity_id=None, blueprint=None, small_image_url=None, large_image_url=None, description=None, url=None, color_id=None):
        self.id = id
        self.name = name
        self.name_tag = name_tag
        self.category = category
        self.entity_id = entity_id
        self.blueprint = blueprint
        self.small_image_url = small_image_url
        self.large_image_url = large_image_url
        self.description = description
        self.url = url
        self.color_id = color_id


    def tek_saddle(self):
        pass

    def saddle(self):
        pass

    def platform_saddle(self):
        pass

