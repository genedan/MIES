import os
import pandas as pd
import numpy as np
import parameters as pm
import datetime
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
import plotly.graph_objects as go


from scipy.stats import gamma
from scipy.stats import pareto
from numpy.random import poisson
from random import choices
from econtools.utility import CobbDouglas
from econtools.budget import Good, Budget
from plotly.offline import plot



# The supreme entity, overseer of all space, time, matter and energy
class God:

    def __init__(self, session, engine):
        self.session = session
        self.connection = engine.connect()

    def make_person(self):
        self.make_population(1)

    def make_population(self, n_people):
        age_class = pm.draw_ac(n_people)
        profession = pm.draw_prof(n_people)
        health_status = pm.draw_hs(n_people)
        education_level = pm.draw_el(n_people)
        income = pareto.rvs(
            b=1,
            scale=pm.person_params['income'],
            size=n_people,
        )
        cobb_c = [pm.person_params['cobb_c']] * n_people
        cobb_d = [pm.person_params['cobb_d']] * n_people

        population = pd.DataFrame(list(
            zip(
                age_class,
                profession,
                health_status,
                education_level,
                income,
                cobb_c,
                cobb_d
            )
        ), columns=[
            'age_class',
            'profession',
            'health_status',
            'education_level',
            'income',
            'cobb_c',
            'cobb_d'
        ])

        population.to_sql(
            'person',
            self.connection,
            index=False,
            if_exists='append'
        )

    def smite(
        self,
        person,
        policy,
        ev_date
    ):

        population = pd.read_sql(self.session.query(person, policy.policy_id).outerjoin(policy).filter(
                policy.effective_date <= ev_date
            ).filter(
                policy.expiration_date >= ev_date
            ).statement, self.connection)

        population['lambda'] = pm.get_poisson_lambda(population)
        population['frequency'] = poisson(population['lambda'])

        population = population[population['frequency'] != 0]
        population['event_date'] = ev_date

        population = population.loc[population.index.repeat(population.frequency)].copy()

        population['gamma_scale'] = pm.get_gamma_scale(population)
        population['severity'] = gamma.rvs(
            a=2,
            scale=population['gamma_scale']
        )

        population = population[['event_date', 'person_id', 'policy_id', 'severity']]
        population.to_sql(
            'event',
            self.connection,
            index=False,
            if_exists='append'
        )
        return population

    def annihilate(self, db):
        os.remove(db)


class Broker:

    def __init__(
            self,
            session,
            engine
    ):
        self.session = session
        self.connection = engine.connect()

    def identify_free_business(
            self,
            person,
            policy,
            curr_date
    ):
        # free business should probably become a view instead
        market = pd.read_sql(self.session.query(
            person,
            policy.policy_id,
            policy.company_id,
            policy.effective_date,
            policy.expiration_date,
            policy.premium
        ).outerjoin(policy).statement, self.connection)
        free_business = market[
            (market['expiration_date'] >= curr_date) |
            (market['policy_id'].isnull())
        ]
        return free_business

    def place_business(
            self,
            free_business,
            companies,
            market_status,
            curr_date,
            *args
    ):
        if market_status == 'initial_pricing':
            free_business['company_id'] = choices(companies.company_id, k=len(free_business))
            free_business['premium'] = 4000
            free_business['effective_date'] = curr_date + datetime.timedelta(1)
            free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)


            for company in companies.company_id:
                new_business = free_business[free_business['company_id'] == company]
                new_business = new_business[[
                    'company_id',
                    'person_id',
                    'effective_date',
                    'expiration_date',
                    'premium'
                ]]

                new_business.to_sql(
                    'policy',
                    self.connection,
                    index=False,
                    if_exists='append'
                )
        else:
            for arg in args:
                free_business['effective_date'] = curr_date + datetime.timedelta(1)
                free_business['expiration_date'] = curr_date.replace(curr_date.year + 1)
                free_business['rands'] = np.random.uniform(len(free_business))
                free_business['quote_' + str(arg.id)] = arg.pricing_model.predict(free_business)

            free_business['premium'] = free_business[free_business.columns[pd.Series(
                free_business.columns).str.startswith('quote_')]].min(axis=1)
            free_business['company_id'] = free_business[free_business.columns[pd.Series(
                free_business.columns).str.startswith('quote_')]].idxmin(axis=1).str[-1]

            renewal_business = free_business[[
                'company_id',
                'person_id',
                'effective_date',
                'expiration_date',
                'premium']]

            renewal_business.to_sql(
                'policy',
                self.connection,
                index=False,
                if_exists='append'
            )
            return free_business


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


class Person:
    def __init__(
        self,
        session,
        engine,
        person,
        person_id
    ):
        self.session = session
        self.connection = engine.connect()
        self.engine = engine
        self.id = person_id

        query = self.session.query(person).filter(
                person.person_id == int(self.id)
            ).statement

        self.data = pd.read_sql(
            query,
            self.connection
        )
        self.income = self.data['income'].loc[0]

        self.utility = CobbDouglas(
            c=self.data['cobb_c'].loc[0],
            d=self.data['cobb_d'].loc[0]
        )

        self.policy = None
        self.budget = None
        self.premium = None
        self.optimal_bundle = None
        self.consumption_figure = None
        self.offer = None
        self.engel = None
        self.demand = None

    def get_policy(
        self,
        policy,
        policy_id
    ):
        query = self.session.query(policy).filter(
            policy.policy_id == int(policy_id)
        ).statement

        self.policy = pd.read_sql(
            query,
            self.connection
        )
        self.premium = self.policy['premium'].loc[0]

    def get_budget(self):
        all_other = Good(1, name='All Other Goods')
        if self.policy is None:
            insurance = Good(4000, name='Insurance')
        else:
            insurance = Good(self.premium, name='Insurance')
        self.budget = Budget(insurance, all_other, income=self.income, name='Budget')

    def get_consumption(self):
        self.optimal_bundle = self.utility.optimal_bundle(
            p1=self.premium,
            p2=1,
            m=self.income
        )

    def get_consumption_figure(self):
        fig = go.Figure()
        fig.add_trace(self.budget.get_line())
        fig.add_trace(self.utility.trace(k=self.optimal_bundle[2], m=self.income / self.premium * 1.5))
        fig.add_trace(self.utility.trace(k=self.optimal_bundle[2] * 1.5, m=self.income / self.premium * 1.5))
        fig.add_trace(self.utility.trace(k=self.optimal_bundle[2] * .5, m=self.income / self.premium * 1.5))

        fig['layout'].update({
            'title': 'Consumption for Person ' + str(self.id),
            'title_x': 0.5,
            'xaxis': {
                'title': 'Amount of Insurance',
                'range': [0, self.income / self.premium * 1.5]
            },
            'yaxis': {
                'title': 'Amount of All Other Goods',
                'range': [0, self.income * 1.5]
            }
        })
        self.consumption_figure = fig
        return fig

    def get_offer(self):
        # only works for Cobb Douglas right now
        def o(m):
            return self.utility.optimal_bundle(
                p1=self.premium,
                p2=1,
                m=m
            )

        self.offer = o

    def get_engel(self):
        # only works for Cobb Douglas right now

        def e(m):
            return self.utility.optimal_bundle(
                p1=self.premium,
                p2=1,
                m=m
            )[0]

        self.engel = e

    def get_demand(self):
        # only works for Cobb Douglas right now

        def d(p):
            return self.utility.optimal_bundle(
                p1=p,
                p2=1,
                m=self.income
            )[0]

        self.demand = d

    def show_consumption(self):
        plot(self.consumption_figure)

    def show_offer(self):
        offer_frame = pd.DataFrame(columns=['income'])
        offer_frame['income'] = np.arange(0, self.income * 2, 1000)
        offer_frame['x1'], offer_frame['x2'] = self.offer(offer_frame['income'])[:2]

        offer_trace = {
            'x': offer_frame['x1'],
            'y': offer_frame['x2'],
            'mode': 'lines',
            'name': 'Offer Curve'
        }

        fig = self.consumption_figure
        fig.add_trace(offer_trace)
        plot(fig)
        return fig

    def show_engel(self):
        engel_frame = pd.DataFrame(columns=['income'])
        engel_frame['income'] = np.arange(0, self.income * 2, 1000)
        engel_frame['x1'] = engel_frame['income'].apply(self.engel)

        engel_trace = {
            'x': engel_frame['x1'],
            'y': engel_frame['income'],
            'mode': 'lines',
            'name': 'Engel Curve'
        }

        fig = go.Figure()
        fig.add_trace(engel_trace)

        fig['layout'].update({
            'title': 'Engel Curve for Person ' + str(self.id),
            'title_x': 0.5,
            'xaxis': {
                'title': 'Amount of Insurance'
            },
            'yaxis': {
                'title': 'Income'
            }
        })

        plot(fig)
        return fig

    def show_demand(self):
        demand_frame = pd.DataFrame(columns=['price'])
        demand_frame['price'] = np.arange(self.premium/100, self.premium * 2, self.premium/100)
        demand_frame['x1'] = demand_frame['price'].apply(self.demand)

        demand_trace = {
            'x': demand_frame['x1'],
            'y': demand_frame['price'],
            'mode': 'lines',
            'name': 'Demand Curve'
        }

        fig = go.Figure()
        fig.add_trace(demand_trace)

        fig['layout'].update({
            'title': 'Demand Curve for Person ' + str(self.id),
            'title_x': 0.5,
            'xaxis': {
                'range': [0, self.income / self.premium * 2],
                'title': 'Amount of Insurance'
            },
            'yaxis': {
                'title': 'Premium'
            }
        })

        plot(fig)
        return fig
