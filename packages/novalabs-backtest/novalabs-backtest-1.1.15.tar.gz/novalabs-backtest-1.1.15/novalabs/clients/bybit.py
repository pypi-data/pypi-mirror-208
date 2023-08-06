import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import pandas as pd
from requests import Request, Session

from novalabs.interfaces.client_interface import ClientInterface
from novalabs.utils.constant import DATA_FORMATING
from novalabs.utils.helpers import interval_to_milliseconds


class Bybit(ClientInterface):
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

        self.based_endpoint = "https://api.bybit.com"

        self._session = Session()

    # API REQUEST FORMAT
    def _send_request(
        self,
        end_point: str,
        request_type: str,
        params: Optional[Dict[str, Any]] = {},
        signed: bool = False,
    ) -> dict:
        if params is None:
            params = {}

        if signed:
            params["api_key"] = self.api_key
            params["timestamp"] = int(time.time() * 1000)
            params = dict(sorted(params.items()))

            query_string = urlencode(params, True)
            query_string = query_string.replace("False", "false").replace(
                "True", "true"
            )

            m = hmac.new(
                self.api_secret.encode("utf-8"),
                query_string.encode("utf-8"),
                hashlib.sha256,
            )
            params["sign"] = m.hexdigest()

        if request_type == "POST":
            request = Request(
                request_type,
                f"{self.based_endpoint}{end_point}",
                data=json.dumps(params),
            )
        elif request_type == "GET":
            request = Request(
                request_type,
                f"{self.based_endpoint}{end_point}",
                params=urlencode(params, True),
            )
        else:
            raise ValueError("Please enter valid request_type")

        prepared = request.prepare()
        prepared.headers["Content-Type"] = "application/json"
        response = self._session.send(prepared, timeout=5)
        data = response.json()

        if data["ret_msg"] != "OK" and data["ret_code"] != 20001:
            print(f"{data['ret_code']} : {data['ret_msg']}")
            raise ValueError("Error when sending request")

        return data

    def get_server_time(self) -> int:
        ts = self._send_request(end_point="/v2/public/time", request_type="GET")[
            "time_now"
        ]
        return int(float(ts) * 1000)

    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int = 0
    ) -> list:
        _interval = self._convert_interval(std_interval=interval)

        data = self._send_request(
            end_point="/public/linear/kline",
            request_type="GET",
            params={
                "symbol": pair,
                "interval": _interval,
                "from": start_time // 1000,
                "limit": self.limit,
            },
        )
        return data["result"]

    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        _interval = self._convert_interval(std_interval=interval)

        kline = self._send_request(
            end_point="/public/linear/kline",
            request_type="GET",
            params={
                "symbol": pair,
                "interval": _interval,
                "from": 1467900800000 // 1000,
                "limit": 1,
            },
        )["result"]

        return kline[0]["open_time"] * 1000

    def get_pairs_info(self, quote_asset: str = "") -> dict:
        data = self._send_request(end_point="/v2/public/symbols", request_type="GET")[
            "result"
        ]

        pairs_info: Dict[str, Any] = {}

        for pair in data:
            contract_cond = (
                (pair["status"] == "Trading")
                if quote_asset == ""
                else (
                    pair["status"] == "Trading"
                    and pair["quote_currency"] == quote_asset
                )
            )

            if contract_cond:
                pairs_info[pair["name"]] = {}
                pairs_info[pair["name"]]["quote_asset"] = pair["quote_currency"]

                pairs_info[pair["name"]]["maxLimitQuantity"] = float(
                    pair["lot_size_filter"]["post_only_max_trading_qty"]
                )
                pairs_info[pair["name"]]["maxMarketQuantity"] = float(
                    pair["lot_size_filter"]["max_trading_qty"]
                )
                pairs_info[pair["name"]]["minQuantity"] = float(
                    pair["lot_size_filter"]["min_trading_qty"]
                )

                pairs_info[pair["name"]]["tick_size"] = float(
                    pair["price_filter"]["tick_size"]
                )
                pairs_info[pair["name"]]["step_size"] = float(
                    pair["lot_size_filter"]["qty_step"]
                )

        return pairs_info

    @staticmethod
    def _convert_interval(std_interval: str) -> str:
        if "m" in std_interval:
            return std_interval[:-1]
        elif "h" in std_interval:
            mul = int(std_interval[:-1])
            return str(60 * mul)
        else:
            return std_interval[-1].upper()

    @staticmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        interval_ms = 1000 * (all_data[1]["start_at"] - all_data[0]["start_at"])
        df = pd.DataFrame(all_data)[DATA_FORMATING["bybit"]["columns"]]

        for var in DATA_FORMATING["bybit"]["num_var"]:
            df[var] = pd.to_numeric(df[var], downcast="float")

        df["open_time"] = 1000 * df["open_time"]
        df["close_time"] = df["open_time"] + interval_ms - 1

        return df.dropna().reset_index(drop=True)

    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        # init our list
        klines = []

        # convert interval to useful value in ms
        timeframe = interval_to_milliseconds(interval)

        # establish first available start timestamp
        if start_ts is not None:
            first_valid_ts = self._get_earliest_timestamp(pair=pair, interval=interval)
            start_ts = max(start_ts, first_valid_ts)

        if end_ts and start_ts and end_ts <= start_ts:
            raise ValueError("end_ts must be greater than start_ts")

        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = self._get_candles(
                pair=pair, interval=interval, start_time=start_ts
            )

            # append this loops data to our output data
            if temp_data:
                klines += temp_data

            # handle the case where exactly the limit amount of data was returned last loop
            # check if we received less than the required limit and exit the loop
            if not len(temp_data) or len(temp_data) < self.limit:
                # exit the while loop
                break

            # increment next call by our timeframe
            start_ts = 1000 * temp_data[-1]["open_time"] + timeframe

            # exit loop if we reached end_ts before reaching <limit> klines
            if end_ts and start_ts >= end_ts:
                break

        df = self._format_data(all_data=klines)

        return df[df["open_time"] <= end_ts]

    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        pass
