import requests
from requests.exceptions import HTTPError
import asyncio
from .option_aggs import OptionAggs
from .daily_oc import DailyOpenClose
from .option_snapshot import OptionSnapshotData
import pandas as pd

import aiohttp
import csv
import httpx
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlencode
from .option_trades import OptionTrade

import requests
from requests.exceptions import HTTPError
from urllib.parse import urlencode


class PolygonOptionsSDK:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.conditions_map = None
            
    async def _request(self, endpoint, params=None):
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f"An HTTP error occurred: {http_err}")
            return None
        except Exception as err:
            print(f"An error occurred: {err}")
            return None

        try:
            return response.json()
        except Exception as err:
            print(f"Error decoding JSON response: {err}")
            return None

    async def _request_all_pages(self, initial_url, params=None):
        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        all_results = []
        next_url = initial_url

        while next_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(next_url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    if "results" in data:
                        all_results.extend(data["results"])

                    next_url = data.get("next_url")
                    if next_url:
                        next_url += f'&{urlencode({"apiKey": self.api_key})}'
                        params = {}

            except httpx.HTTPError as http_err:
                print(f"An HTTP error occurred: {http_err}")
                break
            except Exception as err:
                print(f"An error occurred: {err}")
                break

        return all_results

    async def get_options_contracts(
        self,
        underlying_ticker=None,
        contract_type=None,
        expiration_date=None,
        as_of=None,
        strike_price=None,
        expired=None,
        order=None,
        limit=None,
        sort=None,
    ):
        endpoint = "/v3/reference/options/contracts"
        initial_url = f"{self.base_url}{endpoint}"
        params = {}

        if underlying_ticker is not None:
            params["underlying_ticker"] = underlying_ticker
        if contract_type is not None:
            params["contract_type"] = contract_type
        if expiration_date is not None:
            params["expiration_date"] = expiration_date
        if as_of is not None:
            params["as_of"] = as_of
        if strike_price is not None:
            params["strike_price"] = strike_price
        if expired is not None:
            params["expired"] = expired
        if order is not None:
            params["order"] = order
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        return await self._request_all_pages(initial_url, params=params)
        

    async def get_option_conditions(self):
        """
        Get stock conditions data from the Polygon.io API.
        
        :return: A dictionary with condition IDs as keys and condition names as values.
        """
        url = f"https://api.polygon.io/v3/reference/conditions?asset_class=options&limit=1000&apiKey={self.api_key}"
        response = requests.get(url)
        stock_conditions = {}

        if response.status_code == 200:
            data = response.json()
            conditions_data = data['results']

            for condition in conditions_data:
                condition_id = condition['id']
                condition_name = condition['name']
                stock_conditions[condition_id] = condition_name
        else:
            print(f"Error: {response.status_code}")

        return stock_conditions

    async def load_option_exchanges(self, **kwargs):
        endpoint = "/v3/reference/exchanges"
        exchanges_data = self._request(endpoint, params=kwargs)

        if exchanges_data.get("results"):
            for exchange in exchanges_data["results"]:
                exchange_id = exchange.get("id")
                if exchange_id is not None:
                    self.exchanges_map[str(exchange_id)] = exchange 

    async def get_option_exchanges(self, asset_class=None, locale=None):
        endpoint = "/v3/reference/exchanges"
        params = {}

        if asset_class:
            params["asset_class"] = asset_class
        if locale:
            params["locale"] = locale

        exchanges_data = await self._request(endpoint, params=params)

        return exchanges_data

    async def generate_option_symbol(self, underlying_symbol, expiration_date, option_type, strike_price: float):
        """
        Generate an option symbol for a given underlying symbol, expiration date, option type, and strike price.

        :param underlying_symbol: The symbol of the underlying stock or ETF.
        :param expiration_date: The expiration date of the option in the format 'YYYY-MM-DD'.
        :param option_type: The option type, 'C' for call or 'P' for put.
        :param strike_price: The strike price of the option as a float or integer.
        :return: The generated option symbol as a string.
        """
        # Convert the expiration date to the format 'YYMMDD'
        expiration_date_obj = datetime.strptime(expiration_date, "%Y-%m-%d")
        expiration_date_formatted = expiration_date_obj.strftime("%y%m%d")

        # Convert the strike price to the required format
        strike_price_formatted = '00{:05.0f}0'.format(float(strike_price) * 100)
        
        return f"{underlying_symbol}{expiration_date_formatted}{option_type}{strike_price_formatted}"


    async def get_aggregate_bars(self, options_ticker, multiplier=1, timespan= "day", start_date=None, end_date=None, adjusted=True, sort="asc", limit=120, as_dataframe: Optional[bool] = "false") -> List[OptionAggs]:
        """
        Get aggregate bars for an option contract over a given date range in custom time window sizes.

        :param options_ticker: The ticker symbol of the options contract in 'AAPL200918C00260000' format.
        :param multiplier: The size of the timespan multiplier.
        :param timespan: The size of the time window.
        :param start_date: The start of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param end_date: The end of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted.
        :param sort: Sort the results by timestamp. "asc" will return results in ascending order (oldest at the top), "desc" will return results in descending order (newest at the top).
        :param limit: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000.
        :return: A JSON object containing the results.
        """
        async with aiohttp.ClientSession() as session:
            url=f"https://api.polygon.io/v2/aggs/ticker/O:{options_ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted={adjusted}&sort={sort}&limit={limit}&apiKey={self.api_key}"
            print(url)
            async with session.get(url) as response:
                data = await response.json()
                results = data['results']
                
                return [OptionAggs(i) for i in results if i is not None]

            




    async def get_daily_open_close(self, options_ticker, date, adjusted=True):
        """
        Get the open, close, and after-hours prices of an options contract on a certain date.

        :param options_ticker: The ticker symbol of the options contract.
        :param date: The date of the requested open/close in the format YYYY-MM-DD.
        :param adjusted: Whether or not the results are adjusted for splits. Default is True.
        :return: A dictionary containing the response data.
        """
        async with aiohttp.ClientSession() as session:
            url=f"https://api.polygon.io/v1/open-close/O:{options_ticker}/{date}?adjusted={adjusted}&apiKey={self.api_key}"
            print(url)
            async with session.get(url) as response:
                data = await response.json()
                return DailyOpenClose(data)
    async def get_previous_close(self, options_ticker, adjusted=True):
        """
        Get the previous day's open, high, low, and close (OHLC) for the specified options contract.

        :param options_ticker: The ticker symbol of the options contract.
        :param adjusted: Whether or not the results are adjusted for splits. Default is True.
        :return: A dictionary containing the response data.
        """
        endpoint = f"/v2/aggs/ticker/{options_ticker}/prev"
        params = {"adjusted": adjusted}
        return await self._request(endpoint, params)
    


    async def get_option_trades(self, symbol, limit=50000, sort="desc"):
        """
        Get trades for an options ticker symbol in a given time range.

        :param options_ticker: The options ticker symbol to get trades for.
        :param timestamp: Query by trade timestamp. Either a date with the format YYYY-MM-DD or a nanosecond timestamp.
        :param order: Order results based on the sort field.
        :param limit: Limit the number of results returned, default is 10 and max is 50000.
        :param sort: Sort field used for ordering.
        :return: A DataFrame containing the response data.
        """
        async with aiohttp.ClientSession() as session:
            url=f"https://api.polygon.io/v3/trades/O:{symbol}?limit={limit}&apiKey={self.api_key}"
            print(url)
            async with session.get(url) as response:
                data = await response.json()
                results = data['results']
                trades = [OptionTrade(i) for i in results]
                return trades
     
          
    async def get_last_option_trade(self, options_ticker):
        """
        Get the most recent trade for a given options contract.

        :param options_ticker: The ticker symbol of the options contract.
        :return: A dictionary containing the response data.
        """
        endpoint = f"/v2/last/trade/{options_ticker}"
        return await self._request(endpoint)

    async def get_options_quotes(self, options_ticker, timestamp=None, order=None, limit=None, sort=None):
        """
        Get quotes for an options ticker symbol in a given time range.
        
        :param api_key: str, API key to access Polygon.io API
        :param options_ticker: str, The ticker symbol to get quotes for
        :param timestamp: str, optional, Query by timestamp (date format YYYY-MM-DD or a nanosecond timestamp)
        :param order: str, optional, Order results based on the sort field
        :param limit: int, optional, Limit the number of results returned (default is 10, max is 50000)
        :param sort: str, optional, Sort field used for ordering
        :return: dict, JSON response containing quote data
        """
        endpoint = f"/v3/quotes/{options_ticker}"
        params = {}
        if timestamp:
            params += f"&timestamp={timestamp}"
        if order:
            params += f"&order={order}"
        if limit:
            params += f"&limit={limit}"
        if sort:
            params += f"&sort={sort}"

        return await self._request(endpoint)
    

    async def get_option_contract_snapshot(self, underlying_asset, option_contract):
        """
        Get the snapshot of an option contract for a stock equity.

        :param underlying_asset: The underlying ticker symbol of the option contract.
        :param option_contract: The option contract identifier.
        :return: A JSON object containing the option contract snapshot data.
        """
        endpoint = f"/v3/snapshot/options/{underlying_asset}/{option_contract}"
        return await self._request(endpoint)
    

    async def get_single_option(self, underlying_asset, strike_price=None, expiration_date=None, contract_type=None, order=None, limit=10, sort=None):
        """
        Get the snapshot of all options contracts for an underlying ticker.

        :param underlying_asset: The underlying ticker symbol of the option contract.
        :param strike_price: Query by strike price of a contract.
        :param expiration_date: Query by contract expiration with date format YYYY-MM-DD.
        :param contract_type: Query by the type of contract.
        :param order: Order results based on the sort field.
        :param limit: Limit the number of results returned, default is 10 and max is 250.
        :param sort: Sort field used for ordering.
        :return: A JSON object containing the option chain data.
        """
    
        url = f"https://api.polygon.io/v3/snapshot/options/{underlying_asset}?strike_price={strike_price}&expiration_date={expiration_date}&contract_type={contract_type}&limit=1&apiKey={self.api_key}"
        r = requests.get(url).json()
        ticker_data = r['results']
        break_even = ticker_data[0]['break_even_price']
        print(break_even)
    

        # Create a StockSnapshot object


    async def get_option_chain_all(self, underlying_asset, strike_price=None, expiration_date=None, contract_type=None, order=None, limit=250, sort=None) -> pd.DataFrame:
        """
        Get all options contracts for an underlying ticker across all pages.

        :param underlying_asset: The underlying ticker symbol of the option contract.
        :param strike_price: Query by strike price of a contract.
        :param expiration_date: Query by contract expiration with date format YYYY-MM-DD.
        :param contract_type: Query by the type of contract.
        :param order: Order results based on the sort field.
        :param limit: Limit the number of results returned, default is 10 and max is 250.
        :param sort: Sort field used for ordering.
        :return: A list containing all option chain data across all pages.
        """
        endpoint = f"{self.base_url}/v3/snapshot/options/{underlying_asset}"
        params = {
            "strike_price": strike_price,
            "expiration_date": expiration_date,
            "contract_type": contract_type,
            "order": order,
            "limit": limit,
            "apiKey": self.api_key
        }

        params = {k: v for k, v in params.items() if v is not None}
        response_data = await self._request_all_pages(endpoint, params=params)  # Use _request_all_pages function
        option_data = [OptionSnapshotData(data) for data in response_data]
        data_dicts = [
            {
                "break_even_price": opt.break_even_price,
                "change": opt.change,
                "change_percent": opt.change_percent,
                "day_close": opt.day.close,
                "day_high": opt.day.high,
                "day_last_updated": opt.day.last_updated,
                "day_low": opt.day.low,
                "day_open": opt.day.open,
                "day_previous_close": opt.day.previous_close,
                "day_volume": opt.day.volume,
                "day_vwap": opt.day.vwap,
                "details_contract_type": opt.details.contract_type,
                "details_exercise_style": opt.details.exercise_style,
                "details_expiration_date": opt.details.expiration_date,
                "details_shares_per_contract": opt.details.shares_per_contract,
                "details_strike_price": opt.details.strike_price,
                "details_ticker": opt.details.ticker,
                "greeks_delta": opt.greeks.delta,
                "greeks_gamma": opt.greeks.gamma,
                "greeks_theta": opt.greeks.theta,
                "greeks_vega": opt.greeks.vega,
                "greeks_implied_volatility": opt.greeks.implied_volatility,
                "last_quote_ask": opt.last_quote.ask,
                "last_quote_ask_size": opt.last_quote.ask_size,
                "last_quote_bid": opt.last_quote.bid,
                "last_quote_bid_size": opt.last_quote.bid_size,
                "last_quote_last_updated": opt.last_quote.last_updated,
                "last_quote_midpoint": opt.last_quote.midpoint,
                "last_quote_timeframe": opt.last_quote.timeframe,
                "last_trade_conditions": opt.last_trade.conditions,
                "last_trade_exchange": opt.last_trade.exchange,
                "last_trade_price": opt.last_trade.price,
                "last_trade_sip_timestamp": opt.last_trade.sip_timestamp,
                "last_trade_size": opt.last_trade.size,
                "last_trade_timeframe": opt.last_trade.timeframe,
                "open_interest": opt.open_interest,
                "implied_volatility": opt.implied_volatility,
                "underlying_asset_change_to_break_even": opt.underlying_asset.change_to_break_even,
                "underlying_asset_last_updated": opt.underlying_asset.last_updated,
                "underlying_asset_price": opt.underlying_asset.price,
                "underlying_asset_ticker": opt.underlying_asset.ticker,
                "underlying_asset_timeframe": opt.underlying_asset.timeframe,
            }
            for opt in option_data
        ]

        df = pd.DataFrame(data_dicts)
        return df


    # async def gather_all_options(self, expiration_greater_than=None, expiration_less_than=None):
    #     alloptions = AllOptions()
    #     # Fetch all option contracts 
    #     # and their underlying tickers
    #     option_contracts = await AllOptions().fetch_all_option_contracts(
    #         expiration_date_gte=expiration_greater_than,
    #         expiration_date_lte=expiration_less_than)
            

    #     # Save snapshots to a CSV file
    #     output_file = wafilename
    #     return option_contracts, output_file