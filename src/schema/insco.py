from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Float
from sqlalchemy import ForeignKey


Base = declarative_base()


class Policy(Base):
    __tablename__ = 'policy'

    policy_id = Column(
        Integer,
        primary_key=True
    )
    person_id = Column(Integer)
    effective_date = Column(Date)
    expiration_date = Column(Date)
    premium = Column(Float)

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
