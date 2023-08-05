from arkdata.models.account import Account
from arkdata.models.cart_item import CartItem
from arkdata.models.command import Command
from arkdata.models.order_item import OrderItem
from arkdata.models.product import Product
from arkdata.models.user import User
from arkdata.models.server import Server
from arkdata.models.sessions import Session
from arkdata.models.admin import Admin
from arkdata.models.developer import Developer


__all__ = ['Account',
           'Admin',
           'Developer',
           'CartItem',
           'Command',
           'OrderItem',
           'Product',
           'User',
           'Server',
           'Session',
]


def seed_all_models():
    for model in __all__:
        print(f"\rSeeding {model:.<20}", end='')
        try:
            eval(f'{model}.seed_table()')
            print("completed.")
        except Exception:
            print("ERROR.")


def create_all_models():
    for model in __all__:
        eval(f'{model}.create_table()')


def clear_all_models():
    for model in __all__:
        eval(f'{model}.clear_table()')


def drop_all_models():
    for model in __all__:
        eval(f'{model}.drop_table()')
