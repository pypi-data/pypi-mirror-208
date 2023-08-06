from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load
from .product import ProductSchema

from .base import Base


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = Column(ForeignKey('orders.id'), nullable=False)
    product_id = Column(ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    product = relationship('Product', primaryjoin='Product.id == OrderItem.product_id')


class OrderItemSchema(Schema):

    model_class = OrderItem

    id = fields.Integer()
    order_id = fields.Integer(data_key='orderID')
    product_id = fields.Integer(data_key='productID')
    quantity = fields.Integer()
    price = fields.Integer()

    product = fields.Nested(ProductSchema, many=False)

    @post_load
    def make_order_item(self, data, **kwargs):
        return OrderItem(**data)
