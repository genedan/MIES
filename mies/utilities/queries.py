import numpy as np
import pandas as pd
from sqlalchemy.sql import func

import schema.bank as bank
from schema.bank import Account, Insurer, Person, Transaction
from schema.universe import BankTable, Company, Event, PersonTable
from schema.insco import Claim, ClaimTransaction, Customer, Policy
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


def query_banks():
    session, connection = connect_universe()
    banks_query = session.query(BankTable).statement
    banks = pd.read_sql(
        banks_query,
        connection
    )
    connection.close()
    return banks


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
    connection.close()
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
    connection.close()
    return max_id


def query_bank_id(bank_name):
    session, connection = connect_universe()
    id_query = session.query(BankTable.bank_id).filter(BankTable.bank_name == bank_name).statement
    bank_id = pd.read_sql(id_query, connection).iat[0, 0]
    connection.close()
    return bank_id


def query_accounts_by_person_id(person_ids, bank_name, account_type):
    session, connection = connect_bank(bank_name)

    accounts_query = session.query(
        Person.person_id,
        Person.customer_id,
        Account.account_id
    ).outerjoin(
        Account,
        Person.customer_id == Account.customer_id
    ).filter(
        Account.account_type == account_type
    ).statement

    accounts = pd.read_sql(
        accounts_query,
        connection
    )

    accounts = accounts[accounts['person_id'].isin(person_ids)]

    connection.close()

    return accounts


def query_accounts_by_company_id(insurer_ids, bank_name, account_type):
    session, connection = connect_bank(bank_name)

    accounts_query = session.query(
        Insurer.insurer_id,
        Insurer.customer_id,
        Account.account_id
    ).outerjoin(
        Account,
        Insurer.customer_id == Account.customer_id
    ).filter(
        Account.account_type == account_type
    ).statement

    accounts = pd.read_sql(
        accounts_query,
        connection
    )

    accounts = accounts[accounts['insurer_id'].isin(insurer_ids)]

    connection.close()

    return accounts


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


def query_customers_by_person_id(person_ids, bank_name):
    session, connection = connect_bank(bank_name)

    customer_query = session.query(Person).statement

    customers = pd.read_sql(customer_query, connection)

    customers = customers[customers['person_id'].isin(person_ids)]

    customers = customers['customer_id']

    connection.close()
    return customers


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


def query_customers_by_insurer_id(insurer_ids, bank_name):

    session, connection = connect_bank(bank_name)

    customer_query = session.query(Insurer).statement

    customers = pd.read_sql(customer_query, connection)

    customers = customers[customers['insurer_id'].isin(insurer_ids)]

    customers = customers['customer_id']

    connection.close()

    return customers


def query_events_by_report_date(report_date):

    session, connection = connect_universe()

    event_query = session.query(Event). \
        filter(Event.report_date == report_date). \
        statement

    events = pd.read_sql(event_query, connection)

    connection.close()

    return events


def query_open_case_reserves(company_name):
    session, connection = connect_company(company_name)

    rank_query = session.query(ClaimTransaction,
                               func.rank().over(
                                   order_by=ClaimTransaction.transaction_date,
                                   partition_by=ClaimTransaction.claim_id
                               ).label('rnk')). \
        filter(ClaimTransaction.
               transaction_type.in_([
                    'open claim',
                    'close claim',
                    'reopen claim'])).subquery()

    sub_query = session.query(
        rank_query.c.claim_id,
        func.max(rank_query.c.rnk).label('maxrnk')).\
        group_by(rank_query.c.claim_id).subquery()

    open_query = session.query(
        rank_query.c.claim_id,
        rank_query.c.transaction_type).\
        join(
            sub_query,
            ((rank_query.c.claim_id == sub_query.c.claim_id) &
             (rank_query.c.rnk == sub_query.c.maxrnk))).statement

    open_claims = pd.read_sql(
        open_query,
        connection)

    open_claims['status'] = np.where(
        ~open_claims['transaction_type'].isin(['close claim']),
        'open',
        'closed'
    )

    open_claims = open_claims[open_claims['status'] == 'open']

    open_claims = list(open_claims['claim_id'])

    # add up case reserves over open claims

    case_t_query = session.query(ClaimTransaction).\
        filter(ClaimTransaction.transaction_type == 'set case reserve'). \
        filter(ClaimTransaction.claim_id.in_(open_claims)).subquery()

    case_query = session.query(
        case_t_query.c.claim_id,
        func.sum(case_t_query.c.transaction_amount).
        label('case reserve')).group_by(case_t_query.c.claim_id).subquery()

    claim_query = session.query(
        Claim.claim_id,
        Claim.person_id
    ).subquery()

    result_query = session.query(
        case_query,
        claim_query.c.person_id
    ).outerjoin(
        claim_query,
        case_query.c.claim_id == claim_query.c.claim_id
    ).statement

    case_outstanding = pd.read_sql(
        result_query,
        connection
    )

    return case_outstanding
