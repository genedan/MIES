# queries requiring subqueries from the other files should be defined here

import pandas as pd
from sqlalchemy.sql import func

from mies.schema.bank import Transaction

from mies.schema.insco import Policy

from mies.schema.universe import (
    BankTable,
    Company,
    PersonTable)

from mies.utilities.connections import (
    connect_bank,
    connect_universe,
    connect_company)

from mies.utilities.queries.bank_queries import (
    query_accounts_by_person_id
)


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


def query_bank_id(bank_name):
    session, connection = connect_universe()
    id_query = session.query(BankTable.bank_id).filter(BankTable.bank_name == bank_name).statement
    bank_id = pd.read_sql(id_query, connection).iat[0, 0]
    connection.close()
    return bank_id


def query_banks():
    session, connection = connect_universe()
    banks_query = session.query(BankTable).statement
    banks = pd.read_sql(
        banks_query,
        connection
    )
    connection.close()
    return banks


def query_company():
    session, connection = connect_universe()
    companies_query = session.query(Company).statement
    companies = pd.read_sql(
        companies_query,
        connection
    )
    connection.close()
    return companies


def get_company_ids():
    session, connection = connect_universe()
    companies_query = session.query(Company.company_id).statement
    companies = pd.read_sql(companies_query, connection)
    connection.close()
    return list(companies['company_id'])


def get_company_names():
    session, connection = connect_universe()
    companies_query = session.query(Company.company_name).statement
    companies = pd.read_sql(
        companies_query,
        connection
    )
    connection.close()
    return list(companies['company_name'])


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


def query_incomes(person_ids):
    session, connection = connect_universe()

    income_query = session.query(
        PersonTable.person_id,
        PersonTable.income
    ).statement

    incomes = pd.read_sql(
        income_query,
        connection
    )

    incomes = incomes[incomes['person_id'].isin(person_ids)]

    connection.close()

    return incomes


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


def query_population():
    session, connection = connect_universe()
    query = session.query(PersonTable).statement
    population = pd.read_sql(query, connection)
    connection.close()
    return population


def query_population_wealth():
    """
    get wealth for each person in the population
    """
    population = query_population()

    person_ids = population['person_id']

    banks = query_banks()

    pop_wealth = pd.DataFrame()

    for index, row in banks.iterrows():

        bank_name = row['bank_name']

        session, connection = connect_bank(bank_name)

        debit_query = session.query(
            Transaction.debit_account,
            func.sum(Transaction.transaction_amount)
        ).group_by(Transaction.debit_account).statement

        debit_amounts = pd.read_sql(
            debit_query,
            connection
        )
        debit_amounts.columns = [
            'account_id',
            'debits'
        ]

        credit_query = session.query(
            Transaction.credit_account,
            func.sum(Transaction.transaction_amount)
        ).group_by(Transaction.credit_account).statement

        credit_amounts = pd.read_sql(
            credit_query,
            connection
        )
        credit_amounts.columns = [
            'account_id',
            'credits'
        ]

        person_accounts = query_accounts_by_person_id(
            person_ids,
            bank_name,
            'cash'
        )

        wealth = person_accounts.merge(
            debit_amounts,
            on='account_id',
            how='left'
        )

        wealth = wealth.merge(
            credit_amounts,
            on='account_id',
            how='left'
        )

        wealth['debits'] = wealth['debits'].fillna(0)

        wealth['credits'] = wealth['credits'].fillna(0)

        wealth = wealth[[
            'person_id',
            'account_id',
            'debits',
            'credits'
        ]]

        wealth = wealth.groupby([
            'person_id',
            'account_id'
        ])[[
            'debits',
            'credits'
        ]].agg('sum').reset_index()

        wealth['wealth'] = wealth['debits'] - wealth['credits']

        wealth = wealth[[
            'person_id',
            'wealth'
        ]]
        wealth = wealth.groupby(['person_id'])['wealth'].agg('sum').reset_index()

        pop_wealth.append(wealth)
        connection.close()

    return wealth


def get_uninsured_ids(curr_date):
    population = query_population()
    in_force = query_in_force_policies(curr_date)
    uninsureds = population[~population['person_id'].isin(in_force['person_id'])]['person_id']
    return uninsureds
