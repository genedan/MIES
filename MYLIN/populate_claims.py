#!/usr/bin/python

import psycopg2
import random
import os
from config import config

#keep the config file out of the repository until I figure out a more secure way to handle this
ini_path = os.path.abspath(os.path.join(__file__,"../../..","database.ini"))

#Generate random claims to  be inserted into the Claim table
simple_claims = random.sample(range(1000,10000), 10)
simple_claims = [(x,) for x in simple_claims]
print(simple_claims)

def insert_claim_list(vendor_list):
    """ insert multiple claims into the Claim table  """
    sql = "INSERT INTO Claim(loss_amount) VALUES(%s)"
    conn = None
    try:
        # read database configuration
        params = config(ini_path)
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.executemany(sql,vendor_list)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    # insert multiple claims
    insert_claim_list(simple_claims)
