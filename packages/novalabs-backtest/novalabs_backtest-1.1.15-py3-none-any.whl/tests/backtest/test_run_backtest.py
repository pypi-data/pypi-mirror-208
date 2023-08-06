# from datetime import datetime, timedelta

# from novalabs.strategies.macd_strategy import StratBacktest


# def asserts_run_backtest(test: dict) -> None:
#     strategy = StratBacktest(
#         exchange=test["exchange"],
#         list_pairs=test["list_pairs"],
#         start=datetime(2023, 1, 1),
#         end=datetime(2023, 4, 1),
#         candle="1h",
#         max_holding=timedelta(minutes=720),
#         tp_sl_delta=0.01,
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     df_all_pos, all_stats = strategy.run_backtest(save=False)

#     assert len(df_all_pos) > 0

#     print(f"Test run_backtest for {test['exchange'].upper()} SUCCESSFUL")


# def test_run_backtest() -> None:
#     all_test = [
#         {"exchange": "binance", "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",},
#         {"exchange": "okx", "list_pairs": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "XRP-USDT-SWAP"],
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",},
#         {"exchange": "bybit", "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",},
#         {"exchange": "huobi", "list_pairs": ["BTC-USDT", "ETH-USDT", "XRP-USDT"],
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",},
#         {"exchange": "kucoin", "list_pairs": ["XBTUSDTM", "ETHUSDTM", "XRPUSDTM"],
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",},
#         {"exchange": "oanda", "list_pairs": ["GBP_SGD", "GBP_AUD", "NZD_SGD"],
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": ""},
#     ]
#     for test in all_test:
#         asserts_run_backtest(test)


# test_run_backtest()
