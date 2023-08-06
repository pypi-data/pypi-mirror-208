from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy_utils import database_exists, create_database
from arkdata.database.configuration import DATABASE_URI, TEST_DATABASE_URI
from enum import Enum


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

test_app = Flask(__name__)
test_app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class DatabaseType(Enum):
    production_database = DATABASE_URI
    test_database = TEST_DATABASE_URI


class Database:
    def __init__(self):
        self.database_type = DatabaseType.production_database
        self.production_db = SQLAlchemy(app)
        self.test_db = SQLAlchemy(test_app)

    @property
    def db(self):
        if self.database_type == DatabaseType.production_database:
            if not database_exists(DATABASE_URI):
                create_database(DATABASE_URI)
            return self.production_db
        elif self.database_type == DatabaseType.test_database:
            if not database_exists(TEST_DATABASE_URI):
                create_database(TEST_DATABASE_URI)
            return self.test_db

    def set_test_database(self):
        self.database_type = DatabaseType.test_database

    def set_production_database(self):
        self.database_type = DatabaseType.production_database
