from random import choices

person_params = {
    'age_class': ['Y', 'M', 'E'],
    'profession': ['A', 'B', 'C'],
    'health_status': ['P', 'F', 'G'],
    'education_level': ['H', 'U', 'P'],
    'income': 30000,
    'cobb_c': .1,
    'cobb_d': .9
}

age_params = {
    'Y': 5000,
    'M': 10000,
    'E': 15000
}

prof_params = {
    'A': 2000,
    'B': 4000,
    'C': 8000
}

hs_params = {
    'P': 6000,
    'F': 12000,
    'G': 18000
}

el_params = {
    'H': 4000,
    'U': 8000,
    'P': 12000
}

age_p_params = {
    'Y': .005,
    'M': .01,
    'E': .015
}

prof_p_params = {
    'A': .01,
    'B': .02,
    'C': .03
}

hs_p_params = {
    'P': .0025,
    'F': .0075,
    'G': .01
}

el_p_params = {
    'H': .0075,
    'U': .0125,
    'P': .015
}


def draw_ac(n):
    return choices(person_params['age_class'], k=n)


def draw_prof(n):
    return choices(person_params['profession'], k=n)


def draw_hs(n):
    return choices(person_params['health_status'], k=n)


def draw_el(n):
    return choices(person_params['education_level'], k=n)


def get_gamma_scale(people):
    scale = people['age_class'].map(age_params) + \
            people['profession'].map(prof_params) +\
            people['health_status'].map(hs_params) +\
            people['education_level'].map(el_params)

    return scale


def get_poisson_lambda(people):
    lam = people['age_class'].map(age_p_params) + \
             people['profession'].map(prof_p_params) + \
             people['health_status'].map(hs_p_params) + \
             people['education_level'].map(el_p_params)

    return lam
