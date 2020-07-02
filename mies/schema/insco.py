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

    claim_transaction = relationship(
        'ClaimTransaction',
        primaryjoin='Claim.claim_id == ClaimTransaction.claim_id',
        back_populates='claim'
    )

    def __repr__(self):
        return "<Claim(policy_id ='%s'," \
               "person_id ='%s', " \
               "event_id='%s', " \
               "occurrence_date='%s'," \
               "report_date='%s')>" % (
                self.policy_id,
                self.person_id,
                self.event_id,
                self.occurence_date,
                self.report_date
                )


class ClaimTransaction(Base):
    __tablename__ = 'claim_transaction'

    claim_transaction_id = Column(
        Integer,
        primary_key=True
    )

    claim_id = Column(
        Integer,
        ForeignKey('claim.claim_id')
    )

    transaction_date = Column(Date)

    transaction_type = Column(String)

    transaction_amount = Column(Float)

    claim = relationship(
        'Claim',
        primaryjoin='ClaimTransaction.claim_id == Claim.claim_id',
        back_populates='claim_transaction'
    )

    def __repr__(self):
        return "<ClaimTransaction(policy_id ='%s'," \
               "claim_id ='%s', " \
               "transaction_date='%s', " \
               "transaction_type='%s'," \
               "transaction_amount" % (
                self.claim_id,
                self.transaction_date,
                self.transaction_type,
                self.transaction_amount
                )