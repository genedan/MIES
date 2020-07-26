import plotly.graph_objects as go

import numpy as np
import pandas as pd

from plotly.offline import plot


class Tax:
    def __init__(self, amount, style, base=None):
        self.amount = amount
        self.style = style
        self.base = base


class Subsidy:
    def __init__(self, amount, style, base=None):
        self.amount = amount
        self.style = style
        self.base = base


class Good:
    def __init__(
        self,
        price,
        tax=None,
        subsidy=None,
        ration=None,
        name='Good',
    ):

        self.price = price
        self.tax = tax
        self.subsidy = subsidy
        self.interest_rate = 0
        self.inflation_rate = 0

        if ration is None:
            self.ration = np.Inf
        else:
            self.ration = ration
        self.name = name

    @property
    def adjusted_price(self):
        adjusted_price = self.apply_tax(self.price)
        adjusted_price = self.apply_subsidy(adjusted_price)
        adjusted_price = self.apply_discount(adjusted_price)
        adjusted_price = self.apply_inflation(adjusted_price)
        return adjusted_price

    @property
    def real_interest_rate(self):
        real_interest_rate = (1 + self.interest_rate) / (1 + self.inflation_rate) - 1
        return real_interest_rate

    def apply_tax(self, price):
        if (self.tax is None) or (self.tax.style == 'lump_sum'):
            return price
        if self.tax.style == 'quantity':
            return price + self.tax.amount
        # else, assume ad valorem
        else:
            return price * (1 + self.tax.amount)

    def apply_subsidy(self, price):
        if (self.subsidy is None) or (self.subsidy.style == 'lump_sum'):
            return price
        if self.subsidy.style == 'quantity':
            return price - self.subsidy.value
        # else, assume ad valorem
        else:
            return price * (1 - self.subsidy.amount)

    def apply_discount(self, price):
        return price / (1 + self.interest_rate)

    def apply_inflation(self, price):
        return price * (1 + self.inflation_rate)


class Endowment:
    def __init__(
            self,
            good_x: Good,
            good_y: Good,
            good_x_quantity: float,
            good_y_quantity: float,
            ):
        self.good_x = good_x
        self.good_y = good_y
        self.good_x_quantity = good_x_quantity
        self.good_y_quantity = good_y_quantity

    @property
    def income(self):
        income = self.good_x.adjusted_price * self.good_x_quantity + self.good_y.adjusted_price * self.good_y_quantity
        return income


class Intertemporal(Endowment):
    def __init__(
            self,
            good_x: Good,
            good_y: Good,
            good_x_quantity: float,
            good_y_quantity: float,
            interest_rate: float = 0,
            inflation_rate: float =0
            ):
        Endowment.__init__(
            self,
            good_x,
            good_y,
            good_x_quantity,
            good_y_quantity,
        )
        self.interest_rate = interest_rate
        self.good_y.interest_rate = self.interest_rate


class Budget:
    def __init__(
            self,
            good_x,
            good_y,
            income,
            name=None,
            endowment=None
    ):
        self.good_x = good_x
        self.good_y = good_y
        self.income = income
        self.x_lim = self.income / (min(self.good_x.adjusted_price, self.good_x.price)) * 1.2
        self.y_lim = self.income / (min(self.good_y.adjusted_price, self.good_y.price)) * 1.2
        self.name = name
        self.endowment = endowment

        if endowment is not None:
            self.__check_endowment_consistency()

    @classmethod
    def from_bundle(
            cls,
            good_x,
            good_y,
            income,
            name=None
    ):
        return cls(
            good_x,
            good_y,
            income,
            name
        )

    @classmethod
    def from_endowment(
            cls,
            endowment: Endowment,
            name=None
    ):
        good_x = endowment.good_x
        good_y = endowment.good_y
        income = endowment.income

        return cls(
            good_x,
            good_y,
            income,
            name,
            endowment
        )

    def __check_endowment_consistency(self):
        # raise exception if endowment is not consistent with its components
        if self.endowment.good_x != self.good_x:
            raise Exception("Endowment good_x inconsistent with budget good_x. "
                            "It is recommended to use the from_endowment alternative "
                            "constructor when supplying an endowment")

        if self.endowment.good_y != self.good_y:
            raise Exception("Endowment good_y inconsistent with budget good_y. "
                            "It is recommended to use the from_endowment alternative "
                            "constructor when supplying an endowment")

        if (self.endowment.income != (self.endowment.good_x_quantity * self.good_x.adjusted_price +
                                      self.endowment.good_y_quantity * self.good_y.adjusted_price)) | \
                (self.endowment.income != self.income):

            raise Exception("Endowment income inconsistent with supplied good prices. "
                            "It is recommended to use the from_endowment alternative "
                            "constructor when supplying an endowment")

        if self.endowment.good_x.price != self.good_x.price:
            raise Exception("Endowment good_x price inconsistent with budget good_x price. "
                            "It is recommended to use the from_endowment alternative "
                            "constructor when supplying an endowment")

        if self.endowment.good_y.price != self.good_y.price:
            raise Exception("Endowment good_y price inconsistent with budget good_y price. "
                            "It is recommended to use the from_endowment alternative "
                            "constructor when supplying an endowment")

    def get_line(self, width=2):
        data = pd.DataFrame(columns=['x_values', 'y_values'])
        data['x_values'] = np.arange(int(min(self.x_lim, self.good_x.ration)) + 1)

        if self.good_x.tax:
            data['y_values'] = self.calculate_budget(
                good_x_price=self.good_x.price,
                good_y_price=self.good_y.price,
                good_x_adj_price=self.good_x.adjusted_price,
                good_y_adj_price=self.good_y.adjusted_price,
                m=self.income,
                modifier=self.good_x.tax,
                x_values=data['x_values']
            )
        elif self.good_x.subsidy:
            data['y_values'] = self.calculate_budget(
                good_x_price=self.good_x.price,
                good_y_price=self.good_y.price,
                good_x_adj_price=self.good_x.adjusted_price,
                good_y_adj_price=self.good_y.adjusted_price,
                m=self.income,
                modifier=self.good_x.subsidy,
                x_values=data['x_values']
            )
        else:
            data['y_values'] = (self.income / self.good_y.adjusted_price) - \
                       (self.good_x.adjusted_price / self.good_y.adjusted_price) * data['x_values']

        return {'x': data['x_values'],
                'y': data['y_values'],
                'mode': 'lines',
                'name': self.name,
                'line': {
                    'width': width
                }}

    def calculate_budget(
            self,
            good_x_price,
            good_y_price,
            good_x_adj_price,
            good_y_adj_price,
            m,
            modifier,
            x_values
    ):
        y_int = m / good_y_price
        slope = -good_x_price / good_y_price
        adj_slope = -good_x_adj_price / good_y_adj_price
        base_lower = int(modifier.base[0])
        base_upper = int(min(modifier.base[1], max(m / good_x_price, m / good_x_adj_price)))
        modifier_type = modifier.style

        def lump_sum(x):
            if x in range(modifier.amount + 1):
                x2 = y_int
                return x2
            else:
                x2 = y_int + adj_slope * (x - modifier.amount)
                return x2

        def no_or_all_adj(x):
            x2 = y_int + adj_slope * x
            return x2

        def beg_adj(x):
            if x in range(base_lower, base_upper + 1):
                x2 = y_int + adj_slope * x
                return x2
            else:
                x2 = y_int + slope * (x + (adj_slope/slope - 1) * base_upper)
                return x2

        def mid_adj(x):
            if x in range(base_lower):
                x2 = y_int + slope * x
                return x2
            elif x in range(base_lower, base_upper + 1):
                x2 = y_int + adj_slope * (x + (slope/adj_slope - 1) * (base_lower - 1))
                return x2
            else:
                x2 = y_int + slope * (x + (adj_slope/slope - 1) * (base_upper - base_lower + 1))
                return x2

        def end_adj(x):
            if x in range(base_lower):
                x2 = y_int + slope * x
                return x2
            else:
                x2 = y_int + adj_slope * (x + (slope/adj_slope - 1) * (base_lower - 1))
                print(x, x2)
                return x2

        cases = {
            'lump_sum': lump_sum,
            'no_or_all': no_or_all_adj,
            'beg_adj': beg_adj,
            'mid_adj': mid_adj,
            'end_adj': end_adj,
        }

        if modifier_type == 'lump_sum':
            option = 'lump_sum'
        elif modifier.base == [0, np.Inf]:
            option = 'no_or_all'
        elif (modifier.base[0] == 0) and (modifier.base[1] < max(m/good_x_price, m/good_x_adj_price)):
            option = 'beg_adj'
        elif (modifier.base[0] > 0) and (modifier.base[1] < max(m/good_x_price, m/good_x_adj_price)):
            option = 'mid_adj'
        else:
            option = 'end_adj'

        adj_func = cases[option]
        return x_values.apply(adj_func)

    def show_plot(self):
        fig = go.Figure(data=go.Scatter(self.get_line()))
        fig['layout'].update({
            'title': 'Budget Constraint',
            'title_x': 0.5,
            'xaxis': {
                'range': [0, self.x_lim],
                'title': 'Amount of ' + self.good_x.name
            },
            'yaxis': {
                'range': [0, self.y_lim],
                'title': 'Amount of ' + self.good_y.name
            },
            'showlegend': True
        })
        plot(fig)
