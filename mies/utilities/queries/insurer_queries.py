import numpy as np
import pandas as pd
from sqlalchemy.sql import func


from schema.universe import Event

from schema.insco import (
    Claim,
    ClaimTransaction,
    Customer,
    Policy
)

from utilities.connections import (
    connect_universe,
    connect_company)


def get_customer_ids(company):
    session, connection = connect_company(company)
    id_query = session.query(Customer.person_id).statement
    ids = pd.read_sql(id_query, connection)
    connection.close()
    return ids


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


def query_pricing_model_data(company_name):
    session, connection = connect_company(company_name)

    policy_query = session.query(
        Policy.policy_id,
        Policy.person_id,
        Customer.age_class,
        Customer.profession,
        Customer.health_status,
        Customer.education_level,
        ).outerjoin(
            Customer,
            Policy.person_id == Customer.person_id
        ).statement

    policy = pd.read_sql(policy_query, connection)

    claim = query_incurred_by_claim(company_name)

    claim = claim.drop(columns=['claim_id', 'paid_loss', 'case_reserve'], axis=1)

    claim = claim.groupby(['policy_id'])['incurred_loss'].agg('sum')

    model_set = policy.merge(claim, on='policy_id', how='left')

    model_set['incurred_loss'] = model_set['incurred_loss'].fillna(0)

    return model_set


def query_policy(company_name, policy_id):
    session, connection = connect_company(company_name)
    policy_query = session.query(Policy).filter(Policy.policy_id == policy_id).statement
    policy = pd.read_sql(policy_query, connection)
    connection.close()
    return policy


def query_case_by_claim(company_name):
    session, connection = connect_company(company_name)

    claim_policy = session.query(
        Claim.claim_id,
        Claim.policy_id
    ).subquery()

    case_set = session.query(
        ClaimTransaction.claim_id,
        func.sum(ClaimTransaction.transaction_amount).label('set')
    ).filter(ClaimTransaction.transaction_type == 'set case reserve').group_by(ClaimTransaction.claim_id).subquery()

    case_takedown = session.query(
        ClaimTransaction.claim_id,
        func.sum(ClaimTransaction.transaction_amount).label('takedown')
    ).filter(ClaimTransaction.transaction_type == 'reduce case reserve').group_by(ClaimTransaction.claim_id).subquery()

    case_query = session.query(
        case_set.c.claim_id,
        (func.ifnull(case_set.c.set, 0) - func.ifnull(case_takedown.c.takedown, 0)).label('case_reserve')
    ).outerjoin(case_takedown, case_set.c.claim_id == case_takedown.c.claim_id).subquery()

    claim_case = session.query(
        claim_policy.c.claim_id,
        claim_policy.c.policy_id,
        func.ifnull(case_query.c.case_reserve, 0).label('case_reserve')
    ).outerjoin(case_query, claim_policy.c.claim_id == case_query.c.claim_id).statement

    case_reserve = pd.read_sql(claim_case, connection)

    connection.close()

    return case_reserve


def query_paid_by_claim(company_name):
    session, connection = connect_company(company_name)

    claim_policy = session.query(
        Claim.claim_id,
        Claim.policy_id
    ).subquery()

    payment_query = session.query(
        ClaimTransaction.claim_id,
        func.sum(ClaimTransaction.transaction_amount).label('paid_loss')
    ).filter(ClaimTransaction.transaction_type == 'claim payment').group_by(ClaimTransaction.claim_id).subquery()

    claim_paid = session.query(
        claim_policy.c.claim_id,
        claim_policy.c.policy_id,
        func.ifnull(payment_query.c.paid_loss, 0).label('paid_loss')
    ).outerjoin(payment_query, claim_policy.c.claim_id == payment_query.c.claim_id).statement

    claim_payments = pd.read_sql(claim_paid, connection)

    connection.close()

    return claim_payments


def query_incurred_by_claim(company_name):

    case = query_case_by_claim(company_name)
    case = case.drop(columns=['policy_id'], axis=1)

    paid = query_paid_by_claim(company_name)

    incurred = paid.merge(case, on='claim_id', how='left')

    incurred['incurred_loss'] = incurred['paid_loss'] + incurred['case_reserve']

    return incurred
