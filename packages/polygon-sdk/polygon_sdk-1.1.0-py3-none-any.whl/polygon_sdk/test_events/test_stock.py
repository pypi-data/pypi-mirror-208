from dataclasses import dataclass
from typing import Dict,Any
import pandas as pd
@dataclass
class TestStocksEvent:
    symbol: str
    close: float
    high: float
    low: float
    open: float
    volume: float
    vwap: float
    last_quote_ask_price: float
    last_quote_ask_size: int
    last_quote_bid_price: float
    last_quote_bid_size: int
    last_quote_timestamp: str
    last_trade_conditions: str

    last_exchange: str
    last_price: float
    last_size: int
    last_trade_timestamp: str
    min_close: float
    min_high: float
    min_low: float
    min_open: float
    min_volume: float
    min_vwap: float
    prev_vwap: float
    prev_close: float
    prev_high: float
    prev_low: float
    prev_open: float
    prev_volume: float
    today_change_percent: float
    today_change: float

    @classmethod
    def from_row(cls, row):
        return cls(
            symbol=row['symbol'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            open=row['open'],
            volume=row['volume'],
            vwap=row['vwap'],
            last_quote_ask_price=row['last_quote_ask_price'],
            last_quote_ask_size=row['last_quote_ask_size'],
            last_quote_bid_price=row['last_quote_bid_price'],
            last_quote_bid_size=row['last_quote_bid_size'],
            last_quote_timestamp=row['last_quote_timestamp'],
            last_trade_conditions=row["last_trade_conditions"] if pd.notna(row["last_trade_conditions"]) else "",
            last_exchange=row['last_exchange'],
            last_price=row['last_price'],
            last_size=row['last_size'],
            last_trade_timestamp=row['last_trade_timestamp'],
            min_close=row['min_close'],
            min_high=row['min_high'],
            min_low=row['min_low'],
            min_open=row['min_open'],

            min_volume=row['min_volume'],
            min_vwap=row['min_vwap'],
            prev_vwap=row['prev_vwap'],
            prev_close=row['prev_close'],
            prev_high=row['prev_high'],
            prev_low=row['prev_low'],
            prev_open=row['prev_open'],
            prev_volume=row['prev_volume'],
            today_change_percent=row['today_change_percent'],
            today_change=row['today_change']
        )
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestStocksEvent':
        return cls(**data)