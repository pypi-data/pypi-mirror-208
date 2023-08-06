from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load

from .base import Base


class InvoiceData(Base):
    __tablename__ = 'invoice_data'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    name = Column(String(30), nullable=False)
    zip_code = Column(String(4), nullable=False)
    city = Column(String(25), nullable=False)
    address = Column(String(25), nullable=False)
    tax_number = Column(String(25), nullable=True)
    description = Column(String(50), nullable=True)


class InvoiceDataSchema(Schema):

    model_class = InvoiceData

    id = fields.Integer()
    user_id = fields.Integer(load_only=True, data_key='userID')
    name = fields.String()
    zip_code = fields.String(data_key='zipCode')
    city = fields.String()
    address = fields.String()
    tax_number = fields.String(allow_none=True, data_key='taxNumber')
    description = fields.String(allow_none=True)

    @post_load
    def make_invoice_data(self, data, **kwargs):
        return InvoiceData(**data)
