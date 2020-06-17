import pandas as pd
import numpy as np
import datetime

import sqlalchemy as sa
from random import choices
from schema.universe import Company
from utilities.connections import connect_universe

from sqlalchemy.orm import sessionmaker


class Broker:

    def identify_free_business(
            self,
            person,
            policy,
            curr_date
    ):
        # free business should probably become a view instead
        market = pd.read_sql(self.session.query(
            person,
            policy.policy_id,
            policy.company_id,
            policy.effective_date,
            policy.expiration_date,
            policy.premium
        ).outerjoin(policy).statement, self.connection)
        free_business = market[
            (market['expiration_date'] >= curr_date) |
            (market['policy_id'].isnull())
        ]
        return free_business

    def place_business(
            self,
            free_business,
            companies,
            market_status,
            curr_date,
            *args
    ):
        if market_status == 'initial_pricing':
            free_business['company_id'] = choices(companies.company_id, k=len(free_business))
            free_business['premium'] = 4000
            free_business['effective_date'] = curr_date + datetime.timedelta(1)
            free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)

            for company in companies.company_id:
                new_business = free_business[free_business['company_id'] == company]
                new_business = new_business[[
                    'company_id',
                    'person_id',
                    'effective_date',
                    'expiration_date',
                    'premium'
                ]]

                new_business.to_sql(
                    'policy',
                    self.connection,
                    index=False,
                    if_exists='append'
                )
        else:
            for arg in args:
                free_business['effective_date'] = curr_date + datetime.timedelta(1)
                free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)
                free_business['rands'] = np.random.uniform(len(free_business))
                free_business['quote_' + str(arg.id)] = arg.pricing_model.predict(free_business)

            free_business['premium'] = free_business[free_business.columns[pd.Series(
                free_business.columns).str.startswith('quote_')]].min(axis=1)
            free_business['company_id'] = free_business[free_business.columns[pd.Series(
                free_business.columns).str.startswith('quote_')]].idxmin(axis=1).str[-1]

            renewal_business = free_business[[
                'company_id',
                'person_id',
                'effective_date',
                'expiration_date',
                'premium']]

            renewal_business.to_sql(
                'policy',
                self.connection,
                index=False,
                if_exists='append'
            )
            return free_business

    def identify_companies(self):
        session, connection = connect_universe()
        companies_query = session.query(Company.name).statement
        companies = pd.read_sql(companies_query, connection)
        return companies
