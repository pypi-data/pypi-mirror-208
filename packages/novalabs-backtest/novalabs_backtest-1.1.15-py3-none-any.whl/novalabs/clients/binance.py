import hashlib
import hmac
import time
from typing import Any, Dict
from urllib.parse import urlencode

import pandas as pd
from requests import Request, Session

from novalabs.interfaces.client_interface import ClientInterface
from novalabs.utils.constant import DATA_FORMATING
from novalabs.utils.helpers import interval_to_milliseconds


class Binance(ClientInterface):
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

        self.based_endpoint = "https://fapi.binance.com"
        self._session = Session()

    def _send_request(
        self,
        end_point: str,
        request_type: str,
        params: Dict[str, Any] = {},
        signed: bool = False,
    ) -> dict:
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            query_string = urlencode(params, True).replace("%40", "@")
            m = hmac.new(
                self.api_secret.encode("utf-8"),
                query_string.encode("utf-8"),
                hashlib.sha256,
            )
            params["signature"] = m.hexdigest()

        request = Request(
            request_type,
            f"{self.based_endpoint}{end_point}",
            params=urlencode(params, True).replace("%40", "@"),
        )

        prepared = request.prepare()
        prepared.headers["Content-Type"] = "application/json;charset=utf-8"
        prepared.headers["User-Agent"] = "Novalabs.ai"
        prepared.headers["X-MBX-APIKEY"] = self.api_key

        response = self._session.send(prepared, timeout=5)

        data = response.json()

        return data

    def get_server_time(self) -> int:
        data = self._send_request(end_point="/fapi/v1/time", request_type="GET")
        return int(data["serverTime"])

    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        data = self._send_request(
            end_point="/fapi/v1/klines",
            request_type="GET",
            params={
                "symbol": pair,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": self.limit,
            },
        )

        return list(data)

    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        kline = self._send_request(
            end_point="/fapi/v1/klines",
            request_type="GET",
            params={
                "symbol": pair,
                "interval": interval,
                "startTime": 0,
                "endTime": int(time.time() * 1000),
                "limit": 1,
            },
        )
        return kline[0][0]

    @staticmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        df = pd.DataFrame(all_data, columns=DATA_FORMATING["binance"]["columns"])
        for var in DATA_FORMATING["binance"]["num_var"]:
            df[var] = pd.to_numeric(df[var], downcast="float")
        for var in DATA_FORMATING["binance"]["date_var"]:
            df[var] = pd.to_numeric(df[var], downcast="integer")
        return df.dropna()

    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        output_data = []
        timeframe = interval_to_milliseconds(interval)

        first_valid_ts = self._get_earliest_timestamp(pair=pair, interval=interval)
        start_ts = max(start_ts, first_valid_ts)
        end_ts = end_ts

        if end_ts and start_ts and end_ts <= start_ts:
            raise ValueError("end_ts must be greater than start_ts")

        idx = 0
        while True:
            temp_data = self._get_candles(
                pair=pair, interval=interval, start_time=start_ts, end_time=end_ts
            )

            if temp_data:
                output_data += temp_data
            if not len(temp_data) or len(temp_data) < self.limit:
                break

            start_ts = temp_data[-1][0] + timeframe

            if end_ts and start_ts >= end_ts:
                break

            idx += 1
            if idx % 3 == 0:
                time.sleep(1)

        return self._format_data(all_data=output_data)

    def get_pairs_info(self, quote_asset: str) -> dict:
        info = self._send_request(
            end_point="/fapi/v1/exchangeInfo",
            request_type="GET",
        )
        output: Dict[str, Any] = {}
        for symbol in info["symbols"]:
            if (
                symbol["contractType"] == "PERPETUAL"
                and symbol["status"] == "TRADING"
                and symbol["quoteAsset"] == quote_asset
            ):
                pair = symbol["symbol"]
                output[pair] = {}
                output[pair]["quote_asset"] = symbol["quoteAsset"]
                for fil in symbol["filters"]:
                    if fil["filterType"] == "PRICE_FILTER":
                        output[pair]["tick_size"] = float(fil["tickSize"])
                    elif fil["filterType"] == "LOT_SIZE":
                        output[pair]["step_size"] = float(fil["stepSize"])
                        output[pair]["maxLimitQuantity"] = float(fil["maxQty"])
                    elif fil["filterType"] == "MARKET_LOT_SIZE":
                        output[pair]["maxMarketQuantity"] = float(fil["maxQty"])
                        output[pair]["minQuantity"] = float(fil["minQty"])
        return output

    def _format_long_short_ratio(self, data: list) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(data)
        df["longShortRatio"] = pd.to_numeric(df["longShortRatio"], downcast="float")
        df = df.rename(columns={"timestamp": "open_time"})
        df["longShortRatio"] = df["longShortRatio"].shift(-1)
        return df[["open_time", "longShortRatio"]]

    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        # global long short Account ratio
        glob = self._send_request(
            end_point="/futures/data/globalLongShortAccountRatio",
            request_type="GET",
            params={"symbol": pair, "period": interval, "limit": 500},
        )
        glob_long_short = self._format_long_short_ratio(data=list(glob)).rename(
            columns={"longShortRatio": "globalLongShortRatio"}
        )

        # top long short Account ratio
        top = self._send_request(
            end_point="/futures/data/topLongShortAccountRatio",
            request_type="GET",
            params={"symbol": pair, "period": interval, "limit": 500},
        )
        top_long_short = self._format_long_short_ratio(data=list(top)).rename(
            columns={"longShortRatio": "topLongShortRatio"}
        )

        # top long short Position ratio
        pos = self._send_request(
            end_point="/futures/data/topLongShortPositionRatio",
            request_type="GET",
            params={"symbol": pair, "period": interval, "limit": 500},
        )
        pos_long_short = self._format_long_short_ratio(data=list(pos)).rename(
            columns={"longShortRatio": "topLongShortRatioPositions"}
        )

        # taker long short ratio
        take = self._send_request(
            end_point="/futures/data/takerlongshortRatio",
            request_type="GET",
            params={"symbol": pair, "period": interval, "limit": 500},
        )
        df_take = pd.DataFrame.from_dict(take)
        df_take["buySellRatio"] = pd.to_numeric(
            df_take["buySellRatio"], downcast="float"
        )
        df_take = df_take.rename(columns={"timestamp": "open_time"})

        # open interest
        inter = self._send_request(
            end_point="/futures/data/openInterestHist",
            request_type="GET",
            params={"symbol": pair, "period": interval, "limit": 500},
        )
        df_inter = pd.DataFrame.from_dict(inter)
        df_inter["openInterestClose"] = df_inter["sumOpenInterest"].shift(-1)
        df_inter = df_inter.rename(columns={"timestamp": "open_time"})

        df = pd.merge(glob_long_short, top_long_short, on="open_time", how="left")
        df = pd.merge(df, pos_long_short, on="open_time", how="left")
        df = pd.merge(df, df_take, on="open_time", how="left")
        df = pd.merge(df, df_inter, on="open_time", how="left")

        return df
