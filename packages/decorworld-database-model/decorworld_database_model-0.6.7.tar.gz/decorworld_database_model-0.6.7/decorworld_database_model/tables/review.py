from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load
from .product import ProductSchema
from .base import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    product_id = Column(ForeignKey('products.id'), nullable=False)
    name = Column(String(30), nullable=False)
    rating = Column(Integer, nullable=False)
    description = Column(String(100), nullable=True)

    product = relationship('Product', primaryjoin='Product.id == Review.product_id')


class ReviewSchema(Schema):

    model_class = Review

    id = fields.Integer()
    date = fields.DateTime()
    product_id = fields.Integer(data_key='productId')
    name = fields.String()
    rating = fields.Integer()
    description = fields.String()

    product = fields.Nested(ProductSchema, many=False)

    @post_load
    def make_review(self, data, **kwargs):
        return Review(**data)
