from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    name = Column(String(30), nullable=False)
    zip_code = Column(String(4), nullable=False)
    city = Column(String(25), nullable=False)
    address = Column(String(25), nullable=False)
    description = Column(String(50), nullable=True)


class AddressSchema(Schema):

    model_class = Address

    id = fields.Integer()
    user_id = fields.Integer(load_only=True, data_key='userID')
    name = fields.String()
    zip_code = fields.String(data_key='zipCode')
    city = fields.String()
    address = fields.String()
    description = fields.String(allow_none=True)

    @post_load
    def make_address(self, data, **kwargs):
        return Address(**data)
