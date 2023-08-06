from arkdata.models.account import Account
from arkdata.models.cart_item import CartItem
from arkdata.models.command import Command
from arkdata.models.order_item import OrderItem
from arkdata.models.product import Product
from arkdata.models.user import User
from arkdata.models.sessions import Session


__all__ = ['Account',
           'CartItem',
           'Command',
           'OrderItem',
           'Product',
           'User',
           'Session',
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
