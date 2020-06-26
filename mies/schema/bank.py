from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Float, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Account(Base):
    __tablename__ = 'account'

    account_id = Column(
        Integer,
        primary_key=True
    )

    customer_id = Column(
        Integer,
        ForeignKey('customer.customer_id')
    )

    account_type = Column(String)

    transaction_debit = relationship(
        'Transaction',
        primaryjoin='Transaction.debit_account == Account.account_id',
        back_populates='account_debit'
    )

    transaction_credit = relationship(
        'Transaction',
        primaryjoin='Transaction.credit_account == Account.account_id',
        back_populates='account_credit'
    )

    # transaction = relationship(
    #     "Transaction",
    #     back_populates='account_debit'
    # )

    def __repr__(self):
        return "<Account(" \
               "customer_id='%s', " \
               "account_type='%s', " \
               ")>" % (
                   self.customer_id,
                   self.account_type
               )


class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(
        Integer,
        primary_key=True
    )

    credit_account = Column(
        Integer,
        ForeignKey('account.account_id')
    )

    debit_account = Column(
        Integer,
        ForeignKey('account.account_id')
    )

    transaction_date = Column(Date)

    transaction_amount = Column(Float)

    account_debit = relationship(
        "Account",
        primaryjoin='Transaction.debit_account == Account.account_id',
        back_populates='transaction_debit'
    )

    account_credit = relationship(
        "Account",
        primaryjoin='Transaction.credit_account == Account.account_id',
        back_populates='transaction_credit'
    )

    def __repr__(self):
        return "<Transaction(" \
               "credit_account='%s', " \
               "debit_account='%s', " \
               "transaction_date='%s', " \
               "transaction_amount='%s'" \
               ")>" % (
                   self.credit_account,
                   self.debit_account,
                   self.transaction_date,
                   self.transaction_amount,
               )


class Customer(Base):
    __tablename__ = 'customer'

    customer_id = Column(
        Integer,
        primary_key=True
    )
    person_id = Column(Integer)
    company_id = Column(Integer)