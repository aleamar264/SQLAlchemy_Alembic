from sqlalchemy import  create_engine, URL
url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password='postgres',
    host='db_postgresql',
    database='testuser',
    port=5432
)

engine = create_engine(url, echo=True)


from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

session_ = sessionmaker(engine)

with session_() as session:
    session.execute(text("some text"))
    session.commit()