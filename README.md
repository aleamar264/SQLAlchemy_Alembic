Functions that works like introduction to SQLAlchemy 2.0 and Alembic.

Here we cover the creation of tables (Alembic) and respectives schemas 
(SQLAlchemy), using relationships (ForeignKey and relationship(back_populate)).

How create versions of the schema (migrations) and upgrade/downgrade this.

Also cover how to convert the engine from Sync -> Async, how modify the functions
and how call this.

---

How speed up the querys using join

---

## How create a session in SQLAlchemy.
To create a simple session (conection to database) we need to pass the url and create the conection.

```python
from sqlalchemy import  create_engine, URL
from sqlalchemy.orm import sessionmaker
url = URL.create(
    drivername="postgresql+psycopg2",
    username="some_user",
    password='some_password',
    host='some_host',
    database='some_db',
    port=5432
)
engine = create_engine(url, echo=True)
session_ = sessionmaker(engine)
```

With this block of code, we create an engine and session. If we want, we can create some library called `tool` or `utils` and add this code, to reuse in several scripts.

when we use the session,  need to close the conection when we finish using some query.

```python
session.add(some_query)
session.commit()
session.close()
```

But to don't forget this part, we can use the context manager
```python
with session_() as session:
    session.add(some_query)
    session.commit()
```
## Creation of tables
Like we are using the version 2.0 we now mapped the python variables to SQL variables, for this we use `Mapped` for the type hint.

```python
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)
from sqlalchemy import BIGINT, String


class Base(DeclarativeBase):
    pass

class Example(Base):
    __tablename__ = 'example'
    id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255)
    )
```

For any table that we want to create, we need to follow this patron. If we want to assign the name automatically, we can use the propertie `@declared_attr.directive` in a separate class.

```python
from sqlalchemy.ext.declarative import declared_attr


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class Example(Base, TableNameMixin):
    ...
```

With this way the name of the table should be `"example"`.

Other new feature, is that we can create a new variable for repetitive columns using the type hint `Annotated`.

```python
from typing_extensions import Annotated


int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
str_255 = Annotated[str, mapped_column(String(255))]

class Example(Base, TableNameMixin):
    id: Mapped[int_pk]
    full_name: Mapped[str_255]
```

If we use a lot of times a column with a string of 255 length or a column with primary key integer and autoincrement.

## References between tables

To reference a value from one table to other we use the `ForeignKey`

```python
from sqlalchemy import ForeignKey

fk_ = Annotated[int, mapped_column(Integer, ForeignKey("example.id", ondelete="CASCADE"))]


class Example(Base, TableNameMixin):
    ...


class Example2(Base, TableNameMixin):
    ...
    some_column: Mapped[fk_]

```

## Relationship

## Create tables on PostgreSQL

To create the tables in PostgreSQL we use a tool called Alembic, with this we can modify (alter) the tables, save the versions of the this and come back when want thanks an auxiliar table (version table). In this part alembix generate a code for the creation of the tables, but is not perfect, sometimes we need to make a little revision and make some modifications.

```shell
alembic init name_of_migration
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

The use of `alembic upgrade head` is to use the last version of the tables, if we want to use an specific version we need to pass the `UUID` of the version.

### How configure alembic

Always is a good idea not use hard coded credential, so in this case we use a `.env` file.

```env
POSTGRES_USER=""
POSTGRES_PASSWORD=""
DATABASE_HOST=""
POSTGRES_DB=""
```

```python
from environs import Env

env = Env()
env.read_env('.env')

url = URL.create(
    drivername="postgresql+psycopg2",
    username=env.str("POSTGRES_USER"),
    password=env.str('POSTGRES_PASSWORD'),
    host=env.str('DATABASE_HOST'),
    database=env.str('POSTGRES_DB'),
    port=5432
)

```

First we need to create the url to connect to the database, after that set that url like the url for alembic

```python

config.set_main_option(
    "sqlalchemy.url",
    url.render_as_string(hide_password=False)
)
```

But how we get the tables to create? fot this we need to import all the tables that we created earlier

```python
from mymodel import Base

...

target_metadata = Base.metadata
```

With this, alembic will search all the tables with dependencies of the class `Base`. If we have multiple models, we can use this like a list `target_metadata = [Base.metadata, Base2.metadata, ..., Basen.metadata]`