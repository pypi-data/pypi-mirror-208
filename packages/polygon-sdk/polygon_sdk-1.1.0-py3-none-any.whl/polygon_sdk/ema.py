class ExponentialMovingAverage:
    def __init__(self, sdk):
        self.sdk = sdk


    def get_exponential_moving_average(self, stock_ticker, timestamp=None, timespan="day", adjusted=True, window=50, series_type="close", expand_underlying=None, order="desc", limit=10):
        """
        Get the exponential moving average (EMA) for a ticker symbol over a given time range.

        :param stock_ticker: The ticker symbol for which to get exponential moving average (EMA) data.
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
        endpoint = f"/v1/indicators/ema/{stock_ticker}"
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

        return self._request(endpoint, params=params)