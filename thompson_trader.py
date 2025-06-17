import numpy as np
import pandas as pd
import yfinance as yf

class ThompsonSamplingStockTrader:
    def __init__(self, symbols, stock_data, stats, initial_investment=100000):
        self.symbols = symbols
        self.stock_data = stock_data
        self.stats = stats
        self.initial_investment = initial_investment
        self.reset()

    def reset(self):
        self.posterior_means = {}
        self.posterior_vars = {}
        self.daily_selections = []
        self.daily_rewards = []
        self.portfolio_values = [self.initial_investment]
        self.investment_value = self.initial_investment

    def calculate_returns(self):
        self.returns_data = self.stock_data.pct_change().dropna()
        return self.returns_data

    def initialize_priors(self):
        for symbol in self.symbols:
            mu = self.stats.loc[symbol, 'mean']
            var = self.stats.loc[symbol, 'std'] ** 2
            self.posterior_means[symbol] = mu
            self.posterior_vars[symbol] = var * 1.5

    def select_stock(self):
        samples = {
            symbol: np.random.normal(self.posterior_means[symbol], np.sqrt(self.posterior_vars[symbol]))
            for symbol in self.symbols
        }
        return max(samples, key=samples.get)

    def update_posterior(self, symbol, reward):
        prior_mean = self.posterior_means[symbol]
        prior_var = self.posterior_vars[symbol]
        obs_var = 0.0001
        new_var = 1 / (1 / prior_var + 1 / obs_var)
        new_mean = new_var * (prior_mean / prior_var + reward / obs_var)
        self.posterior_means[symbol] = new_mean
        self.posterior_vars[symbol] = new_var

    def run(self):
        self.calculate_returns()
        self.initialize_priors()
        for date in self.returns_data.index:
            selected = self.select_stock()
            reward = self.returns_data.loc[date, selected]
            self.update_posterior(selected, reward)
            self.investment_value *= (1 + reward)
            self.portfolio_values.append(self.investment_value)
            self.daily_selections.append(selected)
            self.daily_rewards.append(reward)
        return self.portfolio_values


def download_and_prepare_data(symbols, start_date, end_date):
    data = yf.download(symbols, start=start_date, end=end_date, progress=False, group_by='ticker')

    if isinstance(data.columns, pd.MultiIndex):
        close_data = pd.concat([data[ticker]['Close'].rename(ticker)
                                for ticker in data.columns.levels[0]
                                if 'Close' in data[ticker]], axis=1)
    else:
        close_data = data if 'Close' in data else pd.DataFrame()

    close_data = close_data.ffill().dropna(axis=1, how='all')
    valid_symbols = list(close_data.columns)

    returns_data = close_data.pct_change().dropna()
    stats = returns_data.agg(['mean', 'std'], axis=0).T
    stats['sharpe'] = stats['mean'] / stats['std']
    return close_data[valid_symbols], stats.loc[valid_symbols]


def run_multiple_simulations(trader_class, portfolio, data, stats, num_simulations=100, seed=None):
    # Filter portfolio to symbols available in stats
    valid_symbols = [s for s in portfolio if s in stats.index]

    all_portfolios = []
    all_selections = []

    for i in range(num_simulations):
        if seed is not None:
            np.random.seed(seed + i)

        trader = trader_class(valid_symbols, data, stats)
        trader.run()
        all_portfolios.append(trader.portfolio_values)
        all_selections.extend(trader.daily_selections)

    all_portfolios = np.array(all_portfolios)
    avg_portfolio = np.mean(all_portfolios, axis=0)
    std_portfolio = np.std(all_portfolios, axis=0)

    total_returns = (all_portfolios[:, -1] / trader.initial_investment - 1) * 100
    sharpe_ratios = []
    for i in range(num_simulations):
        daily_returns = np.diff(all_portfolios[i]) / all_portfolios[i][:-1]
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
        sharpe_ratios.append(sharpe)

    mean_return = np.mean(total_returns)
    std_return = np.std(total_returns)
    mean_sharpe = np.mean(sharpe_ratios)
    std_sharpe = np.std(sharpe_ratios)

    return avg_portfolio, std_portfolio, mean_return, std_return, mean_sharpe, std_sharpe, all_selections



# Define portfolios here so they can be imported directly
portfolio1 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'SBIN.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS',
    'KOTAKBANK.NS', 'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS',
    'MARUTI.NS'
]

portfolio2 = [
    'COCHINSHIP.NS', 'IRFC.NS', 'JWL.NS', 'SUZLON.NS', 'KAYNES.NS',
    'ADANIGREEN.NS', 'IFCI.NS', 'BLUESTARCO.NS', 'CDSL.NS', 'OIL.NS',
    'TRENT.NS', 'POLICYBZR.NS', 'CUMMINSIND.NS', 'MOTHERSON.NS',
    'VOLTAS.NS'
]
