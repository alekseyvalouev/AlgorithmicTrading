import yfinance as yf
import pandas_datareader as pdr
import datetime 
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
        self.df[variable].plot(grid=True, label=variable)

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

    def apply_MA(self):
        self.df = MA_Strategy(40, 100).modify_dataframe(self.df)

    def get_df(self):
        return self.df

class MA_Strategy:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def modify_dataframe(self, df):
        df['MA %s' % str(self.p1)] = df['Adj Close'].rolling(self.p1).mean()
        df['MA %s' % str(self.p2)] = df['Adj Close'].rolling(self.p2).mean()
        return df



if (__name__ == "__main__"):
    myStockFetcher = StockFetcher('AAPL', '2012-10-1', '2022-1-1')
    myStockFetcher.calculate_percent_change()
    myStockFetcher.plot_variable('Adj Close')
    myStockFetcher.apply_MA()
    myStockFetcher.plot_variable('MA 40')
    myStockFetcher.plot_variable('MA 100')
    plt.show()
    
        