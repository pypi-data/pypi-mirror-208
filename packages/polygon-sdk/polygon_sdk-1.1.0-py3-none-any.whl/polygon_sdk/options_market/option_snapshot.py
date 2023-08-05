class OptionSnapshotData:
    def __init__(self, data):
        self.break_even_price = data.get("break_even_price", {})
        self.change = data.get("change")
        self.change_percent = data.get("change_percent")
        self.day = OptionSnapshotData.DayData(data.get("day", {}))
        self.details = OptionSnapshotData.DetailsData(data.get("details", {}))
        self.greeks = OptionSnapshotData.GreeksData(data.get("greeks", {}))
        self.last_quote = OptionSnapshotData.LastQuoteData(data.get("last_quote", {}))
        self.last_trade = OptionSnapshotData.LastTradeData(data.get("last_trade", {}))
        self.open_interest = data.get("open_interest")
        self.implied_volatility = data.get("implied_volatility")
        self.underlying_asset = OptionSnapshotData.UnderlyingAssetData(data.get("underlying_asset", {}))
    class DayData:
        def __init__(self, day_data):
            self.close = day_data.get("close")
            self.high = day_data.get("high")
            self.last_updated = day_data.get("last_updated")
            self.low = day_data.get("low")
            self.open = day_data.get("open")
            self.previous_close = day_data.get("previous_close")
            self.volume = day_data.get("volume")
            self.vwap = day_data.get("vwap")

    class DetailsData:
        def __init__(self, details_data):
            self.contract_type = details_data.get("contract_type")
            self.exercise_style = details_data.get("exercise_style")
            self.expiration_date = details_data.get("expiration_date")
            self.shares_per_contract = details_data.get("shares_per_contract")
            self.strike_price = details_data.get("strike_price")
            self.ticker = details_data.get("ticker")

    class GreeksData:
        def __init__(self, greeks_data):
            self.delta = greeks_data.get("delta")
            self.gamma = greeks_data.get("gamma")
            self.theta = greeks_data.get("theta")
            self.vega = greeks_data.get("vega")
            self.implied_volatility = greeks_data.get("implied_volatility")

    class LastQuoteData:
        def __init__(self, last_quote_data):
            self.ask = last_quote_data.get("ask")
            self.ask_size = last_quote_data.get("ask_size")
            self.bid = last_quote_data.get("bid")
            self.bid_size = last_quote_data.get("bid_size")
            self.last_updated = last_quote_data.get("last_updated")
            self.midpoint = last_quote_data.get("midpoint")
            self.timeframe = last_quote_data.get("timeframe")

    class LastTradeData:
        def __init__(self, last_trade_data):
            self.conditions = last_trade_data.get("conditions")
            self.exchange = last_trade_data.get("exchange")
            self.price = last_trade_data.get("price")
            self.sip_timestamp = last_trade_data.get("sip_timestamp")
            self.size = last_trade_data.get("size")
            self.timeframe = last_trade_data.get("timeframe")

    class UnderlyingAssetData:
        def __init__(self, underlying_asset_data):
            self.change_to_break_even = underlying_asset_data.get("change_to_break_even")
            self.last_updated = underlying_asset_data.get("last_updated")
            self.price = underlying_asset_data.get("price")
            self.ticker = underlying_asset_data.get("ticker")
            self.timeframe = underlying_asset_data.get("timeframe")

