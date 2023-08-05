from . import models
from . import blueprints
import os
from datetime import datetime


def create_all():
    blueprints.create_all_blueprints()
    models.create_all_models()


def clear_all():
    blueprints.clear_all_blueprints()
    models.clear_all_models()


def drop_all():
    blueprints.drop_all_blueprints()
    models.drop_all_models()


def seed_all():
    blueprints.seed_all_blueprints()
    models.seed_all_models()


def reset():
    drop_all()
    print("Dropped All Tables")
    create_all()
    print("Created All Tables")
    seed_all()

    gamertag = 'zed3kiah'
    print(f"\nCreating user: {gamertag}")
    session = models.User.create_user(gamertag, 'password')
    admin = session.admin()
    admin(nitrado_api_key=os.getenv('NITRADO_API_KEY'))
    start = datetime(2023, 4, 1)
    end = datetime(2023, 12, 1)
    admin.update_subscription(start, end)
    print(f"User {gamertag} was created.")

    gamertag = 'maxquietgamer'
    print(f"\nCreating user: {gamertag}")
    session = models.User.create_user(gamertag, 'password')
    admin = session.admin()
    admin(nitrado_api_key=os.getenv('NITRADO_API_KEY'))
    start = datetime(2023, 4, 1)
    end = datetime(2023, 12, 1)
    admin.update_subscription(start, end)
    print(f"User {gamertag} was created.")


__all__ = ['models', 'blueprints']
