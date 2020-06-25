from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class PersonTable(Base):
    __tablename__ = 'person'

    person_id = Column(
        Integer,
        primary_key=True
    )
    age_class = Column(String)
    profession = Column(String)
    health_status = Column(String)
    education_level = Column(String)
    income = Column(Float)
    wealth = Column(Float)
    cobb_c = Column(Float)
    cobb_d = Column(Float)

    event = relationship(
        "Event",
        back_populates="person"
    )

    def __repr__(self):
        return "<PersonTable(" \
               "age_class='%s', " \
               "profession='%s', " \
               "health_status='%s', " \
               "education_level='%s'" \
               "income='%s'" \
               "wealth='%s'" \
               "cobb_c='%s'" \
               "cobb_d='%s'" \
               ")>" % (
                self.age_class,
                self.profession,
                self.health_status,
                self.education_level,
                self.income,
                self.wealth,
                self.cobb_c,
                self.cobb_d
                )


class Company(Base):
    __tablename__ = 'company'

    company_id = Column(
        Integer,
        primary_key=True
    )
    company_name = Column(String)
    capital = Column(Float)

    def __repr(self):
        return "<Company(" \
               "company_name='%s'," \
               " capital='%s'" \
               ")>" % (
                self.company_name,
                self.capital
                )


class Event(Base):
    __tablename__ = 'event'

    event_id = Column(
        Integer,
        primary_key=True
    )
    event_date = Column(Date)
    report_date = Column(Date)
    person_id = Column(
        Integer,
        ForeignKey('person.person_id')
    )
    ground_up_loss = Column(Float)

    person = relationship(
        "PersonTable",
        back_populates="event"
    )

    def __repr(self):
        return "<Event(" \
               "event_date='%s'," \
               "report_date='%s'," \
               "person_id='%s', " \
               "ground_up_loss='%s'" \
               ")>" % (
                self.event_date,
                self.report_date,
                self.person_id,
                self.ground_up_loss
                )

