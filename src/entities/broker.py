import pandas as pd
import numpy as np
import datetime


from random import choices
from parameters import INITIAL_PREMIUM
from schema.universe import Company
from utilities.connections import connect_universe
from utilities.connections import connect_company
from schema.insco import Policy
from schema.universe import PersonTable


class Broker:

    def identify_free_business(
            self,
            curr_date
    ):
        # get expiring policies for each company
        companies = self.identify_companies()
        market = pd.DataFrame()
        for company in companies:

            session, connection = connect_company(company)

            exp_query = session.query(
                Policy.policy_id,
                Policy.person_id,
                Policy.effective_date,
                Policy.expiration_date,
            ).filter(
                Policy.expiration_date == curr_date
            ).statement

            expiring_book = pd.read_sql(
                exp_query,
                connection)

            market = market.append(
                expiring_book,
                ignore_index=True
            )

            connection.close()

        # get people with no policy
        session, connection = connect_universe()

        new_business_query = session.query(
            PersonTable.person_id
        ).statement

        new_business = pd.read_sql(
            new_business_query,
            connection
        )

        connection.close()

        market = market.append(new_business)

        return market

    def place_business(
            self,
            curr_date,
            *args
    ):
        free_business = self.identify_free_business(curr_date)
        # determine market status
        if sum(free_business['policy_id'].notnull()) == 0:
            market_status = 'initial_pricing'
        else:
            market_status = 'renewal'

        companies = self.query_company()

        if market_status == 'initial_pricing':
            free_business['company_id'] = choices(companies.company_id, k=len(free_business))
            free_business['premium'] = INITIAL_PREMIUM
            free_business['effective_date'] = curr_date + datetime.timedelta(1)
            free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)

            for company in companies.company_id:
                company_name = companies[companies['company_id'] == company]['name']
                company_name = company_name.squeeze()
                new_business = free_business[free_business['company_id'] == company]
                new_business = new_business[[
                    'person_id',
                    'effective_date',
                    'expiration_date',
                    'premium'
                ]]
                session, connection = connect_company(company_name)

                new_business.to_sql(
                    'policy',
                    connection,
                    index=False,
                    if_exists='append'
                )
                connection.close()

        else:
            # for arg in args:
            #     free_business['effective_date'] = curr_date + datetime.timedelta(1)
            #     free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)
            #     free_business['rands'] = np.random.uniform(len(free_business))
            #     free_business['quote_' + str(arg.id)] = arg.pricing_model.predict(free_business)
            #
            # free_business['premium'] = free_business[free_business.columns[pd.Series(
            #     free_business.columns).str.startswith('quote_')]].min(axis=1)
            # free_business['company_id'] = free_business[free_business.columns[pd.Series(
            #     free_business.columns).str.startswith('quote_')]].idxmin(axis=1).str[-1]
            #
            # renewal_business = free_business[[
            #     'company_id',
            #     'person_id',
            #     'effective_date',
            #     'expiration_date',
            #     'premium']]
            #
            # renewal_business.to_sql(
            #     'policy',
            #     self.connection,
            #     index=False,
            #     if_exists='append'
            # )
            # return free_business
            return None

    def identify_companies(self):
        session, connection = connect_universe()
        companies_query = session.query(Company.name).statement
        companies = pd.read_sql(companies_query, connection)
        return list(companies['name'])

    def get_company_ids(self):
        session, connection = connect_universe()
        companies_query = session.query(Company.company_id).statement
        companies = pd.read_sql(companies_query, connection)
        return list(companies['company_id'])

    def query_company(self):
        session, connection = connect_universe()
        companies_query = session.query(Company).statement
        companies = pd.read_sql(companies_query, connection)
        return companies
