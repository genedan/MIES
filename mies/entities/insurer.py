import numpy as np
import os
import pandas as pd
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker

import schema.insco as insco
from schema.insco import Claim, Customer, Policy
from schema.universe import Company
from utilities.connections import connect_company


class Insurer:
    def __init__(
        self,
        starting_capital,
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
        self.company_name = company_name

        self.pricing_model = None
        self.id = self.__register()

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

    def price_book(
        self,
        pricing_formula
    ):
        book_query = self.session.query(
            Policy.policy_id,
            Policy.person_id,
            Customer.age_class,
            Customer.profession,
            Customer.health_status,
            Customer.education_level,
            Claim.incurred_loss).outerjoin(
                Claim,
                Claim.policy_id == Policy.policy_id).\
            outerjoin(Customer, Policy.person_id == Customer.person_id).statement

        book = pd.read_sql(book_query, self.connection)

        book = book.groupby([
            'policy_id',
            'person_id',
            'age_class',
            'profession',
            'health_status',
            'education_level']
        ).agg({'incurred_loss': 'sum'}).reset_index()

        book['rands'] = np.random.uniform(size=len(book))
        book['sevresp'] = book['incurred_loss']

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
