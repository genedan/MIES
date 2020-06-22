import datetime as dt
import pandas as pd
import plotly.graph_objects as go

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

company_1_formula = 'incurred_loss ~ ' \
                    'age_class + ' \
                    'profession + ' \
                    'health_status + ' \
                    'education_level'

company_2_formula = 'incurred_loss ~' \
                    ' age_class'

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

policy_count = policy_count.groupby(['year'])[[
    'company_1',
    'company_2',
    'company_1_prem',
    'company_2_prem'
]].mean().reset_index()


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

fig.write_html('adverse_2_firm.html', auto_open=True)