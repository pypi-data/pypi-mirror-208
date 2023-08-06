# from datetime import datetime

# import pandas as pd

# from novalabs.clients.clients import clients
# from novalabs.utils.constant import STD_CANDLE_FORMAT

# test = {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "XBTUSDTM",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 1, 1).timestamp() * 1000),
#             "end_time": int(datetime(2023, 1, 1).timestamp() * 1000),
#         }

# def asserts_format_data(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     candles = client._get_candles(
#         pair=test["pair"],
#         interval=test["interval"],
#         start_time=test["start_time"],
#         end_time=test["end_time"],
#     )

#     hist_data = client._format_data(all_data=candles)

#     assert type(hist_data) == pd.DataFrame
#     assert "next_open" not in list(hist_data.columns)

#     for var in STD_CANDLE_FORMAT:
#         assert var in list(hist_data.columns)
#         assert hist_data.dtypes[var] in ["int64", "float32", "float64"]

#     # verify the open and closing time
#     assert len(str(hist_data.loc[0, "open_time"])) == 13
#     assert len(str(hist_data.loc[0, "close_time"])) == 13
#     assert str(hist_data.loc[0, "open_time"])[-3:] == "000"
#     assert str(hist_data.loc[0, "close_time"])[-3:] == "999"

#     print(f"Test _get_historical_data for {test['exchange'].upper()} successful")


# def test_format_data() -> None:
#     all_tests = [
#         {
#             "exchange": "binance",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTCUSDT",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#         {
#             "exchange": "okx",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTC-USDT-SWAP",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#         {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "XBTUSDTM",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#         {
#             "exchange": "huobi",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTC-USDT",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#         {
#             "exchange": "bybit",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTCUSDT",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#             "pair": "AUD_CAD",
#             "interval": "1d",
#             "start_time": int(datetime(2020, 9, 1).timestamp() * 1000),
#             "end_time": int(datetime(2022, 9, 1).timestamp() * 1000),
#         },
#     ]

#     for test in all_tests:
#         asserts_format_data(test)


# test_format_data()
