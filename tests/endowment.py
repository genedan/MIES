# test if theoretical properties of endowment are satisfied
from econtools.budget import Budget, Endowment, Good
from econtools.utility import CobbDouglas
from entities.person import Person

# original endowment should lie on budget line

my_person = Person(1)

good_1 = Good(price=1, name='good_1')

good_2 = Good(price=1, name='good_2')

endowment = Endowment(good_x=good_1, good_y=good_2, good_x_quantity=5, good_y_quantity=5)

# test equivalence of initialization methods

endowment_value = 5 * good_1.price + 5 * good_2.price
my_person.income = endowment_value

budget_bundle = Budget(good_x=good_1, good_y=good_2, income=endowment_value)
budget_endowment = Budget.from_endowment(endowment=endowment)

print(budget_bundle.good_x == budget_endowment.good_x)
print(budget_bundle.good_y == budget_endowment.good_y)
print(budget_bundle.income == budget_endowment.income)
print(budget_bundle.x_lim == budget_endowment.x_lim)
print(budget_bundle.y_lim == budget_endowment.y_lim)

budget = budget_endowment

budget.show_plot()

# net buyer of good 1:
cb_utility = CobbDouglas(.7, .3)
my_person.utility = cb_utility
my_person.income = endowment_value
my_person.budget = budget
my_person.premium = good_1.price
my_person.get_consumption(p1=good_1.price, p2=good_2.price)
my_person.get_consumption_figure()
my_person.show_consumption()
print(my_person.optimal_bundle)

# if price of good 1 decreases, person must remain a net buyer:

good_1.price = .5
endowment_value = 5 * good_1.price + 5 * good_2.price
my_person.income = endowment_value

budget = Budget(good_x=good_1, good_y=good_2, income=endowment_value)
my_person.budget = budget
my_person.premium = good_1.price
my_person.get_consumption(p1=good_1.price, p2=good_2.price)
my_person.get_consumption_figure()
my_person.show_consumption()
print(my_person.optimal_bundle)


# net seller of good 1:
good_1 = Good(price=1, name='good_1')

good_2 = Good(price=1, name='good_2')

endowment_value = 5 * good_1.price + 5 * good_2.price
my_person.income = endowment_value

budget = Budget(good_x=good_1, good_y=good_2, income=endowment_value)

cb_utility = CobbDouglas(.3, .7)
my_person.utility = cb_utility
my_person.income = endowment_value
my_person.budget = budget
my_person.premium = good_1.price
my_person.get_consumption(p1=good_1.price, p2=good_2.price, m=endowment_value)
my_person.get_consumption_figure()
my_person.show_consumption()
print(my_person.optimal_bundle)

# if price of good 1 increases, person must remain a net seller:

good_1 = Good(price=2, name='good_1')
endowment_value = 5 * good_1.price + 5 * good_2.price
my_person.income = endowment_value

budget = Budget(good_x=good_1, good_y=good_2, income=endowment_value)
my_person.income = endowment_value
my_person.budget = budget
my_person.premium = good_1.price
my_person.get_consumption(p1=good_1.price, p2=good_2.price)
my_person.get_consumption_figure()
my_person.show_consumption()
print(my_person.optimal_bundle)

# test offer curve, should be nested within utility curve
good_1 = Good(price=1, name='good_1')

good_2 = Good(price=1, name='good_2')

endowment_value = 5 * good_1.price + 5 * good_2.price
my_person.income = endowment_value

budget = Budget(good_x=good_1, good_y=good_2, income=endowment_value)
cb_utility = CobbDouglas(.5, .5)
my_person.utility = cb_utility
my_person.income = endowment_value
my_person.budget = budget
my_person.premium = good_1.price
my_person.get_consumption(p1=good_1.price, p2=good_2.price)
my_person.get_consumption_figure()


my_person.get_offer()
my_person.show_offer(p1=good_1.price, fix_prices=False)