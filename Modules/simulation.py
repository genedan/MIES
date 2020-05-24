import pandas as pd
import datetime as dt

import sqlalchemy as sa
from SQLite.schema import Person, Policy, Base, Company, Event
from sqlalchemy.orm import sessionmaker
from entities import God, Broker, Insurer


pd.set_option('display.max_columns', None)
engine = sa.create_engine('sqlite:///test.db', echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

gsession = Session()


ahura = God(gsession, engine)

ahura.make_population(1000)

pricing_date = dt.date(2019, 12, 31)


rayon = Broker(gsession, engine)
blubb = Insurer(gsession, engine, 4000000, Company, 'blubb')
snubb = Insurer(gsession, engine, 4000000, Company, 'snubb')
blubb_formula = 'severity ~ age_class + profession + health_status + education_level'
snubb_formula = 'severity ~ age_class'
pricing_status = 'initial_pricing'
for i in range(100):

    free_business = rayon.identify_free_business(Person, Policy, pricing_date)

    companies = pd.read_sql(gsession.query(Company).statement, engine.connect())

    rayon.place_business(free_business, companies, pricing_status, pricing_date, blubb, snubb)

    ahura.smite(Person, Policy, pricing_date + dt.timedelta(days=1))

    test = blubb.price_book(Person, Policy, Event, blubb_formula)

    snubb.price_book(Person, Policy, Event, snubb_formula)

    pricing_date = pricing_date.replace(pricing_date.year + 1)

    pricing_status = 'renewal_pricing'


test = pd.read_sql(gsession.query(Policy).filter(Policy.company_id == 1).
                   filter(Policy.expiration_date == pricing_date).statement, engine.connect())
test2 = pd.read_sql(gsession.query(Policy).filter(Policy.company_id == 2).
                    filter(Policy.expiration_date == pricing_date).statement, engine.connect())

test
test2

test['premium'].mean()

test2['premium'].mean()


ahura.annihilate('test.db')

ev = pd.read_sql(gsession.query(Event).filter(Event.event_date == '2060-01-01').statement, engine.connect())
ev2 = pd.read_sql(gsession.query(Event).filter(Event.event_date == '2020-01-01').statement, engine.connect())

ev['severity'].mean()
ev2['severity'].mean()

test['severity'].mean()

test = blubb.get_book(Person, Policy, Event)

test['severity'].mean()

test.to_csv('test2.csv')