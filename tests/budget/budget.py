import datetime as dt
# import numpy as np
import pandas as pd
# import plotly.graph_objects as go

# import econtools as ec

from plotly.offline import plot

from entities.broker import Broker
from entities.god import God
from entities.insurer import Insurer
from entities.person import Person

pd.set_option('display.max_columns', None)

ahura = God()
ahura.make_population(1000)

pricing_date = dt.date(1, 12, 31)


rayon = Broker()

company_1 = Insurer(4000000, 'company_1')
company_1_formula = 'severity ~ age_class + profession + health_status + education_level'

rayon.place_business(pricing_date, company_1)

ahura.smite(pricing_date + dt.timedelta(days=1))

company_1.price_book(company_1_formula)

rayon.place_business(pricing_date, company_1)


my_person = Person(person_id=1)
my_person.get_policy_history()
my_person.get_policy('company_1', 1001)
my_person.get_budget()
my_person.get_consumption()
my_person.get_consumption_figure()

fig = my_person.consumption_figure

fig['layout'].update({
            'title_x': 0.5,
            'width': 1200,
            'height': 627,
            'margin': {
                'l': 10
            }
})

plot(fig)

# fig.write_html('demand.html', auto_open=True)
#
#
# all_other = ec.Good(price=1, name="All Other Goods")
# price = my_person['premium'].loc[0]
# id = my_person['person_id'].loc[0]
# income = my_person['income'].loc[0]
# renewal = ec.Good(price=price, name="Insurance")
#
# original = ec.Good(price=4000, name="Insurance")
# budget_original = ec.Budget(good_x=original, good_y=all_other, income=income, name='Orginal Budget')
# renewal_budget = ec.Budget(good_x=renewal, good_y=all_other, income=income, name='Renewal Budget')
#
# fig = go.Figure()
# fig.add_trace(go.Scatter(budget_original.get_line()))
# fig.add_trace(go.Scatter(renewal_budget.get_line()))
#
#
#
# fig['layout'].update({
#             'title': 'Budget Constraint',
#             'title_x': 0.5,
#             'xaxis': {
#                 'range': [0, 20],
#                 'title': 'Amount of Insurance'
#             },
#             'yaxis': {
#                 'range': [0, 60000],
#                 'title': 'Amount of All Other Goods'
#             },
#             'showlegend': True,
#             'legend': {
#                 'x': .71,
#                 'y': 1
#             },
#             'width': 590,
#             'height': 450,
#             'margin': {
#                 'l':10
#             }
#         })
#
# fig.write_html('mies_budget.html', auto_open=True)
#
#
#
# mysub = ec.Subsidy(amount=2, style='lump_sum', base=[0,np.Inf])
# value_sub = ec.Subsidy(amount=.5, style='value', base=[0, np.Inf])
# mytax = ec.Tax(amount=1, style='value', base=[0, np.Inf])
# insurance1 = ec.Good(price=1)
# insurance2 = ec.Good(price=1, subsidy=mysub, name='Insurance')
# insurance3 = ec.Good(price=1, tax=mytax, name='Insurance')
# insurance4 = ec.Good(price=1, subsidy=value_sub, name='Insurance')
# my_budget1 = ec.Budget(income=10, good_x=insurance1, good_y=all_other, name='No Tax/Sub')
# my_budget2 = ec.Budget(income=10, good_x=insurance2, good_y=all_other, name='Lump Sum Subsidy')
# my_budget3 = ec.Budget(income=10, good_x=insurance3, good_y=all_other, name='Value Tax')
# my_budget4 = ec.Budget(income=10, good_x=insurance4, good_y=all_other, name='Value Subsidy')
#
#
#
#
# ad_val'Ad Valorem Tax: First 2')
# orem_tax = ec.Tax(amount=1, style='value', base=[0,np.Inf])
# quantity_tax = ec.Tax(amount=4, style='quantity', base=[0, np.Inf])
# all_other = ec.Good(price=1, name='All Other Goods')
# ad_valorem_first_two = ec.Tax(amount=1, style='value', base=[0, 2])
#
# insurance_no_tax = ec.Good(price=1, name='Insurance')
# insurance_ad_valorem = ec.Good(price=1, tax=ad_valorem_tax, name='Insurance')
# insurance_value = ec.Good(price=1, tax=quantity_tax, name='Insurance')
# insurance_first_two = ec.Good(price=1, tax=ad_valorem_first_two, name='Insurance')
#
# budget_no_tax = ec.Budget(insurance_no_tax, all_other, income=10, name='No Tax')
# budget_ad_valorem = ec.Budget(insurance_ad_valorem, all_other, income=10, name='Ad Valorem Tax')
# budget_quantity = ec.Budget(insurance_value, all_other, income=10, name='Value Tax')
# budget_first_two = ec.Budget(insurance_first_two, all_other, income=10, name=
# fig = go.Figure()
# fig.add_trace(go.Scatter(budget_no_tax.get_line()))
# fig.add_trace(go.Scatter(budget_ad_valorem.get_line()))
# fig.add_trace(go.Scatter(budget_quantity.get_line()))
# fig.add_trace(go.Scatter(budget_first_two.get_line()))
#
#
# fig['layout'].update({
#             'title': 'Budget Constraint',
#             'title_x': 0.53,
#             'xaxis': {
#                 'range': [0, 12],
#                 'title': 'Amount of Insurance'
#             },
#             'yaxis': {
#                 'range': [0, 12],
#                 'title': 'Amount of All Other Goods'
#             },
#             'showlegend': True,
#             'legend': {
#                 'x': .635,
#                 'y': 1
#             },
#             'width': 530,
#             'height': 450,
#             'margin': {
#                 'l':10
#             }
#         })
#
# fig.write_html('budget_tax1.html', auto_open=True)
#
# lump_sum = ec.Subsidy(2, style='lump_sum', base=[0, np.Inf])
#
# insurance_no_sub = ec.Good(price=1, name='Insurance')
# insurance_lump_sum = ec.Good(price=1, subsidy=lump_sum, name='Insurance')
#
# budget_no_sub = ec.Budget(insurance_no_sub, all_other, income=10, name='No Subsidy')
# budget_lump_sum = ec.Budget(insurance_lump_sum, all_other, income=10, name='Lump Sum')
#
# fig = go.Figure()
# fig.add_trace(go.Scatter(budget_no_sub.get_line()))
# fig.add_trace(go.Scatter(budget_lump_sum.get_line()))
#
#
#
# fig['layout'].update({
#             'title': 'Budget Constraint',
#             'title_x': 0.5,
#             'xaxis': {
#                 'range': [0, 12],
#                 'title': 'Amount of Insurance'
#             },
#             'yaxis': {
#                 'range': [0,12],
#                 'title': 'Amount of All Other Goods'
#             },
#             'showlegend': False,
#             'legend': {
#                 'x': .77,
#                 'y': 1
#             },
#             'width': 590,
#             'height': 450,
#             'margin': {
#                 'l':10
#             }
#         })
#
# fig.write_html('budget_constraint.html', auto_open=True)
#
#
# ahura.annihilate('MIES_Lite.db')
#
#
# insurance_no_sub = ec.Good(price=1, name='Insurance')
# budget_no_sub = ec.Budget(insurance_no_sub, all_other, income=10, name='No Subsidy')
#
#
# from sympy import symbols, diff
#
# c, d, x1, x2 = symbols('c d x1 x2')
# u = (x1 ** c) * (x2 ** d)
#
# mrs = -diff(u, x1) / diff(u, x2)
# print(mrs)
