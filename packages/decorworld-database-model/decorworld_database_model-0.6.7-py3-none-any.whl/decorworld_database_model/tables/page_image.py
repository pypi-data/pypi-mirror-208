from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import LONGBLOB
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class PageImage(Base):
    __tablename__ = 'page_images'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    image = Column(LONGBLOB, nullable=False)


class PageImageSchema(Schema):

    model_class = PageImage

    id = fields.Integer()
    image = fields.String()

    @post_load
    def make_image(self, data, **kwargs):
        return PageImage(**data)
