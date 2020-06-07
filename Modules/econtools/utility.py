import plotly.graph_objects as go
import numpy as np
from econtools import budget
from plotly.offline import plot

class CobbDouglas:

    def __init__(self, c, d):
        self.c = c
        self.d = d

    def optimal_bundle(self, p1, p2, m):
        x1_quantity = (self.c / (self.c + self.d)) * (m / p1)
        x2_quantity = (self.d / (self.c + self.d)) * (m / p2)

        optimal_utility = (x1_quantity ** self.c) * (x2_quantity ** self.d)

        return x1_quantity, x2_quantity, optimal_utility

    def trace(self, k):
        x_values = np.arange(.1, 15,.1)
        y_values = (k/(x_values ** self.c)) ** (1/self.d)

        return {'x': x_values,
                'y': y_values,
                'mode': 'lines',
                'name': str(k)}


mycobb = CobbDouglas(.5, .5)

my_bundle = mycobb.optimal_bundle(1,1,10)

all_other = budget.Good(1, name='All Other Goods')
insurance = budget.Good(1, name='Insurance')
my_budget = budget.Budget(insurance, all_other, income=10, name="My Budget")

myplot = go.Figure()
myplot.add_trace(my_budget.get_line())
myplot.add_trace(mycobb.trace(my_bundle[2]))
myplot.add_trace(mycobb.trace(3))
myplot.add_trace(mycobb.trace(8))

myplot['layout'].update({
    'xaxis': {
        'range': [0, 15]
    },
    'yaxis': {
        'range': [0,15]
    }
})

plot(myplot)

my_budget.show_plot()