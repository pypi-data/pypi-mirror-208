import json
import math
import os
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from novalabs.interfaces.backtest_interface import BacktestInterface
from novalabs.utils.constant import VAR_NEEDED_FOR_POSITION
from novalabs.utils.helpers import (
    convert_candle_to_timedelta,
    convert_max_holding_to_candle_nb,
    interval_to_milliseconds,
)

warnings.filterwarnings("ignore")


class BackTest(BacktestInterface):
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
        super().__init__(
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

        self._verify_all_pairs()

    def build_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        raise Exception("Please write your build_indicator() method.")

    def entry_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        raise Exception("Please write your entry_strategy() method.")

    def exit_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        raise Exception("Please write your exit_strategy() method.")

    def _verify_all_pairs(self) -> None:
        pairs_information = self.client.get_pairs_info(quote_asset=self.quote_asset)
        all_pairs = list(pairs_information.keys())
        for pair in self.list_pairs:
            assert (
                pair in all_pairs
            ), f"{pair} is not a valid trading pair.\nHere is the list of all available pairs on {self.exchange}:\n{all_pairs}"

    def _verify_df_format(self, df: pd.DataFrame) -> None:
        if self.exchange not in ["oanda"]:
            open_time_difference = df["open_time"] - df["open_time"].shift(1)
            close_time_difference = df["close_time"] - df["close_time"].shift(1)
            assert open_time_difference.max() == interval_to_milliseconds(
                self.candle
            ), "Candle interval is wrong for open_time"
            assert close_time_difference.max() == interval_to_milliseconds(
                self.candle
            ), "Candle interval is wrong for close_time"
            assert (
                open_time_difference.max() == open_time_difference.min()
            ), "Time series not respected"
            assert (
                close_time_difference.min() == close_time_difference.max()
            ), "Time series not respected"

    def _create_directories(self) -> None:
        # Create folder if it does not exist yet
        if "database" not in os.listdir(f"{os.getcwd()}"):
            print("Creating Folder /database")
            os.mkdir(f"{os.getcwd()}/database")
        if self.exchange not in os.listdir(f"{os.getcwd()}/database"):
            print(f"Creating Folder /{self.exchange}")
            os.mkdir(f"{os.getcwd()}/database/{self.exchange}")

    def get_historical_data(self, pair: str) -> pd.DataFrame:
        self._create_directories()

        if f"hist_{pair}_{self.candle}.csv" in os.listdir(
            f"{os.getcwd()}/database/{self.exchange}"
        ):
            print(f"READING HISTORICAL DATA FROM /database/{self.exchange}")
            df = pd.read_csv(f"database/{self.exchange}/hist_{pair}_{self.candle}.csv")

            latest_saved_open = df["open_time"].iloc[-1]
            current_time = int(datetime.timestamp(datetime.now()) * 1000)
            if (current_time - latest_saved_open) >= 86400000:
                print(f"UPDATING HISTORICAL DATA FROM /database/{self.exchange}")
                new_candles = self.client.get_historical_data(
                    pair=pair,
                    interval=self.candle,
                    start_ts=latest_saved_open,
                    end_ts=current_time,
                )

                df = (
                    pd.concat([df, new_candles])
                    .reset_index(drop=True)
                    .drop_duplicates("open_time")
                    .sort_values("open_time")
                )

                self._verify_df_format(df)
                df.to_csv(
                    f"database/{self.exchange}/hist_{pair}_{self.candle}.csv",
                    index=False,
                )

            else:
                self._verify_df_format(df)

        else:
            print(f"DOWNLOADING HISTORICAL DATA {pair}")
            df = self.client.get_historical_data(
                pair=pair,
                interval=self.candle,
                start_ts=int(datetime.timestamp(datetime(2019, 1, 1)) * 1000),
                end_ts=int(datetime.timestamp(datetime.now()) * 1000),
            )
            self._verify_df_format(df)
            df.to_csv(
                f"database/{self.exchange}/hist_{pair}_{self.candle}.csv", index=False
            )

        # transform timestamp into datetime + add next_open
        for var in ["open_time", "close_time"]:
            df[var] = pd.to_datetime(df[var], unit="ms")
        df["next_open"] = df["open"].shift(-1)

        return df[
            (df.open_time >= self.start) & (df.open_time <= self.end)
        ].reset_index(drop=True)

    @staticmethod
    def _create_entry_prices_times(df: pd.DataFrame) -> pd.DataFrame:
        df["all_entry_price"] = np.where(
            df.entry_signal.notnull(), df.next_open, np.nan
        )
        df["all_entry_time"] = np.where(
            df.entry_signal.notnull(), df.open_time.shift(-1), np.datetime64("NaT")
        )
        return df

    @staticmethod
    def _create_all_exit_point(df: pd.DataFrame) -> pd.DataFrame:
        all_exit_var = ["closest_sl", "closest_tp", "max_hold_date"]
        if "exit_signal_date" in df.columns:
            all_exit_var.append("exit_signal_date")

        df["all_exit_time"] = df[all_exit_var].min(axis=1)
        condition_exit_type_sl = (df.entry_signal.notnull()) & (
            df["all_exit_time"] == df["closest_sl"]
        )
        condition_exit_type_tp = (df.entry_signal.notnull()) & (
            df["all_exit_time"] == df["closest_tp"]
        )
        max_hold_date_sl = (df.entry_signal.notnull()) & (
            df["all_exit_time"] == df["max_hold_date"]
        )

        if "exit_signal_date" in all_exit_var:
            condition_exit_strat = (df.entry_signal.notnull()) & (
                df["all_exit_time"] == df["exit_signal_date"]
            )
            df["all_exit_point"] = np.where(
                condition_exit_type_sl,
                "SL",
                np.where(
                    condition_exit_type_tp,
                    "TP",
                    np.where(
                        max_hold_date_sl,
                        "MaxHolding",
                        np.where(condition_exit_strat, "ExitSignal", np.nan),
                    ),
                ),
            )
        else:
            df["all_exit_point"] = np.where(
                condition_exit_type_sl,
                "SL",
                np.where(
                    condition_exit_type_tp,
                    "TP",
                    np.where(max_hold_date_sl, "MaxHolding", np.nan),
                ),
            )

        return df

    def _create_closest_exit(self, df: pd.DataFrame) -> pd.DataFrame:
        lead_sl = []
        lead_tp = []
        lead_es = []
        nb_candle = convert_max_holding_to_candle_nb(
            candle=self.candle, max_holding=self.max_holding
        )

        for i in range(1, nb_candle):
            condition_sl_long = (df.low.shift(-i) <= df.stop_loss) & (
                df.entry_signal == 1
            )
            condition_sl_short = (df.high.shift(-i) >= df.stop_loss) & (
                df.entry_signal == -1
            )
            condition_tp_short = (
                (df.low.shift(-i) <= df.take_profit)
                & (df.high.shift(-i) <= df.stop_loss)
                & (df.entry_signal == -1)
            )
            condition_tp_long = (
                (df.entry_signal == 1)
                & (df.high.shift(-i) >= df.take_profit)
                & (df.low.shift(-i) >= df.stop_loss)
            )

            df[f"sl_lead_{i}"] = np.where(
                condition_sl_long | condition_sl_short,
                df.open_time.shift(-i),
                np.datetime64("NaT"),
            )
            df[f"tp_lead_{i}"] = np.where(
                condition_tp_short | condition_tp_long,
                df.open_time.shift(-i),
                np.datetime64("NaT"),
            )
            lead_sl.append(f"sl_lead_{i}")
            lead_tp.append(f"tp_lead_{i}")

            if "exit_signal" in df.columns:
                df[f"es_lead_{i}"] = np.where(
                    (df["exit_signal"].shift(-i) * df["entry_signal"]) == -1,
                    df.open_time.shift(-i - 1),
                    np.datetime64("NaT"),
                )
                lead_es.append(f"es_lead_{i}")
        df["closest_sl"] = df[lead_sl].min(axis=1)
        df["closest_tp"] = df[lead_tp].min(axis=1)
        if "exit_signal" in df.columns:
            df["exit_signal_date"] = df[lead_es].min(axis=1)
        df["max_hold_date"] = np.where(
            df.entry_signal.notnull(),
            df["open_time"].shift(-1) + self.max_holding,
            np.datetime64("NaT"),
        )

        df = df.drop(lead_sl + lead_tp + lead_es, axis=1)
        return df

    def _create_position_df(self, df: pd.DataFrame, pair: str) -> None:
        final_df = df[VAR_NEEDED_FOR_POSITION].dropna().reset_index(drop=True)
        if len(final_df) == 0:
            return None

        # create the variable that indicates if a transaction is good or not
        final_df["not_overlapping"] = np.nan
        # For Loop in all the transaction (from the oldest to the newest)
        # determine if the transaction could have been executed (don't overlap another trade)
        for index, row in final_df.iterrows():
            good = True
            if index == 0:
                self.last_exit_date = row.all_exit_time
            elif row.all_entry_time <= self.last_exit_date:
                good = False
            else:
                self.last_exit_date = row.all_exit_time
            final_df.loc[index, "not_overlapping"] = good

        # keep only the real transaction that can be executed
        final_df = final_df[final_df["not_overlapping"]]
        final_df = final_df.drop("not_overlapping", axis=1)
        final_df.reset_index(drop=True, inplace=True)

        # add back the 'next_open' variable
        final_df = pd.merge(
            final_df,
            df[["open_time", "open"]],
            how="left",
            left_on=["all_exit_time"],
            right_on=["open_time"],
        )
        final_df = final_df.drop("open_time", axis=1)

        # compute the exit price for depending on the exit point category
        final_df["exit_price"] = np.where(
            final_df["all_exit_point"] == "SL",
            final_df["stop_loss"],
            np.where(
                final_df["all_exit_point"] == "TP",
                final_df["take_profit"],
                final_df["open"],
            ),
        )

        # removing non important variables and renaming columns
        final_df = final_df.drop(["open"], axis=1)
        final_df = final_df.rename(
            columns={
                "all_entry_time": "entry_time",
                "entry_signal": "entry_point",
                "all_entry_price": "entry_price",
                "all_exit_time": "exit_time",
                "all_exit_point": "exit_point",
                "take_profit": "tp",
                "stop_loss": "sl",
            }
        )

        final_df = self._compute_profit(final_df)

        self.df_all_positions[pair] = final_df

    def _compute_profit(self, df: pd.DataFrame) -> pd.DataFrame:
        df["nb_minutes_in_position"] = (df.exit_time - df.entry_time).astype(
            "timedelta64[s]"
        ).astype(int) // 60
        df["prc_not_realized"] = (
            df["entry_point"]
            * (df["exit_price"] - df["entry_price"])
            / df["entry_price"]
        )
        df["amt_not_realized"] = df["prc_not_realized"] * 100
        df["tx_fees_paid"] = 100 * (2 + df["prc_not_realized"] - self.fees) * self.fees
        df["PL_amt_realized"] = df["amt_not_realized"] - df["tx_fees_paid"]
        df["PL_prc_realized"] = df["PL_amt_realized"] / 100
        df["next_entry_time"] = df.entry_time.shift(-1)
        df = df.dropna(subset=["next_entry_time"])
        df["minutes_bf_next_position"] = (df.next_entry_time - df.exit_time).astype(
            "timedelta64[s]"
        ).astype(int) // 60

        return df.drop(
            ["prc_not_realized", "amt_not_realized", "next_entry_time"], axis=1
        )

    def _create_timeseries(self, df: pd.DataFrame, pair: str) -> None:
        # create entering and exiting dataset
        entering = df[
            ["entry_time", "entry_point", "entry_price", "tp", "sl", "position_size"]
        ]
        exiting = df[["exit_time", "exit_point", "PL_amt_realized"]]

        # add to the main dataframe the 'entry_point', 'PL_amt_realized' and 'exit_point'
        self.df_pos = pd.merge(
            self.df_pos,
            entering,
            how="left",
            left_on="open_time",
            right_on="entry_time",
        )

        self.df_pos = pd.merge(
            self.df_pos, exiting, how="left", left_on="open_time", right_on="exit_time"
        )

        # create the in position variable and forward fill it
        condition_enter = self.df_pos["entry_point"].notnull()
        condition_exit = self.df_pos["exit_point"].notnull()

        self.df_pos[f"in_position_{pair}"] = np.where(
            condition_enter,
            self.df_pos["entry_point"],
            np.where(condition_exit, 0, np.nan),
        )
        self.df_pos[f"in_position_{pair}"] = (
            self.df_pos[f"in_position_{pair}"].fillna(method="ffill").fillna(0)
        )

        # Pair exposure
        pair_exposure = (
            self.df_pos["position_size"]
            * (self.df_pos["entry_price"] - self.df_pos["sl"])
            / self.df_pos["entry_price"]
        )
        pair_exposure = pair_exposure.abs()
        self.df_pos[f"{pair}_exposure"] = np.where(
            condition_enter, pair_exposure, np.where(condition_exit, 0, np.nan)
        )
        self.df_pos[f"{pair}_exposure"] = (
            self.df_pos[f"{pair}_exposure"].fillna(method="ffill").fillna(0)
        )

        self.df_pos["all_positions"] = (
            self.df_pos["all_positions"] + self.df_pos[f"in_position_{pair}"].abs()
        )

        # Create the cumulative total profit for the pair
        self.df_pos[f"PL_amt_realized_{pair}"] = self.df_pos["PL_amt_realized"].fillna(
            0
        )
        self.df_pos[f"total_profit_{pair}"] = self.df_pos[
            f"PL_amt_realized_{pair}"
        ].cumsum()

        condition_long_pl = (
            (self.df_pos[f"in_position_{pair}"] == 0)
            & (self.df_pos[f"in_position_{pair}"].shift(1) == 1)
        ) | ((self.df_pos[f"in_position_{pair}"] == 1) & condition_exit)

        condition_short_pl = (self.df_pos[f"in_position_{pair}"] == 0) & (
            self.df_pos[f"in_position_{pair}"].shift(1) == -1
        ) | ((self.df_pos[f"in_position_{pair}"] == -1) & condition_exit)

        # add the long profit and short profit for plot
        self.df_pos["Long_PL_amt_realized"] = np.where(
            condition_long_pl, self.df_pos[f"PL_amt_realized_{pair}"], 0
        )
        self.df_pos[f"long_profit_{pair}"] = self.df_pos[
            "Long_PL_amt_realized"
        ].cumsum()
        self.df_pos["Short_PL_amt_realized"] = np.where(
            condition_short_pl, self.df_pos[f"PL_amt_realized_{pair}"], 0
        )
        self.df_pos[f"short_profit_{pair}"] = self.df_pos[
            "Short_PL_amt_realized"
        ].cumsum()

        # clean the variables not needed
        to_drop = [
            "Short_PL_amt_realized",
            "Long_PL_amt_realized",
            f"PL_amt_realized_{pair}",
            "PL_amt_realized",
            "entry_time",
            "entry_point",
            "exit_time",
            "exit_point",
            "entry_price",
            "tp",
            "sl",
            "position_size",
        ]
        self.df_pos.drop(to_drop, axis=1, inplace=True)

        # update the bot total profit or all token
        self.df_pos["total_profit_all_pairs"] = (
            self.df_pos["total_profit_all_pairs"] + self.df_pos[f"total_profit_{pair}"]
        )
        self.df_pos["long_profit_all_pairs"] = (
            self.df_pos["long_profit_all_pairs"] + self.df_pos[f"long_profit_{pair}"]
        )
        self.df_pos["short_profit_all_pairs"] = (
            self.df_pos["short_profit_all_pairs"] + self.df_pos[f"short_profit_{pair}"]
        )

        # update bot total exposure
        self.df_pos["wallet_exposure"] = (
            self.df_pos["wallet_exposure"] + self.df_pos[f"{pair}_exposure"]
        )

        self.df_pos = self.df_pos.drop(
            [f"total_profit_{pair}", f"long_profit_{pair}", f"short_profit_{pair}"],
            axis=1,
        )

    def plot_profit_graph(self, pair: str) -> None:
        begin = np.where(self.df_pos[f"total_profit_{pair}"] != 0)[0].tolist()[0] - 1
        plt.figure(figsize=(10, 10))
        plt.plot(
            self.df_pos.open_time[self.df_pos.index > begin],
            self.df_pos[f"total_profit_{pair}"][self.df_pos.index > begin],
            label="Total Profit",
        )
        plt.plot(
            self.df_pos.open_time[self.df_pos.index > begin],
            self.df_pos[f"long_profit_{pair}"][self.df_pos.index > begin],
            label="Long Profit",
        )
        plt.plot(
            self.df_pos.open_time[self.df_pos.index > begin],
            self.df_pos[f"short_profit_{pair}"][self.df_pos.index > begin],
            label="Short Profit",
        )

        plt.legend()
        plt.title(f"Backtest {self.strategy_name} strategy for {pair}")
        plt.show()

    def plot_wallet_exposure_graph(self) -> None:
        begin = np.where(self.df_pos["wallet_exposure"] != 0)[0].tolist()[0] - 1
        plt.figure(figsize=(10, 10))
        plt.bar(
            self.df_pos.open_time[self.df_pos.index > begin],
            self.df_pos["wallet_exposure"][self.df_pos.index > begin],
            label="Wallet exposure ($)",
            width=0.1,
            color="k",
        )
        plt.legend()
        plt.title(f"Wallet exposure {self.strategy_name} strategy")
        plt.show()

    def _get_pair_stats(self, df: pd.DataFrame, pair: str) -> None:
        # create long and short dataframe
        position_stat = {
            "long": df[df["entry_point"] == 1].reset_index(drop=True),
            "short": df[df["entry_point"] == -1].reset_index(drop=True),
        }

        # create tp, sl, es, ew dataframes
        exit_stat = {
            "tp": df[df["exit_point"] == "TP"].reset_index(drop=True),
            "sl": df[df["exit_point"] == "SL"].reset_index(drop=True),
            "es": df[df["exit_point"] == "MaxHolding"].reset_index(drop=True),
            "ew": df[df["exit_point"] == "ExitSignal"].reset_index(drop=True),
        }

        # create an empty dictionary
        perf_dict: Dict[str, Any] = {}
        perf_dict["pair"] = pair
        have_pos = True if len(df) != 0 else False

        # add general statistics
        perf_dict["total_position"] = len(df)
        perf_dict["avg_minutes_in_position"] = (
            df["nb_minutes_in_position"].mean() if have_pos else 0
        )
        perf_dict["total_profit_amt"] = df["PL_amt_realized"].sum() if have_pos else 0
        perf_dict["total_profit_prc"] = df["PL_prc_realized"].sum() if have_pos else 0
        perf_dict["total_tx_fees"] = df["tx_fees_paid"].sum() if have_pos else 0
        perf_dict["avg_minutes_before_next_position"] = (
            df["minutes_bf_next_position"].mean() if have_pos else 0
        )
        perf_dict["max_minutes_without_position"] = (
            df["minutes_bf_next_position"].max() if have_pos else 0
        )
        perf_dict["min_minutes_without_position"] = (
            df["minutes_bf_next_position"].min() if have_pos else 0
        )
        perf_dict["perc_winning_trade"] = (
            len(df[df.PL_amt_realized > 0]) / len(df) if have_pos else 0
        )
        perf_dict["avg_profit"] = (
            df["PL_prc_realized"].sum() / len(df) if have_pos else 0
        )

        # add statistics per type of positions
        for pos, pos_df in position_stat.items():
            perf_dict[f"nb_{pos}_position"] = len(pos_df)
            perf_dict[f"nb_tp_{pos}"] = len(pos_df[pos_df["exit_point"] == "TP"])
            perf_dict[f"nb_sl_{pos}"] = len(pos_df[pos_df["exit_point"] == "SL"])
            perf_dict[f"nb_exit_{pos}"] = len(
                pos_df[pos_df["exit_point"] == "ExitSignal"]
            )
            perf_dict[f"nb_ew_{pos}"] = len(
                pos_df[pos_df["exit_point"] == "MaxHolding"]
            )
            perf_dict[f"{pos}_profit_amt"] = pos_df["PL_amt_realized"].sum()
            perf_dict[f"{pos}_profit_prc"] = pos_df["PL_prc_realized"].sum()
            perf_dict[f"avg_minutes_in_{pos}"] = pos_df["nb_minutes_in_position"].mean()

        # add statistics per type of exit
        for ext, ext_df in exit_stat.items():
            perf_dict[f"nb_{ext}"] = len(ext_df)
            perf_dict[f"avg_minutes_before_{ext}"] = ext_df[
                "nb_minutes_in_position"
            ].mean()

        # add the statistics to the general stats df_stat
        stat_perf = pd.DataFrame([perf_dict], columns=list(perf_dict.keys()))
        self.df_pairs_stat = pd.concat([self.df_pairs_stat, stat_perf])

    def _all_pairs_real_positions(self) -> None:
        for pair in self.df_all_positions.keys():
            df_concat = self.df_all_positions[pair]
            df_concat["pair"] = pair
            self.df_all_pairs_positions = pd.concat(
                [self.df_all_pairs_positions, self.df_all_positions[pair]]
            )

        if len(self.df_all_pairs_positions) == 0:
            raise Exception(
                "No position has been taken during the whole backtest period"
            )

        self.df_all_pairs_positions = self.df_all_pairs_positions[
            self.df_all_pairs_positions["entry_time"] > self.start
        ]

        self.df_all_pairs_positions = self.df_all_pairs_positions.sort_values(
            by=["exit_time"]
        )

        self.df_all_pairs_positions["position_size"] = (
            self.positions_size
            * self.start_bk
            * self.df_all_pairs_positions["position_size"]
        )

        self.df_all_pairs_positions = self.df_all_pairs_positions.dropna(
            subset=["exit_price", "PL_amt_realized"]
        )

        # Shift all TP or SL exit time bc it is based on the open time
        candle_duration = convert_candle_to_timedelta(candle=self.candle)

        self.df_all_pairs_positions["exit_time"] = np.where(
            self.df_all_pairs_positions["exit_point"].isin(["TP", "SL"]),
            self.df_all_pairs_positions["exit_time"] + candle_duration,
            self.df_all_pairs_positions["exit_time"],
        )

        self.df_all_pairs_positions = self.df_all_pairs_positions.reset_index(drop=True)

        # Delete impossible trades
        t = self.start
        actual_nb_pos = 0
        exit_times: List[Any] = []
        all_rows_to_delete = pd.DataFrame(columns=self.df_all_pairs_positions.columns)
        current_bk = self.start_bk

        while t <= self.end:
            if t in exit_times:
                if self.geometric_sizes:
                    # actualize current bankroll
                    current_bk += self.df_all_pairs_positions[
                        self.df_all_pairs_positions["exit_time"] == t
                    ]["PL_amt_realized"].sum()

                # quit positions
                actual_nb_pos -= exit_times.count(t)
                exit_times = list(filter(t.__ne__, exit_times))

            entry_t = self.df_all_pairs_positions[
                self.df_all_pairs_positions["entry_time"] == t
            ]
            nb_signals = entry_t.shape[0]

            # Delete rows if actual_nb_pos is over maximum pos
            if nb_signals + actual_nb_pos > self.max_pos:
                nb_to_delete = nb_signals - (self.max_pos - actual_nb_pos)

                # Select nb_to_delete random positions
                rows_to_delete = entry_t.sample(n=nb_to_delete)

                # Delete these positions
                self.df_all_pairs_positions = pd.concat(
                    [self.df_all_pairs_positions, rows_to_delete]
                )
                self.df_all_pairs_positions = (
                    self.df_all_pairs_positions.drop_duplicates(keep=False)
                )

                all_rows_to_delete = pd.concat([all_rows_to_delete, rows_to_delete])
                actual_nb_pos = self.max_pos

                # Append exit times
                real_entry_t = self.df_all_pairs_positions[
                    self.df_all_pairs_positions["entry_time"] == t
                ]
                exit_times += real_entry_t["exit_time"].tolist()

            elif nb_signals != 0:
                actual_nb_pos += nb_signals

                # Append exit times
                exit_times += entry_t["exit_time"].tolist()

            # If TP or SL hit during the opening candle
            if t in exit_times:
                if self.geometric_sizes:
                    # actualize current bankroll
                    current_bk += self.df_all_pairs_positions[
                        self.df_all_pairs_positions["exit_time"] == t
                    ]["PL_amt_realized"].sum()

                # quit positions
                actual_nb_pos -= exit_times.count(t)
                exit_times = list(filter(t.__ne__, exit_times))

            # Compute position size
            if self.geometric_sizes and (nb_signals > 0):
                self.df_all_pairs_positions["position_size"] = np.where(
                    self.df_all_pairs_positions["entry_time"] == t,
                    min(current_bk * self.positions_size, 50_000),
                    self.df_all_pairs_positions["position_size"],
                )

                self.df_all_pairs_positions["PL_amt_realized"] = np.where(
                    self.df_all_pairs_positions["entry_time"] == t,
                    self.df_all_pairs_positions["PL_prc_realized"]
                    * self.df_all_pairs_positions["position_size"],
                    self.df_all_pairs_positions["PL_amt_realized"],
                )

            t = t + candle_duration

        if not self.geometric_sizes:
            self.df_all_pairs_positions["PL_amt_realized"] = (
                self.df_all_pairs_positions["position_size"]
                * self.df_all_pairs_positions["PL_prc_realized"]
            )

        self.df_all_pairs_positions["cumulative_profit"] = self.df_all_pairs_positions[
            "PL_amt_realized"
        ].cumsum()

        self.df_all_pairs_positions["bankroll_size"] = (
            self.df_all_pairs_positions["cumulative_profit"] + self.start_bk
        )

        # Re calculate the fees
        self.df_all_pairs_positions["tx_fees_paid"] = (
            self.df_all_pairs_positions["position_size"]
            * self.fees
            * (2 + self.df_all_pairs_positions["PL_prc_realized"])
        )

        # Update self.df_all_positions
        for pair in self.list_pairs:
            self.df_all_positions[pair] = self.df_all_pairs_positions[
                self.df_all_pairs_positions["pair"] == pair
            ]

        # Create timeseries for all pairs
        for pair in self.list_pairs:
            self._create_timeseries(df=self.df_all_positions[pair], pair=pair)

            self._get_pair_stats(df=self.df_all_positions[pair], pair=pair)

        self.df_pairs_stat = self.df_pairs_stat.set_index("pair", drop=False)

    @staticmethod
    def _compute_daily_return(
        row: pd.Series, df_all_pairs_positions: pd.DataFrame
    ) -> pd.Series:
        all_exit_of_the_day = df_all_pairs_positions[
            df_all_pairs_positions["exit_time"] <= row.date + timedelta(days=1)
        ]
        all_exit_of_the_day = all_exit_of_the_day[
            all_exit_of_the_day["exit_time"] > row.date
        ]
        if all_exit_of_the_day["bankroll_size"].values.shape[0] > 0:
            day_profit = (
                100
                * (
                    all_exit_of_the_day["bankroll_size"].values[-1]
                    - all_exit_of_the_day["bankroll_size"].values[0]
                )
                / all_exit_of_the_day["bankroll_size"].values[0]
            )
        else:
            day_profit = 0
        row["daily_percentage_profit"] = day_profit
        if all_exit_of_the_day.shape[0] > 0:
            row["bankroll"] = all_exit_of_the_day["bankroll_size"].values[-1]
        return row

    @staticmethod
    def _compute_drawdown(row: pd.Series, df_daily: pd.DataFrame) -> pd.Series:
        temp = df_daily[df_daily["date"] <= row.date]
        temp = temp[temp["date"] >= temp["bankroll"].idxmax()]
        row["drawdown"] = temp["bankroll"].max() - row.bankroll
        row["last_date_max"] = temp["bankroll"].idxmax()
        row["nb_day_since_last_date_max"] = (row.date - row["last_date_max"]).days
        return row

    def _get_daily_return(
        self, since: datetime, df_all_pairs_pos: pd.DataFrame
    ) -> pd.DataFrame:
        first_day = since - timedelta(hours=since.hour, minutes=since.minute)
        last_day = self.end - timedelta(
            hours=self.end.hour,
            minutes=self.end.minute,
            microseconds=self.end.microsecond,
        )

        df = pd.DataFrame(
            index=pd.date_range(first_day, last_day),
            columns=["daily_percentage_profit", "last_date_max"],
        )
        df["date"] = df.index
        df["bankroll"] = np.nan
        df["drawdown"] = 0

        df = df.apply(
            lambda row: self._compute_daily_return(row, df_all_pairs_pos), axis=1
        )
        df["daily_percentage_profit"] = df["daily_percentage_profit"].fillna(0)
        df["bankroll"] = df["bankroll"].fillna(method="ffill")
        df["bankroll"] = df["bankroll"].fillna(self.start_bk)

        df = df.apply(lambda row: self._compute_drawdown(row, df), axis=1)
        return df

    @staticmethod
    def _get_overview_statistics(
        df_all_pairs_pos: pd.DataFrame, df_day: pd.DataFrame
    ) -> dict:
        overview: Dict[str, Any] = {}

        realized_profit = round(df_all_pairs_pos["PL_amt_realized"].sum(), 1)
        overview["Realized profit"] = f"{realized_profit} $"
        avg_profit = round(df_all_pairs_pos["PL_amt_realized"].mean(), 2)
        overview["Average profit / trade"] = f"{avg_profit} $"
        avg_profit_perc = round(100 * df_all_pairs_pos["PL_prc_realized"].mean(), 2)
        overview["Average profit / trade (%)"] = f"{avg_profit_perc} %"
        std_dev_profit = round(df_all_pairs_pos["PL_amt_realized"].std(), 2)
        overview["Profits std dev"] = f"{std_dev_profit} $"
        std_dev_profit_perc = round(100 * df_all_pairs_pos["PL_prc_realized"].std(), 2)
        overview["Profits std dev (%)"] = f"{std_dev_profit_perc} %"
        avg_position_size = round(df_all_pairs_pos["position_size"].mean(), 2)
        overview["Average position size"] = f"{avg_position_size} $"

        avg_profit_winning_trade = (
            df_all_pairs_pos[df_all_pairs_pos["PL_amt_realized"] > 0][
                "PL_amt_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["PL_amt_realized"] > 0].shape[0]
        )

        avg_profit_perc_winning_trade = (
            df_all_pairs_pos[df_all_pairs_pos["PL_prc_realized"] > 0][
                "PL_prc_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["PL_prc_realized"] > 0].shape[0]
        )

        avg_loss_losing_trade = (
            df_all_pairs_pos[df_all_pairs_pos["PL_amt_realized"] < 0][
                "PL_amt_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["PL_amt_realized"] < 0].shape[0]
        )

        avg_profit_perc_losing_trade = (
            df_all_pairs_pos[df_all_pairs_pos["PL_prc_realized"] < 0][
                "PL_prc_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["PL_prc_realized"] < 0].shape[0]
        )

        overview[
            "Average profit / winning trade"
        ] = f"{round(avg_profit_winning_trade, 2)} $"
        overview[
            "Average profit / winning trade (%)"
        ] = f"{round(100 * avg_profit_perc_winning_trade, 2)} %"

        overview["Average loss / losing trade"] = f"{round(avg_loss_losing_trade, 2)} $"
        overview[
            "Average profit / losing trade (%)"
        ] = f"{round(100 * avg_profit_perc_losing_trade, 2)} %"

        avg_long = (
            df_all_pairs_pos[df_all_pairs_pos["entry_point"] == 1][
                "PL_prc_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["entry_point"] == 1].shape[0]
        )
        overview["Average Long Profit (%)"] = f"{round(100 * avg_long, 2)} %"

        avg_short = (
            df_all_pairs_pos[df_all_pairs_pos["entry_point"] == -1][
                "PL_prc_realized"
            ].sum()
            / df_all_pairs_pos[df_all_pairs_pos["entry_point"] == -1].shape[0]
        )
        overview["Average Short Profit (%)"] = f"{round(100 * avg_short, 2)} %"

        hold = df_all_pairs_pos["nb_minutes_in_position"].mean() // 60
        overview["Average hold duration (in hours)"] = f"{round(hold, 2)} h"

        best_profit = round(df_all_pairs_pos["PL_amt_realized"].max(), 2)
        overview["Best trade profit"] = f"{best_profit} $"
        worst_loss = round(df_all_pairs_pos["PL_amt_realized"].min(), 2)
        overview["Worst trade loss"] = f"{worst_loss} $"
        overview[
            "Cumulative fees paid"
        ] = f"{round(df_all_pairs_pos['tx_fees_paid'].sum(), 2)} $ "
        overview["Nb winning trade"] = df_all_pairs_pos[
            df_all_pairs_pos["PL_amt_realized"] > 0
        ].shape[0]
        overview["Nb losing trade"] = df_all_pairs_pos[
            df_all_pairs_pos["PL_amt_realized"] < 0
        ].shape[0]
        overview["Total nb trade"] = (
            overview["Nb losing trade"] + overview["Nb winning trade"]
        )
        overview[
            "% winning trade"
        ] = f"{round(100 * overview['Nb winning trade'] / overview['Total nb trade'], 1)} %"
        overview["Nb long positions"] = df_all_pairs_pos[
            df_all_pairs_pos["entry_point"] == 1
        ].shape[0]
        overview["Nb short positions"] = df_all_pairs_pos[
            df_all_pairs_pos["entry_point"] == -1
        ].shape[0]
        overview[
            "% Exit signal"
        ] = f"{round(100 * df_all_pairs_pos[df_all_pairs_pos['exit_point'] == 'ExitSignal'].shape[0] / overview['Total nb trade'], 1)} %"
        overview[
            "% Max Holding"
        ] = f"{round(100 * df_all_pairs_pos[df_all_pairs_pos['exit_point'] == 'MaxHolding'].shape[0] / overview['Total nb trade'], 1)} %"
        overview[
            "% TP"
        ] = f"{round(100 * df_all_pairs_pos[df_all_pairs_pos['exit_point'] == 'TP'].shape[0] / overview['Total nb trade'], 1)} %"
        overview[
            "% SL"
        ] = f"{round(100 * df_all_pairs_pos[df_all_pairs_pos['exit_point'] == 'SL'].shape[0] / overview['Total nb trade'], 1)} %"
        overview[
            "Best day profit"
        ] = f"{round(df_day['daily_percentage_profit'].max(), 1)} %"
        overview[
            "Worst day loss"
        ] = f"{round(df_day['daily_percentage_profit'].min(), 1)} %"
        overview["Max Nb Days Underwater"] = int(
            df_day["nb_day_since_last_date_max"].max()
        )

        return overview

    def _get_performance_statistics(
        self, since: datetime, real_profit: float, df_day: pd.DataFrame
    ) -> dict:
        statistics = {}

        # Compute Geometric Returns
        total_return = 100 * real_profit / self.start_bk

        statistics["Total return"] = f"{round(total_return, 2)} %"

        nb_days_backtest = (self.end - since).days
        geometric_return = 100 * (
            (1 + total_return / 100) ** (365 / (nb_days_backtest)) - 1
        )

        statistics["Geometric return (yearly)"] = f"{round(geometric_return, 2)} %"

        # Compute Volatility
        df_day["Distribution"] = np.square(
            df_day["daily_percentage_profit"] - df_day["daily_percentage_profit"].mean()
        )
        volatility = math.sqrt(df_day["Distribution"].sum() / df_day.shape[0])
        volatility = volatility * math.sqrt(365)

        statistics["Annualized standard deviation"] = f"{round(volatility, 2)} %"

        # Compute Sharpe Ratio
        sharpe_ratio = geometric_return / volatility

        statistics["Sharpe Ratio"] = round(sharpe_ratio, 2)

        # Compute Sortino Ratio
        df_down = df_day[df_day["daily_percentage_profit"] < 0].copy()
        df_down["Downside_distribution"] = np.square(
            df_down["daily_percentage_profit"]
            - df_down["daily_percentage_profit"].mean()
        )
        downside_volatility = math.sqrt(
            df_down["Downside_distribution"].sum() / df_day.shape[0]
        )
        downside_volatility = downside_volatility * math.sqrt(365)

        statistics["Downside volatility"] = f"{round(downside_volatility, 2)} %"

        sortino_ratio = geometric_return / downside_volatility
        statistics["Sortino Ratio"] = round(sortino_ratio, 2)

        statistics["Max DrawDown"] = f"{round(df_day['drawdown'].max(), 2)} $"
        start_max_DD = df_day[df_day["date"] == df_day["drawdown"].idxmax()][
            "last_date_max"
        ]
        end_max_DD = df_day[df_day["date"] == df_day["drawdown"].idxmax()]["date"]

        statistics["Max DrawDown start"] = str(
            pd.to_datetime(start_max_DD.values[0]).date()
        )
        statistics["Max DrawDown end"] = str(
            pd.to_datetime(end_max_DD.values[0]).date()
        )

        return statistics

    def _get_pairs_statistics(self) -> dict:
        pairs_stats = {}

        pairs_stats["Best return pair"] = self.df_pairs_stat[
            "total_profit_amt"
        ].idxmax()
        pairs_stats[
            "Best return value"
        ] = f"{round(self.df_pairs_stat['total_profit_amt'].max(), 2)} $"

        pairs_stats["Worst return pair"] = self.df_pairs_stat[
            "total_profit_amt"
        ].idxmin()
        pairs_stats[
            "Worst return value"
        ] = f"{round(self.df_pairs_stat['total_profit_amt'].min(), 2)} $"

        pairs_stats[
            "Pair with most positions"
        ] = f"{self.df_pairs_stat['total_position'].idxmax()} ({self.df_pairs_stat['total_position'].max()})"
        pairs_stats[
            "Pair with less positions"
        ] = f"{self.df_pairs_stat['total_position'].idxmin()} ({self.df_pairs_stat['total_position'].min()})"

        return pairs_stats

    def _print_all_statistics(
        self, since: datetime, overview: dict, statistics: dict, pairs_stats: dict
    ) -> None:
        print("#" * 65)
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", "Overview:", "|", "     ", "#"
            )
        )
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", f'From {since.strftime("%Y-%m-%d")}', "|", "Value", "#"
            )
        )
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", f'To {self.end.strftime("%Y-%m-%d")}', "|", "     ", "#"
            )
        )
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", f"With {self.start_bk} $ starting", "|", "     ", "#"
            )
        )
        print("#" * 65)
        for k, v in overview.items():
            print("{:<5} {:<35} {:<5} {:<15} {:<1}".format("#", k, "|", v, "#"))
            print("#", "-" * 61, "#")
        print("#" * 65)

        print("#" * 65)
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", "Statistics:", "|", "Value", "#"
            )
        )
        print("#" * 65)
        for k, v in statistics.items():
            print("{:<5} {:<35} {:<5} {:<15} {:<1}".format("#", k, "|", v, "#"))
            print("#", "-" * 61, "#")
        print("#" * 65)

        print("#" * 65)
        print(
            "{:<5} {:<35} {:<5} {:<15} {:<1}".format(
                "#", "Pairs stats:", "|", "Value", "#"
            )
        )
        print("#" * 65)
        for k, v in pairs_stats.items():
            print("{:<5} {:<35} {:<5} {:<15} {:<1}".format("#", k, "|", v, "#"))
            print("#", "-" * 61, "#")
        print("#" * 65)

    def _create_full_statistics(self, since: datetime) -> dict:
        df_all_pairs_positions = self.df_all_pairs_positions[
            self.df_all_pairs_positions["entry_time"] > since
        ]

        ################################ Create daily results df ######################

        df_daily = self._get_daily_return(
            since=since, df_all_pairs_pos=df_all_pairs_positions
        )
        ################################ Compute overview #############################

        overview = self._get_overview_statistics(
            df_all_pairs_pos=df_all_pairs_positions, df_day=df_daily
        )
        ################################ Compute statistics #############################

        statistics = self._get_performance_statistics(
            since=since, real_profit=0.0, df_day=df_daily
        )

        ################################## Pairs stats ##################################

        pairs_stats = self._get_pairs_statistics()

        ################################  Print statistics  #############################

        self._print_all_statistics(
            since=since,
            overview=overview,
            statistics=statistics,
            pairs_stats=pairs_stats,
        )

        return {
            "overview": overview,
            "statistics": statistics,
            "pairs_stats": pairs_stats,
            "start": self.start,
            "end": self.end,
        }

    def _max_stop_loss(self, df: pd.DataFrame) -> pd.DataFrame:
        df["stop_loss"] = np.where(
            df["entry_signal"] == 1,
            pd.DataFrame(
                {
                    "stop_loss": df["stop_loss"],
                    "all_entry_price": df["all_entry_price"] * (1 - 1 / self.leverage),
                }
            ).max(axis=1),
            df["stop_loss"],
        )

        df["stop_loss"] = np.where(
            df["entry_signal"] == -1,
            pd.DataFrame(
                {
                    "stop_loss": df["stop_loss"],
                    "all_entry_price": df["all_entry_price"] * (1 + 1 / self.leverage),
                }
            ).min(axis=1),
            df["stop_loss"],
        )

        return df

    def not_any_future_info(self) -> None:
        # Verify entry_point, tp and sl
        nb_total_pos = len(self.df_all_pairs_positions)
        assert (
            nb_total_pos > 0
        ), "There is no position taken by the strategy during this back tested time period"
        random_entry = self.df_all_pairs_positions.sample(n=min(nb_total_pos, 5))

        for i, row in random_entry.iterrows():
            # Get historical DataFrame
            df = self.get_historical_data(pair=row["pair"])
            df = df[df["open_time"] < row["entry_time"]]

            # re-compute indicators, entry signals, tp and sl
            df = self.build_indicators(df)
            df = self.entry_strategy(df)
            df = self._create_entry_prices_times(df)
            df = self._max_stop_loss(df)

            last_row = df.iloc[-1]

            assert row["entry_point"] == last_row["entry_signal"], (
                "Entry point is not the same, make sure you don't have access to futures "
                "information when computing entry point"
            )
            assert row["tp"] == last_row["take_profit"], (
                "TP is not the same, make sure you don't have access to futures "
                "information when computing take profit price"
            )
            assert row["sl"] == last_row["stop_loss"], (
                "SL is not the same, make sure you don't have access to futures "
                "information when computing stop loss price"
            )

        # Verify exit signals
        nb_total_es = len(
            self.df_all_pairs_positions[
                self.df_all_pairs_positions["exit_point"] == "ExitSignal"
            ]
        )
        if nb_total_es > 0:
            random_exit = self.df_all_pairs_positions[
                self.df_all_pairs_positions["exit_point"] == "ExitSignal"
            ].sample(n=min(nb_total_es, 5))

            for i, row in random_exit.iterrows():
                # Get historical DataFrame
                df = self.get_historical_data(pair=row["pair"])
                df = df[df["open_time"] < row["exit_time"]]

                # re-compute indicators, entry signals, tp and sl
                df = self.build_indicators(df)
                df = self.entry_strategy(df)
                df = self._create_entry_prices_times(df)
                df = self.exit_strategy(df)

                last_row = df.iloc[-1]

                assert -row["entry_point"] == last_row["exit_signal"], (
                    "Exit signal is not the same, make sure you don't have access to futures "
                    "information when computing exit signals"
                )

        print("Test PASSED")

    @staticmethod
    def _verify_tp_sl(df: pd.DataFrame) -> None:
        sl_valid = np.where(
            df["entry_signal"] == 1,
            df["stop_loss"] < df["close"],
            np.where(df["entry_signal"] == -1, df["stop_loss"] > df["close"], True),
        )
        tp_valid = np.where(
            df["entry_signal"] == 1,
            df["take_profit"] > df["close"],
            np.where(df["entry_signal"] == -1, df["take_profit"] < df["close"], True),
        )

        assert sl_valid.sum() == len(
            sl_valid
        ), "Some SL are not valid. Please replace your SL correctly."
        assert tp_valid.sum() == len(
            tp_valid
        ), "Some TP are not valid. Please replace your TP correctly."

        # Verify position sizes coefficients are between 0 and 1
        ps_valid = np.where(
            df["entry_signal"].notnull(),
            (df["position_size"] <= 1) & (df["position_size"] > 0),
            True,
        )
        assert ps_valid.sum() == len(ps_valid), (
            "Some position sizes are not valid. "
            "All position sizes values must be between 0 and 1 (> 0 and <= 1)"
        )

    def run_backtest(self, save: bool = True) -> Tuple[pd.DataFrame, dict]:
        for pair in self.list_pairs:
            print(f"BACK TESTING {pair}", "\U000023F3", end="\r")

            df = self.get_historical_data(pair)

            if len(df) == 0:
                print(f"No data for {pair} in the interval")
                continue

            df = self.build_indicators(df)
            df = self.entry_strategy(df)

            for col in ["entry_signal", "stop_loss", "take_profit", "position_size"]:
                assert (
                    col in df.columns
                ), f"Missing {col} column. Please create this column in entry_strategy()"

            self._verify_tp_sl(df)
            df = self._create_entry_prices_times(df)
            df = self._max_stop_loss(df)
            df = self.exit_strategy(df)

            assert (
                "exit_signal" in df.columns
            ), "Missing exit_signal column. Please create this column in entry_strategy()"

            df = self._create_closest_exit(df)
            df = self._create_all_exit_point(df)
            self._create_position_df(df, pair)
            print(f"BACK TESTING {pair}", "\U00002705")

        print("Creating all positions and timeserie graph", "\U000023F3", end="\r")
        self._all_pairs_real_positions()
        self.plot_profit_graph("all_pairs")
        if self.plot_exposure:
            self.plot_wallet_exposure_graph()
        print("Creating all positions and timeserie graph", "\U00002705")

        print("Computing all statistics", "\U000023F3", end="\r")
        all_statistics = self._create_full_statistics(since=self.start)
        print("Computing all statistics", "\U00002705")

        if save:
            if "results" not in os.listdir(f"{os.getcwd()}"):
                os.mkdir(f"{os.getcwd()}/results")

            self.df_pairs_stat.to_csv(
                f"results/{self.strategy_name}_pairs_stats.csv", index=False
            )

            with open(f"results/{self.strategy_name}_overall_stats.json", "w") as fp:
                all_statistics["start"] = all_statistics["start"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                all_statistics["end"] = all_statistics["end"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                json.dump(all_statistics, fp)

        return self.df_all_pairs_positions, all_statistics
