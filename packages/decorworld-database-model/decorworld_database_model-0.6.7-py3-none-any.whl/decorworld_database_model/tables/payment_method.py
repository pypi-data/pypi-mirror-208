from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class PaymentMethod(Base):
    __tablename__ = 'payment_methods'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(30), nullable=False)
    price = Column(Integer, nullable=True)


class PaymentMethodSchema(Schema):

    model_class = PaymentMethod

    id = fields.Integer()
    name = fields.String()
    price = fields.Integer()

    @post_load
    def make_payment_method(self, data, **kwargs):
        return PaymentMethod(**data)
