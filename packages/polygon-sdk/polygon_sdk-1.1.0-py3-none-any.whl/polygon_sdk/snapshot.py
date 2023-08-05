from typing import List, Optional
from dataclasses import dataclass
from typing import Dict
from datetime import datetime
from polygon_sdk.mapping.mapping_dicts import stock_condition_dict,STOCK_EXCHANGES
@dataclass
class Ticker:
    ticker: Optional[str] = None
    today_change: Optional[float] = None
    today_change_perc: Optional[float] = None


@dataclass
class Day:
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    vwap: Optional[float] = None

@dataclass
class LastQuote:
    ask_price: Optional[float] = None
    ask_size: Optional[float] = None
    bid_price: Optional[float] = None
    bid_size: Optional[float] = None
    quote_timestamp: Optional[float] = None

@dataclass
class LastTrade:
    conditions: Optional[List[int]] = None
    trade_id: Optional[str] = None
    trade_price: Optional[float] = None
    trade_size: Optional[int] = None
    trade_timestamp: Optional[int] = None
    trade_exchange: Optional[int] = None

@dataclass
class Min:
    accumulated_volume: Optional[int] = None
    minute_timestamp: Optional[float] = None
    vwap: Optional[float] = None
    volume: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None

@dataclass
class PrevDay:
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    vwap: Optional[float] = None

@dataclass
class StockSnapshot:
    ticker: str
    today_changep: float
    today_change: float
    stock_day: Day
    stock_last_quote: LastQuote
    last_trade: LastTrade
    stock_minute_bar: Min
    prev_day: PrevDay
    
    def __init__(self, ticker_data):
        self.today_changep = ticker_data.get('todaysChangePerc', None)
        self.today_change = ticker_data.get('todaysChange', 0.0)

        day_data = ticker_data.get('day', {})
        self.stock_day = Day(
            open=day_data.get('o'),
            high=day_data.get('h'),
            low=day_data.get('l'),
            close=day_data.get('c'),
            volume=day_data.get('v'),
            vwap=day_data.get('vw'),
        )

        quote_data = ticker_data.get('lastQuote', {})
        self.stock_last_quote = LastQuote(
            ask_price=quote_data.get('P'),
            ask_size=quote_data.get('S'),
            bid_price=quote_data.get('p'),
            bid_size=quote_data.get('s'),
            quote_timestamp=quote_data.get('t'),
        )

        trade_data = ticker_data.get('lastTrade', {})
        self.last_trade = LastTrade(
            conditions=trade_data.get('c'),
            trade_id=trade_data.get('i'),
            trade_price=trade_data.get('p'),
            trade_size=trade_data.get('s'),
            trade_timestamp=trade_data.get('t'),
            trade_exchange=trade_data.get('x'),
        )

        min_data = ticker_data.get('min', {})
        self.stock_minute_bar = Min(
            accumulated_volume=min_data.get('av'),
            minute_timestamp=min_data.get('t'),
            vwap=min_data.get('vw'),
            volume=min_data.get('v'),
            open=min_data.get('o'),
            high=min_data.get('h'),
            low=min_data.get('l'),
            close=min_data.get('c'),
        )

        prev_data = ticker_data.get('prevDay', None)
        self.prev_day = PrevDay(
            open=prev_data.get('o'),
            high=prev_data.get('h'),
            low=prev_data.get('l'),
            close=prev_data.get('c'),
            volume=prev_data.get('v'),
            vwap=prev_data.get('vw'),
        )


from dataclasses import dataclass
from typing import List

@dataclass
class Session:
    open: float
    close: float
    high: float
    low: float
    change: float
    change_percent: float
    previous_close: float
@dataclass
class IndexSnapshot:
    ticker: str
    name: str
    value: float
    session: Session

    def __init__(self, ticker_data):
        self.value = ticker_data[0]['value']
        self.session = Session(**ticker_data[0]['session'])




@dataclass
class CSVSnapshot:
    def __init__(self, ticker_data, condition_codes, exchange_codes):
        try:
            self.symbol = ticker_data['ticker']
            self.stock_changep = ticker_data['todaysChangePerc']
            self.stock_change = ticker_data['todaysChange']

            self.stock_day = ticker_data['day']
            self.stock_o = self.stock_day['o']
            self.stock_h = self.stock_day['h']
            self.stock_l = self.stock_day['l']
            self.stock_c = self.stock_day['c']
            self.stock_v = self.stock_day['v']
            self.stock_vw = self.stock_day['vw']

            self.stock_last_quote = ticker_data['lastQuote']
            self.last_quote_ask_price = self.stock_last_quote['P']
            self.last_quote_ask_size = self.stock_last_quote['S']
            self.last_quote_bid_price = self.stock_last_quote['p']
            self.last_quote_bid_size = self.stock_last_quote['s']
            self.last_quote_timestamp = self.stock_last_quote['t']

            self.last_trade = ticker_data['lastTrade']
            self.last_trade_condition = self.last_trade['c']
            self.last_trade_id = self.last_trade['i']
            self.last_trade_price = self.last_trade['p']
            self.last_trade_size = self.last_trade['s']
            self.last_trade_time = self.last_trade['t']
            self.last_trade_exchange = self.last_trade['x']

            self.stock_minute_bar = ticker_data['min']
            self.minute_av = self.stock_minute_bar['av']
            self.minute_time = self.stock_minute_bar['t']
            self.minute_open = self.stock_minute_bar['o']
            self.minute_high = self.stock_minute_bar['h']
            self.minute_low = self.stock_minute_bar['l']
            self.minute_close = self.stock_minute_bar['c']
            self.minute_volume = self.stock_minute_bar['v']
            self.minute_vwap = self.stock_minute_bar['vw']

            self.prev_day = ticker_data['prevDay']
            self.prev_day_open = self.prev_day['o']
            self.prev_day_high = self.prev_day['h']
            self.prev_day_low = self.prev_day['l']
            self.prev_day_close = self.prev_day['c']
            self.prev_day_volume = self.prev_day['v']
            self.prev_day_vwap = self.prev_day['vw']
            self.condition_name = self.decode_conditions(self.last_trade_condition, condition_codes)
            self.exchange_name = self.decode_exchange(self.last_trade_exchange)
            print(self.condition_name, self.exchange_name)
        except (KeyError, TypeError, AttributeError, UnboundLocalError):
            pass
    @staticmethod
    def decode_conditions(conditions: List[int], condition_codes: Dict[int, str]) -> List[str]:
        if conditions is None:
            return None
        return [condition_codes.get(c, f"Unknown condition {c}") for c in conditions]
    
    @staticmethod
    def decode_exchange(exchange: int) -> str:
        exchange_codes = STOCK_EXCHANGES
        return exchange_codes.get(exchange, f"Unknown exchange {exchange}")
    @staticmethod
    def decode_timestamp(timestamp: int) -> str:
        if timestamp is None:
            return None
        dt = datetime.fromtimestamp(timestamp / 1000.0)
        return dt.strftime("%Y/%m/%d %I:%M %p")
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'stock_changep': self.stock_changep,
            'stock_change': self.stock_change,
            'open': self.stock_o,
            'high': self.stock_h,
            'low': self.stock_l,
            'close': self.stock_c,
            'volume': self.stock_v,
            'vwap': self.stock_vw,
            'last_quote_ask_price': self.last_quote_ask_price,
            'last_quote_ask_size': self.last_quote_ask_size,
            'bid_price': self.last_quote_bid_price,
            'bid_size': self.last_quote_bid_size,
            'last_quote_timestamp': self.last_quote_timestamp,
            'last_condition': self.condition_name,
            'last_exchange': self.exchange_name,
            'last_id': self.last_trade_id,
            'last_price': self.last_trade_price,
            'last_size': self.last_trade_size,
            'last_trade_timestamp': self.last_trade_time,

            'prev_open': self.prev_day_open,
            'prev_high': self.prev_day_high,
            'prev_low': self.prev_day_low,
            'prev_close': self.prev_day_close,
            'prev_volume': self.prev_day_volume,
            'prev_vwap': self.prev_day_vwap,
            'min_av': self.minute_av,
            'min_time': self.minute_time,
            'min_open': self.minute_open,
            'min_high': self.minute_high,
            'min_low': self.minute_low,
            'min_close': self.minute_close,
            'min_volume': self.minute_volume,
            'min_vwap': self.minute_vwap

            # Add more attributes here as needed
        }

