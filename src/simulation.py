import pandas as pd
import datetime as dt

from entities.god import God
from entities.broker import Broker
from entities.insurer import Insurer


pd.set_option('display.max_columns', None)


ahura = God()

ahura.make_population(1000)

pricing_date = dt.date(1, 12, 31)

rayon = Broker()

company_1 = Insurer(4000000, 'company_1')

company_2 = Insurer(4000000, 'company_2')

#company_3 = Insurer(gsession, engine, 4000000, Company, 'company_3')
#rands = Insurer(gsession, engine, 4000000, Company, 'rands')
#sevrsp = Insurer(gsession, engine, 4000000, Company, 'sevresp')
#company_4 = Insurer(gsession, engine, 4000000, Company, 'company_4')

company_1_formula = 'incurred_loss ~ ' \
                    'age_class + ' \
                    'profession + ' \
                    'health_status + ' \
                    'education_level'

company_2_formula = 'incurred_loss ~' \
                    ' age_class'
#company_3_formula = 'severity ~ age_class + profession'
#rands_formula = 'severity ~ rands'
#sevrsp_formula = 'severity ~ sevresp'
#company_4_formula = 'severity ~ age_class + profession + health_status'


policy_count = pd.DataFrame(columns=['year', 'company_1', 'company_2', 'company_1_prem', 'company_2_prem'])
for i in range(50):

    rayon.place_business(
        pricing_date,
        company_1,
        company_2
    )

    event_date = pricing_date + dt.timedelta(days=1)

    ahura.smite(event_date)

    rayon.report_claims(event_date)

    company_1.price_book(company_1_formula)

    company_2.price_book(company_2_formula)

    pricing_date = pricing_date.replace(pricing_date.year + 1)

    policy_count = policy_count.append({
        'year': pricing_date.year,
        'company_1': len(company_1.in_force(pricing_date)),
        'company_2': len(company_2.in_force(pricing_date)),
        'company_1_prem': company_1.in_force(pricing_date)['premium'].mean(),
        'company_2_prem': company_2.in_force(pricing_date)['premium'].mean()
    }, ignore_index=True)

policy_count = policy_count.groupby(['year'])[['company_1',
                                               'company_2',
                                               # 'company_3',
                                               #'rands',
                                               # 'company_4',
                                               'company_1_prem',
                                               'company_2_prem'
                                               # 'company_3_prem',
                                               #'rands_prem',
                                               # 'company_4_prem'
                                               ]].mean().reset_index()

policy_count

import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_1'],
                         mode='lines',
                         name='Company 1'))


fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_2'],
                         mode='lines',
                         name='Company 2'))

# fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_3'],
#                          mode='lines',
#                          name='Company 3'))

# fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['rands'],
#                          mode='lines',
#                          name='rands'))

# fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_4'],
#                          mode='lines',
#                          name='Company 4'))

fig.update_layout(title='Insurer Market Share',
                  title_x=0.5,
                  xaxis_title='Underwriting Period',
                  yaxis_title='Policy Count',
                  yaxis_range=[0, 1000])

fig.write_html('first_figure3.html', auto_open=True)


fig = go.Figure()
fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_1'],
                         mode='lines',
                         name='Company 1'))


fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_2'],
                         mode='lines',
                         name='Company 2'))

# fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_3'],
#                          mode='lines',
#                          name='Company 3'))
#
#
#
# fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_4'],
#                          mode='lines',
#                          name='Company 4'))

fig.update_layout(title='Insurer Market Share',
                  title_x=0.5,
                  xaxis_title='Underwriting Period',
                  yaxis_title='Policy Count',
                  yaxis_range=[0, 800])

fig.write_html('first_figure6.html', auto_open=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_1_prem'],
                         mode='lines',
                         name='Company 1'))


fig2.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_2_prem'],
                         mode='lines',
                         name='Company 2'))

# fig2.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_3_prem'],
#                          mode='lines',
#                          name='Company 3'))
#
#
# fig2.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_4_prem'],
#                          mode='lines',
#                          name='Company 4'))

fig2.update_layout(title='Average Premium per Policy',
                  title_x=0.5,
                  xaxis_title='Underwriting Period',
                  yaxis_title='Average Premium')
                  #yaxis_range=[0, 600])

fig2.write_html('first_figure7.html', auto_open=True)

