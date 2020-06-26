from utilities.queries import query_population
from entities.bank import Bank
from entities.god import God

ahura = God()
ahura.make_population(1000)

blargo = Bank(4000000, 'blargo')

population = query_population()
ids = population['person_id']
blargo.assign_account(ids, 'cash')