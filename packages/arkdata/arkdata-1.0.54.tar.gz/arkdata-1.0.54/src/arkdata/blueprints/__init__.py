from .armour import Armour
from .ammunition import Ammunition
from .artifact import Artifact
from .attachment import Attachment
from .consumable import Consumable
from .creature import Creature
from .dye import Dye
from .egg import Egg
from .farm import Farm
from .recipe import Recipe
from .resource import Resource
from .saddle import Saddle
from .seed import Seed
from .skin import Skin
from .structure import Structure
from .tool import Tool
from .trophy import Trophy
from .weapon import Weapon


__all__ = ['Ammunition',
           'Armour',
           'Artifact',
           'Attachment',
           'Consumable',
           'Creature',
           'Dye',
           'Egg',
           'Farm',
           'Recipe',
           'Resource',
           'Saddle',
           'Seed',
           'Skin',
           'Structure',
           'Tool',
           'Trophy',
           'Weapon',
]

def seed_all_blueprints():
    for bp in __all__:
        print(f"\rSeeding {bp:.<20}", end='')
        try:
            eval(f'{bp}.seed_table()')
            print("completed.")
        except Exception:
            print("ERROR.")


def create_all_blueprints():
    for bp in __all__:
        eval(f'{bp}.create_table()')


def clear_all_blueprints():
    for bp in __all__:
        eval(f'{bp}.clear_table()')


def drop_all_blueprints():
    for bp in __all__:
        eval(f'{bp}.drop_table()')
