from econtools.budget import Budget, Intertemporal, Good
from econtools.statics import Consumption
from econtools.utility import CobbDouglas

# test if intercepts plot appropriately with an interest rate of 10%
m1 = Good(
    price=1,
    name='Time 1 Consumption'
)

m2 = Good(
    price=1,
    name='Time 2 Consumption'
)

endowment = Intertemporal(
    good_x=m1,
    good_y=m2,
    good_x_quantity=5,
    good_y_quantity=5,
    interest_rate=.10
)

budget = Budget.from_endowment(
    endowment,
    name='budget'
)

utility = CobbDouglas(.5, 0.5)

consumption = Consumption(budget=budget, utility=utility)

consumption.show_consumption()


utility.show_plot()