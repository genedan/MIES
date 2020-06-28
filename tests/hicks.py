from econtools.budget import Budget, Good
from econtools.hicks import Hicks
from entities.person import Person

my_person = Person(1)

my_person.data

my_person.get_policy_history()
my_person.policy_history
my_person.get_policy('company_1', 1)

my_person.policy
my_person.premium

my_person.get_budget()

all_other = Good(1)
insurance = Good(1000)
new_budget = Budget(insurance, all_other, income=my_person.income, name='new_budget')


test = Hicks(my_person.budget, new_budget, my_person.utility)

test.show_plot()