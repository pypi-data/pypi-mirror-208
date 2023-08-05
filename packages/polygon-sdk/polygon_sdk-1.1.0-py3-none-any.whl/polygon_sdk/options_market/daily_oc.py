class DailyOpenClose:
    def __init__(self, data):


        self.from_date = data.get('from')
        self.symbol = data.get('symbol')
        self.open = data.get('open')
        self.close = data.get('close')
        self.low = data.get('low')
        self.high =  data.get('high')
        self.volume = data.get('volume')
        self.ah = data.get('ah', None)
        self.pm = data.get('pm', None)