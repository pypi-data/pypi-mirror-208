from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    product_id = Column(ForeignKey('products.id'), nullable=False)


class FavoriteSchema(Schema):

    model_class = Favorite

    id = fields.Integer()
    user_id = fields.Integer(data_key='userID')
    product_id = fields.Integer(data_key='productID')

    @post_load
    def make_favorite(self, data, **kwargs):
        return Favorite(**data)
