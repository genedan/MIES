import datetime as dt
from utilities.queries import query_population
from entities.bank import Bank
from entities.god import God
from utilities.queries import query_accounts_by_person_id
from utilities.queries import query_customers_by_person_id, query_population_wealth


ahura = God()
ahura.make_population(1000)

blargo = Bank(4000000, 'blargo')
blargo.id
pricing_date = dt.date(1, 12, 31)
population = query_population()
ids = population['person_id']

blargo.get_customers(ids=ids, customer_type='person')
customer_ids = query_customers_by_person_id(ids, 'blargo')
blargo.assign_accounts(customer_ids=customer_ids, account_type='cash')
ahura.grant_wealth(person_ids=ids, bank=blargo, transaction_date=pricing_date)
ahura.send_paychecks(person_ids=ids, bank=blargo, transaction_date=pricing_date)

test = query_population_wealth()

test

ahura.annihilate()

