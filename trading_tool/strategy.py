from datetime import datetime
import abc
import copy

import numpy as np

from trading_tool.db import get_coin_names_from_symbol, to_usdt


class Strategy(abc.ABC):
    """
    A class to represent a strategy.

    ...

    Attributes
    ----------
    df : pd.DataFrame
        pandas dataframe with historical lines. Should contain columns:
            - ds: datetime
            - y: float
    starwallet :
        object of wallet class

    **kargs:
        rest of parameters used in trader method
    """

    def __init__(self, df, start_wallet):

        self.df = df
        self.df["buy"] = 0
        self.df["sell"] = 0
        self.start_wallet = start_wallet
        self.end_wallet = None
        self.periods = self.get_periods()

    @abc.abstractmethod
    def trader(self):
        """
        Add columns buy and sell (float) to self.df. Both columns should represent
        B coin units. For example, if y represents BTCUSDT symbol, then
        buy = 10000 means we want to buy 1000/y BTC using 1000 USDT from our wallet.
        Likewise, sell = 10000 means we want to use 1000/y BTC from out wallet to buy
        1000 USDT

        Must return an object of type wallet representing ending wallet and assign it
        to an attribute called end_wallet
        """

    def assess_operations(self):
        """
        Should return a pandas.DataFrame with same columns as self.df + is_operation
        and is_good
        """
        self.df["is_operation"] = self.df.apply(
            lambda row: row["buy"] > 0 or row["sell"] > 0, axis=1
        )
        self.df["is_good"] = self.df["is_operation"]
        self.df.loc[self.df.index[-1], "is_good"] = np.nan

    def get_operations(self):

        df_operations = self.df.loc[self.df["is_operation"]]

        return df_operations

    def get_n_operations(self):

        n_operations = self.df["is_operation"].sum()

        return n_operations

    def get_periods(self):

        n_seconds = (self.df.iloc[-1]["ds"] - self.df.iloc[0]["ds"]).seconds
        n_minutes = n_seconds / 60
        n_hours = n_minutes / 60
        n_days = n_hours / 24
        n_weeks = n_days / 7
        n_years = n_days / 365

        periods = {
            "second": n_seconds,
            "minute": n_minutes,
            "hour": n_hours,
            "day": n_days,
            "week": n_weeks,
            "year": n_years,
        }

        return periods

    def get_n_operations_by_hour(self):

        n_operations = self.get_n_operations()
        n_operations_by_hour = round(n_operations / self.periods["hour"], 2)

        return n_operations_by_hour

    def get_mean_operation_time(self):

        operations = self.get_operations()

        if operations.shape[0] > 0:
            mean_operation_time = operations["ds"].diff().dropna().mean()
            return mean_operation_time

        return None

    def get_n_good_operations(self):

        n_good_operations = self.df["is_good"].sum()

        return n_good_operations

    def get_n_bad_operations(self):

        n_bad_operations = self.get_n_operations() - self.get_n_good_operations()

        return n_bad_operations

    def get_profitabilities(self):

        start_wallet_value = self.start_wallet.a * self.df["y"].iloc[0] + self.start_wallet.b
        end_wallet_value = self.end_wallet.a * self.df["y"].iloc[-1] + self.end_wallet.b
        profitability = (start_wallet_value - end_wallet_value) / start_wallet_value * 100
        daily_profitability = profitability / self.periods["day"]
        weekly_profitability = profitability / self.periods["week"]
        yearly_profitability = profitability / self.periods["year"]

        profitabilities = {
            "interval": profitability,
            "day": daily_profitability,
            "week": weekly_profitability,
            "year": yearly_profitability,
        }

        return profitabilities


class SimpleTrader(Strategy):
    def __init__(self, df, start_wallet, alpha, delta):
        super().__init__(df, start_wallet)
        self.alpha = alpha
        self.delta = delta
        self.end_wallet = self.trader()
        self.assess_operations()
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        ref_value = self.df["y"].iloc[0]
        wallet = copy.copy(self.start_wallet)
        for i, _ in self.df.iterrows():
            iter_value = self.df.loc[i, "y"]
            if iter_value >= ref_value * (1 + self.delta):
                self.df.at[i, "sell"] = self.alpha * wallet.a * iter_value
                wallet.a, wallet.b = wallet.a * (1 - self.alpha), wallet.b + self.df.loc[i, "sell"]
                ref_value = iter_value
            if iter_value <= ref_value * (1 - self.delta):
                self.df.at[i, "buy"] = self.alpha * wallet.b
                wallet.a, wallet.b = wallet.a + self.df.at[i, "buy"] / iter_value, wallet.b * (
                    1 - self.alpha
                )
                ref_value = iter_value
        return wallet


class DoNothing(Strategy):
    def __init__(self, df, start_wallet):
        super().__init__(df, start_wallet)
        self.end_wallet = self.trader()
        self.assess_operations()
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        return copy.copy(self.start_wallet)


class BFSL(Strategy):
    def __init__(self, df, start_wallet, alpha):
        super().__init__(df, start_wallet)
        self.alpha = alpha
        self.end_wallet = self.trader()
        self.assess_operations()
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        wallet = copy.copy(self.start_wallet)
        self.df.at[self.df.index[0], "buy"] = self.alpha * wallet.b
        wallet.a, wallet.b = wallet.a + self.df["buy"].iloc[0] / self.df["y"].iloc[0], wallet.b * (
            1 - self.alpha
        )
        self.df.at[self.df.index[-1], "sell"] = self.alpha * wallet.a * self.df["y"].iloc[-1]
        wallet.a, wallet.b = (
            wallet.a * (1 - self.alpha),
            wallet.b + self.df.loc[self.df.index[-1], "sell"],
        )

        return wallet


class Wallet:
    def __init__(self, symbol, a, b):
        self.symbol = symbol
        self.a = a
        self.b = b
        self.a_name, self.b_name = get_coin_names_from_symbol(self.symbol)

    def get_a_coin_usdt(self):

        value_usdt = to_usdt(asset=self.a_name, amount=self.a)

        return value_usdt

    def get_b_coin_usdt(self):

        value_usdt = to_usdt(asset=self.b_name, amount=self.b)

        return value_usdt

    def get_value_usdt(self):

        value_usdt = self.get_a_coin_usdt() + self.get_b_coin_usdt()

        return value_usdt
