from econtools.budget import Budget, Good
from econtools.slutsky import Slutsky
from entities.person import Person
from econtools.utility import CobbDouglas


my_person = Person(1)

my_person.data

my_person.get_policy_history()
my_person.policy_history
my_person.get_policy('company_1', 1)

my_person.policy
my_person.premium

my_person.get_budget()

my_person.get_consumption()
my_person.get_consumption_figure()
#my_person.show_consumption()

all_other = Good(1)
insurance = Good(1000)
new_budget = Budget(insurance, all_other, income=my_person.income, name='new_budget')

testcobb = my_person.utility
testcobb.optimal_bundle(new_budget.good_x.price, new_budget.good_y.price, my_person.income)
my_person.optimal_bundle

test = Slutsky(my_person.budget, new_budget, my_person.utility)
test.substitution_effect
test.income_effect
#test.show_plot()

check_old_bundle = my_person.optimal_bundle
check_new_bundle = my_person.utility.optimal_bundle(new_budget.good_x.price, new_budget.good_y.price, my_person.income)

check_old_bundle
test.substitution_bundle
check_new_bundle
check_new_bundle[0] - check_old_bundle[0]
test.substitution_effect + test.income_effect


my_person.calculate_slutsky(new_budget)
my_person.slutsky.show_plot()