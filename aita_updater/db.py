from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config


def db_create_engine():
    db_string = config('DB_STRING')
    try:
        engine = create_engine(db_string)
    except TypeError:
        raise ValueError("You need to specify DB_STRING in .env")
    return engine


@contextmanager
def session_context(engine):
    session = sessionmaker(engine)()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        session.invalid = True


