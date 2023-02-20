import requests
import json

class ExchangeAPI:
    def __init__(self, sql=False):
        self.APIKEY = 'ZqgdDnBRDagA9cpUQZDcQAYLbcgRgMHT'
        self.HEADER = {'apikey' : self.APIKEY}
        self.URL = 'https://api.apilayer.com/exchangerates_data/latest?base=USD&symbols=USD,UAH,PLN,EUR,CAD'

    def get_exchange_values(self):
        '''EXAMPLE OF DATA
            {
            "success": true,
            "timestamp": 1676645763,
            "base": "UAH",
            "date": "2023-02-17",
            "rates": {
                "USD": 0.027206,
                "EUR": 0.025567
                }
            }'''
        return json.loads(requests.get(self.URL, headers=self.HEADER).text)

    def get_one_exchange_value(self, code):
        url = 'https://api.apilayer.com/exchangerates_data/latest?base=USD&symbols={}'.format(code)
        return json.loads(requests.get(url, headers=self.HEADER).text)
