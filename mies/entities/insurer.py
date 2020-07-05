import numpy as np
import os
import pandas as pd
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker

import schema.insco as insco
from entities.bank import Bank
from schema.insco import Claim, ClaimTransaction, Customer, Policy
from schema.universe import Company
from utilities.connections import connect_company
from utilities.queries import query_customers_by_insurer_id
from utilities.queries import query_open_case_reserves
from utilities.queries import query_accounts_by_person_id
from utilities.queries import query_pricing_model_data


class Insurer:
    def __init__(
        self,
        starting_capital,
        bank: Bank,
        inception_date,
        company_name
    ):
        if not os.path.exists('db/companies'):
            os.makedirs('db/companies')
        self.engine = sa.create_engine(
            'sqlite:///db/companies/' + company_name + '.db',
            echo=True
        )
        session = sessionmaker(bind=self.engine)
        insco.Base.metadata.create_all(self.engine)
        self.session = session()
        self.connection = self.engine.connect()
        self.capital = starting_capital
        self.bank = bank
        self.cash_account = None
        self.liability_account = None
        self.capital_account = None
        self.company_name = company_name

        self.pricing_model = None
        self.id = self.__register()
        self.__get_bank_account(inception_date)

    def __register(self):
        # populate universe company record
        insurer_table = pd.DataFrame([[self.capital, self.company_name]], columns=['capital', 'company_name'])
        universe_engine = sa.create_engine(
            'sqlite:///db/universe.db',
            echo=True
        )
        session = sessionmaker(bind=universe_engine)
        universe_session = session()
        universe_connection = universe_engine.connect()
        insurer_table.to_sql(
            'company',
            universe_connection,
            index=False,
            if_exists='append'
        )
        self.id = pd.read_sql(universe_session.query(Company.company_id).
                              filter(Company.company_name == self.company_name).
                              statement, universe_connection).iat[0, 0]
        universe_connection.close()
        return self.id

    def __get_bank_account(self, transaction_date):
        self.bank.get_customers(self.id, 'insurer')
        customer_id = query_customers_by_insurer_id([self.id], self.bank.name)
        self.cash_account = self.bank.assign_account(customer_id, 'cash')
        self.liability_account = self.bank.assign_account(customer_id, 'liability')
        self.capital_account = self.bank.assign_account(customer_id, 'capital')
        self.bank.make_transaction(self.cash_account, self.liability_account, transaction_date, self.capital)

    def price_book(
        self,
        pricing_formula
    ):

        book = query_pricing_model_data(self.company_name)

        self.pricing_model = smf.glm(
            formula=pricing_formula,
            data=book,
            family=sm.families.Tweedie(
                link=statsmodels.genmod.families.links.log,
                var_power=1.5
            )).fit()

        return self.pricing_model

    def get_book(
        self,
        person,
        policy,
        event
    ):
        book_query = self.session.query(
            policy.policy_id,
            person.person_id,
            person.age_class,
            person.profession,
            person.health_status,
            person.education_level,
            event.severity).outerjoin(
            person,
            person.person_id == policy.person_id).outerjoin(event, event.policy_id == policy.policy_id).filter(
            policy.company_id == int(self.id))

        book = pd.read_sql(book_query.statement, self.connection)

        book = book.groupby([
            'policy_id',
            'person_id',
            'age_class',
            'profession',
            'health_status',
            'education_level'
        ]).agg({'severity': 'sum'}).reset_index()

        return book

    def in_force(
            self,
            date
    ):
        session, connection = connect_company(self.company_name)
        in_force_query = session.query(Policy).filter(
                date >= Policy.effective_date).filter(date <= Policy.expiration_date).statement

        in_force = pd.read_sql(
            in_force_query,
            connection
        )
        connection.close()
        return in_force

    def pay_claims(self, transaction_date):
        # send checks to bank
        case_reserves = query_open_case_reserves(self.company_name)

        accounts_to_pay = query_accounts_by_person_id(
            case_reserves['person_id'],
            self.bank.name, 'cash'
        )

        case_reserves = case_reserves.merge(
            accounts_to_pay,
            on='person_id',
            how='left'
        )

        case_reserves['transaction_date'] = transaction_date

        case_reserves = case_reserves.rename(columns={
            'case reserve': 'transaction_amount',
            'account_id': 'debit_account'
        })

        case_reserves['credit_account'] = self.cash_account

        payments = case_reserves[[
            'debit_account',
            'credit_account',
            'transaction_date',
            'transaction_amount']].copy()

        self.bank.make_transactions(payments)

        # people then use checks to pay their for their own losses

        payments = payments.rename(
            columns={
                'debit_account': 'credit_account',
            }
        )

        payments['debit_account'] = self.bank.liability_account

        self.bank.make_transactions(payments)


        # reduce case reserves

        objects = []

        for index, row in case_reserves.iterrows():
            reserve_takedown = ClaimTransaction(
                claim_id = row['claim_id'],
                transaction_date=row['transaction_date'],
                transaction_type='reduce case reserve',
                transaction_amount=row['transaction_amount']
            )
            claim_payment = ClaimTransaction(
                claim_id=row['claim_id'],
                transaction_date=row['transaction_date'],
                transaction_type='claim payment',
                transaction_amount=row['transaction_amount']
            )
            close_claim = ClaimTransaction(
                claim_id=row['claim_id'],
                transaction_date=row['transaction_date'],
                transaction_type='close claim',
                transaction_amount=0
            )
            objects.append(reserve_takedown)
            objects.append(claim_payment)
            objects.append(close_claim)

        self.session.add_all(objects)
        self.session.commit()
