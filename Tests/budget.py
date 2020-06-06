import pandas as pd
import datetime as dt
import sqlalchemy as sa
import econtools as ec
from SQLite.schema import Person, Policy, Base, Company, Event
from sqlalchemy.orm import sessionmaker
from entities import God, Broker, Insurer
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot


pd.set_option('display.max_columns', None)


engine = sa.create_engine('sqlite:///MIES_Lite.db', echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

gsession = Session()


ahura = God(gsession, engine)
ahura.make_population(1000)

pricing_date = dt.date(1, 12, 31)


rayon = Broker(gsession, engine)
company_1 = Insurer(gsession, engine, 4000000, Company, 'company_1')
company_1_formula = 'severity ~ age_class + profession + health_status + education_level'
pricing_status = 'initial_pricing'
free_business = rayon.identify_free_business(Person, Policy, pricing_date)
companies = pd.read_sql(gsession.query(Company).statement, engine.connect())

rayon.place_business(free_business, companies, pricing_status, pricing_date, company_1)
ahura.smite(Person, Policy, pricing_date + dt.timedelta(days=1))
company_1.price_book(Person, Policy, Event, company_1_formula)
pricing_status = 'renewal_pricing'
rayon.place_business(free_business, companies, pricing_status, pricing_date, company_1)

ahura.annihilate('MIES_Lite.db')

myquery = gsession.query(Person.person_id, Person.income, Policy.policy_id, Policy.premium).\
    outerjoin(Policy, Person.person_id == Policy.person_id).\
    filter(Person.person_id == str(1)).\
    filter(Policy.policy_id == str(1001))

my_person = pd.read_sql(myquery.statement, engine.connect())

my_person

all_other = ec.Good(price=2, name="All Other Goods")
price = my_person['premium'].loc[0]
id = my_person['person_id'].loc[0]
income = my_person['income'].loc[0]
insurance = ec.Good(price=price, name="Insurance")
my_budget = ec.Budget(good_x=insurance, good_y=all_other, income=income, name=str(id))
my_budget.show_plot()


mysub = ec.Subsidy(amount=2, style='lump_sum', base=[0,np.Inf])
value_sub = ec.Subsidy(amount=.5, style='value', base=[0, np.Inf])
mytax = ec.Tax(amount=1, style='value', base=[0, np.Inf])
insurance1 = ec.Good(price=1)
insurance2 = ec.Good(price=1, subsidy=mysub, name='Insurance')
insurance3 = ec.Good(price=1, tax=mytax, name='Insurance')
insurance4 = ec.Good(price=1, subsidy=value_sub, name='Insurance')
my_budget1 = ec.Budget(income=10, good_x=insurance1, good_y=all_other, name='No Tax/Sub')
my_budget2 = ec.Budget(income=10, good_x=insurance2, good_y=all_other, name='Lump Sum Subsidy')
my_budget3 = ec.Budget(income=10, good_x=insurance3, good_y=all_other, name='Value Tax')
my_budget4 = ec.Budget(income=10, good_x=insurance4, good_y=all_other, name='Value Subsidy')

fig = go.Figure()
fig.add_trace(go.Scatter(my_budget1.get_line()))
fig.add_trace(go.Scatter(my_budget2.get_line()))
fig.add_trace(go.Scatter(my_budget3.get_line()))
fig.add_trace(go.Scatter(my_budget4.get_line()))

fig['layout'].update({
            'title': 'Budget Constraint',
            'title_x': 0.5,
            'xaxis': {
                'range': [0, 20],
                'title': 'Amount of Insurance'
            },
            'yaxis': {
                'range': [0, 6],
                'title': 'Amount of All Other Goods'
            },
            'showlegend': True
        })

plot(fig)