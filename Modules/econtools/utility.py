import plotly.graph_objects as go
import numpy as np

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

    def trace(self, k, m):
        x_values = np.arange(.01, m * 1.5,.01)
        y_values = (k/(x_values ** self.c)) ** (1/self.d)

        return {'x': x_values,
                'y': y_values,
                'mode': 'lines',
                'name': 'Utility: ' + str(int(round(k)))}

    def show_plot(self, k=5, m=10):
        fig = go.Figure(data=self.trace(k, m))
        fig.add_trace(self.trace(k * 1.5, m))
        fig.add_trace(self.trace(k * .5, m))
        fig['layout'].update({
            'title': 'Cobb Douglas Utility',
            'title_x': 0.5,
            'xaxis': {
                'range': [0, m * 1.5],
                'title': 'Amount of Good X'
            },
            'yaxis': {
                'range': [0, m * 1.5],
                'title': 'Amount of Good Y'
            },
            'showlegend': True
        })

        plot(fig)
        return fig


