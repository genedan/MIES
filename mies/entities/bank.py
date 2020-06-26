import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

import schema.bank as bank


class Bank:
    def __init__(self, starting_capital, bank_name, path='db/banks/'):
        if not os.path.exists(path):
            os.makedirs(path)
        self.engine = sa.create_engine(
            'sqlite:///' + path + bank_name + '.db',
            echo=True
        )
        session = sessionmaker(bind=self.engine)
        bank.Base.metadata.create_all(self.engine)
        self.session = session()
        self.connection = self.engine.connect()
        self.capital = starting_capital
        self.name = bank_name

    def get_customers(self, person_ids):
        new_customers = pd.DataFrame()
        new_customers['customer_id']

    def assign_account(self, customer_ids, account_type):
        new_accounts = pd.DataFrame()
        new_accounts['account_id'] = person_ids
        new_accounts['account_type'] = account_type

        new_accounts.to_sql(
            name='account',
            con=self.connection,
            index=False,
            if_exists='append'
        )
