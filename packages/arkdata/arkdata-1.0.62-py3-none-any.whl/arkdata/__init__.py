from . import models
from . import blueprints
from . import nitrado
import os
from datetime import datetime


def create_all():
    blueprints.create_all()
    models.create_all()
    nitrado.drop_all()


def clear_all():
    blueprints.clear_all()
    models.clear_all()
    nitrado.drop_all()


def drop_all():
    blueprints.drop_all()
    models.drop_all()
    nitrado.drop_all()


def seed_all():
    blueprints.seed_all()
    models.seed_all()
    nitrado.seed_all()


def reset():
    drop_all()
    print("Dropped All Tables")
    create_all()
    print("Created All Tables")
    seed_all()


__all__ = ['models', 'blueprints']
