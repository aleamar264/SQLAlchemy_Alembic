from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import DECIMAL, String, ForeignKey, Integer, create_engine, URL, BIGINT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import func


url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="postgres",
    host="db_postgresql",
    database="testuser",
    port=5432,
)
engine = create_engine(url, echo=True)


class Base(DeclarativeBase):
    pass


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


"""This way of create the table is when  we dont create any Annotated
variable"""
# class Users(Base, TimeStampMixin, TableNameMixin):
#     telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
#     full_name: Mapped[str] = mapped_column(String(255), nullable=False)
#     username: Mapped[str] = mapped_column(String(255), nullable=True)
#     language_code: Mapped[str] = mapped_column(String(255), nullable=False)
#     referrer_id: Mapped[int] = mapped_column(
#         BIGINT, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
#     )


int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
user_fk = Annotated[
    int, mapped_column(BIGINT, ForeignKey("users.telegram_id", ondelete="CASCADE"))
]
str_255 = Annotated[str, mapped_column(String(255))]


class Users(Base, TimeStampMixin, TableNameMixin):
    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    full_name: Mapped[str_255]
    username: Mapped[Optional[str_255]]
    # language_code: Mapped[str_255]
    language_code: Mapped[str] = mapped_column(String(15))
    referrer_id: Mapped[Optional[user_fk]]

    orders: Mapped[list["Orders"]] = relationship(back_populates="user")


class Products(Base, TimeStampMixin, TableNameMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str]] = mapped_column(String(3000))
    price: Mapped[float] = mapped_column(DECIMAL(precision=16, scale=4))


class Orders(Base, TimeStampMixin, TableNameMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]
    products: Mapped[list["OrderProducts"]] = relationship()
    user: Mapped["Users"] = relationship(back_populates="orders")


class OrderProducts(Base, TableNameMixin):
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    quatity: Mapped[int]
    product: Mapped["Products"] = relationship()
