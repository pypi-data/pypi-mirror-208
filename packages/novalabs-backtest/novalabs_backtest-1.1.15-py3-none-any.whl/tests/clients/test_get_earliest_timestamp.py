# import time
# from datetime import datetime

# from novalabs.clients.clients import clients


# def assert_get_earliest_timestamp(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     data = client._get_earliest_timestamp(pair=test["pair"], interval=test["interval"])

#     server_date = datetime.utcfromtimestamp(data // 1000)

#     assert len(str(data)) == 13
#     assert data < int(time.time() * 1000)

#     print(f"Earliest Date: {server_date} -- Timestamp (ms): {data}")
#     print(f"Test _get_earliest_timestamp for {test['exchange'].upper()} successful")


# def test_get_earliest_timestamp() -> None:
#     all_test = [
#         {
#             "exchange": "binance",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTCUSDT",
#             "interval": "1d",
#         },
#         {
#             "exchange": "okx",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "LTC-USD-SWAP",
#             "interval": "1d",
#         },
#         {
#             "exchange": "huobi",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTC-USDT",
#             "interval": "1d",
#         },
#         {
#             "exchange": "bybit",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTCUSDT",
#             "interval": "1d",
#         },
#         {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "pair": "BTCUSDT",
#             "interval": "1d",
#         },
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#             "pair": "AUD_CAD",
#             "interval": "1d",
#         },
#     ]

#     for test in all_test:
#         assert_get_earliest_timestamp(test)


# test_get_earliest_timestamp()
