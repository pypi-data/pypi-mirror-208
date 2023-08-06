from __future__ import annotations
from dotenv import dotenv_values, load_dotenv
from sqlalchemy import create_engine
import os


load_dotenv()


class Configuration:
    @classmethod
    def new_configuration(cls, env_file: str) -> Configuration:
        print("\tos.environ:")
        for k, v in os.environ.items():
            if 'MYSQL' in k:
                print(f"\t\t{k}={v}")
        print(f"\tdotenv_values() [{len(dotenv_values())}]:")
        for k, v in dotenv_values().items():
            if 'MYSQL' in k:
                print(f"\t\t{k}={v}")
        print(f"\tdotenv_values({repr(env_file)}):")
        for k, v in dotenv_values(env_file).items():
            if 'MYSQL' in k:
                print(f"\t\t{k}={v}")

        config = {
            **os.environ,
            **dotenv_values(),
            **dotenv_values(env_file),
        }
        print(f"\tconfig({repr(env_file)}):")
        for k, v in config.items():
            if 'MYSQL' in k:
                print(f"\t\t{k}={v}")

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
    def development(cls):
        print('development:')
        return cls.new_configuration('.env.development')

    @classmethod
    def production(cls):
        print('production:')
        return cls.new_configuration('.env.production')

    @classmethod
    def testing(cls):
        print('testing:')
        return cls.new_configuration('.env.testing')

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
        url = f"mysql://{self.username}{password}@{self.host}:{self.port}{database}{kwargs}"
        return url

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
