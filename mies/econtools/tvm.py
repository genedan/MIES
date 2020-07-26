# time value of money
import pandas as pd


class Payments:
    """
    A DataFrame that includes payment amounts, times, and interest rates
    """
    def __init__(
            self,
            data: pd.DataFrame
    ):
        self.data = data
        self.data['discount_factor'] = 1 / (1 + self.data['interest_rate'])
        self.data['pv_factor'] = self.data['discount_factor'].cumprod()

    def present_value(self):
        self.data['present_value'] = self.data['payment'] * self.data['pv_factor']
        present_value = self.data['present_value'].sum()
        return present_value


class Annuity:

    def __init__(
            self,
            interest_rate,
            number_of_payments,
            payment_amount=1):
        self.payment_amount = payment_amount
        self.interest_rate = interest_rate
        self.number_of_payments = number_of_payments

    def present_value(self):
        pv = self.payment_amount * (1 - (1 + self.interest_rate) ** (-self.number_of_payments)) / self.interest_rate
        return pv

    def future_value(self):
        fv = self.payment_amount * (((1 + self.interest_rate) ** self.number_of_payments) - 1) / self.interest_rate
        return fv


class Bond:

    def __init__(
            self,
            face_value,
            interest_rate,
            coupon_rate,
            number_of_payments):
        self.face_value = face_value
        self.interest_rate = interest_rate
        self.coupon_rate = coupon_rate
        self.coupon = self.face_value * self.coupon_rate
        self.data = pd.DataFrame()
        self.number_of_payments = number_of_payments
        self.data['t'] = pd.Series(range(1, self.number_of_payments + 1))
        self.data['coupon'] = self.coupon
        self.data['discount_factor'] = 1 / (1 + self.interest_rate)
        self.data['other_payments'] = 0
        self.data.iloc[-1, self.data.columns.get_loc('other_payments')] = self.face_value
        self.data['pv_factor'] = self.data['discount_factor'].cumprod()

    def present_value(self):
        self.data['present_value'] = (self.data['coupon'] + self.data['other_payments']) * self.data['pv_factor']
        pv = self.data['present_value'].sum()
        return pv


class Perpetuity:

    def __init__(
            self,
            interest_rate,
            payment_amount
    ):
        self.payment_amount = payment_amount
        self.interest_rate = interest_rate

    def present_value(self):
        pv = self.payment_amount / self.interest_rate
        return pv

