import json
import requests
from typing import Optional
from .models import Broker, BracketOrder, Asset
from .logger import logger


class Alpaca(Broker):
    def __init__(self, api_key, api_secret, paper: Optional[bool] = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper

        ALPACA_TRADE_API_URL_PAPER = "https://paper-api.alpaca.markets"
        ALPACA_TRADE_API_URL_LIVE = "https://api.alpaca.markets"

        if self.paper is True:
            self.api_url = ALPACA_TRADE_API_URL_PAPER
        else:
            self.api_url = ALPACA_TRADE_API_URL_LIVE

        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        }

    def market_is_open(self) -> bool:
        logger.debug("Checking if market is open...")
        endpoint = '/v2/clock'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        json_response = response.json()
        return json_response['is_open']

    def get_assets(self) -> dict:
        endpoint = '/v2/assets'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        json_response = response.json()
        assets = []
        for asset_dict in json_response:
            asset = Asset(
                id=asset_dict["id"],
                asset_class=asset_dict["class"],
                exchange=asset_dict["exchange"],
                symbol=asset_dict["symbol"],
                name=asset_dict["name"],
                status=asset_dict["status"],
                tradable=asset_dict["tradable"],
                marginable=asset_dict["marginable"],
                maintenance_margin_requirement=asset_dict["maintenance_margin_requirement"],
                shortable=asset_dict["shortable"],
                easy_to_borrow=asset_dict["easy_to_borrow"],
                fractionable=asset_dict["fractionable"]
            )
            assets.append(asset)
        return assets

    def get_asset(self, symbol):
        endpoint = f'/v2/assets/{symbol}'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        asset_dict = response.json()
        asset = Asset(
            id=asset_dict["id"],
            asset_class=asset_dict["class"],
            exchange=asset_dict["exchange"],
            symbol=asset_dict["symbol"],
            name=asset_dict["name"],
            status=asset_dict["status"],
            tradable=asset_dict["tradable"],
            marginable=asset_dict["marginable"],
            maintenance_margin_requirement=asset_dict["maintenance_margin_requirement"],
            shortable=asset_dict["shortable"],
            easy_to_borrow=asset_dict["easy_to_borrow"],
            fractionable=asset_dict["fractionable"]
        )
        return asset

    def in_position(self, ticker) -> bool:
        endpoint = f'/v2/positions/{ticker}'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        logger.info(f"Checking Positions for symbol {ticker}")
        if response.status_code == 404:
            logger.debug("Not In Position...")
            return False
        else:
            logger.debug("Currently In Position...")
            return True

    def check_account_balance(self) -> float:
        endpoint = '/v2/account'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        json_response = response.json()
        account_balance = float(json_response["non_marginable_buying_power"])
        logger.info(f"ACCOUNT NON-MARGINABLE BUYING POWER: {account_balance}")
        return account_balance

    def check_account_equity(self) -> float:
        endpoint = '/v2/account'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        json_response = response.json()
        account_equity = float(json_response["equity"])
        logger.info(f"ACCOUNT EQUITY: {account_equity}")
        return account_equity

    def check_existing_orders(self, ticker) -> list[str]:
        endpoint = '/v2/orders'
        url = self.api_url + endpoint
        response = requests.get(url=url, headers=self.headers)
        json_response = response.json()
        logger.info("Checking Pending Orders..")
        orders = []
        if len(json_response) == 0:
            logger.info("No Orders Found")
        else:
            for order in json_response:
                if order['symbol'] == ticker:
                    logger.info(f"PENDING ORDER FOUND WITH ID: {order['client_order_id']} ({order['id']}) - {order['symbol']} {order['side']} {order['qty']}")
                    logger.info(order)
                    orders.append(order['id'])
        return orders

    def submit_order(self, order: BracketOrder) -> dict:
        endpoint = '/v2/orders'
        url = self.api_url + endpoint
        order = order.asAlpacaOrder()
        logger.info(f"ORDER TO SUBMIT:\n{json.dumps(order)}\n")
        response = requests.post(url=url, headers=self.headers, data=json.dumps(order))
        json_response = response.json()
        logger.info(f"ORDER RESPONSE:\n{json_response}\n")
        return json_response

    def cancel_order(self, order_id: str) -> None:
        endpoint = f'/v2/orders/{order_id}'
        url = self.api_url + endpoint
        requests.delete(url=url, headers=self.headers)
