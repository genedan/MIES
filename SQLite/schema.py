from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    person_id = Column(
        Integer,
        primary_key=True
    )
    age_class = Column(String)
    profession = Column(String)
    health_status = Column(String)
    education_level = Column(String)

    policy = relationship(
        "Policy",
        back_populates="person"
    )
    event = relationship(
        "Event",
        back_populates="person"
    )

    def __repr__(self):
        return "<Person(" \
               "age_class='%s', " \
               "profession='%s', " \
               "health_status='%s', " \
               "education_level='%s'" \
               ")>" % (
                self.age_class,
                self.profession,
                self.health_status,
                self.education_level
                )


class Company(Base):
    __tablename__ = 'company'

    company_id = Column(
        Integer,
        primary_key=True
    )
    name = Column(String)
    capital = Column(Float)

    policy = relationship(
        "Policy",
        back_populates="company"
    )

    def __repr(self):
        return "<Company(" \
               "name='%s'," \
               " capital='%s'" \
               ")>" % (
                self.name,
                self.capital
                )


class Policy(Base):
    __tablename__ = 'policy'

    policy_id = Column(
        Integer,
        primary_key=True
    )
    company_id = Column(
        Integer,
        ForeignKey('company.company_id')
    )
    person_id = Column(
        Integer,
        ForeignKey('person.person_id')
    )
    effective_date = Column(Date)
    expiration_date = Column(Date)
    premium = Column(Float)

    company = relationship(
        "Company",
        back_populates="policy"
    )
    person = relationship(
        "Person",
        back_populates="policy"
    )
    event = relationship(
        "Event",
        back_populates="policy"
    )

    def __repr__(self):
        return "<Policy(person_id ='%s'," \
               "effective_date ='%s', " \
               "expiration_date='%s', " \
               "premium='%s')>" % (
                self.person_id,
                self.effective_date,
                self.expiration_date,
                self.premium
                )


class Event(Base):
    __tablename__ = 'event'

    event_id = Column(
        Integer,
        primary_key=True
    )
    event_date = Column(Date)
    person_id = Column(
        Integer,
        ForeignKey('person.person_id')
    )
    policy_id = Column(
        Integer,
        ForeignKey('policy.policy_id')
    )
    severity = Column(Float)

    person = relationship(
        "Person",
        back_populates="event"
    )
    policy = relationship(
        "Policy",
        back_populates="event"
    )


class Claim(Base):
    __tablename__ = 'claim'

    claim_id = Column(
        Integer,
        primary_key=True
    )
    policy_id = Column(
        Integer,
        ForeignKey('policy.policy_id')
    )
    loss = Column(Float)
