from arkdata.database.cursor import sqlalchemy
from arkdata.database.table import Table


def drop_all():
    sqlalchemy.db.drop_all()


def create_all():
    sqlalchemy.db.create_all()


__all__ = ['create_all', 'drop_all']


