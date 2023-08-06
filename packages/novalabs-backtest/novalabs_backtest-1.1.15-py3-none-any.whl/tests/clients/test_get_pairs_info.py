# from novalabs.clients.clients import clients


# def asserts_get_pairs_info(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     info = client.get_pairs_info(test["quote_asset"])

#     assert type(info) == dict

#     if test["to_test_USDT"]:
#         for key, value in info.items():
#             assert "USDT" in key
#             assert "USDT" == value["quote_asset"]

#     print(f"Test get_pairs_info for {test['exchange'].upper()} SUCCESSFUL")


# def test_get_pairs_info() -> None:
#     all_test = [
#         {
#             "exchange": "binance",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "okx",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "huobi",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "bybit",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#             "quote_asset": "USD",
#             "to_test_USDT": False,
#         }
#     ]
#     for test in all_test:
#         asserts_get_pairs_info(test)


# test_get_pairs_info()
