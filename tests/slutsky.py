import tests.base_sim
from econtools.budget import Budget, Good
from econtools.slutsky import Slutsky
from entities.person import Person

my_person = Person(1)

my_person.get_policy_history()
my_person.get_policy('company_1', 1)


my_person.get_budget()
my_person.get_consumption()

# rate change
all_other = Good(1)
insurance = Good(1000)
new_budget = Budget(insurance, all_other, income=my_person.income, name='new_budget')

testcobb = my_person.utility
testcobb.optimal_bundle(new_budget.good_x.price, new_budget.good_y.price, my_person.income)


slutsy_res = Slutsky(my_person.budget, new_budget, my_person.utility)


# manual calc
check_old_bundle = my_person.optimal_bundle
check_new_bundle = my_person.utility.optimal_bundle(new_budget.good_x.price, new_budget.good_y.price, my_person.income)

check_total_effect = check_new_bundle[0] - check_old_bundle[0]
slutsky_total_res = slutsy_res.substitution_effect + slutsy_res.income_effect


my_person.calculate_slutsky(new_budget)

# test rates
# should be zero
print(slutsy_res.slutsky_rate - slutsy_res.total_effect / slutsy_res.delta_p)
