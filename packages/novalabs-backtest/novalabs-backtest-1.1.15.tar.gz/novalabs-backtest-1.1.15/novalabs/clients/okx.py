import base64
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

import numpy as np
import pandas as pd
from requests import Request, Session

from novalabs.interfaces.client_interface import ClientInterface
from novalabs.utils.constant import DATA_FORMATING
from novalabs.utils.helpers import interval_to_milliseconds


class OKX(ClientInterface):
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        limit: int = 90,
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, passphrase=passphrase, limit=limit
        )

        self.based_endpoint = "https://www.okx.com"
        self._session = Session()

    def _send_request(
        self,
        end_point: str,
        request_type: str,
        params: Optional[Mapping[str, Any]] = {},
        signed: bool = False,
    ) -> dict:
        now = datetime.utcnow()
        timestamp = now.isoformat("T", "milliseconds") + "Z"
        request = Request(
            request_type, f"{self.based_endpoint}{end_point}", data=params
        )
        prepared = request.prepare()

        if signed:
            body = ""
            if params:
                body = json.dumps(params)
                prepared.body = body

            to_hash = str(timestamp) + str.upper(request_type) + end_point + body

            mac = hmac.new(
                bytes(self.api_secret, encoding="utf8"),
                bytes(to_hash, encoding="utf-8"),
                digestmod="sha256",
            )

            signature = base64.b64encode(mac.digest())

            prepared.headers["OK-ACCESS-KEY"] = self.api_key
            prepared.headers["OK-ACCESS-SIGN"] = signature.decode("utf-8")
            prepared.headers["OK-ACCESS-PASSPHRASE"] = self.passphrase

        prepared.headers["Content-Type"] = "application/json"
        prepared.headers["OK-ACCESS-TIMESTAMP"] = timestamp
        prepared.headers["User-Agent"] = "Novalabs.ai"

        response = self._session.send(prepared)

        return response.json()

    def get_server_time(self) -> int:
        return int(
            self._send_request(
                end_point="/api/v5/public/time",
                request_type="GET",
            )[
                "data"
            ][0]["ts"]
        )

    def get_pairs_info(self, quote_asset: str) -> dict:
        data = self._send_request(
            end_point="/api/v5/public/instruments?instType=SWAP", request_type="GET"
        )["data"]

        pairs_info: Dict[str, Any] = {}

        for pair in data:
            if (
                pair["settleCcy"] == quote_asset
                and pair["state"] == "live"
                and pair["instType"] == "SWAP"
                and pair["ctType"] == "linear"
            ):
                pairs_info[pair["instId"]] = {}

                pairs_info[pair["instId"]]["based_asset"] = pair["ctValCcy"]
                pairs_info[pair["instId"]]["quote_asset"] = pair["settleCcy"]

                size_increment = np.format_float_positional(
                    float(pair["ctVal"]), trim="-"
                )
                price_increment = np.format_float_positional(
                    float(pair["tickSz"]), trim="-"
                )

                pairs_info[pair["instId"]]["maxQuantity"] = float("inf")
                pairs_info[pair["instId"]]["minQuantity"] = float(size_increment)

                price_precision = (
                    int(str(price_increment)[::-1].find("."))
                    if float(pair["tickSz"]) < 1
                    else 1
                )
                pairs_info[pair["instId"]]["tick_size"] = float(pair["tickSz"])
                pairs_info[pair["instId"]]["pricePrecision"] = price_precision

                qty_precision = (
                    int(str(size_increment)[::-1].find("."))
                    if float(pair["ctVal"]) < 1
                    else 1
                )
                pairs_info[pair["instId"]]["step_size"] = float(pair["minSz"])
                pairs_info[pair["instId"]]["quantityPrecision"] = qty_precision

                pairs_info[pair["instId"]]["earliest_timestamp"] = int(pair["listTime"])

                pairs_info[pair["instId"]]["contract_value"] = float(pair["ctVal"])
                pairs_info[pair["instId"]]["contract_multiplier"] = float(
                    pair["ctMult"]
                )

        return pairs_info

    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        _bar = interval if "m" in interval else interval.upper()
        _endpoint = f"/api/v5/market/history-candles?instId={pair}&bar={_bar}&before={start_time}&after={end_time}&limit={self.limit}"
        return self._send_request(
            end_point=_endpoint,
            request_type="GET",
        )["data"]

    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        data = self._send_request(
            end_point=f"/api/v5/public/instruments?instType=SWAP&instId={pair}",
            request_type="GET",
        )["data"]
        return int(data[0]["listTime"])

    @staticmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        df = pd.DataFrame(all_data, columns=DATA_FORMATING["okx"]["columns"])
        df = df.sort_values(by="open_time").reset_index(drop=True)

        for var in DATA_FORMATING["okx"]["num_var"]:
            df[var] = pd.to_numeric(df[var], downcast="float")
        for var in ["open_time"]:
            df[var] = df[var].astype(int)

        df = df.sort_values(by="open_time").reset_index(drop=True)
        interval_ms = df.loc[1, "open_time"] - df.loc[0, "open_time"]
        df["close_time"] = df["open_time"] + interval_ms - 1

        return df.dropna().drop_duplicates("open_time")

    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        klines: List[Any] = []

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

            # append this loops data to our output data
            if temp_data:
                klines += temp_data
            else:
                break

            # handle the case where exactly the limit amount of data was returned last loop
            # check if we received less than the required limit and exit the loop

            # increment next call by our timeframe
            start_time = int(temp_data[0][0])
            # exit loop if we reached end_ts before reaching <limit> klines
            if start_time >= end_ts:
                break

            # sleep after every 3rd call to be kind to the API
            idx += 1
            if idx % 20 == 0:
                time.sleep(1)

        data = self._format_data(all_data=klines)
        return data[(data["open_time"] >= start_ts) & (data["open_time"] <= end_ts)]

    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        pass
