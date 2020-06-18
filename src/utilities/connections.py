import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import schema.universe as universe


def connect_universe():
    engine = sa.create_engine(
        'sqlite:///db/universe.db',
        echo=True
    )
    session = sessionmaker(bind=engine)()
    connection = engine.connect()
    return session, connection


def connect_company(company_name):
    engine = sa.create_engine(
        'sqlite:///db/' + company_name + '.db',
        echo=True)
    session = sessionmaker(bind=engine)()
    connection = engine.connect()
    return session, connection
