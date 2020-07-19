# import tests.base_sim
from econtools.budget import Budget, Endowment, Good
from econtools.utility import CobbDouglas
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


slutsky_res = Slutsky(old_budget=my_person.budget, new_budget=new_budget, utility_function=my_person.utility)
slutsky_res.get_slutsky_plot()
slutsky_res.show_plot()

# manual calc
check_old_bundle = my_person.optimal_bundle
check_new_bundle = my_person.utility.optimal_bundle(new_budget.good_x.price, new_budget.good_y.price, my_person.income)

check_total_effect = check_new_bundle[0] - check_old_bundle[0]
slutsky_total_res = slutsky_res.substitution_effect + slutsky_res.income_effect


my_person.calculate_slutsky(new_budget)

# test rates
# should be zero
print(slutsky_res.slutsky_rate - slutsky_res.total_effect / slutsky_res.delta_p)



# test endowment

income = 40000
insurance = Good(4000, name='insurance')
ins_amt = income * .5 / insurance.price


insurance2 = Good(8000, name='insurance')
all_other = Good(1, name='all other goods')
all_other_amt = income - ins_amt * insurance.price



old_endowment = Endowment(good_x=insurance, good_y=all_other, good_x_quantity=ins_amt, good_y_quantity=all_other_amt)

new_endowment = Endowment(good_x=insurance2, good_y=all_other, good_x_quantity=ins_amt, good_y_quantity=all_other_amt)

old_budget = Budget.from_endowment(old_endowment)
new_budget = Budget.from_endowment(new_endowment)

test = Slutsky(old_budget, new_budget, utility_function=CobbDouglas(.5, .5))

test.get_slutsky_plot()
test.show_plot()


milk = Good(3, name='milk')
all_other = Good(1, name='all other goods')
milk_q = 40

milk2 = Good(4, name='milk')
old_endowment = Endowment(good_x=milk, good_y=all_other, good_x_quantity=milk_q, good_y_quantity=30)
new_endowment = Endowment(good_x=milk2, good_y=all_other, good_x_quantity=milk_q, good_y_quantity=30)
old_budget = Budget.from_endowment(old_endowment)
new_budget = Budget.from_endowment(new_endowment)

test = Slutsky(old_budget, new_budget, utility_function=CobbDouglas(.5, .5))
test.get_slutsky_plot()
test.show_plot()
