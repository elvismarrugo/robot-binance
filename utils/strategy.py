import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta
from talib import EMA, RSI, MACD


class Indicators:

    def __init__(self, data):
        self.data = data
        self.close = data.get('Close')
        self.low = data.get('Low')
        self.high = data.get('High')

    def ema(self, timeperiod: int):
        return EMA(
            self.close,
            timeperiod=timeperiod
        ).iloc[-1]

    def rsi(self, timeperiod: int):
        return RSI(
            self.close,
            timeperiod=timeperiod
        ).iloc[-1]

    def macd(self, fastperiod, slowperiod, signalperiod):
        _macd, macdsignal, _ = MACD(
            self.close,
            fastperiod,
            slowperiod,
            signalperiod
        )
        return _macd.iloc[-1], macdsignal.iloc[-1]

    def adx(self):
        return ta.adx(self.high, self.low, self.close)['ADX_14']  # .iloc[-1]

    # def macd_lazybear(self):
    #     squeeze = ta.squeeze(self.high, self.low, self.close, lazybear=True)
    #     squeeze.columns = ['SQZ', 'SQZ_ON', 'SQZ_OFF', 'SQZ_NO']
    #     return squeeze['SQZ']  #.iloc[-1]

    def lazybear(self):
        length = 20
        mult = 2.0
        length_KC = 20
        mult_KC = 1.5

        # Calculate Bollinger Bands BB
        m_avg = self.close.rolling(window=length).mean()
        m_std = self.close.rolling(window=length).std(ddof=0) * mult
        self.data['upper_BB'] = m_avg + m_std
        self.data['lower_BB'] = m_avg - m_std

        # Calculate True Range
        self.data['tr0'] = abs(self.high - self.low)
        self.data['tr1'] = abs(self.high - self.close.shift())
        self.data['tr2'] = abs(self.low - self.close.shift())
        self.data['tr'] = self.data[['tr0', 'tr1', 'tr2']].max(axis=1)

        # Calculate Keltner Channel KC
        range_ma = self.data['tr'].rolling(window=length_KC).mean()
        self.data['upper_KC'] = m_avg + range_ma * mult_KC
        self.data['lower_KC'] = m_avg - range_ma * mult_KC

        #
        highest = self.high.rolling(window=length_KC).max()
        lowest = self.low.rolling(window=length_KC).min()
        m1 = (highest + lowest) / 2
        self.data['SQZ'] = self.close - (m1 + m_avg) / 2
        y = np.array(range(0, length_KC))
        def func(x): return np.polyfit(y, x, 1)[
            0] * (length_KC - 1) + np.polyfit(y, x, 1)[1]
        self.data['SQZ'] = self.data['SQZ'].rolling(
            window=length_KC).apply(func, raw=True)

        return self.data

    def grahp_lazybear(self):
        df = self.lazybear()

        fig = plt.figure()
        df['SQZ'].plot(color='blue', label="Lazybear")
        plt.axhline(y=0, color='r', linestyle='-')
        plt.legend(loc='best')

        plt.grid(linestyle='-.')
        plt.show()
        plt.close(fig)

    def grahp_adx(self):
        adx = self.adx()

        fig = plt.figure()
        adx.plot(color='blue', label="ADX")
        plt.axhline(y=23, color='r', linestyle='-')
        plt.legend(loc='best')

        plt.grid(linestyle='-.')
        plt.show()
        plt.close(fig)

    def trading_latino(self):
        # self.macd_lazybear()
        return self.ema(10), self.ema(55), self.adx(),  self.lazybear()
