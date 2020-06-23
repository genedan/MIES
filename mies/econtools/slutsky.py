from econtools.budget import Budget
from econtools.utility import CobbDouglas
from entities.person import Person


class Slutsky:

    def __init__(
            self,
            old_budget: Budget,
            new_budget: Budget,
            utility_function: CobbDouglas  # need to replace with utility superclass
    ):
        self.old_budget = old_budget
        self.new_budget = new_budget
        self.utility = utility_function

        self.old_consumption = self.utility.optimal_bundle(
            self.old_budget.good_x.price,
            self.old_budget.good_y.price,
            self.old_budget.income
        )

        self.pivoted_budget = self.calculate_pivoted_budget()
        self.substitution_bundle = self.calculate_substitution_bundle()
        self.substitution_effect = self.calculate_substitution_effect()
        self.final_budget = None

    def calculate_pivoted_budget(self):
        delta_p = self.new_budget.good_x.price - self.old_budget.good_x.price
        delta_m = self.old_consumption[0] * delta_p
        pivoted_income = self.old_budget.income + delta_m
        pivoted_budget = Budget(
            self.old_budget.good_x,
            self.old_budget.good_y,
            pivoted_income
        )
        return pivoted_budget

    def calculate_substitution_bundle(self):
        substitution_bundle = self.utility.optimal_bundle(
            self.pivoted_budget.good_x.price,
            self.pivoted_budget.good_y.price,
            self.pivoted_budget.income
        )
        return substitution_bundle

    def calculate_substitution_effect(self):
        substitution_effect = self.substitution_bundle[0] - self.old_consumption[0]
        return substitution_effect

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
my_person.show_consumption()