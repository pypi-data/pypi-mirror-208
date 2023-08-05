import httpx
from urllib.parse import urlencode, unquote
from .mapping.mapping_dicts import stock_condition_desc_dict,stock_condition_dict,option_condition_desc_dict,option_condition_dict,STOCK_EXCHANGES,OPTIONS_EXCHANGES
import csv
from .extra_data import ExtraData
from .indices_snapshot import Indices,IndicesData
from .aggregates import AggregatesData
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from datetime import datetime, timedelta
from .tickernews import keyword_hooks
from .company_info import CompanyInformation

from .snapshot import StockSnapshot, CSVSnapshot
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import List, Dict, Any
from .models import Dividend

from cfg import nasdaq
import requests

ten_days_ago = datetime.utcnow() - timedelta(days=5)
date_string = ten_days_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

from .quote import Quote
import aiohttp
from datetime import datetime, timedelta
from .embeddings import make_news_embed

class AsyncPolygonSDK:
    def __init__(self, api_key, symbol=None):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.conditions_map = stock_condition_dict
        self.exchanges_map = {}
        self.session = httpx.AsyncClient()
        self.symbol = symbol
    
    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("Closing session")
        await self.session.__aexit__(exc_type, exc, tb)

    async def _request(self, endpoint, params=None):
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as http_err:
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
                response = await self.session.get(next_url, params=params)
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
    
    async def company_information(self, ticker: str):
        url = f'https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                results = data.get('results')
                company_info = CompanyInformation(results)

                return company_info



    async def find_gaps(self, o, h, l, c, t):
        """
        Finds the gap-up and gap-down points in the given stock data.

        Args:
            o (List[float]): The list of opening prices.
            h (List[float]): The list of high prices.
            l (List[float]): The list of low prices.
            c (List[float]): The list of closing prices.
            t (List[datetime]): The list of timestamps corresponding to each data point.

        Returns:
            A tuple containing two lists of tuples. The first list contains the timestamps and indices of gap-up points,
            and the second list contains the timestamps and indices of gap-down points.

        Usage:
            To find gap-up and gap-down points in the stock data for a given symbol, you can call:
            ```
            o, h, l, c, t = await sdk.get_stock_data("AAPL")
            gap_ups, gap_downs = await sdk.find_gaps(o, h, l, c, t)
            print(f"Gap-up points: {gap_ups}")
            print(f"Gap-down points: {gap_downs}")
            ```
        """
        gap_ups = []
        gap_downs = []

        for i in range(1, len(o)):
            if o[i] > h[i-1]:  # Check if the opening price is greater than the previous high price
                gap_ups.append(i)
            elif o[i] < l[i-1]:  # Check if the opening price is less than the previous low price
                gap_downs.append(i)

        gap_ups_with_timestamps = [(t[i], i) for i in gap_ups]
        gap_downs_with_timestamps = [(t[i], i) for i in gap_downs]

        return gap_ups_with_timestamps, gap_downs_with_timestamps
    

    async def get_all_indices(self) -> pd.DataFrame:
        url = f"https://api.polygon.io/v3/snapshot/indices?apiKey={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                r = await resp.json()
                results = r['results']
                name = Indices(results)
                session = IndicesData(results)
                data = { 
                    'ticker': name.ticker,
                    'Name': name.name,
                    'Dollar Change':session.change,
                    'Change Percent':session.change_percent,
                    'Close':session.close,
                    'High':session.high,
                    'Open':session.open,
                    'Low':session.low,
                    'Previous Close':session.previous_close
                }
                df = pd.DataFrame(data)
                df.to_csv('files/indices/indices_data.csv')

                return df


    # async def financials(self, symbol, return_as_datafame: bool=False):
    #     url=f"https://api.polygon.io/vX/reference/financials?ticker={symbol}&limit=100&apiKey={self.api_key}"
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as resp:
    #             r = await resp.json()
    #             results = r['results']
    #             print(results)
    #             financials = [i['financials'] for i in results]
    #             balance_sheet = BalanceSheet(financials)
    #             comp_incomes = ComprehensiveIncome(financials)
    #             cash = CashFlow(financials)
    #             income = IncomeStatement(financials)
    #             data = { 
    #                 'Assets': balance_sheet.assets_value,
    #                 'Current Assets':balance_sheet.current_assets_value,
    #                 'Current Liabilities':balance_sheet.current_liabilities_value,
    #                 'Equity Attributable to Non-Controlling Interest':balance_sheet.equity_attributable_to_noncontrolling_interest_value,
    #                 'Equity Attributable to Parent':balance_sheet.equity_attributable_to_parent_value,
    #                 'Equity Value':balance_sheet.equity_value,
    #                 'Assets Value':balance_sheet.fixed_assets_value,
    #                 'Liabilities and Equity':balance_sheet.liabilities_and_equity_value,
    #                 'Liabilities':balance_sheet.liabilities_value,
    #                 'Non-current Assets':balance_sheet.noncurrent_assets_value,
    #                 'Non-current Liabilities':balance_sheet.noncurrent_liabilities_value,
    #                 'Other Thn Fixed Non-current Assets':balance_sheet.other_than_fixed_noncurrent_assets_value,
    #                 'Exchange Gains and Losses':cash.exchange_gains_losses_value,
    #                 'Net Cash Flow':cash.net_cash_flow,
    #                 'Net Cash Flow Continuing':cash.net_cash_flow_continuing_value,
    #                 'Net Cash Flow From Financing Continuing':cash.net_cash_flow_from_financing_activities_continuing_value,
    #                 'Net Cash Flow From Financing':cash.net_cash_flow_from_financing_activities_value,
    #                 'Net Cash Flow From Investing Continuing':cash.net_cash_flow_from_investing_activities_continuing_value,
    #                 'Net Cash Flow From Investing':cash.net_cash_flow_from_investing_activities_value,
    #                 'Net Cash Flow From Operating Continuing':cash.net_cash_flow_from_operating_activities_continuing_value,
    #                 'Net Cash Flow From Operating':cash.net_cash_flow_from_operating_activities_value,
    #                 'Comprehensive Income Loss Attributable to Non-controlling Interest':comp_incomes.comprehensive_income_loss_attributable_to_noncontrolling_interest_value,
    #                 'Comprehensive Income Loss Attributable to Parent':comp_incomes.comprehensive_income_loss_attributable_to_parent_value,

    #                 'Comprehensive Income Loss':comp_incomes.comprehensive_income_loss_value,
    #                 'Other Comprehensive Income Loss':comp_incomes.other_comprehensive_income_loss_value,
    #                 'Basic Earnings Per Share':income.basic_earnings_per_share_value,
    #                 'Diluted Earnings Per Share':income.diluted_earnings_per_share_value,
    #                 'Benefits Costs and Expenses':income.benefits_costs_expenses_value,
    #                 'Cost of Revenue':income.cost_of_revenue_value,
    #                 'Cost and Expenses':income.costs_and_expenses_value,
        
    #                 'Gross Profit Value':income.gross_profit_value,
    #                 'Income Loss From Continuing Operations After Tax':income.income_loss_from_continuing_operations_after_tax_value,
    #                 'Income Loss From Continuing Operations Before Tax':income.income_loss_from_continuing_operations_before_tax_value,
    #                 'Income Loss From  Discontinued Operations Net of Tax':income.income_loss_from_discontinued_operations_net_of_tax_value,
    #                 'Income Tax Expense Benefit - Current':income.income_tax_expense_benefit_current_value,
    #                 'Income Tax Epense Benefit - Deferred':income.income_tax_expense_benefit_deferred_value,
    #                 'Interest Income Expense After Provision For Losses':income.interest_income_expense_after_provision_for_losses_value,
    #                 'Interest Income Expense Operating - Net':income.interest_income_expense_operating_net_value,
    #                 'Net Income Loss Attributable to Non-controlling Interest':income.net_income_loss_attributable_to_noncontrolling_interest_value,
    #                 'Net Income Loss Attributable to Parent':income.net_income_loss_attributable_to_parent_value,

    #                 'Net Income Loss':income.net_income_loss_value,
    #                 'Operating Expenses':income.operating_expenses_value,
    #                 'Operating Income Loss': income.operating_income_loss_value,
    #                 'Participating Securities Distributed and Undistributed Earnings Loss - Basic': income.participating_securities_distributed_and_undistributed_earnings_loss_basic_value,
    #                 'Preferred Stock Dividends and Other Adjustments': income.preferred_stock_dividends_and_other_adjustments_value,
    #                 'Provision for Loan Lease and Other Losses': income.provision_for_loan_lease_and_other_losses_value,
    #                 'Revenues': income.revenues_value



    #                 }

    #             return balance_sheet,comp_incomes,cash,income



   
    async def find_gap_price_range(self, o, h, l, c, t, gap_index, filled=None):
        if o[gap_index] > h[gap_index - 1]:
            direction = "up"
            gap_low = h[gap_index - 1]
            gap_high = l[gap_index]
        elif o[gap_index] < l[gap_index - 1]:
            direction = "down"
            gap_low = h[gap_index]
            gap_high = l[gap_index - 1]
        else:
            direction = "unknown"
            gap_low = None
            gap_high = None

        if filled is None:
            return gap_low, gap_high
        else:
            fill_index = None
            for i in range(gap_index + 1, len(c)):
                if direction == "up":
                    if l[i] <= gap_high and h[i] >= gap_low:
                        fill_index = i
                        break
                elif direction == "down":
                    if h[i] >= gap_high and l[i] <= gap_low:
                        fill_index = i
                        break

            if filled is True:
                if fill_index is not None:
                    return t[fill_index]
                else:
                    return None
            else:
                if fill_index is not None:
                    return t[fill_index]
                else:
                    return None            
    async def fetch_historical_crypto_data(self, pair, days, timeframe, multiplier):
        now = datetime.now()
        days_ago = now - timedelta(days=days)
        to_date = now.strftime("%Y-%m-%d")
        from_date = days_ago.strftime("%Y-%m-%d")

        endpoint = f"/v2/aggs/ticker/X:{pair}/range/{multiplier}/{timeframe}/{from_date}/{to_date}?adjusted=true&sort=asc&limit=5000"
        data = await self._request(endpoint)

        if isinstance(data, dict):
            if "results" not in data or not data["results"]:
                print(f"Warning: No historical data found for {pair}. API response: {data}")
                return []
            else:
                return data["results"]
        else:
            print(f"Error fetching historical data for {pair}. API response: {data}")
            raise ValueError("Error fetching historical data")
        
    async def get_snapshot(self, symbol):
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json_data = await response.json()
                ticker_data = json_data.get('ticker')

                if ticker_data is not None:
                    try:
                        stock_snapshot = StockSnapshot(ticker_data)
                        return stock_snapshot
                    except Exception as e:
                        print(f"Error creating StockSnapshot: {e}")
                        return None
                else:
                    print("No ticker data found.")
                    return None

    async def get_exchanges(self, asset_class=None, locale=None) -> Dict[str, Any]:
        """
        Get exchanges data from the Polygon.io API.

        :param asset_class: Optional string specifying the asset class to filter exchanges (e.g., 'stocks', 'options', 'crypto', 'fx').
        :param locale: Optional string specifying the locale to filter exchanges (e.g., 'us', 'global').
        :return: A dictionary containing the exchanges data.
        """
        endpoint = "/v3/reference/exchanges"
        params = {}

        if asset_class:
            params["asset_class"] = asset_class
        if locale:
            params["locale"] = locale

        exchanges_data = await self._request(endpoint, params=params)

        return exchanges_data
    

    async def fetch_and_store_exchanges(self):
        exchange_data = await self.get_exchanges(asset_class="stocks", locale="us")
        self.exchanges_map = {exchange["id"]: exchange["name"] for exchange in exchange_data}
    
    async def get_polygon_logo(self, symbol):
        url = f'https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={self.api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if 'results' not in data:
                    # No results found
                    return None
                
                results = data['results']
                branding = results.get('branding')

                if branding and 'icon_url' in branding:
                    encoded_url = branding['icon_url']
                    decoded_url = unquote(encoded_url)
                    url_with_api_key = f"{decoded_url}?apiKey={self.api_key}"
                    return url_with_api_key        
    async def ticker_news(self, keyword_hooks):
        sent_articles = set()
        while True:
            endpoint = "/v2/reference/news"
            response = await self._request(endpoint)

            if not response or "results" not in response:
                continue

            results = response['results']
            publisher = [i['publisher'] if 'publisher' in i and i['publisher'] else 'N/A' for i in results]
            home_url = [i['homepage_url'] if 'homepage_url' in i and i['homepage_url'] else 'N/A' for i in publisher]
            icon_url = [i['logo_url'] if 'logo_url' in i and i['logo_url'] else 'N/A' for i in publisher]
            name = [i['name'] if 'name' in i and i['name'] else "N/A" for i in results]
            title = [i['title'] if 'title' in i and i['title'] else 'N/A' for i in results]
            author = [i['author'] if 'author' in i and i['author'] else 'N/A' for i in results]
            article_url = [i['article_url'] if 'article_url' in i and i['article_url'] else 'N/A' for i in results]
            tickers = [i['ticker'] if 'ticker' in i and i['ticker'] else 'N/A' for i in results]
            amp_url = [i['amp_url'] if 'amp_url' in i and i['amp_url'] else 'N/A' for i in results]
            image_url = [i['image_url'] if 'image_url' in i and i['image_url'] else 'N/A' for i in results]
            description = [i['description'] if 'description' in i and i['description'] else 'N/A' for i in results]
            keywords = [i['keywords'] if 'keywords' in i and i['keywords'] else 'N/A' for i in results]

            for article_index, article_url in enumerate(article_url):
                if article_url in sent_articles:
                    continue

                article_keywords = keywords[article_index]
                sent_webhook = False

                for keyword, webhook_url in keyword_hooks.items():
                    if keyword in article_keywords:
                        await make_news_embed(webhook_url, image_url[article_index], title[article_index], description[article_index], name[article_index], icon_url[article_index], article_url, tickers[article_index], home_url[article_index], article_keywords, author[article_index])
                        sent_articles.add(article_url)
                        sent_webhook = True
                        print(f"New article processed: {title[article_index]} {keywords}")


                if not sent_webhook:
                    continue
    async def get_dividends_for_next_12_days(self, date_str):
        endpoint = "/v3/reference/dividends"
        params = {
            "record_date": date_str,
            "order": "asc"  # Optional: sort in ascending order
        }

        response = await self._request(endpoint, params)
        if response and "results" in response:
            dividends = [Dividend(**dividend_data) for dividend_data in response["results"]]
            return dividends
        else:
            return None

    async def get_stock_conditions(self, asset_class) -> Dict[int, str]:
        """
        Get stock conditions data from the Polygon.io API.

        :return: A dictionary with condition IDs as keys and condition names as values.
        """
        url = f"https://api.polygon.io/v3/reference/conditions?asset_class={asset_class}&limit=1000&apiKey={self.api_key}"
        stock_conditions = {}

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    conditions_data = data['results']

                    for condition in conditions_data:
                        condition_id = condition['id']
                        condition_name = condition['name']
                        stock_conditions[condition_id] = condition_name
                else:
                    print(f"Error: {response.status}")

        return stock_conditions

    async def get_all_snapshots(self, tickers=None, include_otc=False, output_file='snapshots.csv') -> List[CSVSnapshot]:
        endpoint = "/v2/snapshot/locale/us/markets/stocks/tickers"
        params = {
            'apiKey': self.api_key,
            'include_otc': include_otc
        }

        if tickers:
            params['tickers'] = ','.join(tickers)

        response_data = await self._request(endpoint, params=params)
        print(response_data)
        ticker_data_list = []
        for single_ticker_data in response_data['tickers']:
            if single_ticker_data is not None:
                print("Ticker data:", single_ticker_data)
                csv_snapshot = CSVSnapshot(single_ticker_data, self.conditions_map, self.exchanges_map)
                ticker_data_list.append(csv_snapshot)

        # Write snapshots to a CSV file
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = list(ticker_data_list[0].to_dict().keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for snapshot in ticker_data_list:
                writer.writerow(snapshot.to_dict())
    
        return ticker_data_list
        
    async def get_quotes(self, ticker, timestamp=None, order="desc", limit=500, sort=None):
        """
        Get NBBO quotes for a ticker symbol in a given time range.

        :param ticker: The stock ticker symbol.
        :param kwargs: Optional keyword arguments.
            timestamp: Query by timestamp. Either a date with the format 'YYYY-MM-DD' or a nanosecond timestamp.
            order: Order results based on the sort field.
            limit: Limit the number of results returned, default is 10 and max is 50000.
            sort: Sort field used for ordering.
        :return: A list of Quote objects containing the NBBO quotes for the specified stock ticker.
        """
        endpoint = f"/v3/quotes/{ticker}"
        params = {
            'timestamp': timestamp,
            'order': order,
            'limit': limit,
            'sort': sort
        }


        self.params = {k: v for k, v in params.items() if v is not None}
        response_data = await self._request(endpoint, self.params)
        if response_data is None:
            return []

        ticker_data = [Quote.from_dict(ticker) for ticker in response_data.get('results', []) if ticker is not None]
        return ticker_data
    
    async def get_aggregates(self, ticker, multiplier, timespan, from_date, to_date, order="asc", limit=50):
        """
        Retrieve aggregate data for a given stock ticker.

        :param stock_ticker: The stock ticker symbol as a string.
        :param multiplier: The multiplier for the timespan as an integer.
        :param timespan: The timespan as a string (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
        :param from_date: The start date for the data as a string in YYYY-MM-DD format.
        :param to_date: The end date for the data as a string in YYYY-MM-DD format.
        :return: An instance of AggregatesData containing the aggregate data.
        """
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted=true&sort={order}&limit={limit}&apiKey={self.api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                all_results = []
                next_url = url
                data = await response.json()
                while next_url:
                    try:
                        response = await self.session.get(next_url)
                        response.raise_for_status()
                        data = response.json()

                        if "results" in data:
                            all_results.extend(data["results"])

                        next_url = data.get("next_url")
                        if next_url:
                            next_url += f'&{urlencode({"apiKey": self.api_key})}'

                    except httpx.HTTPError as http_err:
                        print(f"An HTTP error occurred: {http_err}")
                        break
                    except Exception as err:
                        print(f"An error occurred: {err}")
                        break

                aggregates_data = AggregatesData({"results": all_results, "ticker": ticker})

                return aggregates_data
            

    async def calculate_moving_averages(self, aggregates_data):
        """
        Calculates the moving averages for the given aggregates data.

        Args:
            aggregates_data (AggregatesData): The aggregates data containing the close prices.

        Returns:
            dict: A dictionary containing the moving averages for different periods.

        Raises:
            None.

        Example Usage:
            aggregates_data = await sdk.get_aggregates('AAPL', 1, 'day', "2023-05-01", "2023-05-11")
            moving_averages = await sdk.calculate_moving_averages(aggregates_data)
            print(moving_averages)
        """
        moving_averages = {}
        periods = [21, 50, 200, 252]  # Define the desired MA periods
        close_prices = np.array(aggregates_data.close)

        for period in periods:
            moving_average = np.convolve(close_prices, np.ones(period), 'valid') / period
            moving_averages[f'{period}_day_SMA'] = moving_average

        return moving_averages
    
    
    async def get_support_resistance_levels(self, stock_ticker, multiplier, timespan, from_date, to_date, window=10):
        """
        Calculate support and resistance levels for a given stock ticker using historic aggregate data.

        :param stock_ticker: The stock ticker symbol as a string.
        :param multiplier: The multiplier for the timespan as an integer.
        :param timespan: The timespan as a string (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
        :param from_date: The start date for the data as a string in YYYY-MM-DD format.
        :param to_date: The end date for the data as a string in YYYY-MM-DD format.
        :param window: The window size for finding local minima and maxima as an integer (default: 10).
        :return: A tuple containing two lists: support levels and resistance levels.
        """
        # Retrieve historic aggregate data
        try:
            aggregates_data = await self.get_aggregates(stock_ticker, multiplier, timespan, from_date, to_date, limit=50000)
            closing_prices = np.array([i['c'] for i in aggregates_data])

            # Define comparator functions for local minima and maxima
            local_minima_comparator = np.less
            local_maxima_comparator = np.greater

            # Find local minima and maxima within the specified window
            local_minima_indices = argrelextrema(closing_prices, local_minima_comparator, order=window)
            local_maxima_indices = argrelextrema(closing_prices, local_maxima_comparator, order=window)

            # Extract support and resistance levels from local minima and maxima
            support_levels = closing_prices[local_minima_indices].tolist()
            resistance_levels = closing_prices[local_maxima_indices].tolist()
            return support_levels, resistance_levels
        except (TypeError, KeyError):
            print(f"Error")



        
    

    async def get_simple_moving_average(self, ticker, timestamp=None, timespan='day', adjusted=True, window=None,
                                series_type='close', expand_underlying=False, order='desc', limit=None):
        """
        Get the simple moving average (SMA) for a ticker symbol over a given time range for a ticker or options symbol.

        :param ticker: The stock ticker symbol or options symbol. Use 'generate_option_symbol' to create the needed symbol.
        :param timestamp: Optional timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param timespan: Optional aggregate time window. Default is 'day'.
        :param adjusted: Optional boolean to adjust aggregates for splits. Default is True.
        :param window: Optional window size to calculate the SMA. Default is 50.
        :param series_type: Optional price to use for SMA calculation. Default is 'close'.
        :param expand_underlying: Optional boolean to include aggregates in the response. Default is False.
        :param order: Optional order to return results, ordered by timestamp. Default is 'desc'.
        :param limit: Optional limit for the number of results returned. Default is 10, max is 5000.
        :return: A JSON object containing the SMA data.
        """
        endpoint = f"/v1/indicators/sma/{ticker}"

        params = {
                "timestamp": timestamp,
                "timespan": timespan,
                "adjusted": adjusted,
                "window": window,
                "series_type": series_type,
                "expand_underlying": expand_underlying,
                "order": order,
                "limit": limit
            }

            # Remove parameters with None values
        self.params = {k: v for k, v in params.items() if v is not None}

        request = await self._request(endpoint, params=self.params)
        try:
            results = request['results']
            underlying = results['underlying']
            underlying_data = requests.get(underlying['url'] + f'&apiKey={self.api_key}').json()
            underlying_results = underlying_data['results']
            underlying_vw = underlying_results[0]['vw']

            values = results['values']
            value = values[0]['value']
            prev_value = values[1]['value']

            value_trend = value - prev_value
            if value_trend < 0:
                value_trend = "increasing"
            else:
                value_trend = "decreasing"
            historic_values = [i['value'] for i in values]
            return value, underlying_vw, value_trend, historic_values
        except (TypeError, KeyError):
            pass


    async def get_polygon_logo(self, symbol):
        url = f'https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={self.api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if 'results' not in data:
                    # No results found
                    return None
                
                results = data['results']
                branding = results.get('branding')

                if branding and 'icon_url' in branding:
                    encoded_url = branding['icon_url']
                    decoded_url = unquote(encoded_url)
                    url_with_api_key = f"{decoded_url}?apiKey={self.api_key}"
                    return url_with_api_key

    async def get_exponential_moving_average(self, ticker, timestamp=None, timespan: str=None, adjusted=True, window: str=None, series_type="close", expand_underlying=None, order="desc", limit: str=None):
        """
        Get the exponential moving average (EMA) for a ticker symbol over a given time range.

        :param ticker: The stock ticker symbol or options symbol. Use 'generate_option_symbol' to create the needed symbol.
        :param timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param timespan: The size of the aggregate time window.
        :param adjusted: Whether or not the aggregates used to calculate the EMA are adjusted for splits.
        :param window: The window size used to calculate the EMA.
        :param series_type: The price in the aggregate which will be used to calculate the EMA.
        :param expand_underlying: Whether or not to include the aggregates used to calculate this indicator in the response.
        :param order: The order in which to return the results, ordered by timestamp.
        :param limit: Limit the number of results returned, default is 10 and max is 5000.
        :return: A JSON object containing the EMA data.
        """
        endpoint = f"/v1/indicators/ema/{ticker}"
        params = {
            "timestamp": timestamp,
            "timespan": timespan,
            "adjusted": adjusted,
            "window": window,
            "series_type": series_type,
            "expand_underlying": expand_underlying,
            "order": order,
            "limit": limit
        }

        # Remove parameters with None values
        params = {k: v for k, v in params.items() if v is not None}

        request= await self._request(endpoint, params=params)
        try:
            results = request['results']
            response = results['values']
            underlying = results['underlying']
            underlying_data = requests.get(underlying['url'] + f'&apiKey={self.api_key}').json()
            underlying_results = underlying_data['results']
            underlying_vw = underlying_results[0]['vw']
            values = results['values']
            value = values[0]['value']
            prev_value = values[1]['value']
            historic_values = [i['value'] for i in values]

            value_trend = value - prev_value
            if value_trend < 0:
                value_trend = "increasing"
            else:
                value_trend = "decreasing"


            return value, underlying_vw, value_trend, historic_values
        except (KeyError, TypeError) as e:
            print(f"KeyError in get_macd: {e}. The requested key is not available in the response.")
            return None         
           

    async def get_macd(self, ticker, timestamp=None, timespan: str=None, adjusted=True, short_window=12, long_window=26, signal_window=9, series_type="close", expand_underlying=None, order="desc", limit: str=None):
        """
        Get moving average convergence/divergence (MACD) data for a ticker symbol over a given time range.

        :param ticker: The stock ticker symbol or options symbol. Use 'generate_option_symbol' to create the needed symbol.
        :param timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param timespan: The size of the aggregate time window.
        :param adjusted: Whether or not the aggregates used to calculate the MACD are adjusted for splits.
        :param short_window: The short window size used to calculate MACD data.
        :param long_window: The long window size used to calculate MACD data.
        :param signal_window: The window size used to calculate the MACD signal line.
        :param series_type: The price in the aggregate which will be used to calculate the MACD.
        :param expand_underlying: Whether or not to include the aggregates used to calculate this indicator in the response.
        :param order: The order in which to return the results, ordered by timestamp.
        :param limit: Limit the number of results returned, default is 10 and max is 5000.
        :return: A JSON object containing the MACD data.
        """
        endpoint = f"/v1/indicators/macd/{ticker}"
        params = {
            "timestamp": timestamp,
            "timespan": timespan,
            "adjusted": adjusted,
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
            "series_type": series_type,
            "expand_underlying": expand_underlying,
            "order": order,
            "limit": limit
        }

        # Remove parameters with None values
        params = {k: v for k, v in params.items() if v is not None}

        request = await self._request(endpoint, params=params)
        try:
            results = request['results']
            values = results['values']
            macd = [i['value'] for i in values]
            signal = [i['signal'] for i in values]
            histogram = [i['histogram'] for i in values]

        except (KeyError, TypeError) as e:
            print(f"KeyError in get_macd: {e}. The requested key is not available in the response.")
            return None

        return macd, signal, histogram


    


    async def get_rsi(self, ticker, timestamp=None, timespan: str="hour", adjusted=True, window=14, series_type="close", expand_underlying=None, order="desc", limit:str = 10):
        """
        Get the relative strength index (RSI) for a ticker symbol over a given time range.

        :param ticker: The stock ticker symbol or options symbol. Use 'generate_option_symbol' to create the needed symbol.
        :param timestamp: Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
        :param timespan: The size of the aggregate time window.
        :param adjusted: Whether or not the aggregates used to calculate the RSI are adjusted for splits.
        :param window: The window size used to calculate the RSI.
        :param series_type: The price in the aggregate which will be used to calculate the RSI.
        :param expand_underlying: Whether or not to include the aggregates used to calculate this indicator in the response.
        :param order: The order in which to return the results, ordered by timestamp.
        :param limit: Limit the number of results returned, default is 10 and max is 5000.
        :return: A JSON object containing the RSI data.
        """
        endpoint = f"/v1/indicators/rsi/{ticker}"
        params = {
            "timestamp": timestamp,
            "timespan": timespan,
            "adjusted": adjusted,
            "window": window,
            "series_type": series_type,
            "expand_underlying": expand_underlying,
            "order": order,
            "limit": limit
        }

        # Remove parameters with None values
        params = {k: v for k, v in params.items() if v is not None}

        request = await self._request(endpoint, params=params)
        values = []  # Initialize values as an empty list
        if request is not None:
            results = request['results']
            values = results.get('values', [])

        rsi_values = [entry.get('value', None) for entry in values]
        
        try:
            return rsi_values
        except IndexError:
            return None


    async def get_ticker_narrative(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.polygon.io/v2/reference/news?ticker={symbol}&order=desc&limit=1&apiKey={self.api_key}") as response:
                data = await response.json()

                results = data['results']
                filtered_results = [i for i in results if len(i['tickers']) == 1 and symbol in i['tickers']]
                print(filtered_results)
                if len(filtered_results) > 0:
                    article = filtered_results[0]
                    title = article['title']
                    description = article['description']
                    return {
                        'title': title,
                        'description': description
                    }
                else:
                    return None
    async def format_timestamp(self, timestamp: datetime) -> str:
        return timestamp.strftime("%Y/%m/%d %I:%M %p")               


