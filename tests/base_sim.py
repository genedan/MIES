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

company_1_formula = 'incurred_loss ~ ' \
                    'age_class + ' \
                    'profession + ' \
                    'health_status + ' \
                    'education_level'

company_2_formula = 'incurred_loss ~' \
                    ' age_class'


for i in range(10):

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
