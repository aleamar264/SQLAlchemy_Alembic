"""Alembic
Initial migration
    - alembic revision --autogenerate -m "Initial migration"
    - alembic upgrade head (+1/2/3/4/....)
"""

import asyncio
from curses import echo
import random
from re import L
from typing import Optional, Sequence
from faker import Faker
from sqlalchemy import bindparam, delete, func, select, update
from sqlalchemy.orm import Session, aliased
from lesson2 import OrderProducts, Orders, Products, Users
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Repo:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    # def add_user(self, telegram_id: int, full_name: str,
    #              language_code: str, username: Optional[str] = None):

    #     user = Users(
    #         telegram_id = telegram_id,
    #         full_name=full_name,
    #         username=username,
    #         language_code=language_code
    #     )

    #     self.session.add(user)
    #     self.session.commit()
    #     return user

    async def add_user(
        self,
        telegram_id: int,
        full_name: str,
        language_code: str,
        username: Optional[str] = None,
        referrer_id: Optional[int] = None,
    ):
        stmt = (
            insert(Users)
            .values(
                telegram_id=telegram_id,
                full_name=full_name,
                language_code=language_code,
                referrer_id=referrer_id,
                username=username,
            )
            .on_conflict_do_update(
                index_elements=[Users.telegram_id],
                set_=dict(username=username, full_name=full_name),
            )
            .returning(Users)
        )

        stmt = select(Users).from_statement(stmt)
        result = await self.session.scalars(stmt)
        await self.session.commit()
        return result.first()

    async def get_user_by_id(self, telegram_id: int) -> Optional[Users]:
        stmt = select(Users).where(Users.telegram_id == telegram_id)
        results = await self.session.execute(stmt)
        return results.scalars().first()

    async def get_users(self) -> Sequence[Users]:
        stmt = select(Users)
        results = await self.session.execute(stmt)
        return results.scalars().all()

    async def add_order(self, user_id: int) -> Optional[Orders]:
        smtm = select(Orders).from_statement(
            insert(Orders).values(user_id=user_id).returning(Orders)
        )
        result = await self.session.scalars(smtm)
        await self.session.commit()
        return result.first()

    async def add_product(
        self, title: str, description: str, price: int
    ) -> Optional[Products]:
        smtm = select(Products).from_statement(
            insert(Products)
            .values(title=title, description=description, price=price)
            .returning(Products)
        )
        result = await self.session.scalars(smtm)
        await self.session.commit()
        return result.first()

    async def add_product_to_order(
        self, order_id: int, product_id: int, quatity: int
    ) -> Optional[OrderProducts]:
        order_product = OrderProducts(
            order_id=order_id, product_id=product_id, quatity=quatity
        )
        self.session.add(order_product)
        await self.session.commit()

    async def select_all_invited_users(self):
        """Inner JOIN or JOIN"""
        ParentUser = aliased(Users)
        ReferralUser = aliased(Users)

        stmt = select(
            ParentUser.full_name.label("parent_name"),
            ReferralUser.full_name.label("referral_name"),
        ).join(ReferralUser, ReferralUser.referrer_id == ParentUser.telegram_id)

        result = await self.session.execute(stmt)
        return result.all()

    async def get_all_user_orders(self, telegram_id: int):
        stmt = (
            select(Products, Orders, Users)
            .join(Users.orders)
            .join(Orders.products)
            .join(Products)
            .where(Users.telegram_id == telegram_id)
        )
        results = await self.session.execute(stmt)
        return results.all()

    async def get_total_number_of_orders(self):
        stmt = (
            select(func.count(Orders.order_id).label("quantity"), Users.full_name)
            .join(Users)
            .group_by(Users.telegram_id)
        )

        result = await self.session.execute(stmt)
        return result

    async def get_total_number_of_orders_with_sum(self):
        stmt = (
            select(func.sum(OrderProducts.quatity).label("quantity"), Users.full_name)
            .join(Orders, Orders.order_id == OrderProducts.order_id)
            .join(Users)
            .group_by(Users.telegram_id)
            .having(func.sum(OrderProducts.quatity) > 15000)
        )

        result = await self.session.execute(stmt)
        return result

    async def set_new_referrer(self, user_id: int, referrer_id: int):
        stmt = (
            update(Users)
            .where(Users.telegram_id == user_id)
            .values(referrer_id=referrer_id)
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_user_by_id(self, telegram_id: int):
        stmt = delete(Users).where(Users.telegram_id == telegram_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_products_to_order(self, order_id: int, products: list[dict]):
        """bindparam extract the value from the key given in the dictionary.

        Like this is a list, we can add multiple values in one list"""
        stmt = insert(OrderProducts).values(
            order_id=order_id,
            product_id=bindparam("prodcut_id"),
            quatity=bindparam("quatity"),
        )

        await self.session.execute(stmt, products)


async def seed_fake_data(repo: Repo):
    Faker.seed(0)
    fake = Faker()
    users = []
    orders = []
    products = []

    for _ in range(10):
        referrer_id = None if not users else users[-1].telegram_id
        user = repo.add_user(
            telegram_id=fake.pyint(),
            full_name=fake.name(),
            language_code=fake.language_code(),
            username=fake.user_name(),
            referrer_id=referrer_id,
        )
        users.append(user)

    for _ in range(10):
        order = repo.add_order(
            user_id=random.choice(users).telegram_id,
        )
        orders.append(order)

    for _ in range(10):
        product = repo.add_product(
            title=fake.word(), description=fake.sentence(), price=fake.pyint()
        )
        products.append(product)

    for order in orders:
        for product in random.sample(products, 3):
            await repo.add_product_to_order(
                order_id=order.order_id,
                product_id=product.product_id,
                quatity=fake.pyint(),
            )


if __name__ == "__main__":
    from environs import Env
    from sqlalchemy import URL, create_engine
    from sqlalchemy.orm import sessionmaker

    env = Env()
    env.read_env(".env")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=env.str("POSTGRES_USER"),
        password=env.str("POSTGRES_PASSWORD"),
        host=env.str("DATABASE_HOST"),
        database=env.str("POSTGRES_DB"),
        port=5432,
    )
    # sychronous
    # engine = create_engine(url)
    # session_pool = sessionmaker(engine)
    # async
    engine = create_async_engine(url, echo=True)
    session_pool = async_sessionmaker(engine)

    async def main():
        async with session_pool() as session:
            repo = Repo(session)
            # Fake data
            # seed_fake_data(repo)
            # Add user manually
            # repo.add_user(
            #     telegram_id=1,
            #     full_name="Jhon Doe",
            #     username="some_joe",
            #     language_code='en'
            # )

            # user = repo.get_user_by_id(1)
            # print(f"user: {user.full_name}: {user.telegram_id}")
            # for row in repo.select_all_invited_users():
            #     print(f"Parent: {row.parent_name}, Referral: {row.referral_name}")

            # for user in repo.get_users():
            #     print(f"User: {user.full_name} ({user.telegram_id})")
            #     for orders in user.orders:
            #         print(f"    Order: {orders.order_id}")
            #         for product in orders.products:
            # print(f"    Product: {product.product.title}")

            # users_orders = repo.get_all_user_orders(telegram_id=9882)
            # for product, order, user in users_orders:
            #     print(
            #         f"#{product.product_id}  Product: {product.title} Order: {order.order_id} - {user.full_name}"
            #     )

            # number_of_orders = repo.get_total_number_of_orders()
            # for num_of_order, full_name in number_of_orders:
            #     print(f"Total number of orders: {num_of_order} by {full_name}")

            sum_of_orders = await repo.get_total_number_of_orders_with_sum()
            for quantity, full_name in sum_of_orders:
                print(f"Sum of orders {quantity} - {full_name}")

    asyncio.run(main())
