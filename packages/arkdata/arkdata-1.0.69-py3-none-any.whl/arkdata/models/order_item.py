from ..database.cursor import sqlalchemy
from ..database.table import Table
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from arkdata import models


class OrderItem(sqlalchemy.db.Model, Table):
    xuid = Column(String(100), unique=True, nullable=False)
    order_number = Column(String(100), unique=True, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    delivered = Column(Boolean, nullable=False, default=False)
    date = Column(DateTime, nullable=False, default=datetime.now())

    @classmethod
    def ship(cls, orders: list):
        for order in orders:
            order.delivered = True
        cls.commit()

    @classmethod
    def total(cls, xuid, order_id) -> int:
        orders = OrderItem.find_all_by(xuid=xuid, order_id=order_id)
        total = 0
        for order in orders:
            product = models.Product.find_by(product_id=order.product_id)
            total += product.price
        return total

    def __init__(self, xuid=None, order_id=None, product_id=None, quantity=1, delivered=False, date=datetime.now()):
        self.xuid = xuid
        self.order_number = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.delivered = delivered
        self.date = date



