from econtools.budget import Budget
from econtools.slutsky import Slutsky
from econtools.utility import CobbDouglas


class Hicks(Slutsky):
    def __init__(
            self,
            old_budget: Budget,
            new_budget: Budget,
            utility_function: CobbDouglas  # need to replace with utility superclass
    ):
        Slutsky.__init__(
            self,
            old_budget,
            new_budget,
            utility_function
        )
        self.name = 'Hicks'
        self.hicks_rate = self.substitution_rate - self.income_rate
        self.plot = self.get_plot()

    def calculate_pivoted_budget(self):
        """
        Pivot the budget line at the new price so the consumer still as the same utility
        """
        old_utility = self.old_bundle[2]
        c = self.utility.c
        d = self.utility.d
        p1_p = self.new_budget.good_x.price
        p2 = self.old_budget.good_y.price
        x1_no_m = (((c / (c + d)) * (1 / p1_p)) ** c)
        x2_no_m = (((d / (c + d)) * (1 / p2)) ** d)
        pivoted_income = old_utility / (x1_no_m * x2_no_m)
        pivoted_budget = Budget(
            self.new_budget.good_x,
            self.old_budget.good_y,
            pivoted_income,
            'Pivoted Budget'
        )
        return pivoted_budget
