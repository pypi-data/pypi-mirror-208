from __future__ import annotations
from flask import Flask, Blueprint
from flask.ctx import AppContext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
from arkdata.database.configuration import Configuration
from sqlalchemy import inspect
from enum import Enum


DATABASE_URI = Configuration.mysql_database().uri()
TEST_DATABASE_URI = Configuration.test_mysql_database().uri()


class DatabaseType(Enum):
    production_database = DATABASE_URI
    test_database = TEST_DATABASE_URI


class Database:
    @classmethod
    def default_app(cls, *args, **kwargs):
        app = Flask(__name__, *args, **kwargs)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    @classmethod
    def default_test_app(cls, *args, **kwargs):
        test_app = Flask(__name__, *args, **kwargs)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return test_app

    def __init__(self):
        if not database_exists(DATABASE_URI):
            create_database(DATABASE_URI)
        if not database_exists(TEST_DATABASE_URI):
            create_database(TEST_DATABASE_URI)
        self.database_type = DatabaseType.production_database
        self.production_app: Flask = Database.default_app()
        self.production_db: SQLAlchemy = SQLAlchemy(self.production_app)
        self.test_app: Flask = Database.default_test_app()
        self.test_db: SQLAlchemy = SQLAlchemy(self.test_app)

    @property
    def app(self) -> Flask:
        if self.database_type == DatabaseType.production_database:
            if self.production_app is None:
                raise ConnectionError("Cursor needs to be connected to the database.")
            return self.production_app
        else:
            if self.test_app is None:
                raise ConnectionError("Cursor needs to be connected to the database.")
            return self.test_app

    @property
    def db(self) -> SQLAlchemy:
        if self.database_type == DatabaseType.production_database:
            if self.production_db is None:
                raise ConnectionError("Cursor needs to be connected to the database.")
            return self.production_db
        elif self.database_type == DatabaseType.test_database:
            if self.test_db is None:
                raise ConnectionError("Cursor needs to be connected to the database.")
            return self.test_db

    def is_connected(self):
        if self.database_type == DatabaseType.production_database:
            if self.production_app is None or self.production_db is None:
                return False
        elif self.test_app is None or self.test_db is None:
            return False
        with self.app_context():
            return self.db.engine is not None

    def set_test_database(self) -> None:
        self.database_type = DatabaseType.test_database

    def set_production_database(self) -> None:
        self.database_type = DatabaseType.production_database

    def app_context(self) -> AppContext:
        return self.app.app_context()

    def has_table(self, table_name: str):
        with self.app_context():
            inspector = inspect(self.db.engine)
            return inspector.has_table(table_name)

    def create_database(self):
        if self.database_exists():
            return
        if self.database_type == DatabaseType.production_database:
            create_database(DATABASE_URI)
        else:
            create_database(TEST_DATABASE_URI)

    def database_exists(self) -> bool:
        if self.database_type == DatabaseType.production_database:
            return database_exists(DATABASE_URI)
        else:
            return database_exists(TEST_DATABASE_URI)

    def drop_database(self) -> None:
        if not self.database_exists():
            return
        if self.database_type == DatabaseType.production_database:
            drop_database(DATABASE_URI)
        else:
            drop_database(TEST_DATABASE_URI)

    def rollback(self) -> None:
        with self.app_context():
            self.db.session.rollback()

    def tables(self) -> list:
        with self.app_context():
            try:
                inspector = inspect(self.db.engine)
                return inspector.get_table_names()
            except Exception as e:
                if not self.database_exists():
                    return []
                raise e

    def register_blueprint(self, blueprint: Blueprint):
        self.production_app.register_blueprint(blueprint)
        self.test_app.register_blueprint(blueprint)

    @property
    def template_folder(self):
        return self.app.template_folder

    @template_folder.setter
    def template_folder(self, path: str):
        self.production_app.template_folder = path
        self.test_app.template_folder = path

    @property
    def static_folder(self):
        return self.app.static_folder

    @static_folder.setter
    def static_folder(self, path: str):
        self.production_app.static_folder = path
        self.test_app.static_folder = path

    @property
    def static_url_path(self):
        return self.app.static_url_path

    @static_url_path.setter
    def static_url_path(self, path: str):
        self.production_app.static_url_path = path
        self.test_app.static_url_path = path

    def __call__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self.production_app, k, v)
            setattr(self.test_app, k, v)
        return self


sqlalchemy = Database()
