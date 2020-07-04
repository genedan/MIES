import datetime as dt
from entities.broker import Broker
from entities.insurer import Insurer
from utilities.queries import query_population
from entities.bank import Bank
from entities.god import God
from utilities.queries import query_customers_by_person_id

ahura = God()
ahura.make_population(1000)

blargo = Bank(4000000, 'blargo')
blargo.id
pricing_date = dt.date(1, 12, 31)
population = query_population()
ids = population['person_id']

test = blargo.get_customers(ids=ids, customer_type='person')
customer_ids = query_customers_by_person_id(ids, 'blargo')
blargo.assign_accounts(customer_ids=customer_ids, account_type='cash')
ahura.grant_wealth(person_ids=ids, bank=blargo, transaction_date=pricing_date)
ahura.send_paychecks(person_ids=ids, bank=blargo, transaction_date=pricing_date)

rayon = Broker()

company_1 = Insurer(4000000, blargo, pricing_date, 'company_1')

company_1_formula = 'incurred_loss ~ ' \
                    'age_class + ' \
                    'profession + ' \
                    'health_status + ' \
                    'education_level'

rayon.place_business(
        pricing_date,
        blargo,
        company_1
    )

event_date = pricing_date + dt.timedelta(days=1)

ahura.smite(event_date)

rayon.report_claims(event_date)

company_1.pay_claims(event_date + dt.timedelta(days=1))

from utilities.queries import query_open_case_reserves
from utilities.queries import query_case_by_claim
query_open_case_reserves('company_1')
query_case_by_claim('company_1')

ahura.annihilate()