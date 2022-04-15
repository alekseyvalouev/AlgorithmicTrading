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
        self.figure, self.axis = plt.subplots(2, 2)

        if (ticker != None):
            self.fetch(ticker, start, end)
            self.calculate_percent_change()
            self.calc_rolling_volatility(50)

    def fetch(self, ticker, time_start, time_end):
        self.df = yf.download(ticker, time_start, time_end)
        self.ticker = ticker
        self.index = yf.download('^IXIC', time_start, time_end)
        self.axis[1, 1].plot(self.index['Adj Close'])

    def format_csv(self):
        self.df.to_csv('data/%s_%s_%s.csv' % (self.ticker, str(self.time_start), str(self.time_end)))

    def read_csv(self, filename):
        self.df = pd.read_csv('data/%s' % filename)

    def plot_variable(self, variable):
        self.df[variable].plot(grid=True, legend=True, ax=self.axis[1, 0])

    def calculate_percent_change(self):
        self.df['Shifted'] = self.df['Adj Close'].shift(-1)
        self.df['Pct. Change'] = self.df['Shifted']/self.df['Adj Close']-1

    def show_returns(self):
        self.df['Pct. Change'].hist(bins=50)
        plt.title('Returns for %s' % self.ticker)

    def calc_rolling_volatility(self, window):
        self.calculate_percent_change()
        self.df['Rolling Volatility'] = self.df['Pct. Change'].rolling(window).std() * math.sqrt(window)

    def show_rolling_volatility(self):
        self.df['Rolling Volatility'].plot()
        plt.title('Volatility for %s' % self.ticker)

    def apply_MA(self, periods):
        self.df = MA_Strategy(periods).modify_dataframe(self.df)

    def plot_MA(self, periods):
        for period in periods:
            self.plot_variable('MA %s' % str(period))

    def MA_Signals(self, p1, p2, p3):
        self.signals = pd.DataFrame(index=self.df.index)
        # copy moving averages from main dataframe
        self.signals['MA %i' % p1] = self.df['MA %i' % p1]
        self.signals['MA %i' % p2] = self.df['MA %i' % p2]
        self.signals['MA %i' % p3] = self.df['MA %i' % p3]
        # define temporary signal columns
        self.signals['signal_point_one'] = 0.0
        self.signals['signal_point_two'] = 0.0
        # target price (exit)
        self.signals['target'] = np.NaN
        # first point in fibonacci sequence
        self.signals['p1_numerical'] = np.NaN
        # second point in fibonacci sequence
        self.signals['p2_numerical'] = np.NaN
        # find signals
        self.signals['signal_point_one'][p1:] = np.where(self.signals['MA %i' % p2][p1:] > self.signals['MA %i' % p1][p1:], 1.0, 0.0)  
        self.signals['signal_point_two'][p1:] = np.where(self.signals['MA %i' % p3][p1:] > self.signals['MA %i' % p2][p1:], 1.0, 0.0)  
        # clean signal columns
        self.signals['first_points'] = self.signals['signal_point_one'].diff()
        self.signals['second_points'] = self.signals['signal_point_two'].diff()
        # 30 day rolling average
        self.signals['30_rolling'] = self.df['Adj Close'].rolling(30).mean()
        # create first two points
        self.signals['p1_numerical'][:] = np.where(self.signals['first_points'][:] > 0, self.signals['30_rolling'], 0.0)
        self.signals['p2_numerical'][:] = np.where(self.signals['second_points'][:] > 0, self.signals['30_rolling'], 0.0)
        # create temporary running first point array
        self.signals['filled_p1'] = self.signals['p1_numerical'].replace(to_replace=0, method='ffill')
        # create target prices
        self.signals['target'] = np.where(self.signals['p2_numerical'] > 0, self.signals['filled_p1'] + 1.618*(self.signals['filled_p1']-self.signals['p2_numerical']), 0)
        self.signals['target'] = self.signals['target'].replace(to_replace=0, method='ffill')
        # now create dummy variable to track when close price is > target price
        self.signals['positions_sell'] = np.where(self.signals['target'] < self.df['Adj Close'], -1.0, 0.0)
        self.signals['positions_sell'] = self.signals['positions_sell'].diff()
        self.signals['positions_buy'] = np.where(self.signals['second_points'] > 0, 1.0, 0.0)
        self.signals['positions_buy'] = self.signals['positions_buy'].diff()
        # fill final positions column with positions from both buy and sell columns
        self.signals['signal'] = self.signals['positions_sell']
        self.signals['signal'] = np.where(self.signals['positions_buy'] > 0, 1.0, self.signals['signal'])

    def plot_fibonacci_extensions(self):
        self.axis[1, 0].plot(self.signals.loc[self.signals['positions_buy'] > 0].index, 
                self.df['Adj Close'][self.signals['positions_buy'] > 0],
                '^', markersize=10, color='g')

        self.axis[1, 0].plot(self.signals.loc[self.signals['positions_sell'] < 0].index, 
                self.df['Adj Close'][self.signals['positions_sell'] < 0],
                'v', markersize=10, color='r')

        self.axis[1, 0].plot(self.signals['target'], '--')

    def back_test(self):
        initial_capital= float(100000.0)

        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)

        positions[self.ticker] = 100*self.signals['signal'].cumsum()

        self.end_holdings = positions[self.ticker][-1]   
        
        self.portfolio = positions.multiply(self.df['Adj Close'], axis=0)

        pos_diff = positions.diff()

        self.portfolio['holdings'] = (positions.multiply(self.df['Adj Close'], axis=0)).sum(axis=1)

        self.portfolio['cash'] = initial_capital - (pos_diff.multiply(self.df['Adj Close'], axis=0)).sum(axis=1).cumsum()   

        self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']

        self.portfolio['returns'] = self.portfolio['total'].pct_change()

    def plot_total(self):
        self.portfolio['total'].plot(lw=2., ax=self.axis[0, 0], grid=True)

    def plot_holding(self):
        self.axis[0, 1].plot(self.end_holdings*self.df['Adj Close'])

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
    myStockFetcher = StockFetcher('AAPL', '2019-1-1', '2022-4-1')
    myStockFetcher.calculate_percent_change()
    myStockFetcher.apply_MA([10, 40, 100])
    myStockFetcher.MA_Signals(10, 40, 100)
    myStockFetcher.plot_MA([10, 40, 100])
    myStockFetcher.plot_variable('Adj Close')
    myStockFetcher.plot_fibonacci_extensions()
    myStockFetcher.back_test()
    myStockFetcher.plot_total()
    myStockFetcher.plot_holding()
    plt.show()
    
        