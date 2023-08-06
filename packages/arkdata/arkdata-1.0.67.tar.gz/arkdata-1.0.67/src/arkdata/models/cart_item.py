from ..database.cursor import sqlalchemy
from ..database.table import Table
from sqlalchemy import Column, String, Integer
from arkdata import models
from secrets import token_hex


class CartItem(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), nullable=False)
    product_id = Column(Integer, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    @classmethod
    def purchase(cls, xuid: str):
        cart_items = CartItem.find_all_by(xuid=xuid)
        order_number = token_hex(10).upper()
        for item in cart_items:
            order = models.OrderItem(
                xuid=item.xuid,
                order_id=order_number,
                product_id=item.product_id,
                quantity=item.quantity,
            )
            item.delete()
            sqlalchemy.db.session.add(order)
        sqlalchemy.db.session.commit()

    @classmethod
    def total(cls, xuid) -> int:
        cart_items = CartItem.find_all_by(xuid=xuid)
        total = 0
        for cart_item in cart_items:
            product = models.Product.find_by(product_id=cart_item.product_id)
            total += product.price
        return total


    def __init__(self, xuid=None, product_id=None, quantity=1):
        self.xuid = xuid
        self.product_id = product_id
        self.quantity = quantity
