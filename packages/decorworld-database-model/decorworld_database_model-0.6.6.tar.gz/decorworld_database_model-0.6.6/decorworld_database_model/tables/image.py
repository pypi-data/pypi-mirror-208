from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_id = Column(ForeignKey('products.id'), nullable=False)
    image = Column(LONGBLOB, nullable=False)


class ImageSchema(Schema):

    model_class = Image

    id = fields.Integer()
    product_id = fields.Integer(data_key='productID')
    image = fields.String()

    @post_load
    def make_image(self, data, **kwargs):
        return Image(**data)
