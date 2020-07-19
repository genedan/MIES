# test if theoretical properties of endowment are satisfied
from econtools.budget import Budget, Endowment, Good
from econtools.utility import CobbDouglas
from entities.person import Person

# original endowment should lie on budget line

my_person = Person(1)

good_1 = Good(price=1, name='good_1')

good_2 = Good(price=1, name='good_2')

endowment = Endowment(good_x=good_1, good_y=good_2, good_x_quantity=5, good_y_quantity=5)

# check exception handling

good_3 = Good(price=5, name='good_2')

# raise good x exception
exception_bundle = Budget(good_x=good_3, good_y=good_2, income=10, endowment=endowment)

# raise good y exception
exception_bundle = Budget(good_x=good_1, good_y=good_3, income=10, endowment=endowment)

# raise income exception
exception_bundle = Budget(good_x=good_1, good_y=good_2, income=11, endowment=endowment)