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

# Sector classification for Indian stocks
sector_mapping = {
    # Banking & Financial Services
    'HDFCBANK.NS': 'Banking & Financial',
    'ICICIBANK.NS': 'Banking & Financial',
    'SBIN.NS': 'Banking & Financial',
    'KOTAKBANK.NS': 'Banking & Financial',
    'AXISBANK.NS': 'Banking & Financial',
    'BAJFINANCE.NS': 'Banking & Financial',
    'IFCI.NS': 'Banking & Financial',
    'IRFC.NS': 'Banking & Financial',
    'CDSL.NS': 'Banking & Financial',
    
    # Information Technology
    'TCS.NS': 'Information Technology',
    'INFY.NS': 'Information Technology',
    'KAYNES.NS': 'Information Technology',
    'POLICYBZR.NS': 'Information Technology',
    
    # Oil & Gas
    'RELIANCE.NS': 'Oil & Gas',
    'OIL.NS': 'Oil & Gas',
    
    # Consumer Goods
    'HINDUNILVR.NS': 'Consumer Goods',
    'ITC.NS': 'Consumer Goods',
    'ASIANPAINT.NS': 'Consumer Goods',
    'MARUTI.NS': 'Consumer Goods',
    'TRENT.NS': 'Consumer Goods',
    'BLUESTARCO.NS': 'Consumer Goods',
    'VOLTAS.NS': 'Consumer Goods',
    
    # Telecommunications
    'BHARTIARTL.NS': 'Telecommunications',
    
    # Engineering & Construction
    'LT.NS': 'Engineering & Construction',
    'COCHINSHIP.NS': 'Engineering & Construction',
    'CUMMINSIND.NS': 'Engineering & Construction',
    
    # Power & Energy
    'SUZLON.NS': 'Power & Energy',
    'ADANIGREEN.NS': 'Power & Energy',
    
    # Metals & Mining
    'JWL.NS': 'Metals & Mining',
    
    # Auto Components
    'MOTHERSON.NS': 'Auto Components'
}

def get_sector_allocation(selections, symbols):
    """Calculate sector-wise allocation from stock selections"""
    sector_counts = {}
    total_selections = len(selections)
    
    for selection in selections:
        if selection in sector_mapping:
            sector = sector_mapping[selection]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    # Convert to percentages
    sector_allocation = {sector: (count / total_selections) * 100 
                        for sector, count in sector_counts.items()}
    
    return sector_allocation

def get_portfolio_sectors(symbols):
    """Get sector breakdown for a given portfolio"""
    sector_counts = {}
    for symbol in symbols:
        if symbol in sector_mapping:
            sector = sector_mapping[symbol]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    # Convert to percentages
    total_stocks = len(symbols)
    sector_breakdown = {sector: (count / total_stocks) * 100 
                       for sector, count in sector_counts.items()}
    
    return sector_breakdown

def calculate_buy_and_hold_performance(symbols, data, initial_investment=100000):
    """Calculate buy-and-hold strategy performance"""
    if len(symbols) == 0:
        return [], 0, 0
    
    # Equal weight allocation
    weights = np.ones(len(symbols)) / len(symbols)
    
    # Calculate portfolio returns
    returns_data = data[symbols].pct_change().dropna()
    portfolio_returns = (returns_data * weights).sum(axis=1)
    
    # Calculate cumulative portfolio value
    portfolio_values = [initial_investment]
    for ret in portfolio_returns:
        portfolio_values.append(portfolio_values[-1] * (1 + ret))
    
    # Calculate metrics
    total_return = (portfolio_values[-1] / initial_investment - 1) * 100
    daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
    
    return portfolio_values, total_return, sharpe_ratio

def calculate_random_selection_performance(symbols, data, initial_investment=100000, seed=None):
    """Calculate random selection strategy performance"""
    if len(symbols) == 0:
        return [], 0, 0
    
    if seed is not None:
        np.random.seed(seed)
    
    returns_data = data[symbols].pct_change().dropna()
    portfolio_values = [initial_investment]
    
    for date in returns_data.index:
        # Randomly select one stock each day
        selected_stock = np.random.choice(symbols)
        daily_return = returns_data.loc[date, selected_stock]
        portfolio_values.append(portfolio_values[-1] * (1 + daily_return))
    
    # Calculate metrics
    total_return = (portfolio_values[-1] / initial_investment - 1) * 100
    daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
    
    return portfolio_values, total_return, sharpe_ratio

def calculate_risk_metrics(portfolio_values):
    """Calculate various risk metrics for a portfolio"""
    if len(portfolio_values) < 2:
        return {
            'max_drawdown': 0,
            'volatility': 0,
            'var_95': 0,
            'cvar_95': 0,
            'calmar_ratio': 0
        }
    
    # Calculate daily returns
    daily_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    
    # Maximum Drawdown
    peak = portfolio_values[0]
    max_drawdown = 0
    for value in portfolio_values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        max_drawdown = max(max_drawdown, drawdown)
    
    # Volatility (annualized)
    volatility = np.std(daily_returns) * np.sqrt(252)
    
    # Value at Risk (95% confidence)
    var_95 = np.percentile(daily_returns, 5)
    
    # Conditional Value at Risk (95% confidence)
    cvar_95 = np.mean(daily_returns[daily_returns <= var_95])
    
    # Calmar Ratio (annualized return / max drawdown)
    total_return = (portfolio_values[-1] / portfolio_values[0] - 1)
    annualized_return = (1 + total_return) ** (252 / len(daily_returns)) - 1
    calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
    
    return {
        'max_drawdown': max_drawdown * 100,  # Convert to percentage
        'volatility': volatility * 100,      # Convert to percentage
        'var_95': var_95 * 100,              # Convert to percentage
        'cvar_95': cvar_95 * 100,            # Convert to percentage
        'calmar_ratio': calmar_ratio
    }

def calculate_portfolio_risk_metrics(portfolio_values_list):
    """Calculate risk metrics for multiple portfolio simulations"""
    all_metrics = []
    
    for portfolio_values in portfolio_values_list:
        metrics = calculate_risk_metrics(portfolio_values)
        all_metrics.append(metrics)
    
    # Calculate mean and std of risk metrics
    mean_metrics = {}
    std_metrics = {}
    
    for key in all_metrics[0].keys():
        values = [m[key] for m in all_metrics]
        mean_metrics[key] = np.mean(values)
        std_metrics[key] = np.std(values)
    
    return mean_metrics, std_metrics
