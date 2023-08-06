import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

import numpy as np
import pandas as pd
from requests import Request, Session

from novalabs.interfaces.client_interface import ClientInterface
from novalabs.utils.constant import DATA_FORMATING
from novalabs.utils.helpers import (
    interval_to_milliseconds,
    interval_to_minutes,
    milliseconds_to_interval,
)


class Kucoin(ClientInterface):
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        limit: int = 200,
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, passphrase=passphrase, limit=limit
        )

        self.based_endpoint = "https://api-futures.kucoin.com"
        self._session = Session()

    def _send_request(
        self,
        end_point: str,
        request_type: str,
        params: Optional[Mapping[str, Any]] = {},
        signed: bool = False,
    ) -> dict:
        request = Request(
            request_type, f"{self.based_endpoint}{end_point}", data=json.dumps(params)
        )
        prepared = request.prepare()

        timestamp = int(time.time() * 1000)

        prepared.headers["Content-Type"] = "application/json"
        prepared.headers["KC-API-KEY-VERSION "] = "2"
        prepared.headers["User-Agent"] = "NovaLabs"
        prepared.headers["KC-API-TIMESTAMP"] = str(timestamp)

        if signed:
            final_dict = ""
            if params:
                final_dict = json.dumps(params)

            sig_str = f"{timestamp}{request_type}{end_point}{final_dict}".encode(
                "utf-8"
            )
            signature = base64.b64encode(
                hmac.new(
                    self.api_secret.encode("utf-8"), sig_str, hashlib.sha256
                ).digest()
            )

            prepared.headers["KC-API-SIGN"] = signature.decode("utf-8")
            prepared.headers["KC-API-KEY"] = self.api_key
            prepared.headers["KC-API-PASSPHRASE"] = self.passphrase

        response = self._session.send(prepared)
        return response.json()

    def get_server_time(self) -> int:
        return self._send_request(end_point="/api/v1/timestamp", request_type="GET")[
            "data"
        ]

    def get_pairs_info(self, quote_asset: str) -> dict:
        data = self._send_request(
            end_point="/api/v1/contracts/active", request_type="GET", signed=False
        )["data"]

        pairs_info: Dict[str, Any] = {}

        for pair in data:
            if pair["status"] == "Open" and pair["quoteCurrency"] == quote_asset:
                if pair["multiplier"] > 0:
                    step_size = pair["lotSize"] * pair["multiplier"]
                else:
                    step_size = pair["lotSize"]

                pairs_info[pair["symbol"]] = {}
                pairs_info[pair["symbol"]]["quote_asset"] = pair["quoteCurrency"]

                price_increment = np.format_float_positional(pair["tickSize"], trim="-")

                pairs_info[pair["symbol"]]["maxQuantity"] = float(pair["maxOrderQty"])
                pairs_info[pair["symbol"]]["minQuantity"] = float(step_size)

                pairs_info[pair["symbol"]]["tick_size"] = float(pair["tickSize"])

                if float(pair["tickSize"]) < 1:
                    pairs_info[pair["symbol"]]["pricePrecision"] = int(
                        str(price_increment)[::-1].find(".")
                    )
                else:
                    pairs_info[pair["symbol"]]["pricePrecision"] = 0

                pairs_info[pair["symbol"]]["step_size"] = float(step_size)
                if step_size < 1:
                    pairs_info[pair["symbol"]]["quantityPrecision"] = int(
                        str(step_size)[::-1].find(".")
                    )
                else:
                    pairs_info[pair["symbol"]]["quantityPrecision"] = 1

                pairs_info[pair["symbol"]]["multiplier"] = pair["multiplier"]

        return pairs_info

    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        _interval_min = interval_to_minutes(interval)

        _endpoint = f"/api/v1/kline/query?symbol={pair}&granularity={_interval_min}&from={start_time}"
        data = self._send_request(end_point=f"{_endpoint}", request_type="GET")

        return data["data"]

    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        _interval_min = interval_to_minutes(interval)
        beg = int(datetime(2022, 1, 1).timestamp() * 1000)
        _endpoint = (
            f"/api/v1/kline/query?symbol={pair}&granularity={_interval_min}&from={beg}"
        )

        data = self._send_request(end_point=f"{_endpoint}", request_type="GET")["data"]

        return data[0][0]

    @staticmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        df = pd.DataFrame(all_data, columns=DATA_FORMATING["kucoin"]["columns"])
        df = df.drop_duplicates("open_time")
        for var in DATA_FORMATING["kucoin"]["num_var"]:
            df[var] = pd.to_numeric(df[var], downcast="float")

        interval_ms = df["open_time"].iloc[1] - df["open_time"].iloc[0]

        final_data = df.drop_duplicates().reset_index(drop=True)
        _first_time = datetime.fromtimestamp(final_data.loc[0, "open_time"] // 1000.0)
        _last_time = datetime.fromtimestamp(
            final_data.loc[len(final_data) - 1, "open_time"] // 1000.0
        )
        _freq = milliseconds_to_interval(interval_ms)

        final_timeseries = pd.DataFrame(
            pd.date_range(
                start=_first_time, end=_last_time, freq=_freq, tz="US/Eastern"
            ),
            columns=["open_time"],
        )

        final_timeseries["open_time"] = (
            final_timeseries["open_time"].astype(np.int64) // 10**6
        )

        clean_df = final_timeseries.merge(final_data, on="open_time", how="left")

        all_missing = clean_df.isna().sum().sum()

        if all_missing > 0:
            print(f"Kucoin returned {all_missing} NAs ! FFill and  BFill Applied")
            clean_df = clean_df.ffill()
            clean_df = clean_df.bfill()

        clean_df["close_time"] = clean_df["open_time"] + interval_ms - 1

        for var in ["open_time", "close_time"]:
            clean_df[var] = clean_df[var].astype(int)

        return clean_df.dropna()

    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        # init our list
        klines = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        first_valid_ts = self._get_earliest_timestamp(pair=pair, interval=interval)

        start_time = max(start_ts, first_valid_ts)

        idx = 0
        while True:
            end_t = int(start_time + timeframe * self.limit)
            end_time = min(end_t, end_ts)

            temp_data = self._get_candles(
                pair=pair, interval=interval, start_time=start_time, end_time=end_time
            )
            # exit loop if we reached end_ts before reaching klines
            if start_time >= end_ts or not len(temp_data):
                break

            # append this loops data to our output data
            if temp_data:
                klines += temp_data

            # increment next call by our timeframe
            start_time = temp_data[-1][0]

            # sleep after every 3rd call to be kind to the API
            idx += 1
            if idx % 3 == 0:
                time.sleep(1)

        data = self._format_data(all_data=klines)

        return data[(data["open_time"] >= start_ts) & (data["open_time"] <= end_ts)]

    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        pass
