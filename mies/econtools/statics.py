# used for comparative statics
import plotly.graph_objects as go

from plotly.offline import plot

from econtools.budget import Budget
from econtools.utility import CobbDouglas
from econtools.hicks import Hicks
from econtools.slutsky import Slutsky


class Consumption:
    def __init__(
            self,
            budget: Budget,
            utility: CobbDouglas
    ):
        self.budget = budget
        self.income = self.budget.income
        self.utility = utility
        self.optimal_bundle = self.get_consumption()
        self.fig = self.get_consumption_figure()
        self.slutsky = None
        self.hicks = None

    def get_consumption(self):
        optimal_bundle = self.utility.optimal_bundle(
            p1=self.budget.good_x.adjusted_price,
            p2=self.budget.good_y.adjusted_price,
            m=self.budget.income
        )

        return optimal_bundle

    def get_consumption_figure(self):
        fig = go.Figure()
        fig.add_trace(self.budget.get_line())
        fig.add_trace(self.utility.trace(
            k=self.optimal_bundle[2],
            m=self.income / self.budget.good_x.adjusted_price * 1.5
        ))

        fig.add_trace(self.utility.trace(
            k=self.optimal_bundle[2] * 1.5,
            m=self.income / self.budget.good_x.adjusted_price * 1.5
        ))

        fig.add_trace(self.utility.trace(
            k=self.optimal_bundle[2] * .5,
            m=self.income / self.budget.good_x.adjusted_price * 1.5
        ))

        fig['layout'].update({
            'title': 'Consumption',
            'title_x': 0.5,
            'xaxis': {
                'title': 'Amount of ' + self.budget.good_x.name,
                'range': [0, self.income / self.budget.good_x.adjusted_price * 1.5]
            },
            'yaxis': {
                'title': 'Amount of ' + self.budget.good_y.name,
                'range': [0, self.income * 1.5]
            }
        })

        return fig

    def calculate_slutsky(self, new_budget):
        self.slutsky = Slutsky(
            old_budget=self.budget,
            new_budget=new_budget,
            utility_function=self.utility
        )
        self.slutsky.plot['layout'].update({
            'title': 'Slutsky Decomposition'
        })
        self.slutsky.plot['layout'].update({'title_x': 0.5})

    def calculate_hicks(self, new_budget):
        self.hicks = Hicks(
            old_budget=self.budget,
            new_budget=new_budget,
            utility_function=self.utility
        )
        self.hicks.plot['layout'].update({
            'title': 'Hicks Decomposition'
        })
        self.hicks.plot['layout'].update({'title_x': 0.5})

    def show_consumption(self):
        plot(self.fig)
