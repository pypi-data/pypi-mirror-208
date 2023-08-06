import abc
from typing import Union

import pandas as pd


class ClientInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self, api_key: str, api_secret: str, passphrase: str, limit: int
    ) -> None:
        """
        Initialize the exchange API client with the specified credentials and parameters.

        Args:
            key: A string representing the API key for the exchange.
            secret: A string representing the secret key for the exchange.
            passphrase: A string representing the passphrase for the exchange.
            limit: number of candle that can be query at once

        Returns:
            None.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.limit = limit

    @abc.abstractmethod
    def _send_request(
        self, end_point: str, request_type: str, params: dict, signed: bool
    ) -> Union[dict, list]:
        """
        Send a request to the specified exchange API endpoint with the given parameters.

        Args:
            end_point: A string representing the API endpoint to send the request to.
            request_type: A string representing the type of HTTP request to send, e.g. 'GET' or 'POST'.
            params: A dictionary of parameters to include in the request.
            signed: A boolean flag indicating whether to include authentication information in the request.

        Returns:
            A dictionary containing the response data from the API endpoint.

        Raises:
            APIClientError: If there is an error with the API client, such as an invalid API key or missing required parameters.
            APIConnectionError: If there is an error connecting to the API endpoint, such as a network issue or a timeout.
            APIResponseError: If the API endpoint returns an error response, such as a 400 or 500 status code.
        """
        pass

    @abc.abstractmethod
    def get_server_time(self) -> int:
        """
        Retrieve the current server time from the exchange API server.

        Returns:
            An integer value representing the current server time in milliseconds.
        """
        pass

    @abc.abstractmethod
    def get_pairs_info(self, quote_asset: str) -> dict:
        """
        Retrieve information about available trading pairs on the exchange.

        Args:
            quote_asset: A string representing the quote asset to filter the trading pairs by, e.g. 'USDT'.

        Returns:
            A dictionary or list containing information about available trading pairs on the exchange. If there is no
            trading pair matching the quote asset, an empty dictionary or list will be returned.

            The dictionary has the following structure:
            {
                "pair_symbol": {
                    "quote_asset": str,
                    "tick_size": float,
                    "step_size": float,
                    "maxLimitQuantity": float,
                    "maxMarketQuantity": float,
                    "minQuantity": float
                },
                ...
            }
        """

    pass

    @abc.abstractmethod
    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        """
        Retrieve a batch of historical candlestick data for a specified trading pair, interval, and time range.

        Args:
            pair: A string representing the trading pair to retrieve data for, e.g. 'BTC-USD'.
            interval: A string representing the time interval of the candlesticks to retrieve, e.g. '1h' for 1 hour intervals.
            start_time: An integer representing the start time for the candlestick data in milliseconds since the Unix epoch.
            end_time: An integer representing the end time for the candlestick data in milliseconds since the Unix epoch.

        Returns:
            A dictionary containing the candlestick data for the specified trading pair, interval, and time range, with a
            maximum limit

        """
        pass

    @abc.abstractmethod
    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        """
        Retrieve the earliest available timestamp for candlestick data for the specified trading pair and time interval.

        Args:
            pair: A string representing the trading pair to retrieve data for, e.g. 'BTC-USD'.
            interval: A string representing the time interval of the candlesticks to retrieve, e.g. '1h' for 1 hour intervals.

        Returns:
            An integer representing the earliest available timestamp for candlestick data in milliseconds since the Unix epoch.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        """
        Format the raw candlestick data into a standardized pandas dataframe for further analysis.

        Args:
            all_data: A list or dict containing the raw candlestick data from the exchange API endpoint.

        Returns:
            A pandas dataframe containing the formatted candlestick data, including the following columns:
                - open_time: The opening time of the candlestick in milliseconds since the Unix epoch.
                - open: The opening price of the trading pair during the candlestick interval.
                - high: The highest price of the trading pair during the candlestick interval.
                - low: The lowest price of the trading pair during the candlestick interval.
                - close: The closing price of the trading pair during the candlestick interval.
                - volume: The trading volume during the candlestick interval.
                - close_time: The closing time of the candlestick in milliseconds since the Unix epoch.

            The dataframe may also contain additional columns specific to the exchange, such as the number of trades.
        """
        pass

    @abc.abstractmethod
    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        """
        Retrieve full historical candlestick data for a specified trading pair and time range, and return it as a
        standardized pandas dataframe.

        Args:
            pair: A string representing the trading pair for which to retrieve data, in the format "BTC/USD".
            interval: A string representing the granularity of the candlesticks to retrieve, in units of time (e.g. '1m' for
                1 minute intervals, '1h' for 1 hour intervals, etc.).
            start_ts: An integer representing the starting timestamp in milliseconds for the data to retrieve.
            end_ts: An integer representing the ending timestamp in milliseconds for the data to retrieve.

        Returns:
            A pandas dataframe containing the full historical candlestick data for the specified trading pair and time range,
            formatted as follows:
                - open_time: The opening time of the candlestick in milliseconds since the Unix epoch.
                - open: The opening price of the trading pair during the candlestick interval.
                - high: The highest price of the trading pair during the candlestick interval.
                - low: The lowest price of the trading pair during the candlestick interval.
                - close: The closing price of the trading pair during the candlestick interval.
                - volume: The trading volume during the candlestick interval.
            The dataframe will also contain any additional market data that is available, such as the number of trades.
        """
        pass

    @abc.abstractmethod
    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        """
        Retrieve extra market data for a specified trading pair and time interval, and return it as a Pandas DataFrame.
        It's important to know that those datapoints may not be supported on production

        Args:
            pair: A string representing the trading pair for which to retrieve market data.
            interval: A string representing the time interval for which to retrieve market data.

        Returns:
            A Pandas DataFrame containing extra market data for the specified trading pair and time interval, including
            global and top long/short account and position ratios, taker long/short ratios, and open interest.
        """
        pass
