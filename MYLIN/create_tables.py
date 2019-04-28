import psycopg2
import os
from config import config

#keep the config file out of the repository until I figure out a more secure way to handle this
ini_path = os.path.abspath(os.path.join(__file__,"../../..","database.ini"))

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE Claim (
            vendor_id SERIAL PRIMARY KEY,
            loss_amount NUMERIC NOT NULL
        )
        """,
        )
    conn = None
    try:
        # read the connection parameters
        params = config(ini_path)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
