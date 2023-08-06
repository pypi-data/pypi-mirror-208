from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from ta.trend import macd_diff

from novalabs.utils.backtest import BackTest

pd.options.mode.chained_assignment = None


class StratBacktest(BackTest):
    def __init__(
        self,
        exchange: str,
        list_pairs: list,
        strategy_name: str = "macd",
        candle: str = "1m",
        start: datetime = datetime(2022, 1, 1),
        end: datetime = datetime.now(),
        start_bk: int = 1000,
        leverage: int = 2,
        max_pos: int = 1,
        max_holding: timedelta = timedelta(minutes=5),
        quote_asset: str = "USDT",
        geometric_sizes: bool = True,
        plot_all_pairs_charts: bool = False,
        plot_exposure: bool = False,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        backtest_id: str = "",
        tp_sl_delta: float = 0.005,
    ):
        BackTest.__init__(
            self,
            exchange=exchange,
            strategy_name=strategy_name,
            candle=candle,
            list_pairs=list_pairs,
            start=start,
            end=end,
            start_bk=start_bk,
            leverage=leverage,
            max_pos=max_pos,
            max_holding=max_holding,
            quote_asset=quote_asset,
            geometric_sizes=geometric_sizes,
            plot_all_pairs_charts=plot_all_pairs_charts,
            plot_exposure=plot_exposure,
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            backtest_id=backtest_id,
        )

        self.tp_sl_delta = tp_sl_delta

    def build_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df["macd"] = macd_diff(close=df["close"])
        return df

    def entry_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        df["entry_signal"] = np.nan
        df["take_profit"] = np.nan
        df["stop_loss"] = np.nan
        df["position_size"] = 1 / 2

        long_conditions = (df["macd"] > 0) & (df["macd"].shift(1) < 0)
        short_conditions = (df["macd"] < 0) & (df["macd"].shift(1) > 0)
        df["entry_signal"] = np.where(
            long_conditions, 1, np.where(short_conditions, -1, np.nan)
        )

        df["take_profit"] = np.where(
            df["entry_signal"] == 1,
            df["close"] * (1 + self.tp_sl_delta),
            np.where(
                df["entry_signal"] == -1, df["close"] * (1 - self.tp_sl_delta), np.nan
            ),
        )
        df["stop_loss"] = np.where(
            df["entry_signal"] == 1,
            df["close"] * (1 - self.tp_sl_delta),
            np.where(
                df["entry_signal"] == -1, df["close"] * (1 + self.tp_sl_delta), np.nan
            ),
        )

        return df

    def exit_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        df["exit_signal"] = np.nan
        return df
