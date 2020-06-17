import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import schema.universe as universe


def connect_universe():
    engine = sa.create_engine(
        'sqlite:///db/universe.db',
        echo=True
    )
    session = sessionmaker(bind=engine)
    universe.Base.metadata.create_all(engine)
    session = session()
    connection = engine.connect()
    return session, connection
