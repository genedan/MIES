import os
import pandas as pd
import parameters as pm
import sqlalchemy as sa
import schema.universe as universe
import shutil

from sqlalchemy.orm import sessionmaker
from scipy.stats import gamma
from scipy.stats import pareto
from numpy.random import poisson

from entities.bank import Bank
from utilities.queries import query_population, query_accounts_by_person_id


# The supreme entity, overseer of all space, time, matter and energy
class God:

    def __init__(self):
        if not os.path.exists('db'):
            os.makedirs('db')
        self.engine = sa.create_engine(
            'sqlite:///db/universe.db',
            echo=True
        )
        session = sessionmaker(bind=self.engine)
        universe.Base.metadata.create_all(self.engine)
        self.session = session()
        self.connection = self.engine.connect()

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

    def grant_wealth(self, person_ids, bank: Bank, transaction_date):
        """
        assign an initial amount of starting wealth per person
        """
        accounts = query_accounts_by_person_id(person_ids, bank.name)
        accounts['transaction_amount'] = pareto.rvs(
            b=1,
            scale=pm.person_params['income'],
            size=accounts.shape[0],
        )
        accounts = accounts[['account_id', 'transaction_amount']]
        accounts = accounts.rename(columns={'account_id': 'debit_account'})
        accounts['credit_account'] = bank.liability_account
        accounts['transaction_date'] = transaction_date
        bank.make_transactions(accounts)


    def smite(
        self,
        ev_date
    ):

        population = query_population()

        population['lambda'] = pm.get_poisson_lambda(population)
        population['frequency'] = poisson(population['lambda'])

        population = population[population['frequency'] != 0]
        population['event_date'] = ev_date
        # claims reported immediately for now
        population['report_date'] = ev_date

        population = population.loc[population.index.repeat(population.frequency)].copy()

        population['gamma_scale'] = pm.get_gamma_scale(population)
        population['ground_up_loss'] = gamma.rvs(
            a=2,
            scale=population['gamma_scale']
        )

        population = population[['event_date', 'report_date', 'person_id', 'ground_up_loss']]
        population.to_sql(
            'event',
            self.connection,
            index=False,
            if_exists='append'
        )
        return population

    def annihilate(self):
        self.connection.close()
        shutil.rmtree('db')
