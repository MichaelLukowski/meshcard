import logging
import re
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector


def setup_database(
    user,
    password,
    database,
    root_user="postgres",
    host="",
    no_drop=False,
    no_user=False,
):  # pragma: no cover
    """
    setup the user and database
    """

    if not no_drop:
        try_drop_test_data(user, database)

    engine = create_engine(
        "postgresql://{user}@{host}/postgres".format(user=root_user, host=host)
    )
    conn = engine.connect()
    conn.execute("commit")

    create_stmt = 'CREATE DATABASE "{database}"'.format(database=database)
    try:
        conn.execute(create_stmt)
    except Exception:
        logging.warning("Unable to create database")

    if not no_user:
        try:
            user_stmt = "CREATE USER {user} WITH PASSWORD '{password}'".format(
                user=user, password=password
            )
            conn.execute(user_stmt)

            perm_stmt = (
                "GRANT ALL PRIVILEGES ON DATABASE {database} to {password}"
                "".format(database=database, password=password)
            )
            conn.execute(perm_stmt)
            conn.execute("commit")
        except Exception:
            logging.warning("Unable to add user")
    conn.close()


def create_tables(host, user, password, database):  # pragma: no cover
    """
    create tables
    """
    engine = create_engine(
        "postgresql://{user}:{pwd}@{host}/{db}".format(
            user=user, host=host, pwd=password, db=database
        )
    )
    conn = engine.connect()

    create_card_table = "CREATE TABLE node_cards (\
        commons_name VARCHAR NOT NULL, card JSONB, PRIMARY KEY (commons_name))"

    try:
        conn.execute(create_card_table)
    except Exception:
        logging.warning("Unable to create table")
        raise
    finally:
        conn.close()


