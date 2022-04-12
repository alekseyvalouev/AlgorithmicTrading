import pandas_datareader as pdr
import datetime 
import pandas as pd
import matplotlib.pyplot as plt
import math

class StockFetcher:
    def __init__(self):
        self.ticker = None
        self.df = None

    def fetch(self, ticker, time_start, time_end):
        self.df = pdr.get_data_yahoo(ticker, 
                          start=time_start, 
                          end=time_end)
        self.ticker = ticker

    def format_csv(self):
        self.df.to_csv('data/%s_%s_%s.csv' % (self.ticker, str(self.time_start), str(self.time_end)))

    def read_csv(self, filename):
        self.df = pd.read_csv('data/%s' % filename)

    def plot_variable(self, variable):
        self.df[variable].plot(grid=True)
        plt.show()

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



if (__name__ == "__main__"):
    myStockFetcher = StockFetcher()
    myStockFetcher.fetch('AAPL', datetime.datetime(2006, 10, 1), datetime.datetime(2012, 1, 1))
    myStockFetcher.calc_rolling_volatility(50)
    myStockFetcher.show_rolling_volatility()
        