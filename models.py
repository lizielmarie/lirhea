from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from datetime import datetime


# New way to define Base in SQLAlchemy 2.0+
class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'products'

    id         : Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id : Mapped[str]      = mapped_column(String(10), unique=True, nullable=False)
    name       : Mapped[str]      = mapped_column(String(100), nullable=False)
    stock      : Mapped[int]      = mapped_column(Integer, nullable=False, default=0)
    price      : Mapped[float]    = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.product_id} | {self.name} | Stock: {self.stock}>'


class Order(Base):
    __tablename__ = 'orders'

    id         : Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id : Mapped[str]      = mapped_column(String(10), ForeignKey('products.product_id'), nullable=False)
    quantity   : Mapped[int]      = mapped_column(Integer, nullable=False)
    total      : Mapped[float]    = mapped_column(Float, nullable=False)
    status     : Mapped[str]      = mapped_column(String(20), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Order {self.id} | Product {self.product_id} | Qty: {self.quantity} | {self.status}>'


class Payment(Base):
    __tablename__ = 'payments'

    id         : Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id   : Mapped[int]      = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    amount     : Mapped[float]    = mapped_column(Float, nullable=False)
    status     : Mapped[str]      = mapped_column(String(20), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Payment {self.id} | Order {self.order_id} | Amount: {self.amount} | {self.status}>'