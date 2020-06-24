from econtools.budget import Budget
from econtools.utility import CobbDouglas
from entities.person import Person

class Hicks:
    def __init__(
            self,
            old_budget: Budget,
            new_budget: Budget,
            utility_function: CobbDouglas  # need to replace with utility superclass
    ):
        self.old_budget = old_budget
        self.new_budget = new_budget
        self.utility = utility_function