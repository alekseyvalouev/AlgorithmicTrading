import yfinance as yf
import pandas_datareader as pdr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

class StockFetcher:
    def __init__(self, ticker=None, start=None, end=None):
        self.ticker = None
        self.df = None

        if (ticker != None):
            self.fetch(ticker, start, end)
            self.calculate_percent_change()
            self.calc_rolling_volatility(50)

    def fetch(self, ticker, time_start, time_end):
        self.df = yf.download(ticker, time_start, time_end)
        self.ticker = ticker

    def format_csv(self):
        self.df.to_csv('data/%s_%s_%s.csv' % (self.ticker, str(self.time_start), str(self.time_end)))

    def read_csv(self, filename):
        self.df = pd.read_csv('data/%s' % filename)

    def plot_variable(self, variable):
        self.df[variable].plot(grid=True, legend=True)

    def calculate_percent_change(self):
        self.df['Shifted'] = self.df['Adj Close'].shift(-1)
        self.df['Pct. Change'] = self.df['Shifted']/self.df['Adj Close']-1

    def show_returns(self):
        self.df['Pct. Change'].hist(bins=50)
        plt.title('Returns for %s' % self.ticker)
        plt.show()

    def calc_rolling_volatility(self, window):
        self.calculate_percent_change()
        self.df['Rolling Volatility'] = self.df['Pct. Change'].rolling(window).std() * math.sqrt(window)

    def show_rolling_volatility(self):
        self.df['Rolling Volatility'].plot()
        plt.title('Volatility for %s' % self.ticker)
        plt.show()

    def apply_MA(self, periods):
        self.df = MA_Strategy(periods).modify_dataframe(self.df)

    def plot_MA(self, periods):
        for period in periods:
            self.plot_variable('MA %s' % str(period))

    def MA_Signals(self, p1, p2):
        self.signals = pd.DataFrame(index=self.df.index)
        self.signals['MA %i' % p1] = self.df['MA %i' % p1]
        self.signals['MA %i' % p2] = self.df['MA %i' % p2]
        self.signals['signal'] = 0.0
        self.signals['signal'][p1:] = np.where(self.signals['MA %i' % p1][p1:] > self.signals['MA %i' % p2][p1:], 1.0, 0.0)  
        self.signals['positions'] = self.signals['signal'].diff()

    def plot_MA_signals(self, p1, p2):
        plt.plot(self.signals.loc[self.signals.positions == 1.0].index, 
                self.signals['MA %i' % p1][self.signals.positions == 1.0],
                '^', markersize=10, color='m')
                
        plt.plot(self.signals.loc[self.signals.positions == -1.0].index, 
                self.signals['MA %i' % p2][self.signals.positions == -1.0],
                'v', markersize=10, color='k')

    def get_df(self):
        return self.df

class MA_Strategy:
    def __init__(self, periods):
        self.periods = periods

    def modify_dataframe(self, df):
        for period in self.periods:
            df['MA %s' % str(period)] = df['Adj Close'].rolling(period).mean()
        return df

if (__name__ == "__main__"):
    myStockFetcher = StockFetcher('AAPL', '2020-9-1', '2022-1-1')
    myStockFetcher.calculate_percent_change()
    myStockFetcher.plot_variable('Adj Close')
    myStockFetcher.apply_MA([10, 40, 100])
    myStockFetcher.plot_MA([10, 40, 100])
    myStockFetcher.MA_Signals(10, 40)
    myStockFetcher.plot_MA_signals(10, 40)
    plt.show()
    
        