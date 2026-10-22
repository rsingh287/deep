"""
Crypto & Stock Risk Metrics Engine
Provides live market data fetching, risk calculation (Sharpe, Max Drawdown),
and volatility analysis using Yahoo Finance.
"""

import json

import numpy as np
import yfinance as yf


def calculate_risk_metrics(ticker_symbol: str, period: str = "1y") -> str:
    """
    Fetches historical data for a ticker and calculates annualized return,
    volatility, Sharpe Ratio, and Maximum Drawdown.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)

        if df.empty:
            return json.dumps({"error": f"No data found for {ticker_symbol}"})

        # Calculate daily returns
        df["Daily_Return"] = df["Close"].pct_change()

        # Drop NaN
        returns = df["Daily_Return"].dropna()

        # Metrics
        trading_days = 252
        annualized_return = returns.mean() * trading_days
        annualized_volatility = returns.std() * np.sqrt(trading_days)

        # Assuming risk-free rate of 0 for simplicity
        sharpe_ratio = (
            annualized_return / annualized_volatility
            if annualized_volatility != 0
            else 0
        )

        # Max Drawdown
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()

        result = {
            "ticker": ticker_symbol,
            "period": period,
            "current_price": round(df["Close"].iloc[-1], 2),
            "annualized_return_percent": round(annualized_return * 100, 2),
            "annualized_volatility_percent": round(annualized_volatility * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown_percent": round(max_drawdown * 100, 2),
        }

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print(calculate_risk_metrics("BTC-USD", "1y"))
