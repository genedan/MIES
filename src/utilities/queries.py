import pandas as pd

from schema.universe import PersonTable
from utilities.connections import connect_universe


def query_population():
    session, connection = connect_universe()
    query = session.query(PersonTable).statement
    population = pd.read_sql(query, connection)
    return population