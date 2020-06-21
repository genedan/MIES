from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Float, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

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
        back_populates="customer"
    )

    def __repr__(self):
        return "<Customer(" \
               "age_class='%s', " \
               "profession='%s', " \
               "health_status='%s', " \
               "education_level='%s'" \
               ")>" % (
                   self.age_class,
                   self.profession,
                   self.health_status,
                   self.education_level,
               )


class Policy(Base):
    __tablename__ = 'policy'

    policy_id = Column(
        Integer,
        primary_key=True
    )
    person_id = Column(
        Integer,
        ForeignKey('customer.person_id')
    )
    effective_date = Column(Date)
    expiration_date = Column(Date)
    premium = Column(Float)

    customer = relationship(
        "Customer",
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
    person_id = Column(Integer)
    event_id = Column(Integer)
    occurrence_date = Column(Date)
    report_date = Column(Date)
    incurred_loss = Column(Float)

    def __repr__(self):
        return "<Claim(policy_id ='%s'," \
               "person_id ='%s', " \
               "event_id='%s', " \
               "occurrence_date='%s'," \
               "report_date='%s'," \
               "incurred_loss='%s')>" % (
                self.policy_id,
                self.person_id,
                self.event_id,
                self.occurence_date,
                self.report_date,
                self.incurred_loss
                )
