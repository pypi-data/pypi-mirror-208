from __future__ import annotations
import os
from dotenv import dotenv_values, load_dotenv
from collections import defaultdict
from sqlalchemy import create_engine


load_dotenv()


config = defaultdict(lambda: None)
config.update({
    **os.environ,                       # load computer environment variables
    **dotenv_values(),            # override computer environment variables with .env variables
    **dotenv_values(".env.secret"),     # load sensitive variables
})


class Configuration:
    @classmethod
    def mysql_database(cls) -> Configuration:
        username = 'MYSQL_USERNAME' in config and config['MYSQL_USERNAME'] or 'root'
        password = 'MYSQL_PASSWORD' in config and config['MYSQL_PASSWORD'] or None

        host = 'MYSQL_HOST' in config and config['MYSQL_HOST'] or "127.0.0.1"
        port = 'MYSQL_PORT' in config and config['MYSQL_PORT'] or "3306"
        database = 'MYSQL_DATABASE' in config and config['MYSQL_DATABASE'] or None
        options = {}
        if 'MYSQL_SSL_MODE' in config:
            options["ssl"] = 'require'
        return Configuration(username=username, host=host, port=port, password=password, database=database, **options)

    @classmethod
    def test_mysql_database(cls) -> Configuration:
        username = 'MYSQL_TEST_USERNAME' in config and config['MYSQL_TEST_USERNAME'] or 'root'
        password = 'MYSQL_TEST_PASSWORD' in config and config['MYSQL_TEST_PASSWORD'] or None

        host = 'MYSQL_TEST_HOST' in config and config['MYSQL_TEST_HOST'] or "127.0.0.1"
        port = 'MYSQL_TEST_PORT' in config and config['MYSQL_TEST_PORT'] or "3306"
        database = 'MYSQL_TEST_DATABASE' in config and config['MYSQL_TEST_DATABASE'] or None
        options = {}
        if 'MYSQL_TEST_SSL_MODE' in config:
            options["ssl"] = 'require'
        return Configuration(username=username, host=host, port=port, password=password, database=database, **options)

    def __init__(
            self,
            username: str = "root",
            host: str = "127.0.0.1",
            port: str = "3306",
            password: str = None,
            database: str = None,
            **kwargs
    ):
        self.username = username
        self.host = host
        self.port = port
        self.database = database
        self.password = password
        self.kwargs = kwargs

    def uri(self):
        password = f':{self.password}' if self.password else ''
        database = f'/{self.database}' if self.database else ''
        kwargs = '?' + '&'.join([f'{k}={v}' for k, v in self.kwargs.items()]) if self.kwargs else ''
        return f"mysql://{self.username}{password}@{self.host}:{self.port}{database}{kwargs}"

    def engine(self):
        password = f':{self.password}' if self.password else ''
        database = f'/{self.database}' if self.database else ''
        uri = f"mysql://{self.username}{password}@{self.host}:{self.port}{database}"
        return create_engine(uri, connect_args=self.kwargs)

    def __str__(self):
        return self.uri()

    def __repr__(self):
        username = f"username={self.username}"
        host = f"host={self.host}"
        port = f"port={self.port}"
        database = f"database={self.database}"
        args = ', '.join([database, host, port, username])
        return f'<Configuration({args})>'
