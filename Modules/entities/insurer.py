import pandas as pd
import numpy as np
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf


class Insurer:
    def __init__(
        self, session,
        engine,
        starting_capital,
        company,
        company_name
    ):
        self.capital = starting_capital
        self.session = session
        self.connection = engine.connect()
        self.company_name = company_name
        insurer_table = pd.DataFrame([[self.capital, self.company_name]], columns=['capital', 'name'])
        insurer_table.to_sql(
            'company',
            self.connection,
            index=False,
            if_exists='append'
        )
        self.id = pd.read_sql(self.session.query(company.company_id).
                              filter(company.name == self.company_name).
                              statement, self.connection).iat[0, 0]
        self.pricing_model = ''

    def price_book(
        self,
        person,
        policy,
        event,
        pricing_formula
    ):
        book_query = self.session.query(
            policy.policy_id,
            person.person_id,
            person.age_class,
            person.profession,
            person.health_status,
            person.education_level,
            event.severity).outerjoin(
                person,
                person.person_id == policy.person_id).\
            outerjoin(event, event.policy_id == policy.policy_id).\
            filter(policy.company_id == int(self.id))

        book = pd.read_sql(book_query.statement, self.connection)

        book = book.groupby([
            'policy_id',
            'person_id',
            'age_class',
            'profession',
            'health_status',
            'education_level']
        ).agg({'severity': 'sum'}).reset_index()

        book['rands'] = np.random.uniform(size=len(book))
        book['sevresp'] = book['severity']

        self.pricing_model = smf.glm(
            formula=pricing_formula,
            data=book,
            family=sm.families.Tweedie(
                link=statsmodels.genmod.families.links.log,
                var_power=1.5
            )).fit()

        return self.pricing_model

    def get_book(
        self,
        person,
        policy,
        event
    ):
        book_query = self.session.query(
            policy.policy_id,
            person.person_id,
            person.age_class,
            person.profession,
            person.health_status,
            person.education_level,
            event.severity).outerjoin(
            person,
            person.person_id == policy.person_id).outerjoin(event, event.policy_id == policy.policy_id).filter(
            policy.company_id == int(self.id))

        book = pd.read_sql(book_query.statement, self.connection)

        book = book.groupby([
            'policy_id',
            'person_id',
            'age_class',
            'profession',
            'health_status',
            'education_level'
        ]).agg({'severity': 'sum'}).reset_index()

        return book

    def in_force(
            self,
            policy,
            date
    ):

        in_force = pd.read_sql(
            self.session.query(policy).filter(policy.company_id == int(self.id)).filter(
                date >= policy.effective_date).filter(date <= policy.expiration_date).statement,
            self.connection
        )

        return in_force
