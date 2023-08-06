# from datetime import datetime

# from novalabs.clients.clients import clients
# from novalabs.utils.helpers import interval_to_milliseconds

# def assert_get_historical_data(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     earliest_start = client._get_earliest_timestamp(
#         pair=test["pair"], interval=test["interval"]
#     )
#     real_start = max(earliest_start, test["start_ts"])
#     time_milli = interval_to_milliseconds(interval=test["interval"])

#     df = client.get_historical_data(
#         pair=test["pair"],
#         interval=test["interval"],
#         start_ts=real_start,
#         end_ts=test["end_ts"],
#     )

#     if test["exchange"] not in ['oanda']:

#         df["open_time_difference"] = df["open_time"] - df["open_time"].shift(1)
#         df["close_time_difference"] = df["close_time"] - df["close_time"].shift(1)

#         assert (
#             df["open_time_difference"].max() == time_milli
#         ), "Candle interval is wrong for open_time"
#         assert (
#             df["close_time_difference"].max() == time_milli
#         ), "Candle interval is wrong for close_time"

#         assert (
#             df["open_time_difference"].max() == df["open_time_difference"].min()
#         ), "Time series not respected"
#         assert (
#             df["close_time_difference"].min() == df["close_time_difference"].max()
#         ), "Time series not respected"

#     assert df["open_time"].min() >= real_start
#     assert df["open_time"].max() <= test["end_ts"]

#     print(f"Test _get_historical_data for {test['exchange'].upper()} successful")


# def test_get_historical_data() -> None:
#     all_tests = [
#         {
#             "exchange": "binance",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "interval": "4h",
#             "pair": "ETHUSDT",
#             "start_ts": int(datetime(2018, 1, 1).timestamp() * 1000),
#             "end_ts": int(datetime(2022, 4, 10).timestamp() * 1000),
#         },
#         {
#             "exchange": "okx",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "interval": "1d",
#             "pair": "ETH-USDT-SWAP",
#             "start_ts": int(datetime(2018, 1, 1).timestamp() * 1000),
#             "end_ts": int(datetime(2022, 4, 10).timestamp() * 1000),
#         },
#         {
#             "exchange": "huobi",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "interval": "1h",
#             "pair": "BTC-USDT",
#             "start_ts": int(datetime(2018, 1, 1).timestamp() * 1000),
#             "end_ts": int(datetime(2022, 4, 10).timestamp() * 1000),
#         },
#         {
#             "exchange": "bybit",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "interval": "1h",
#             "pair": "BTCUSDT",
#             "start_ts": int(datetime(2018, 1, 1).timestamp() * 1000),
#             "end_ts": int(datetime(2022, 4, 10).timestamp() * 1000),
#         },
#         {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "interval": "1h",
#             "pair": "XBTUSDTM",
#             "start_ts": int(datetime(2022, 1, 1).timestamp() * 1000),
#             "end_ts": int(datetime.now().timestamp() * 1000),
#         },
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#             "pair": "AUD_CAD",
#             "interval": "1h",
#             "start_ts": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_ts": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#     ]

#     for test in all_tests:
#         assert_get_historical_data(test)


# test_get_historical_data()
