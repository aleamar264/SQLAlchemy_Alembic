from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, URL
from sqlalchemy import text

url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password='postgres',
    host='db_postgresql',
    database='testuser',
    port=5432
)

print(url)
engine = create_engine(url, echo=True)

session_pool = sessionmaker(engine)
# with session_pool() as session:
# session.execute(text("""
# CREATE TABLE users
# (
#     telegram_id   BIGINT PRIMARY KEY,
#     full_name     VARCHAR(255) NOT NULL,
#     username      VARCHAR(255),
#     language_code VARCHAR(255) NOT NULL,
#     created_at    TIMESTAMP DEFAULT NOW(),
#     referrer_id   BIGINT,
#     FOREIGN KEY (referrer_id)
#         REFERENCES users (telegram_id)
#         ON DELETE SET NULL
# );

# INSERT INTO users (telegram_id, full_name, username, language_code, referrer_id)
# VALUES (1, 'John Doe', 'johndoe', 'en', NULL),
# (2, 'Jane Doe', 'janedoe', 'en', 1);
#     """))
# session.commit()
# results = session.execute(text("""
#     SELECT * FROM users;
# """))
# for row in results:
#     print(row)
