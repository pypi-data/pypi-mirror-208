import requests
from urllib.parse import urlencode
class OptionTrade:
    def __init__(self, trade_data):
        self.exchange = trade_data.get('exchange')
        self.participant_timestamp = trade_data.get('sip_timestamp')
        self.price = trade_data.get('price')
        self.size = trade_data.get('size')
        self.conditions = trade_data.get('conditions')


    def __str__(self):
        return f"Trade(price={self.price}, size={self.size}, timestamp={self.sip_timestamp}, conditions={self.conditions})"

    def __repr__(self):
        return self.__str__()