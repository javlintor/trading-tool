import abc
import copy

import numpy as np

from trading_tool.db import get_coin_names_from_symbol, to_usdt


def is_good_operation(row):
    # Return NaN if y_s1 is NaN
    if np.isnan(row["y_s1"]):
        return np.nan

    # Check if the operation is a buy and y < y_s1, or if the operation is not a buy and y > y_s1
    comb1 = row["is_buy"] and (row["y"] < row["y_s1"])
    comb2 = not row["is_buy"] and (row["y"] > row["y_s1"])

    # Return True if either condition is satisfied
    ret = comb1 or comb2

    return ret
    

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
        # Add a new column called "is_operation" that is True if the row has a buy or sell operation
        self.df["is_operation"] = self.df.apply(
            lambda row: row["buy"] > 0 or row["sell"] > 0, axis=1
        )
        # Add a new column called "is_buy" that is True if the row has a buy operation
        self.df["is_buy"] = self.df["buy"] > 0
        # Add a new column called "y_s1" that contains the y value of the next row with an operation
        self.df["y_s1"] = self.df.loc[self.df["is_operation"]]["y"].shift(-1)
        # Add a new column called "is_good" that is True if the operation is good according to the is_good_operation function
        self.df["is_good"] = self.df.apply(is_good_operation, axis=1)


    def get_operations(self):
        # Return a DataFrame containing only the rows that have an operation
        df_operations = self.df.loc[self.df["is_operation"]]

        return df_operations

    def get_n_operations(self):
        # Sum the number of operations in the DataFrame
        n_operations = self.df["is_operation"].sum()

        return n_operations

    def get_periods(self):
    # Calculate the number of seconds, minutes, hours, days, weeks, and years in the DataFrame
        n_seconds = (self.df.iloc[-1]["ds"] - self.df.iloc[0]["ds"]).seconds
        n_minutes = n_seconds / 60
        n_hours = n_minutes / 60
        n_days = n_hours / 24
        n_weeks = n_days / 7
        n_years = n_days / 365
        # Create a dictionary containing the number of each type of period
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
        # Get the total number of operations
        n_operations = self.get_n_operations()
        # Divide the total number of operations by the number of hours in the DataFrame
        n_operations_by_hour = round(n_operations / self.periods["hour"], 2)

        return n_operations_by_hour

    def get_mean_operation_time(self):
        # Get a DataFrame containing only the rows with operations
        operations = self.get_operations()

        if operations.shape[0] > 1:
            # Calculate the mean time between operations, in minutes
            mean_operation_time = (
                operations["ds"].diff().dropna().apply(lambda x: x.seconds // 60).mean()
            )
            # Round the mean time to 2 decimal places
            mean_operation_time = round(mean_operation_time, 2)
            # Format the mean time as a string
            mean_operation_time_str = f"{mean_operation_time} minutes"
            return mean_operation_time_str

        return "-"


    def get_n_good_operations(self):
        # Get the number of good operations by summing the "is_good" column
        n_good_operations = self.df["is_good"].sum()

        return n_good_operations

    def get_n_bad_operations(self):
        # Get the number of bad operations by subtracting the number of good operations from the total number of operations
        n_bad_operations = self.get_n_operations() - self.get_n_good_operations()

        return n_bad_operations

    def get_profitabilities(self):
        # Calculate the starting value of the wallet using the formula:
        # a * y-value at index 0 + b
        start_wallet_value = self.start_wallet.a * self.df["y"].iloc[0] + self.start_wallet.b
        # Calculate the ending value of the wallet using the formula:
        # a * y-value at index -1 + b
        # where -1 is the last index in the DataFrame
        end_wallet_value = self.end_wallet.a * self.df["y"].iloc[-1] + self.end_wallet.b
        # Calculate the overall profitability as a percentage
        profitability = (end_wallet_value - start_wallet_value) / start_wallet_value * 100
        # Calculate daily, weekly, and yearly profitabilities
        daily_profitability = profitability / self.periods["day"]
        weekly_profitability = profitability / self.periods["week"]
        yearly_profitability = profitability / self.periods["year"]
        # Get the number of operations
        n_operations = self.get_n_operations()
        # If there are no operations, set mean profitability to "NA"
        if n_operations == 0:
            mean_profitability = "NA"
        else:
            # Calculate mean profitability as a percentage
            mean_profitability = profitability / self.get_n_operations()

        # Return a dictionary of profitabilities
        profitabilities = {
            "interval": profitability,
            "mean": mean_profitability,
            "day": daily_profitability,
            "week": weekly_profitability,
            "year": yearly_profitability,
        }

        return profitabilities



class SimpleStrategy(Strategy):
    def __init__(self, df, start_wallet, alpha, delta):
        # Initialize the base Strategy class with the given DataFrame, start_wallet
        super().__init__(df, start_wallet)
        # Set alpha and delta values
        self.alpha = alpha
        self.delta = delta
        # Apply the trader strategy and set the end_wallet
        self.end_wallet = self.trader()
        # Assess the operations performed by the trader
        self.assess_operations()
        # Calculate profitabilities for the strategy
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        # Set the reference value to the initial y-value in the DataFrame
        ref_value = self.df["y"].iloc[0]
        # Make a copy of the starting wallet
        wallet = copy.copy(self.start_wallet)
        # Iterate through the DataFrame
        for i, _ in self.df.iterrows():
            # Get the current y-value
            iter_value = self.df.loc[i, "y"]
            # If the current y-value is greater than or equal to the reference value
            # multiplied by (1 + delta), sell alpha * wallet.a * iter_value
            if iter_value >= ref_value * (1 + self.delta):
                self.df.at[i, "sell"] = self.alpha * wallet.a * iter_value
                # Update wallet.a and wallet.b
                wallet.a, wallet.b = wallet.a * (1 - self.alpha), wallet.b + self.df.loc[i, "sell"]
                # Set the reference value to the current y-value
                ref_value = iter_value
            # If the current y-value is less than or equal to the reference value
            # multiplied by (1 - delta), buy alpha * wallet.b / iter_value
            if iter_value <= ref_value * (1 - self.delta):
                self.df.at[i, "buy"] = self.alpha * wallet.b
                # Update wallet.a and wallet.b
                wallet.a, wallet.b = wallet.a + self.df.at[i, "buy"] / iter_value, wallet.b * (
                    1 - self.alpha
                )
                # Set the reference value to the current y-value
                ref_value = iter_value
        # Return the updated wallet
        return wallet



class DummyStrategy(Strategy):
    def __init__(self, df, start_wallet):
        # Initialize the base Strategy class with the given DataFrame, start_wallet
        super().__init__(df, start_wallet)
        # Apply the trader strategy and set the end_wallet
        self.end_wallet = self.trader()
        # Assess the operations performed by the trader
        self.assess_operations()
        # Calculate profitabilities for the strategy
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        # Return a copy of the starting wallet without making any changes
        return copy.copy(self.start_wallet)



class BFSL(Strategy):
    def __init__(self, df, start_wallet, alpha):
        super().__init__(df, start_wallet)
        self.alpha = alpha
        self.end_wallet = self.trader()
        self.assess_operations()
        self.profitabilities = self.get_profitabilities()

    def trader(self):
        # Create a copy of the start_wallet
        wallet = copy.copy(self.start_wallet)
        # Set the buy amount in the dataframe at the first index
        self.df.at[self.df.index[0], "buy"] = self.alpha * wallet.b
        # Update the wallet with the buy amount and update the b amount
        wallet.a, wallet.b = wallet.a + self.df["buy"].iloc[0] / self.df["y"].iloc[0], wallet.b * (
            1 - self.alpha
        )
        # Set the sell amount in the dataframe at the last index
        self.df.at[self.df.index[-1], "sell"] = self.alpha * wallet.a * self.df["y"].iloc[-1]
        # Update the wallet with the sell amount and update the a amount
        wallet.a, wallet.b = (
            wallet.a * (1 - self.alpha),
            wallet.b + self.df.loc[self.df.index[-1], "sell"],
        )

        return wallet



class MovingAverageStrategy(Strategy):
    """
    df must contain aditional big_ma_window rows if compute_ma=True
    If compute_ma=False, then df must contain big_ma and small_ma columns
    """

    def __init__(self, df, start_wallet, big_ma_window, small_ma_window, alpha, compute_ma=True):
        super().__init__(df, start_wallet)
        self.df = df
        # create moving average columns
        self.big_ma_window = big_ma_window
        self.small_ma_window = small_ma_window
        if compute_ma:
            self.compute_ma()
        self.df["diff"] = self.df["big_ma"] - self.df["small_ma"]
        self.df.dropna(inplace=True)
        self.alpha = alpha
        self.end_wallet = self.trader()
        self.assess_operations()
        self.profitabilities = self.get_profitabilities()

    def compute_ma(self):
        # Compute the moving average for the big and small windows
        self.df["big_ma"] = self.df["y"].rolling(self.big_ma_window).mean()
        self.df["small_ma"] = self.df["y"].rolling(self.small_ma_window).mean()

    def trader(self):
        wallet = copy.copy(self.start_wallet)
        # Get the difference of the moving averages at the previous index
        previous_diff = self.df["diff"].iloc[0]
        # Iterate over the remaining rows of the dataframe
        for i, _ in self.df.iloc[1:].iterrows():

            # Get the difference of the moving averages at the current index
            iter_diff = self.df["diff"].loc[i]

            # If the previous difference is positive and the current difference is negative, sell
            if previous_diff > 0 and iter_diff < 0:

                # Set the sell amount in the dataframe and update the wallet
                self.df.at[i, "sell"] = self.alpha * wallet.a * self.df["close"].loc[i]
                wallet.a, wallet.b = wallet.a * (1 - self.alpha), wallet.b + self.df.loc[i, "sell"]

            # If the previous difference is negative and the current difference is positive, buy
            if previous_diff < 0 and iter_diff > 0:

                # Set the buy amount in the dataframe and update the wallet
                self.df.at[i, "buy"] = self.alpha * wallet.b
                wallet.a, wallet.b = wallet.a + self.df.at[i, "buy"] / self.df["close"].loc[
                    i
                ], wallet.b * (1 - self.alpha)

            previous_diff = iter_diff

        return wallet



class Wallet:
    """
    The Wallet class represents a collection of assets that can be traded. 
    It has attributes for the symbol of the assets, the amount of assets a and b, 
    and their corresponding names. It also has methods for converting the amount 
    of each asset to USDT using a given time, and for calculating the total value 
    of the wallet in USDT.
    """
    def __init__(self, symbol, a, b):
        self.symbol = symbol
        self.a = a
        self.b = b
        self.a_name, self.b_name = get_coin_names_from_symbol(self.symbol)

    def get_a_coin_usdt(self, time=None):
        # Convert the amount of asset a to USDT using the specified time
        value_usdt = to_usdt(asset=self.a_name, amount=self.a, time=time)

        return value_usdt

    def get_b_coin_usdt(self, time=None):
        # Convert the amount of asset b to USDT using the specified time
        value_usdt = to_usdt(asset=self.b_name, amount=self.b, time=time)

        return value_usdt

    def get_value_usdt(self, time=None):
        # Get the total value of the wallet in USDT by adding the values of assets a and b
        value_usdt = self.get_a_coin_usdt(time) + self.get_b_coin_usdt(time)

        return value_usdt

