# import time
# from datetime import datetime

# from novalabs.clients.clients import clients


# def asserts_get_server_time(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     server_time = client.get_server_time()

#     min_dif = (time.time() - 1) * 1000
#     max_dif = (time.time() + 1) * 1000

#     assert type(server_time) == int
#     assert (server_time > min_dif) and (server_time < max_dif)
#     assert len(str(server_time)) == 13

#     server_date = datetime.utcfromtimestamp(server_time // 1000)

#     print(f"Date: {server_date} -- Timestamp (ms): {server_time}")
#     print(f"Test get_server_time for {test['exchange'].upper()} SUCCESSFUL")


# def test_get_server_time() -> None:
#     all_test = [
#         {"exchange": "binance", "api_key": "", "api_secret": "", "passphrase": ""},
#         {"exchange": "okx", "api_key": "", "api_secret": "", "passphrase": ""},
#         {"exchange": "huobi", "api_key": "", "api_secret": "", "passphrase": ""},
#         {"exchange": "bybit", "api_key": "", "api_secret": "", "passphrase": ""},
#         {"exchange": "kucoin", "api_key": "", "api_secret": "", "passphrase": ""},
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#         },
#     ]
#     for test in all_test:
#         asserts_get_server_time(test)


# test_get_server_time()
