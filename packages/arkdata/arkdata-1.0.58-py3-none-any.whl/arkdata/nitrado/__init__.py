from .service import Service
from .gameserver import GameServer
from .player import Player
from .log import Log


__all__ = [
    'Service',
    'GameServer',
    'Player',
    'Log'
]


def seed_all():
    for model in __all__:
        print(f"\rSeeding {model:.<20}", end='')
        try:
            eval(f'{model}.seed_table()')
            print("completed.")
        except Exception:
            print("ERROR.")


def create_all():
    for model in __all__:
        eval(f'{model}.create_table()')


def clear_all():
    for model in __all__:
        eval(f'{model}.clear_table()')


def drop_all():
    for model in __all__:
        eval(f'{model}.drop_table()')
