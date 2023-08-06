import json
import time
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

import pandas as pd
from requests import Request, Session

from novalabs.interfaces.client_interface import ClientInterface
from novalabs.utils.helpers import (
    interval_to_milliseconds,
    interval_to_oanda_granularity,
)


class Oanda(ClientInterface):
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        limit: int = 1000,
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, passphrase=passphrase, limit=limit
        )
        self.based_endpoint = "https://api-fxpractice.oanda.com"
        self._session = Session()

    def _send_request(
        self,
        end_point: str,
        request_type: str,
        params: Optional[Mapping[str, Any]] = {},
        signed: bool = False,
    ) -> dict:
        url = f"{self.based_endpoint}{end_point}"
        request = Request(request_type, url, data=json.dumps(params))
        prepared = request.prepare()
        prepared.headers["Content-Type"] = "application/json"
        prepared.headers["OANDA-Agent"] = "Novalabs.ai"
        prepared.headers["Authorization"] = f"Bearer {self.api_secret}"
        prepared.headers["Accept-Datetime-Format"] = "UNIX"

        response = self._session.send(prepared)
        return response.json()

    @staticmethod
    def get_server_time() -> int:
        return int(time.time() * 1000)

    def get_pairs_info(self, quote_asset: str) -> dict:
        response = self._send_request(
            end_point=f"/v3/accounts/{self.api_key}/instruments",
            params={"accountID": self.api_key},
            request_type="GET",
        )["instruments"]

        pairs_info: Dict[str, Any] = {}

        for pair in response:
            if pair["type"] == "CURRENCY":
                _name = pair["name"]

                pairs_info[_name] = {}

                pairs_info[_name]["maxQuantity"] = float(pair["maximumOrderUnits"])
                pairs_info[_name]["minQuantity"] = float(pair["minimumTradeSize"])

                pairs_info[_name]["pricePrecision"] = int(pair["displayPrecision"])
                pairs_info[_name]["quantityPrecision"] = 1

        return pairs_info

    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        gran = interval_to_oanda_granularity(interval=interval)
        _start = start_time / 1000
        _end = end_time / 1000

        return self._send_request(
            end_point=f"/v3/instruments/{pair}/candles?price=M&granularity={gran}&from={_start}&to={_end}",
            params={
                "price": "M",
                "granularity": gran,
                "from": str(_start),
                "to": str(_end),
            },
            request_type="GET",
        )["candles"]

    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        starting_date = int(datetime(2018, 1, 1).timestamp())
        gran = interval_to_oanda_granularity(interval=interval)

        response = self._send_request(
            end_point=f"/v3/instruments/{pair}/candles?price=M&granularity={gran}&from={starting_date}&count=10",
            params={
                "price": "M",
                "granularity": gran,
                "count": 10,
                "from": str(starting_date),
            },
            request_type="GET",
        )["candles"][0]["time"]

        return int(float(response) * 1000)

    @staticmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        final: Dict[str, list] = {
            "open_time": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
        }

        for info in all_data:
            final["open_time"].append(int(float(info["time"]) * 1000))
            final["open"].append(float(info["mid"]["o"]))
            final["high"].append(float(info["mid"]["h"]))
            final["low"].append(float(info["mid"]["l"]))
            final["close"].append(float(info["mid"]["c"]))
            final["volume"].append(float(info["volume"]))

        df = pd.DataFrame(final)
        df = df.drop_duplicates("open_time")
        interval_ms = df["open_time"].iloc[1] - df["open_time"].iloc[0]
        df["close_time"] = df["open_time"] + interval_ms - 1

        for var in ["open_time", "close_time"]:
            df[var] = df[var].astype(int)

        return df.dropna().drop_duplicates().reset_index(drop=True)

    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        # init our list
        klines = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        first_valid_ts = self._get_earliest_timestamp(pair=pair, interval=interval)

        start_time = int(max(start_ts, first_valid_ts))

        idx = 0
        while True:
            end_t = int(start_time + timeframe * self.limit)
            end_time = min(end_t, end_ts)

            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = self._get_candles(
                pair=pair, interval=interval, start_time=start_time, end_time=end_time
            )

            # append this loops data to our output data
            if temp_data:
                klines += temp_data

            if len(temp_data) == 0:
                break
            # handle the case where exactly the limit amount of data was returned last loop
            # check if we received less than the required limit and exit the loop

            # increment next call by our timeframe
            start_time = int(float(temp_data[-1]["time"]) * 1000)

            # exit loop if we reached end_ts before reaching <limit> klines
            if end_time >= end_ts or start_time >= end_ts:
                break

            # sleep after every 3rd call to be kind to the API
            idx += 1
            if idx % 3 == 0:
                time.sleep(1)

        data = self._format_data(all_data=klines)

        return data[(data["open_time"] >= start_ts) & (data["open_time"] <= end_ts)]

    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        pass
