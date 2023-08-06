from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from sqlalchemy import func
from sqlalchemy import String
from marshmallow import fields
from marshmallow import Schema
from marshmallow import post_load
from enum import Enum as ENUM
from .order_item import OrderItemSchema
from .shipping_method import ShippingMethodSchema
from .payment_method import PaymentMethodSchema
from marshmallow_enum import EnumField

from .base import Base


class OrderStatus(ENUM):
    RECEIVED = 'Beérkezett'
    CONFIRMED = 'Visszaigazolt'
    TRANSIT = 'Szállítás alatt'
    CLOSED = 'Lezárt'
    DELETED = 'Törölt'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_number = Column(String(25), nullable=False, unique=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, server_default='78')
    order_date = Column(DateTime, nullable=False, server_default=func.now())
    updated_date = Column(DateTime, nullable=True, onupdate=func.now())
    status = Column(Enum(OrderStatus), nullable=False)
    contact_email = Column(String(30), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    shipping_name = Column(String(30), nullable=False)
    shipping_zip_code = Column(String(4), nullable=False)
    shipping_city = Column(String(25), nullable=False)
    shipping_address = Column(String(25), nullable=False)
    shipping_description = Column(String(50), nullable=True)
    invoice_name = Column(String(30), nullable=False)
    invoice_zip_code = Column(String(4), nullable=False)
    invoice_city = Column(String(25), nullable=False)
    invoice_address = Column(String(25), nullable=False)
    invoice_tax_number = Column(String(25), nullable=True)
    invoice_description = Column(String(50), nullable=True)
    shipping_method = Column(ForeignKey('shipping_methods.id'), nullable=False)
    payment_method = Column(ForeignKey('payment_methods.id'), nullable=False)

    order_items = relationship('OrderItem', primaryjoin='Order.id == OrderItem.order_id')
    shipping = relationship('ShippingMethod', primaryjoin='Order.shipping_method == ShippingMethod.id')
    payment = relationship('PaymentMethod', primaryjoin='Order.payment_method == PaymentMethod.id')


class OrderSchema(Schema):

    model_class = Order

    id = fields.Integer()
    order_number = fields.String(data_key='orderNumber')
    user_id = fields.Integer(load_only=True, data_key='userID')
    order_date = fields.DateTime(data_key='orderDate')
    updated_date = fields.DateTime(data_key='updatedDate', allow_none=True)
    status = EnumField(OrderStatus, by_value=True)
    contact_email = fields.String(data_key='contactEmail')
    contact_phone = fields.String(data_key='contactPhone')
    shipping_name = fields.String(data_key='shippingName')
    shipping_zip_code = fields.String(data_key='shippingZipCode')
    shipping_city = fields.String(data_key='shippingCity')
    shipping_address = fields.String(data_key='shippingAddress')
    shipping_description = fields.String(data_key='shippingDescription', allow_none=True)
    invoice_name = fields.String(data_key='invoiceName')
    invoice_zip_code = fields.String(data_key='invoiceZipCode')
    invoice_city = fields.String(data_key='invoiceCity')
    invoice_address = fields.String(data_key='invoiceAddress')
    invoice_tax_number = fields.String(data_key='invoiceTaxNumber', allow_none=True)
    invoice_description = fields.String(data_key='invoiceDescription', allow_none=True)
    shipping_method = fields.Integer(data_key='shippingMethod')
    payment_method = fields.Integer(data_key='paymentMethod')

    order_items = fields.Nested(OrderItemSchema, many=True, data_key='orderItems')
    shipping = fields.Nested(ShippingMethodSchema, many=False)
    payment = fields.Nested(PaymentMethodSchema, many=False)

    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)
