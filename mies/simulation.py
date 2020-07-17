import pandas as pd
import datetime as dt

from mies.entities.god import God
from mies.entities.bank import Bank
from mies.entities.broker import Broker
from mies.entities.insurer import Insurer
from mies.utilities.queries import query_population, query_customers_by_person_id


pd.set_option('display.max_columns', None)


ahura = God()

ahura.make_population(1000)

pricing_date = dt.date(1, 12, 31)

blargo = Bank(4000000, 'blargo')
rayon = Broker()

company_1 = Insurer(4000000, blargo, pricing_date, 'company_1')

company_2 = Insurer(4000000, blargo, pricing_date, 'company_2')

company_1_formula = 'incurred_loss ~ ' \
                    'age_class + ' \
                    'profession + ' \
                    'health_status + ' \
                    'education_level'

company_2_formula = 'incurred_loss ~' \
                    ' age_class'


population = query_population()
ids = population['person_id']

blargo.get_customers(ids=ids, customer_type='person')
customer_ids = query_customers_by_person_id(ids, 'blargo')
blargo.assign_accounts(customer_ids=customer_ids, account_type='cash')
ahura.grant_wealth(person_ids=ids, bank=blargo, transaction_date=pricing_date)



policy_count = pd.DataFrame(columns=['year', 'company_1', 'company_2', 'company_1_prem', 'company_2_prem'])
for i in range(50):

    rayon.place_business(
        pricing_date,
        blargo,
        company_1,
        company_2
    )

    event_date = pricing_date + dt.timedelta(days=1)

    ahura.smite(event_date)

    rayon.report_claims(event_date)

    company_1.pay_claims(event_date + dt.timedelta(days=1))

    company_2.pay_claims(event_date + dt.timedelta(days=1))

    company_1.price_book(company_1_formula)

    company_2.price_book(company_2_formula)

    pricing_date = pricing_date.replace(pricing_date.year + 1)


    ahura.send_paychecks(person_ids=ids, bank=blargo, transaction_date=pricing_date)

    policy_count = policy_count.append({
        'year': pricing_date.year,
        'company_1': len(company_1.in_force(pricing_date)),
        'company_2': len(company_2.in_force(pricing_date)),
        'company_1_prem': company_1.in_force(pricing_date)['premium'].mean(),
        'company_2_prem': company_2.in_force(pricing_date)['premium'].mean()
    }, ignore_index=True)

policy_count = policy_count.groupby(['year'])[['company_1',
                                               'company_2',
                                               'company_1_prem',
                                               'company_2_prem'
                                               ]].mean().reset_index()


import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_1'],
                         mode='lines',
                         name='Company 1'))


fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_2'],
                         mode='lines',
                         name='Company 2'))

fig.update_layout(title='Insurer Market Share',
                  title_x=0.5,
                  xaxis_title='Underwriting Period',
                  yaxis_title='Policy Count',
                  yaxis_range=[0, 1000])

fig['layout'].update({
            'title_x': 0.45,
            'width': 550,
            'height': 400,
            'margin': {
                'l':10
            }
})

fig.write_html('first_figure3.html', auto_open=True)


fig = go.Figure()
fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_1'],
                         mode='lines',
                         name='Company 1'))


fig.add_trace(go.Scatter(x=policy_count['year'], y=policy_count['company_2'],
                         mode='lines',
                         name='Company 2'))

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


fig2.update_layout(title='Average Premium per Policy',
                  title_x=0.5,
                  xaxis_title='Underwriting Period',
                  yaxis_title='Average Premium')
                  #yaxis_range=[0, 600])

fig2.write_html('first_figure7.html', auto_open=True)

