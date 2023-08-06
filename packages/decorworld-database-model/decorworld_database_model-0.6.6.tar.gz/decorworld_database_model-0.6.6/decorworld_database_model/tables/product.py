from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import relationship
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load
from .image import ImageSchema

from .base import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category_id = Column(ForeignKey('categories.id'), nullable=False)
    name = Column(String(50), nullable=False)
    number = Column(String(25), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    available_for_preorder = Column(Boolean, nullable=False, server_default=text('false'))
    discount = Column(Integer, nullable=False, server_default=text('0'))
    uploaded = Column(DateTime, nullable=False, server_default=func.now())
    show = Column(Boolean, nullable=False, server_default=text("true"))

    image = relationship('Image', foreign_keys='Image.product_id')


class ProductSchema(Schema):

    model_class = Product

    id = fields.Integer()
    category_id = fields.Integer(data_key='categoryID')
    name = fields.String()
    number = fields.String()
    price = fields.Integer()
    quantity = fields.Integer()
    description = fields.String()
    available_for_preorder = fields.Boolean(data_key='availableForPreorder')
    discount = fields.Integer()
    uploaded = fields.DateTime()
    show = fields.Boolean()

    image = fields.Nested(ImageSchema)

    @post_load
    def make_product(self, data, **kwargs):
        return Product(**data)
