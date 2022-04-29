from datetime import datetime
import abc

import numpy as np


def simple_strategy(df, alpha=0.1, delta=0.01, wallet=(1, 1), reverse=False):

    buy = []
    sell = []

    while df.shape[0] > 0:

        actual = df["close"].iloc[0]

        buy_limit = actual * (1 - delta)
        sell_limit = actual * (1 + delta)

        buy_future = df.loc[df["close"] <= buy_limit]
        sell_future = df.loc[df["close"] >= sell_limit]

        if buy_future.shape[0] > 0:
            buy_hor = buy_future.iloc[0]["dateTime"]
        else:
            buy_hor = datetime.max

        if sell_future.shape[0] > 0:
            sell_hor = sell_future.iloc[0]["dateTime"]
        else:
            sell_hor = datetime.max

        next_brake = min(buy_hor, sell_hor)
        if next_brake == datetime.max:
            break

        df = df.loc[df["dateTime"] > next_brake]

        is_buy = buy_hor < sell_hor
        if reverse:
            is_buy = ~is_buy

        if is_buy:

            if wallet[1] > 0:
                wallet = wallet[0] + alpha * wallet[1] / actual, wallet[1] * (1 - alpha)
                buy.append(next_brake)

        else:

            if wallet[0] > 0:
                wallet = wallet[0] * (1 - alpha), wallet[1] + alpha * wallet[0] * actual
                sell.append(next_brake)

    return buy, sell, wallet


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
        tuple with starting amounts of each coin

    **kargs:
        rest of parameters used in trader method
    """

    def __init__(self, df, start_wallet):

        self.df = df.copy()
        self.df["buy"] = 0
        self.df["sell"] = 0
        self.start_wallet = start_wallet
        self.periods = self.get_periods()

    @abc.abstractmethod
    def trader(self):
        """
        Add columns buy and sell (float) to self.df. Both columns should represent
        B coin units. For example, if y represents BTCUSDT symbol, then
        buy = 10000 means we want to buy 1000/y BTC using 1000 USDT from our wallet.
        Likewise, sell = 10000 means we want to use 1000/y BTC from out wallet to buy
        1000 USDT
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

    def get_end_wallet(self):

        wallet = self.start_wallet
        operations = self.get_operations()
        for _, row in operations.iterrows():
            buy_sell = row["buy"] - row["sell"]
            wallet = wallet[0] + buy_sell / row["y"], wallet[1] - buy_sell
        return wallet

    def get_profitability(self):

        start_wallet_value = self.start_wallet[0] * self.df["y"].iloc[0] + self.start_wallet[1]
        end_wallet = self.get_end_wallet()
        end_wallet_value = end_wallet[0] * self.df["y"].iloc[-1] + end_wallet[1]
        profitability = start_wallet_value / end_wallet_value
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


class DoNothing(Strategy):
    def __init__(self, df, start_wallet):
        super().__init__(df, start_wallet)
        self.trader()
        self.assess_operations()

    def trader(self):
        pass


class BFSL(Strategy):
    def __init__(self, df, start_wallet, alpha):
        super().__init__(df, start_wallet)
        self.alpha = alpha
        self.trader()
        self.assess_operations()

    def trader(self):
        self.df.loc[0, "buy"] = self.alpha
