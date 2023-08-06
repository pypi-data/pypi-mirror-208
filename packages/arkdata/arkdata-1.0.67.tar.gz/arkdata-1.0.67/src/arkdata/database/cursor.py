from __future__ import annotations
from flask import Flask, Blueprint
from flask.ctx import AppContext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
from arkdata.configuration import Configuration
from sqlalchemy import inspect
from enum import Enum
from dotenv import dotenv_values

DEVELOPMENT_URI = Configuration.development().uri()
PRODUCTION_URI = Configuration.production().uri()
TESTING_URI = Configuration.testing().uri()


class DatabaseType(Enum):
    development = DEVELOPMENT_URI
    testing = TESTING_URI
    production = PRODUCTION_URI


class Database:
    @classmethod
    def default_development_app(cls, *args, **kwargs):
        app = Flask(__name__, *args, **kwargs)
        app.config['SQLALCHEMY_DATABASE_URI'] = DEVELOPMENT_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    @classmethod
    def default_production_app(cls, *args, **kwargs):
        app = Flask(__name__, *args, **kwargs)
        app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    @classmethod
    def default_testing_app(cls, *args, **kwargs):
        test_app = Flask(__name__, *args, **kwargs)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = TESTING_URI
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return test_app

    def __init__(self):
        if not database_exists(DEVELOPMENT_URI):
            create_database(DEVELOPMENT_URI)
        if not database_exists(PRODUCTION_URI):
            create_database(PRODUCTION_URI)
        if not database_exists(TESTING_URI):
            create_database(TESTING_URI)
        env = dotenv_values('.env')
        if 'ENVIRONMENT' in env and env['ENVIRONMENT'].lower() == 'production':
            self.database_type = DatabaseType.production
        elif 'ENVIRONMENT' in env and env['ENVIRONMENT'].lower() == 'testing':
            self.database_type = DatabaseType.testing
        else:
            self.database_type = DatabaseType.development
        self.development_app: Flask = Database.default_development_app()
        self.development_db: SQLAlchemy = SQLAlchemy(self.development_app)
        self.production_app: Flask = Database.default_production_app()
        self.production_db: SQLAlchemy = SQLAlchemy(self.production_app)
        self.testing_app: Flask = Database.default_testing_app()
        self.testing_db: SQLAlchemy = SQLAlchemy(self.testing_app)

    @property
    def app(self) -> Flask:
        if self.database_type == DatabaseType.development:
            app = self.development_app
        elif self.database_type == DatabaseType.production:
            app = self.production_app
        else:
            app = self.testing_app
        if app is None:
            raise ConnectionError("Cursor needs to be connected to the database.")
        return app

    @property
    def db(self) -> SQLAlchemy:
        if self.database_type == DatabaseType.development:
            db = self.development_db
        elif self.database_type == DatabaseType.production:
            db = self.production_db
        else:
            db = self.testing_db
        if db is None:
            raise ConnectionError("Cursor needs to be connected to the database.")
        return db

    def is_connected(self):
        if self.app is None or self.db is None:
            return False
        with self.app_context():
            return self.db.engine is not None

    def set_development_database(self) -> None:
        self.database_type = DatabaseType.development

    def set_testing_database(self) -> None:
        self.database_type = DatabaseType.testing

    def set_production_database(self) -> None:
        self.database_type = DatabaseType.production

    def app_context(self) -> AppContext:
        return self.app.app_context()

    def has_table(self, table_name: str):
        with self.app_context():
            inspector = inspect(self.db.engine)
            return inspector.has_table(table_name)

    def create_database(self):
        if self.database_exists():
            return
        if self.database_type == DatabaseType.development:
            create_database(DEVELOPMENT_URI)
        if self.database_type == DatabaseType.production:
            create_database(PRODUCTION_URI)
        else:
            create_database(TESTING_URI)

    def database_exists(self) -> bool:
        if self.database_type == DatabaseType.development:
            return database_exists(DEVELOPMENT_URI)
        elif self.database_type == DatabaseType.production:
            return database_exists(PRODUCTION_URI)
        else:
            return database_exists(TESTING_URI)

    def drop_database(self) -> None:
        if not self.database_exists():
            return
        if self.database_type == DatabaseType.production:
            drop_database(DEVELOPMENT_URI)
        elif self.database_type == DatabaseType.production:
            drop_database(PRODUCTION_URI)
        else:
            drop_database(TESTING_URI)

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
        self.development_app.register_blueprint(blueprint)
        self.production_app.register_blueprint(blueprint)
        self.testing_app.register_blueprint(blueprint)

    @property
    def template_folder(self):
        return self.app.template_folder

    @template_folder.setter
    def template_folder(self, path: str):
        self.development_app.template_folder = path
        self.production_app.template_folder = path
        self.testing_app.template_folder = path

    @property
    def static_folder(self):
        return self.app.static_folder

    @static_folder.setter
    def static_folder(self, path: str):
        self.development_app.static_folder = path
        self.production_app.static_folder = path
        self.testing_app.static_folder = path

    @property
    def static_url_path(self):
        return self.app.static_url_path

    @static_url_path.setter
    def static_url_path(self, path: str):
        self.development_app.static_url_path = path
        self.production_app.static_url_path = path
        self.testing_app.static_url_path = path

    def __call__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self.production_app, k, v)
            setattr(self.testing_app, k, v)
        return self


sqlalchemy = Database()
