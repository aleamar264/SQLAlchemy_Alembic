FROM python:3.12-alpine
RUN apk update && apk upgrade

WORKDIR /home/app
RUN  pip install --upgrade pip
RUN pip install  psycopg2-binary asyncpg SQLAlchemy alembic environs