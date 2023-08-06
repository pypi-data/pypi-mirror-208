# from datetime import datetime

# from novalabs.clients.clients import clients


# def asserts_get_candles(test: dict) -> None:
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

#     assert type(candles) == list
#     assert len(candles) == test["expected_lenght"]

#     print(f"Test get_server_time for {test['exchange'].upper()} SUCCESSFUL")


# def test_get_candles() -> None:
#     all_test = [
#         {
#             'exchange': 'binance',
#             'api_key': "",
#             'api_secret': "",
#             'passphrase': "",
#             'pair': 'BTCUSDT',
#             'interval': '1m',
#             'start_time': int(datetime(2020, 9, 1).timestamp() * 1000),
#             'end_time': int(datetime(2022, 9, 1).timestamp() * 1000),
#             'expected_lenght': 1000
#         },
#         {
#             'exchange': 'okx',
#             'api_key': "",
#             'api_secret': "",
#             'passphrase': "",
#             'pair': 'BTC-USDT-SWAP',
#             'interval': '1m',
#             'start_time': int(datetime(2020, 9, 1).timestamp() * 1000),
#             'end_time': int(datetime(2022, 9, 1).timestamp() * 1000),
#             'expected_lenght': 100
#         },
#         {
#             'exchange': 'huobi',
#             'api_key': "",
#             'api_secret': "",
#             'passphrase': "",
#             'pair': 'BTC-USDT',
#             'interval': '1m',
#             'start_time': int(datetime(2020, 9, 1).timestamp() * 1000),
#             'end_time': int(datetime(2022, 9, 1).timestamp() * 1000),
#             'expected_lenght': 2000
#         },
#         {
#             'exchange': 'bybit',
#             'api_key': "",
#             'api_secret': "",
#             'passphrase': "",
#             'pair': 'BTCUSDT',
#             'interval': '1h',
#             'start_time': int(datetime(2020, 9, 1).timestamp() * 1000),
#             'end_time': int(datetime(2022, 9, 1).timestamp() * 1000),
#             'expected_lenght': 200
#         },
#         {
#             'exchange': 'kucoin',
#             'api_key': "",
#             'api_secret': "",
#             'passphrase': "",
#             'pair': 'XBTUSDTM',
#             'interval': '1h',
#             'start_time': int(datetime(2020, 9, 1).timestamp() * 1000),
#             'end_time': int(datetime(2022, 9, 1).timestamp() * 1000),
#             'expected_lenght': 200
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
#             "expected_lenght": 521,
#         },
#     ]
#     for test in all_test:
#         asserts_get_candles(test)


# test_get_candles()
