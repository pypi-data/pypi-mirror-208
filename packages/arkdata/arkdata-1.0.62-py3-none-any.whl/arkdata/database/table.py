from __future__ import annotations
from .cursor import sqlalchemy
from typing_extensions import TypedDict
from sqlalchemy import Integer, Column, String
import json
from pathlib import Path
from datetime import datetime
import sys


def datetime_now():
    return str(datetime.now())


class Table:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(100), default=datetime_now)
    updated_at = Column(String(100), default=datetime_now)

    @classmethod
    def all(cls) -> list[Table | sqlalchemy.db.Model]:
        with sqlalchemy.app_context():
            return sqlalchemy.db.session.query(cls).all()

    @classmethod
    def find_by(cls, **kwargs) -> Table | sqlalchemy.db.Model | None:
        if len(kwargs) == 0:
            return
        args = [cls.__dict__[param] == arg for param, arg in kwargs.items()]
        with sqlalchemy.app_context():
            return sqlalchemy.db.session.query(cls).filter(*args).first()

    @classmethod
    def find_all_by(cls, **kwargs) -> list[Table | sqlalchemy.db.Model]:
        if len(kwargs) == 0:
            return []
        args = [cls.__dict__[param] == arg for param, arg in kwargs.items()]
        with sqlalchemy.app_context():
            record = sqlalchemy.db.session.query(cls).filter(*args).all()
            return record

    @classmethod
    def columns(cls) -> list[str]:
        return cls.metadata.tables[cls.__tablename__].columns.keys()

    @classmethod
    def first(cls) -> Table | sqlalchemy.db.Model:
        with sqlalchemy.app_context():
            return sqlalchemy.db.session.query(cls).first()

    @classmethod
    def length(cls) -> int:
        with sqlalchemy.app_context():
            return sqlalchemy.db.session.query(cls).count()

    @classmethod
    def bulk_insert(cls, values: list[dict]) -> BulkInsert:
        with sqlalchemy.app_context():
            inserted_records = []
            failed = []
            for kwargs in values:
                try:
                    record = cls(**kwargs)
                    sqlalchemy.db.session.add(record)
                    inserted_records.append(record)
                except Exception:
                    failed.append(failed)
            sqlalchemy.db.session.commit()
            inserted_record_ids = [r.id for r in inserted_records]
            inserted = sqlalchemy.db.session.query(cls).filter(cls.id.in_(inserted_record_ids)).all()
            return {
                "inserted": inserted,
                "inserted_count": len(inserted),
                "failed": failed,
                "failed_count": len(failed),
            }

    @classmethod
    def bulk_update(cls, values: list[dict]) -> BulkUpdate:
        with sqlalchemy.app_context():
            updated_ids = []
            failed = []
            for kwargs in values:
                try:
                    if 'id' not in kwargs:
                        failed.append(kwargs)
                        continue
                    record = cls.find_by(id=kwargs['id'])
                    if record is None:
                        failed.append(kwargs)
                        continue
                    for key, val in kwargs.items():
                        setattr(record, key, val)
                    record.updated_at = datetime_now()
                    updated_ids.append(record.id)
                    sqlalchemy.db.session.add(record)
                except Exception:
                    failed.append(kwargs)
            sqlalchemy.db.session.commit()
            updated = sqlalchemy.db.session.query(cls).filter(cls.id.in_(updated_ids)).all()
            return {
                "updated": updated,
                "updated_count": len(updated),
                "failed": failed,
                "failed_count": len(failed),
            }

    @classmethod
    def bulk_delete(cls, items: list[Table | sqlalchemy.db.Model]) -> BulkDelete:
        with sqlalchemy.app_context():
            deleted = []
            failed = []
            for item in items:
                try:
                    data = dict(item)
                    sqlalchemy.db.session.delete(item)
                    deleted.append(data)
                except Exception:
                    failed.append(item)
            sqlalchemy.db.session.commit()
            return {
                'deleted': deleted,
                'deleted_count': len(deleted),
                'failed': failed,
                'failed_count': len(failed),
            }

    @classmethod
    def drop_table(cls) -> bool:
        if cls.table_exists():
            with sqlalchemy.app_context():
                try:
                    cls.__table__.drop(sqlalchemy.db.engine)
                except Exception:
                    return False
        return not cls.table_exists()

    @classmethod
    def create_table(cls) -> bool:
        if not cls.table_exists():
            with sqlalchemy.app_context():
                try:
                    cls.__table__.create(sqlalchemy.db.engine, checkfirst=True)

                    return True
                except Exception:
                    return False

    @classmethod
    def clear_table(cls) -> None:
        if cls.table_exists():
            cls.drop_table()
            cls.create_table()

    @classmethod
    def table_exists(cls) -> bool:
        return sqlalchemy.has_table(cls.__tablename__)

    @classmethod
    def __file_path(cls) -> Path:
        """File path of current class"""
        return Path(sys.modules[cls.__module__].__file__)

    @classmethod
    def __seed_path(cls) -> Path:
        """Directory of the seeds"""
        parent = cls.__file_path().parent
        seeds = parent / Path('seeds')
        if not seeds.exists():
            seeds.mkdir()
        return seeds

    @classmethod
    def __seed_table(cls, path: Path or str) -> None:
        if not cls.table_exists():
            cls.create_table()
        file = Path(path)
        if not file.exists():
            raise FileNotFoundError(f'Could not find: {str(file)}')
        if not file.suffix.lower() == '.json':
            raise FileNotFoundError(f'File must be of type .json : {str(file)}')
        with open(file, 'r') as r:
            values = json.load(r)
            assert isinstance(values, list)
            cls.bulk_insert(values)

    @classmethod
    def seed_table(cls) -> None:
        name = cls.__tablename__.lower()
        file = cls.__seed_path() / Path(f'{name}.json')
        if not file.exists():
            with open(file, 'w') as w:
                json.dump([], w)
            return
        cls.__seed_table(file)

    @classmethod
    def group_by(cls):
        # TODO: add a group by
        # need execution to consoladate because
        # not all bots in the same server
        # e.g. group_by server_id
        pass

    def create(self) -> Table | sqlalchemy.db.Model:
        with sqlalchemy.app_context():
            sqlalchemy.db.session.add(self)
            sqlalchemy.db.session.commit()
            return self.find_by(id=self.id)

    def delete(self) -> bool:
        with sqlalchemy.app_context():
            try:
                sqlalchemy.db.session.delete(self)
                sqlalchemy.db.session.commit()
                return True
            except Exception:
                return False

    def keys(self) -> list[str]:
        return self.columns()

    def values(self) -> list:
        return [getattr(self, key) for key in self.keys()]

    def items(self):
        for key in self.columns():
            yield key, getattr(self, key)

    def __getitem__(self, key):
        assert key in self.keys(), f"'{key}' must be of {self.columns()}"
        return getattr(self, key)

    def __call__(self, *args, **kwargs):
        difference = set(kwargs.keys()).difference(set(self.columns()))
        error_message = f"{difference} are not Columns of '{self.__tablename__}': {self.columns()}"
        assert len(difference) == 0, error_message
        with sqlalchemy.app_context():
            for key, val in kwargs.items():
                setattr(self, key, val)
            self.updated_at = datetime_now()
            sqlalchemy.db.session.add(self)
            sqlalchemy.db.session.commit()
            return self.find_by(id=self.id)

    def __str__(self):
        table_name = self.__tablename__.title().replace("_", "")
        items = []
        for k, v in dict(self).items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96m{table_name}\033[0m({args})>\033[0m'

    def __repr__(self):
        table_name = self.__tablename__.title().replace("_", "")
        items = []
        for k, v in dict(self).items():
            items.append(f"{k}={repr(v)}")
        args = ', '.join(items)
        return f'{table_name}({args})'


class BulkInsert(TypedDict, total=True):
    inserted: list[Table | sqlalchemy.db.Model]
    inserted_count: int
    failed: list[Table | sqlalchemy.db.Model]
    failed_count: int


class BulkUpdate(TypedDict, total=True):
    updated: list[Table | sqlalchemy.db.Model]
    updated_count: int
    failed: list[Table | sqlalchemy.db.Model]
    failed_count: int


class BulkDelete(TypedDict, total=True):
    deleted: list[Table | sqlalchemy.db.Model]
    deleted_count: int
    failed: list[Table | sqlalchemy.db.Model]
    failed_count: int