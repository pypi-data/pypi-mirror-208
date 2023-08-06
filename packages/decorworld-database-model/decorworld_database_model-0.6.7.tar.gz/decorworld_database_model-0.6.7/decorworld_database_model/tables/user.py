from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import TINYINT
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    active = Column(TINYINT, nullable=False, server_default='0')
    registration_date = Column(DateTime, nullable=False, server_default=func.now())
    activation_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True, onupdate=func.now())
    role = Column(String(5), nullable=False, server_default='User')


class UserSchema(Schema):

    model_class = User

    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    password = fields.String(load_only=True)
    active = fields.Integer()
    registration_date = fields.DateTime(data_key='registrationDate')
    activation_date = fields.DateTime(data_key='activationDate')
    updated_date = fields.DateTime(data_key='updatedDate')
    role = fields.String()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)
