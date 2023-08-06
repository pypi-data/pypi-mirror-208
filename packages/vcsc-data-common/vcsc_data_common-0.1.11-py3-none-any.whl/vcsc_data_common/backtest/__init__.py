import logging
import json
import requests
import time


class BackTestException(Exception):
    pass


class BackTest:
    def __init__(self, paper_trading_api_end_point: str) -> None:
        self.paper_trading_api_end_point = paper_trading_api_end_point

    def update_symbol_prices(self, symbol_prices):
        url = f"{self.paper_trading_api_end_point}/backtest/updateSymbolInfo"

        payload = json.dumps({
            "priceData": symbol_prices
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if(response.status_code != 200):
            raise BackTestException('updateSymbolInfo api error')

    def create_user(self, username: str, portfolio_model: int, trading_model: int, limit_symbol: int, force_sell_date_count: int):
        url = f"{self.paper_trading_api_end_point}/user/createPaperUser"

        payload = json.dumps({
            "username": username,
            "realAccount": "068C373737",
            "limitSymbol": limit_symbol,
            "forceSellDateCount": force_sell_date_count,
            "tradingModel": portfolio_model,
            "portfolioModel": trading_model,
            "tradingInitAmount": 1000000000
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if(response.status_code != 200):
            raise BackTestException('create_user api error')

    def execute_forcesell(self, tradingDate: str):
        url = f"{self.paper_trading_api_end_point}/backtest/executeForceSell"

        payload = json.dumps({
            "tradingDate": tradingDate,
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if(response.status_code != 200):
            raise BackTestException('execute_forcesell api error')

    def settle_depository_schedule(self, tradingDate: str):
        url = f"{self.paper_trading_api_end_point}/backtest/settleDepositorySchedule"

        payload = json.dumps({
            "tradingDate": tradingDate,
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if(response.status_code != 200):
            raise BackTestException('settle_depository_schedule api error')
