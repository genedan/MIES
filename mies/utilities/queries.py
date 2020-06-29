import numpy as np
import pandas as pd
from sqlalchemy.sql import func

import schema.bank as bank
from schema.bank import Account, Person
from schema.universe import BankTable, Company, PersonTable
from schema.insco import Customer, Policy
from utilities.connections import (
    connect_universe,
    connect_company,
    connect_bank)


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


def query_person(person_id):
    session, connection = connect_universe()
    person_query = session.query(PersonTable).filter(PersonTable.person_id == person_id).statement
    person = pd.read_sql(person_query, connection)
    connection.close()
    return person


def query_policy_history(person_id):
    policies = query_all_policies()
    policies = policies[policies['person_id'] == person_id]
    return policies


def query_policy(company_name, policy_id):
    session, connection = connect_company(company_name)
    policy_query = session.query(Policy).filter(Policy.policy_id == policy_id).statement
    policy = pd.read_sql(policy_query, connection)
    connection.close()
    return policy


def query_last_bank_customer_id(bank_name):
    session, connection = connect_bank(bank_name)
    max_id_query = session.query(func.max(bank.Customer.customer_id)).statement
    max_id = pd.read_sql(max_id_query, connection).squeeze()
    max_id_query = session.query(bank.Customer.customer_id).statement
    max_id = pd.read_sql(max_id_query, connection)
    return max_id


def query_bank_id(bank_name):
    session, connection = connect_universe()
    id_query = session.query(BankTable.bank_id).filter(BankTable.bank_name == bank_name).statement
    bank_id = pd.read_sql(id_query, connection).iat[0, 0]
    return bank_id


def query_accounts_by_person_id(ids, bank_name):
    session, connection = connect_bank(bank_name)
    accounts_query = session.query(Person.person_id, Person.customer_id, Account.account_id).outerjoin(Account, Person.person_id == Account.account_id).statement
    accounts = pd.read_sql(accounts_query, connection)
    return accounts