# from pprint import pprint
from time import sleep
from urllib import response

from binance.spot import Spot
import pandas as pd

import config
from utils.strategy import Indicators


class RobotBinance:
    #
    # Bot para Binance que permite automatizar las compras y ventas en el mercado Spot
    #

    __api_key = config.API_KEY
    __api_secret = config.API_SECRET
    binance_client = Spot(key=__api_key, secret=__api_secret)

    def __init__(self, pair: str, temporality: str):
        self.pair = pair.upper()
        self.temporality = temporality
        self.symbol = self.pair.removesuffix("USDT")

    def _request(self, endpoint: str, parameters: dict = None):
        while True:
            try:
                response = getattr(self.binance_client, endpoint)
                return response() if parameters is None else response(**parameters)
            except:
                print(
                    f'El endpoint { endpoint } ha fallado.\nParametros: {parameters}\n\n')
                sleep(2)

    def binance_account(self) -> dict:
        return self._request('account')

    def cryptocurrencies(self) -> list[dict]:
        return [crypto for crypto in self.binance_account().get('balances') if float(crypto.get('free')) > 0]

    def symbol_price(self, pair: str = None):
        symbol = self.pair if pair is None else pair
        return float(self._request('ticker_price', {'symbol': symbol.upper()}).get('price'))

    def candlestick(self, limit: int = 200) -> pd.DataFrame:
        params = {
            'symbol': self.pair,
            'interval': self.temporality,
            'limit': limit
        }

        candle = pd.DataFrame(self._request(
            'klines',
            params
        ),
            columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                     'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                     'Taker buy quote asset volume', 'Ignore'
                     ],
            dtype=float)

        return candle[['Open time', 'Close time', 'Open', 'High', 'Low', 'Close', 'Volume']]


if __name__ == '__main__':
    bot = RobotBinance("SOLUSDT", "4h")
    ema10, ema55, adx, squeeze = Indicators(bot.candlestick()).trading_latino()
    print(ema10, ema55, adx.iloc[-1], squeeze['SQZ'].iloc[-1])
    Indicators(bot.candlestick()).grahp_lazybear()
    Indicators(bot.candlestick()).grahp_adx()

    # pprint(Indicators(bot.candlestick()).lazybear())
    # actual_price = bot.symbol_price()
    # if actual_price > ema10 and actual_price > ema55 and adx.iloc[-1] > adx.iloc[-2] and squeeze.iloc[-1] > squeeze.iloc[-2]:
    # pprint('condiciones para el alza')

# bot = RobotBinance("SOLUSDT", "4h")
# pprint(bot.binance_client().klines("BTCUSDT", "1h"))
# pprint(bot.binance_account().get('balances').get('free'))
# pprint(bot.cryptocurrencies())
# pprint(bot.symbol_price("BTCUSDT"))
# pprint(bot.candlestick())
# pprint(bot.symbol_price('dotusdt'))
# pprint(bot.binance_client.accountt())
# pprint(bot.candlestick())
