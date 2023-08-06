import abc
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from novalabs.clients.clients import clients
from novalabs.utils.constant import FEES
from novalabs.utils.helpers import get_timedelta_unit


class BacktestInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        exchange: str,
        strategy_name: str,
        candle: str,
        list_pairs: list,
        start: datetime,
        end: datetime,
        start_bk: float,
        leverage: int,
        max_pos: int,
        max_holding: timedelta,
        quote_asset: str = "USDT",
        geometric_sizes: bool = False,
        plot_all_pairs_charts: bool = False,
        plot_exposure: bool = False,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        backtest_id: str = "",
    ) -> None:
        """

        This is the initialization method for the `BackTest` class, which is used for backtesting trading strategies. The method is marked as an abstract method using the `abc.abstractmethod` decorator, which means that it must be implemented by any concrete subclass of `BackTest`.

        Args:
            - exchange (str): The exchange to backtest on (e.g., 'bybit', 'binance', 'okx', 'huobi', 'kucoin', 'oanda' or 'btcex').
            - strategy_name (str): The name of the strategy being backtested.
            - candle (str): The candle size / timeframe with format `%m` or `%h` or `%d` (e.g., '5m' for five minute candles).
            - list_pairs (list): A list of pairs to backtest.
            - start (datetime): The start datetime of the backtest.
            - end (datetime): The end datetime of the backtest.
            - start_bk (float): The starting bankroll size for the backtest.
            - leverage (int): The leverage to use for trades.
            - max_pos (int): The maximum number of simultaneous positions.
            - max_holding (timedelta): The maximum holding time of a position.
            - quote_asset (str): The quote asset (default is 'USDT').
            - geometric_sizes (bool): If True, adjust position sizes with bankroll evolution. If profit > 0 positions sizes will increase proportionally, else will decrease (default is False).
            - plot_all_pairs_charts (bool): If True, print each pair's profits charts. Else, save and print only cumulative profits chart (default is False).
            - plot_exposure (bool): If True, plot wallet exposure through time.
            - api_key (str): The exchange's API KEY (**only for oanda**).
            - api_secret (str): The exchange's API SECRET (**only for oanda**).
            - passphrase (str): The passphrase (**only for oanda**).
            - backtest_id (str): The ID of the backtest.
        Returns:
            None.
        """

        self.exchange = exchange
        self.quote_asset = quote_asset
        self.strategy_name = strategy_name
        self.backtest_id = backtest_id
        self.positions_size = leverage / max_pos
        self.geometric_sizes = geometric_sizes
        self.leverage = leverage

        self.client = clients(
            exchange=exchange,
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
        )

        self.start_bk = start_bk
        self.actual_bk = self.start_bk
        self.start = start
        self.end = end
        self.candle = candle
        self.fees = FEES[exchange]
        self.list_pairs = list_pairs
        self.last_exit_date = np.nan
        self.max_pos = max_pos
        self.max_holding = max_holding
        self.plot_all_pairs_charts = plot_all_pairs_charts
        self.plot_exposure = plot_exposure
        self.time_step = get_timedelta_unit(interval=candle)

        self.pairs_info = self.client.get_pairs_info(quote_asset=quote_asset)

        # Initialize DataFrames
        self.df_all_positions: Dict[str, Any] = {}
        self.df_pairs_stat = pd.DataFrame()
        self.df_pos = pd.DataFrame()

        frequency = (
            self.candle.replace("m", "min") if "m" in self.candle else self.candle
        )
        self.df_pos["open_time"] = pd.date_range(start=start, end=end, freq=frequency)
        for var in [
            "all_positions",
            "total_profit_all_pairs",
            "long_profit_all_pairs",
            "short_profit_all_pairs",
            "wallet_exposure",
        ]:
            self.df_pos[var] = 0

        self.position_cols: List[Any] = []
        self.df_all_pairs_positions = pd.DataFrame()

    @abc.abstractmethod
    def build_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Must be re-written to fit with your strategy (cf. documentation -> Usage -> Example -> Write build_indicators()).

        Args:
            - df (DataFrame): DataFrame returned by get_historical_data().
        Returns:
            DataFrame returned by get_historical_data() with all the indicators (new columns added) neccessary to the strategy.
        """
        raise Exception("Please write your build_indicator() method.")

    @abc.abstractmethod
    def entry_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Must be re-written to fit with your strategy (cf. documentation -> Usage -> Example -> Write entry_strategy()).

        Args:
            - df (DataFrame): DataFrame returned by build_indicators().

        Returns:
            DataFrame returned by build_indicators() with 4 new columns.
                - entry_signal (int): **-1** for entering short at the next open, **+1** for long.
                - position_size (float): **float between 0 and 1**. Position size in quote asset = bankroll * position_size * (self.leverage / self.max_pos)
                - stop_loss (float): stop loss price.
                - take_profit (float): take profit price.
        """
        raise Exception("Please write your entry_strategy() method.")

    @abc.abstractmethod
    def exit_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Must be re-written to fit with your strategy (cf. documentation -> Usage -> Example -> Write exit_strategy()).

        Args:
            - df (DataFrame): DataFrame returned by entry_strategy().

        Returns:
            DataFrame returned by entry_strategy() with 1 new column.
                - exit_signal (int): **-1** for exiting long (sell the asset) at the next open, **+1** for for exiting short (buy the asset).
        """
        raise Exception("Please write your exit_strategy() method.")

    @abc.abstractmethod
    def _verify_all_pairs(self) -> None:
        """
        This is a private method that verifies whether the trading pairs specified in the `list_pairs` attribute of the `BackTest` class are valid. The method calls the `get_pairs_info` method of the client associated with the `BackTest` instance to retrieve information about all available trading pairs on the exchange, and then checks whether each pair in the `list_pairs` attribute is present in the list of available pairs. If a pair is not valid, the method raises an `AssertionError` with a message indicating which pair is not valid and a list of all available pairs on the exchange.

        Returns:
            None.

        Raises:
            - AssertionError: If any of the trading pairs specified in the `list_pairs` attribute are not valid.
        """
        pass

    @abc.abstractmethod
    def _verify_df_format(self, df: pd.DataFrame) -> None:
        """
        Verifies the format of a Pandas DataFrame containing OHLC data.

        Args:
            df (pd.DataFrame): DataFrame containing OHLC data, with columns for open_time, close_time, open, high, low, and close.

        Returns:
            None.

        Raises:
            AssertionError: If the candle interval for open time or close time is incorrect, or if the time series is not
            respected.
        """
        pass

    @abc.abstractmethod
    def _create_directories(self) -> None:
        """
        Creates the directories to store historical data.

        This function checks if the 'database' directory exists in the current working directory.
        If not, it creates the 'database' directory. It then checks if a subdirectory with the name of the exchange exists
        inside the 'database' directory. If not, it creates the subdirectory with the name of the exchange inside the
        'database' directory.

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    def get_historical_data(self, pair: str) -> pd.DataFrame:
        """
        Downloads historical data for a given trading pair and interval.

        The function first checks if historical data for the given trading pair and interval already exists in the
        '/database' folder. If yes, it reads the csv file into a pandas dataframe and checks if the data is up to date.
        If the data is outdated (older than 24 hours), it updates the dataframe with new data from the exchange API
        and saves the updated data to the csv file. If the data file does not exist, it downloads the historical
        data from the exchange API, saves it to a csv file and returns the data as a pandas dataframe.

        Args:
            pair (str): trading pair to download the historical data for.

        Returns:
            pd.DataFrame: pandas dataframe containing the historical data for the given trading pair and interval.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _create_entry_prices_times(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all_entry_price and all_entry_time columns in a DataFrame based on entry signals.

        Args:
            df (pd.DataFrame): DataFrame that contains the 'entry_signal' column with the following properties:
                1 -> enter long position
                -1 -> enter short position
                nan -> no actions

        Returns:
            pd.DataFrame: DataFrame with 'all_entry_price' and 'all_entry_time' columns added based on the entry signals.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _create_all_exit_point(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a column with the type of exit for each position, based on the exit signal and holding time.
        If a position is closed due to a Stop Loss, it will have a value of 'SL' in the 'all_exit_point' column.
        If it is closed due to a Take Profit, it will have a value of 'TP' in the 'all_exit_point' column.
        If it is closed due to reaching the maximum holding time, it will have a value of 'MaxHolding' in the 'all_exit_point' column.
        If it is closed due to an exit signal, it will have a value of 'ExitSignal' in the 'all_exit_point' column.
        If a position is still open, it will have a value of NaN in the 'all_exit_point' column.

        Args:
            df: DataFrame containing the columns 'entry_signal', 'closest_sl', 'closest_tp', 'max_hold_date' and 'exit_signal_date' (optional).

        Returns:
            DataFrame with an additional column 'all_exit_point' indicating the type of exit for each position.
        """
        pass

    @abc.abstractmethod
    def _create_closest_exit(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds columns to the DataFrame indicating the closest stop-loss, take-profit, and exit-signal to the current candle.
        Drops leading variables once the closest stop-loss and take-profit are found.

        Args:
            df: A pandas DataFrame with columns 'high', 'low', 'open', 'open_time', 'close_time', 'entry_signal',
                'stop_loss', 'take_profit', 'exit_signal', and 'max_holding'.

        Returns:
            A pandas DataFrame with added columns 'closest_sl', 'closest_tp', 'max_hold_date', 'exit_signal_date',
            'sl_lead_i', 'tp_lead_i', and 'es_lead_i' for 1 <= i < max_holding in the DataFrame df. The leading variables
            (i.e. the 'sl_lead_i', 'tp_lead_i', and 'es_lead_i' columns) are dropped in the returned DataFrame.
        """
        pass

    @abc.abstractmethod
    def _create_position_df(self, df: pd.DataFrame, pair: str) -> None:
        """
        This function creates a dataframe with all the necessary information for each position,
        including the entry and exit time, price and point, the take profit, stop loss,
        and the computed profit.

        Args:
            df: the dataframe that contains the information to compute the position data
            pair: the trading pair for which to compute the position data

        Returns:
            None (the function only adds the computed dataframe to the class variable df_all_positions)
        """
        pass

    @abc.abstractmethod
    def _compute_profit(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the profit and loss for each position in the input dataframe.

        Args:
            df: pandas dataframe containing the following columns:
                - entry_time: datetime of position entry
                - entry_point: int indicating the entry signal (1 for long, -1 for short)
                - entry_price: float indicating the price at entry
                - exit_time: datetime of position exit
                - exit_point: str indicating the type of exit point (SL, TP, MaxHolding, ExitSignal)
                - exit_price: float indicating the price at exit
                - take_profit: float indicating the take profit value
                - stop_loss: float indicating the stop loss value

        Returns:
            A pandas dataframe with the following columns:
                - entry_time: datetime of position entry
                - entry_point: int indicating the entry signal (1 for long, -1 for short)
                - entry_price: float indicating the price at entry
                - exit_time: datetime of position exit
                - exit_point: str indicating the type of exit point (SL, TP, MaxHolding, ExitSignal)
                - exit_price: float indicating the price at exit
                - take_profit: float indicating the take profit value
                - stop_loss: float indicating the stop loss value
                - nb_minutes_in_position: int indicating the duration of the position in minutes
                - tx_fees_paid: float indicating the transaction fees paid
                - PL_amt_realized: float indicating the realized profit or loss amount
                - PL_prc_realized: float indicating the realized profit or loss percentage
                - minutes_bf_next_position: int indicating the time in minutes between the exit of the current position and the
                                            entry of the next position

        """
        pass

    @abc.abstractmethod
    def _create_timeseries(self, df: pd.DataFrame, pair: str) -> None:
        """
        Creates a timeseries for a given currency pair using the input DataFrame and updates the main DataFrame with the
        results. The function adds the entry point, realized profit, and exit point to the main DataFrame, creates an
        "in_position" variable and forward fills it, computes the pair exposure, creates a cumulative total profit for
        the pair, and updates the bot's total profit and exposure.

        Args:
            df: A pandas DataFrame containing the input data.
            pair: A string representing the currency pair to create the timeseries for.

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    def plot_profit_graph(self, pair: str) -> None:
        """
        Plots the total profit, long profit, and short profit over time for a specific pair.

        Parameters:
        pair (str): The trading pair to plot the profit graph for.

        Returns:
        None.
        """
        pass

    @abc.abstractmethod
    def plot_wallet_exposure_graph(self) -> None:
        """
        Plots a graph of wallet exposure over time.

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    def _get_pair_stats(self, df: pd.DataFrame, pair: str) -> None:
        """
        Calculates various performance statistics for a given pair and stores the results in the
        `df_pairs_stat` dataframe.

        This function takes a pandas DataFrame of backtest results for a given pair and calculates various
        performance statistics such as total positions, average minutes in position, total profit amount,
        total transaction fees, etc. The function also calculates statistics per type of position (long or short)
        and per type of exit (TP, SL, ExitSignal, MaxHolding) and adds them to the results.
        The results are stored in the `df_pairs_stat` dataframe for future use in reporting and analysis.

        Args:
            df (pd.DataFrame): A pandas DataFrame containing the backtest results for a given pair.
            pair (str): The trading pair being analyzed.

        Returns:
            None. The results are stored in the `df_pairs_stat` dataframe.


        """
        pass

    @abc.abstractmethod
    def _all_pairs_real_positions(self) -> None:
        """
        This method aims to delete all positions that could not have been taken because the maximum position
        limit would be reached. It creates a concatenated DataFrame containing all positions across all pairs.
        If no position has been taken during the backtest period, it will raise an exception. The DataFrame is
        then sorted by exit time and entries that are above the maximum position limit are deleted. If the number
        of signals is zero, it is skipped, and the exit times are appended. If the signal number is above zero,
        the actual number of positions will increase by the number of signals. The method then computes the position
        size and updates the DataFrame's position_size column. The exit times are appended again, and it repeats
        the same process. The cumulative_profit column is created by calculating the cumulative sum of the realized
        profit, and the bankroll_size column is obtained by adding the cumulative_profit column to the initial bankroll.
        Finally, it calls _create_timeseries and _get_pair_stats to create time series data for all pairs and gather
        statistics about the pairs.

        Args:
            - None
        Returns:
            None. The results are stored in the `df_pairs_stat` dataframe and `df_all_positions`.

        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _compute_daily_return(
        row: pd.Series, df_all_pairs_positions: pd.DataFrame
    ) -> pd.Series:
        """
        Computes the daily return of the trading strategy based on the positions taken during the day. This function is
        used in conjunction with the `apply` method on a DataFrame to create a new column 'daily_percentage_profit'.

        Parameters:
        row (pd.Series): a row of a pandas DataFrame containing information about a specific trading day.
        df_all_pairs_positions (pd.DataFrame): a pandas DataFrame containing all the positions taken by the trading strategy.

        Returns:
        pd.Series: a pandas Series object containing the daily return of the trading strategy.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _compute_drawdown(row: pd.Series, df_daily: pd.DataFrame) -> pd.Series:
        """
        This method computes the drawdown of a given row by comparing the bankroll of the current day with the highest
        bankroll since the start of the backtest.

        Parameters:
        row (pd.Series): The row of data for which to compute the drawdown.
        df_daily (pd.DataFrame): The daily dataframe with the cumulative profit and bankroll.

        Returns:
        pd.Series: The updated row with the computed drawdown, last date of maximum bankroll, and number of days since
        the last date of maximum bankroll.
        """
        pass

    @abc.abstractmethod
    def _get_daily_return(
        self, since: datetime, df_all_pairs_pos: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Computes the daily percentage profit, bankroll, and drawdown for each day between `since` and the end of the backtest,
        based on the positions held in `df_all_pairs_pos`.

        Args:
            - since (datetime): The starting date for the backtest period.
            - df_all_pairs_pos (pd.DataFrame): The DataFrame containing the positions of all pairs.

        Returns:
        a DataFrame with the following columns:
        - date: The date of the daily return
        - daily_percentage_profit: The percentage profit for the day
        - bankroll: The bankroll for the day
        - drawdown: The maximum drawdown since the last peak in the bankroll
        - last_date_max: The date of the last peak in the bankroll
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _get_overview_statistics(
        df_all_pairs_pos: pd.DataFrame, df_day: pd.DataFrame
    ) -> dict:
        """
        Computes and returns a dictionary containing various statistics related to the trading strategy.

        Args:
            df_all_pairs_pos (pd.DataFrame): A DataFrame containing all the trading positions taken by the strategy.
            df_day (pd.DataFrame): A DataFrame containing daily statistics such as daily return and drawdown.

        Returns:
            dict: A dictionary containing the following statistics:
            - 'Realized profit'
            - 'Average profit / trade'
            - 'Average profit / trade (%)'
            - 'Profits std dev'
            - 'Profits std dev (%)'
            - 'Average position size'
            - 'Average profit / winning trade'
            - 'Average profit / winning trade (%)'
            - 'Average loss / losing trade'
            - 'Average profit / losing trade (%)'
            - 'Average Long Profit (%)'
            - 'Average Short Profit (%)'
            - 'Average hold duration (in hours)'
            - 'Best trade profit'
            - 'Worst trade loss'
            - 'Cumulative fees paid'
            - 'Nb winning trade'
            - 'Nb losing trade'
            - 'Total nb trade'
            - '% winning trade'
            - 'Nb long positions'
            - 'Nb short positions'
            - '% Exit signal'
            - '% Max Holding'
            - '% TP'
            - '% SL'
            - 'Best day profit'
            - 'Worst day loss'
            - 'Max Nb Days Underwater'
        """
        pass

    @abc.abstractmethod
    def _get_performance_statistics(
        self, since: datetime, real_profit: float, df_day: pd.DataFrame
    ) -> dict:
        """
        Calculates various performance statistics based on backtesting results.

        Args:
            since (datetime): Start date of the backtesting period.
            real_profit (float): Total profit obtained during the backtesting period.
            df_day (pd.DataFrame): Pandas DataFrame containing daily profit and loss information.

        Returns:
            dict: A dictionary containing various performance statistics calculated based on the input data.

            The statistics calculated include:
            - Total return: the total percentage return on the backtesting period
            - Geometric return (yearly): the yearly geometric return on investment
            - Annualized standard deviation: the annualized standard deviation of daily returns
            - Sharpe Ratio: a measure of risk-adjusted return
            - Sortino Ratio: a measure of risk-adjusted return that only considers downside volatility
            - Max DrawDown: the maximum loss experienced during the backtesting period
            - Max DrawDown start: the date at which the maximum drawdown started
            - Max DrawDown end: the date at which the maximum drawdown ended

            The function returns a dictionary containing all of these statistics, rounded to two decimal places where applicable.
        """
        pass

    @abc.abstractmethod
    def _get_pairs_statistics(self) -> dict:
        """Calculates various statistics related to pairs trading.

        Returns:
            dict: A dictionary containing various statistics related to pairs trading.

        The statistics calculated include:
        - Best return pair: the pair that yielded the highest profit during the backtesting period
        - Best return value: the value of the highest profit obtained during the backtesting period
        - Worst return pair: the pair that yielded the lowest profit during the backtesting period
        - Worst return value: the value of the lowest profit obtained during the backtesting period
        - Pair with most positions: the pair that had the highest number of positions during the backtesting period, along with the total number of positions taken
        - Pair with less positions: the pair that had the lowest number of positions during the backtesting period, along with the total number of positions taken

        The function returns a dictionary containing all of these statistics, rounded to two decimal places where applicable.
        """
        pass

    @abc.abstractmethod
    def _print_all_statistics(
        self, since: datetime, overview: dict, statistics: dict, pairs_stats: dict
    ) -> None:
        """Prints all performance statistics to the console.

        Args:
            since (datetime): Start date of the backtesting period.
            overview (dict): A dictionary containing various overview statistics.
            statistics (dict): A dictionary containing various performance statistics.
            pairs_stats (dict): A dictionary containing various statistics related to pairs trading.

        Returns:
            None

        This function takes as input the dictionaries containing the various performance statistics, and prints them to the console in a formatted manner. The statistics are grouped into three sections: Overview, Statistics, and Pairs stats.
        The Overview section contains high-level statistics about the backtesting period, including the start and end dates, the starting account balance, and the total profit or loss.
        The Statistics section contains various performance statistics related to the backtesting period, including the total return, annualized standard deviation, Sharpe Ratio, and Sortino Ratio.
        The Pairs stats section contains various statistics related to pairs trading, including the best and worst performing pairs, as well as the pairs with the most and least positions.
        Each section is printed with a header, and each statistic is printed with its corresponding value, separated by a vertical bar. The function uses a fixed-width format to ensure that the output is properly aligned.
        """
        pass

    @abc.abstractmethod
    def _create_full_statistics(self, since: datetime) -> dict:
        """Creates a dictionary containing all performance statistics.

        Args:
            since (datetime): Start date of the backtesting period.

        Returns:
            dict: A dictionary containing various performance statistics, including overview, statistics, pairs stats, start date, and end date.

        This function takes as input the start date of the backtesting period, and returns a dictionary containing all performance statistics related to the backtesting period. These statistics are grouped into several categories:

        - Overview: high-level statistics about the backtesting period, including the start and end dates, the starting account balance, and the total profit or loss.
        - Statistics: various performance statistics related to the backtesting period, including the total return, annualized standard deviation, Sharpe Ratio, and Sortino Ratio.
        - Pairs stats: various statistics related to pairs trading, including the best and worst performing pairs, as well as the pairs with the most and least positions.
        - Start date: the start date of the backtesting period.
        - End date: the end date of the backtesting period.

        The function first filters the dataframe containing all pairs positions to only include positions that occurred after the start date. It then calculates the daily returns and uses them to compute the overview and performance statistics. Finally, it computes various statistics related to pairs trading and prints all of the statistics to the console using the _print_all_statistics function.

        The function returns a dictionary containing all of these statistics.
        """
        pass

    @abc.abstractmethod
    def _max_stop_loss(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates the maximum stop loss for each position.

        Args:
            df (pd.DataFrame): A dataframe containing information about each position.

        Returns:
            pd.DataFrame: A modified dataframe containing the maximum stop loss for each position.

        This function takes as input a dataframe containing information about each position, and calculates the maximum stop loss for each position. The maximum stop loss is calculated differently depending on whether the position is a long or short position.
        For a long position, the maximum stop loss is calculated as the maximum value between the stop loss specified in the input dataframe and the entry price multiplied by (1 - 1 / leverage). This ensures that the stop loss is set at a level that is proportional to the leverage used in the trade.
        For a short position, the maximum stop loss is calculated as the minimum value between the stop loss specified in the input dataframe and the entry price multiplied by (1 + 1 / leverage). This ensures that the stop loss is set at a level that is proportional to the leverage used in the trade.
        The function then modifies the input dataframe by adding a new column called 'stop_loss', which contains the maximum stop loss for each position. The modified dataframe is then returned.
        """
        pass

    @abc.abstractmethod
    def not_any_future_info(self) -> None:
        """Verifies that the backtesting process does not use any future information.

        This function checks that the backtesting process does not use any future information to compute the entry points, stop losses, take profits, or exit signals of each position. It does this by verifying that the entry points, stop losses, and take profits of a randomly selected subset of positions are the same when recomputed using only the historical data available at the time of entry.
        The function then checks that the exit signals of a randomly selected subset of positions are the same when recomputed using only the historical data available at the time of exit.
        If any discrepancies are found between the original positions and the recomputed positions, an assertion error is raised. If all positions pass the test, a message is printed to the console indicating that the test has passed.

        Returns:
            None
        Raises:
            AssertionError: if any discrepancies are found between the original positions and the recomputed positions.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _verify_tp_sl(df: pd.DataFrame) -> None:
        """
        Verify that stop loss and take profit levels are valid and that position size coefficients are between 0 and 1.
        Raises an AssertionError if any of these conditions are not met.

        Args:
        - df: A pandas DataFrame containing the trade data with columns for entry signal, stop loss, take profit, close price,
            and position size.

        Returns:
        - None
        """
        pass

    @abc.abstractmethod
    def run_backtest(self, save: bool = True) -> Tuple[pd.DataFrame, dict]:
        """
        Runs the backtest for all pairs in the `list_pairs` attribute.

        Args:
            save (bool, optional): Whether to save the results. Defaults to True.

        Returns:
            tuple[pd.DataFrame, dict]: A tuple containing the DataFrame of all pairs' positions and a dictionary of
            all computed statistics.
        """
        pass
