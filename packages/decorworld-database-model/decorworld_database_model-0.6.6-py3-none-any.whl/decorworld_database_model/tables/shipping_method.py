from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class ShippingMethod(Base):
    __tablename__ = 'shipping_methods'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(30), nullable=False)
    price = Column(Integer, nullable=False)


class ShippingMethodSchema(Schema):

    model_class = ShippingMethod

    id = fields.Integer()
    name = fields.String()
    price = fields.Integer()

    @post_load
    def make_shipping_method(self, data, **kwargs):
        return ShippingMethod(**data)
