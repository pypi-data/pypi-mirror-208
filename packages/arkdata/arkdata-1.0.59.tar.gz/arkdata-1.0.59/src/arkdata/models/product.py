from ..database.cursor import sqlalchemy
from ..database.table import Table
from .. import models
from sqlalchemy import Column, String, Integer, Text
from pathlib import Path
import arkdata
import os


class Product(sqlalchemy.db.Model, Table):
    name = Column(String(100), unique=False, nullable=False)
    price = Column(Integer, unique=False, nullable=True, default=65535)
    type = Column(String(100), unique=False, nullable=False)

    def __init__(self, name=None, price=65535, type=None, *args, **kwargs):
        self.name = name
        self.price = price
        self.type = type

    def item(self):
        if self.type == 'CREATURE':
            return models.Creature.find_by(name=self.name)
        elif self.type == 'AMMUNITION':
            return models.Ammunition.find_by(name=self.name)
        elif self.type == 'ARMOUR':
            return models.Armour.find_by(name=self.name)
        elif self.type == 'ARTIFACT':
            return models.Artifact.find_by(name=self.name)
        elif self.type == 'ATTACHMENT':
            return models.Attachment.find_by(name=self.name)
        elif self.type == 'CART_ITEM':
            return models.CartItem.find_by(name=self.name)
        elif self.type == 'ORDER_ITEM':
            return models.OrderItem.find_by(name=self.name)
        elif self.type == 'CONSUMABLE':
            return models.Consumable.find_by(name=self.name)
        elif self.type == 'DYE':
            return models.Dye.find_by(name=self.name)
        elif self.type == 'EGG':
            return models.Egg.find_by(name=self.name)
        elif self.type == 'FARM':
            return models.Farm.find_by(name=self.name)
        elif self.type == 'RECIPE':
            return models.Recipe.find_by(name=self.name)
        elif self.type == 'RESOURCE':
            return models.Resource.find_by(name=self.name)
        elif self.type == 'SADDLE':
            return models.Saddle.find_by(name=self.name)
        elif self.type == 'SEED':
            return models.Seed.find_by(name=self.name)
        elif self.type == 'SKIN':
            return models.Skin.find_by(name=self.name)
        elif self.type == 'STRUCTURE':
            return models.Structure.find_by(name=self.name)
        elif self.type == 'TOOL':
            return models.Tool.find_by(name=self.name)
        elif self.type == 'TROPHY':
            return models.Trophy.find_by(name=self.name)
        elif self.type == 'WEAPON':
            return models.Weapon.find_by(name=self.name)



