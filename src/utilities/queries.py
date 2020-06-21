import pandas as pd

from schema.universe import Company, PersonTable
from schema.insco import Customer, Policy
from utilities.connections import (
    connect_universe,
    connect_company)


def query_population():
    session, connection = connect_universe()
    query = session.query(PersonTable).statement
    population = pd.read_sql(query, connection)
    connection.close()
    return population


def query_company():
    session, connection = connect_universe()
    companies_query = session.query(Company).statement
    companies = pd.read_sql(
        companies_query,
        connection
    )
    connection.close()
    return companies


def query_all_policies():
    companies = query_company()
    policies = pd.DataFrame()

    for index, row in companies.iterrows():
        company_id = row['company_id']
        company_name = row['company_name']
        session, connection = connect_company(company_name)
        query = session.query(Policy).statement
        policy_c = pd.read_sql(
            query,
            connection
        )
        policy_c['company_id'] = company_id
        policy_c['company_name'] = company_name
        policies = policies.append(policy_c)
        connection.close()

    return policies


def query_in_force_policies(curr_date):
    companies = get_company_names()
    in_force = pd.DataFrame()

    for company in companies:
        session, connection = connect_company(company)

        exp_query = session.query(
            Policy
        ).filter(
            Policy.expiration_date == curr_date
        ).statement

        company_in_force = pd.read_sql(
            exp_query,
            connection)

        in_force = in_force.append(
            company_in_force,
            ignore_index=True
        )

        connection.close()
    return in_force


def get_company_names():
    session, connection = connect_universe()
    companies_query = session.query(Company.company_name).statement
    companies = pd.read_sql(
        companies_query,
        connection
    )
    connection.close()
    return list(companies['company_name'])


def get_company_ids():
    session, connection = connect_universe()
    companies_query = session.query(Company.company_id).statement
    companies = pd.read_sql(companies_query, connection)
    connection.close()
    return list(companies['company_id'])


def get_uninsured_ids(curr_date):
    population = query_population()
    in_force = query_in_force_policies(curr_date)
    uninsureds = population[~population['person_id'].isin(in_force['person_id'])]['person_id']
    return uninsureds


def get_customer_ids(company):
    session, connection = connect_company(company)
    id_query = session.query(Customer.person_id).statement
    ids = pd.read_sql(id_query, connection)
    return ids