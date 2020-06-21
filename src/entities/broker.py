import numpy as np
import pandas as pd
import datetime

from random import choices
from parameters import INITIAL_PREMIUM

from utilities.connections import(
    connect_universe,
    connect_company
)
from utilities.queries import (
    get_company_names,
    get_customer_ids,
    get_uninsured_ids,
    query_company,
    query_all_policies,
    query_in_force_policies,
    query_population
)

from schema.universe import (
    Event
)


class Broker:

    def identify_free_business(
            self,
            curr_date
    ):
        # get expiring policies for each company
        market = query_in_force_policies(curr_date)

        # get people with no policy
        new_business = pd.DataFrame(get_uninsured_ids(curr_date))

        market = market.append(new_business)

        return market

    def place_business(
            self,
            curr_date,
            *args
    ):
        free_business = self.identify_free_business(curr_date)
        population = query_population()
        free_business = free_business.merge(population, on='person_id', how='left')
        # determine market status
        if sum(free_business['policy_id'].notnull()) == 0:
            market_status = 'initial_pricing'
        else:
            market_status = 'renewal'

        companies = query_company()

        if market_status == 'initial_pricing':
            free_business['company_id'] = choices(
                companies.company_id,
                k=len(free_business)
            )
            free_business['premium'] = INITIAL_PREMIUM
            free_business['effective_date'] = curr_date + datetime.timedelta(1)
            free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)

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
            free_business['company_id'] = free_business['company_id'].astype('int')

        for company in companies.company_id:
            company_name = companies[companies['company_id'] == company]['company_name']
            company_name = company_name.squeeze()
            new_business = free_business[free_business['company_id'] == company]
            new_policies = new_business[[
                'person_id',
                'effective_date',
                'expiration_date',
                'premium'
            ]]

            customer = new_business[[
                'person_id',
                'age_class',
                'profession',
                'health_status',
                'education_level'

            ]]

            existing_customers = get_customer_ids(company_name)
            customer = customer[~customer['person_id'].isin(existing_customers['person_id'])]

            session, connection = connect_company(company_name)

            new_policies.to_sql(
                'policy',
                connection,
                index=False,
                if_exists='append'
            )

            customer.to_sql(
                'customer',
                connection,
                index=False,
                if_exists='append'
            )
            connection.close()

    def report_claims(self, report_date):
        # match events to policies in which they are covered
        session, connection = connect_universe()

        event_query = session.query(Event).\
            filter(Event.report_date == report_date).\
            statement

        events = pd.read_sql(event_query, connection)
        connection.close()

        policies = query_all_policies()
        claims = events.merge(
            policies,
            on='person_id',
            how='left'
        )
        claims = claims.query(
            'event_date >= effective_date '
            'and event_date <= expiration_date'
        )

        claims = claims.drop([
            'effective_date',
            'expiration_date',
            'premium',
            'company_id'
        ], axis=1)

        companies = get_company_names()
        for company in companies:
            reported_claims = claims[claims['company_name'] == company]

            reported_claims = reported_claims.rename(columns={
                'event_date': 'occurrence_date',
                'ground_up_loss': 'incurred_loss'
            })

            reported_claims = reported_claims.drop(['company_name'], axis=1)

            session, connection = connect_company(company)
            reported_claims.to_sql(
                'claim',
                connection,
                index=False,
                if_exists='append'
            )
            connection.close()
