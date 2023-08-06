from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from novalabs.utils.backtest import BackTest


class StratBacktest(BackTest):
    def __init__(
        self,
        exchange: str,
        strategy_name: str,
        list_pairs: list,
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
        entry_l_prob: float = 0.2,
        entry_s_prob: float = 0.2,
        exit_prob: float = 0.2,
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

        # all optimized hyperparameters or set to stone
        self.entry_long_prob = entry_l_prob
        self.entry_short_prob = entry_s_prob
        self.exit_probability = exit_prob
        self.tp_sl_delta = tp_sl_delta

    def build_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df["entry_long"] = np.random.random(df.shape[0])
        df["entry_short"] = np.random.random(df.shape[0])
        df["exit_point"] = np.random.random(df.shape[0])
        return df

    def entry_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        df["entry_signal"] = np.nan
        df["take_profit"] = np.nan
        df["stop_loss"] = np.nan
        df["position_size"] = 1 / 2

        long_conditions = df["entry_long"] < self.entry_long_prob
        short_conditions = (
            df["entry_short"] < self.entry_short_prob + self.entry_long_prob
        )

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
        df["exit_signal"] = np.where(
            df["exit_point"] < self.exit_probability,
            1,
            np.where(df["exit_point"] < self.exit_probability * 2, -1, np.nan),
        )
        return df
