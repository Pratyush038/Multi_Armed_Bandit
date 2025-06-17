# Thompson Sampling Stock Trader

**Optimal Stock Trading Strategy Using Thompson Sampling in the Context of Multi-Armed Bandits**

## Overview

This project implements a stock trading strategy using the Thompson Sampling algorithm within a Multi-Armed Bandit (MAB) framework. It simulates decision-making to select optimal stocks over time, balancing exploration and exploitation, with the goal of maximizing portfolio returns.

## Features

- Applies the Thompson Sampling algorithm to historical stock data
- Simulates portfolio performance over time
- Compares different stock groups (e.g., large-cap vs. top-performing mid/small-cap)
- Provides metrics such as total return and Sharpe ratio
- Interactive visualization and control through a Streamlit interface

## Project Structure

- `app.py` – Main Streamlit app interface
- `thompson_trader.py` – Core logic for the Thompson Sampling simulation
- `requirements.txt` – List of Python dependencies
- `.gitignore` – Ensures large or sensitive files are not tracked

## Future Improvements

- Integrate real-time data for live simulations
- Add more bandit strategies for comparison (e.g., UCB, ε-Greedy)
- Extend to portfolio optimization with constraints
- Deploy online with persistent state saving
