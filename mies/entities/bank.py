import datetime as dt
import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

import mies.schema.bank as bank
from mies.schema.bank import Account, Customer, Insurer, Person, Transaction
from mies.schema.bank import Bank as BankTable
from mies.utilities.connections import connect_universe
from mies.utilities.queries import query_bank_id


class Bank:
    def __init__(self, starting_capital, bank_name, path='db/banks/', date_established=dt.datetime(1, 12, 31)):
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
        self.name = bank_name
        self.date_established = date_established
        self.id = self.__register()
        self.get_customers(self.id, 'bank')
        self.cash_account = self.assign_account(
            customer_id=self.id,
            account_type='cash'
        )
        self.capital_account = self.assign_account(self.id, 'capital')
        self.liability_account = self.assign_account(self.id, 'liability')
        self.make_transaction(
            self.cash_account,
            self.capital_account,
            self.date_established,
            starting_capital
        )

    def __register(self):
        # populate universe company record
        insurer_table = pd.DataFrame([[self.name]], columns=['bank_name'])
        session, connection = connect_universe()
        insurer_table.to_sql(
            'bank',
            connection,
            index=False,
            if_exists='append'
        )
        bank_id = query_bank_id(self.name)
        return bank_id

    def get_customers(self, ids, customer_type):
        new_customers = pd.DataFrame()
        new_customers[customer_type + '_id'] = pd.Series(ids)
        new_customers['customer_type'] = customer_type

        objects = []
        for index, row in new_customers.iterrows():
            if customer_type == 'person':
                customer_type_table = Person(person_id=row[customer_type + '_id'])
            elif customer_type == 'insurer':
                customer_type_table = Insurer(insurer_id=row[customer_type + '_id'])
            else:
                customer_type_table = BankTable(bank_id=row[customer_type + '_id'])

            customer = Customer(
                customer_type=customer_type
            )
            customer_type_table.customer.append(customer)
            objects.append(customer_type_table)
            #self.session.add(customer_type_table)
            #self.session.commit()
        self.session.add_all(objects)
        self.session.commit()

    def assign_accounts(self, customer_ids, account_type):
        """
        assign multiple accounts given customer ids
        """
        new_accounts = pd.DataFrame()
        new_accounts['customer_id'] = customer_ids
        new_accounts['account_type'] = account_type

        new_accounts.to_sql(
            'account',
            self.connection,
            index=False,
            if_exists='append'
        )

    def assign_account(self, customer_id, account_type):
        """
        assign a single account for a customer
        """
        account = Account(customer_id=int(customer_id), account_type=account_type)
        self.session.add(account)
        self.session.commit()
        return account.account_id

    def make_transaction(self, debit_account, credit_account, transaction_date, transaction_amount):
        """
        make a single transaction
        """
        transaction = Transaction(
            debit_account=int(debit_account),
            credit_account=int(credit_account),
            transaction_date=transaction_date,
            transaction_amount=transaction_amount
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction.transaction_id

    def make_transactions(self, data: pd.DataFrame):
        """
        accepts a DataFrame to make multiple transactions
        need debit, credit, transaction date, transaction amount
        """
        data['debit_account'] = data['debit_account'].astype(int)
        data['credit_account'] = data['credit_account'].astype(int)
        data.to_sql(
            'transaction',
            self.connection,
            index=False,
            if_exists='append'
        )

