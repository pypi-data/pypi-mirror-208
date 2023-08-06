from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(25), nullable=False)


class CategorySchema(Schema):

    model_class = Category

    id = fields.Integer()
    name = fields.String()

    @post_load
    def make_category(self, data, **kwargs):
        return Category(**data)
