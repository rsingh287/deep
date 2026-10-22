"""
================================================================================
ANTIGRAVITY AI WORKSTATION: INSTITUTIONAL FUTURES TRADING & RISK ENGINE (CME/NYMEX)
================================================================================
Specialized Futures Trading Architecture for Global Commodity & Equity Index Futures:
- E-mini S&P 500 (ES=F) & E-mini Nasdaq 100 (NQ=F)
- Gold Futures (GC=F) & Silver Futures (SI=F)
- Crude Oil (CL=F) & Natural Gas (NG=F) & Copper (HG=F)
Computes CME Contract Specs, Tick Values, Point Multipliers, Initial Margin, and Rollover.
"""

# CME / NYMEX / COMEX Official Futures Contract Specifications
FUTURES_CONTRACT_SPECS = {
    "ES=F": {
        "name": "E-mini S&P 500 Futures",
        "exchange": "CME",
        "tick_size": 0.25,
        "tick_value_usd": 12.50,  # $50 per full index point
        "point_multiplier": 50.0,
        "initial_margin_usd": 12980.0,  # Standard CME Initial Margin per contract
        "maintenance_margin_usd": 11800.0,
        "trading_hours": "23/5 Electronic CME Globex",
    },
    "NQ=F": {
        "name": "E-mini Nasdaq 100 Futures",
        "exchange": "CME",
        "tick_size": 0.25,
        "tick_value_usd": 5.00,  # $20 per full index point
        "point_multiplier": 20.0,
        "initial_margin_usd": 18700.0,
        "maintenance_margin_usd": 17000.0,
        "trading_hours": "23/5 Electronic CME Globex",
    },
    "GC=F": {
        "name": "Gold Futures (100 oz)",
        "exchange": "COMEX",
        "tick_size": 0.10,
        "tick_value_usd": 10.00,  # $100 per $1.00 move
        "point_multiplier": 100.0,
        "initial_margin_usd": 11000.0,
        "maintenance_margin_usd": 10000.0,
        "trading_hours": "23/5 Electronic NYMEX Globex",
    },
    "CL=F": {
        "name": "Crude Oil WTI Futures (1,000 bbl)",
        "exchange": "NYMEX",
        "tick_size": 0.01,
        "tick_value_usd": 10.00,  # $1,000 per $1.00 move
        "point_multiplier": 1000.0,
        "initial_margin_usd": 6800.0,
        "maintenance_margin_usd": 6180.0,
        "trading_hours": "23/5 Electronic NYMEX Globex",
    },
    "SI=F": {
        "name": "Silver Futures (5,000 oz)",
        "exchange": "COMEX",
        "tick_size": 0.005,
        "tick_value_usd": 25.00,  # $5,000 per $1.00 move
        "point_multiplier": 5000.0,
        "initial_margin_usd": 9500.0,
        "maintenance_margin_usd": 8636.0,
        "trading_hours": "23/5 Electronic COMEX",
    },
    "NG=F": {
        "name": "Natural Gas Futures (10,000 MMBtu)",
        "exchange": "NYMEX",
        "tick_size": 0.001,
        "tick_value_usd": 10.00,  # $10,000 per $1.00 move
        "point_multiplier": 10000.0,
        "initial_margin_usd": 5500.0,
        "maintenance_margin_usd": 5000.0,
        "trading_hours": "23/5 Electronic NYMEX Globex",
    },
    "HG=F": {
        "name": "Copper Futures (25,000 lbs)",
        "exchange": "COMEX",
        "tick_size": 0.0005,
        "tick_value_usd": 12.50,  # $25,000 per $1.00 move
        "point_multiplier": 25000.0,
        "initial_margin_usd": 6200.0,
        "maintenance_margin_usd": 5600.0,
        "trading_hours": "23/5 Electronic COMEX",
    },
}


def calculate_futures_position_risk(
    symbol,
    entry_price,
    stop_loss_price,
    take_profit_price,
    account_equity=100000.0,
    max_risk_pct=1.5,
):
    """
    Calculates exact Contract Sizing, Dollar Risk per Contract, Margin Usage, and PnL Targets.
    """
    spec = FUTURES_CONTRACT_SPECS.get(symbol)
    if not spec:
        return {"error": f"Symbol {symbol} not in Futures contract directory"}

    point_mult = spec["point_multiplier"]
    spec["tick_value_usd"]
    tick_sz = spec["tick_size"]
    init_margin = spec["initial_margin_usd"]

    # Risk per single contract in dollars
    point_distance_sl = abs(entry_price - stop_loss_price)
    point_distance_tp = abs(take_profit_price - entry_price)

    dollar_risk_per_contract = point_distance_sl * point_mult
    dollar_gain_per_contract = point_distance_tp * point_mult

    ticks_to_sl = point_distance_sl / tick_sz
    ticks_to_tp = point_distance_tp / tick_sz

    # Maximum allowed portfolio dollar risk (e.g. 1.5% of $100k = $1,500)
    max_dollar_risk = account_equity * (max_risk_pct / 100.0)

    # Optimal Contract Count based on Risk Limit & Available Margin
    contracts_by_risk = int(max_dollar_risk / (dollar_risk_per_contract + 1e-6))
    max_contracts_by_margin = int(
        (account_equity * 0.40) / init_margin
    )  # Max 40% margin utilization

    recommended_contracts = max(1, min(contracts_by_risk, max_contracts_by_margin))
    total_margin_req = recommended_contracts * init_margin
    total_dollar_risk = recommended_contracts * dollar_risk_per_contract
    total_dollar_target = recommended_contracts * dollar_gain_per_contract

    r_multiple = total_dollar_target / (total_dollar_risk + 1e-6)

    return {
        "symbol": symbol,
        "contract_name": spec["name"],
        "exchange": spec["exchange"],
        "entry_price": entry_price,
        "stop_loss_price": stop_loss_price,
        "take_profit_price": take_profit_price,
        "ticks_to_sl": int(ticks_to_sl),
        "ticks_to_tp": int(ticks_to_tp),
        "dollar_risk_per_contract": round(dollar_risk_per_contract, 2),
        "dollar_reward_per_contract": round(dollar_gain_per_contract, 2),
        "recommended_contracts": recommended_contracts,
        "total_margin_required_usd": round(total_margin_req, 2),
        "total_portfolio_risk_usd": round(total_dollar_risk, 2),
        "total_portfolio_target_usd": round(total_dollar_target, 2),
        "reward_to_risk_ratio": round(r_multiple, 2),
    }


def format_futures_markdown_report(prediction_results, account_equity=100000.0):
    """Renders Institutional CME Futures Contract Risk & Position Sizing Table."""
    md = []
    md.append("\n---")
    md.append("### 🏛️ INSTITUTIONAL CME / NYMEX FUTURES CONTRACT ENGINE")
    md.append(
        f"`Account Equity: ${account_equity:,.2f}` | `Risk Budget per Trade: 1.5% ($1,500)` | `Exchange Protocol: CME Globex Direct`\n"
    )

    md.append(
        "| Futures Ticker | Contract Name | Exchange | Rec Contracts | Initial Margin Req | Dollar Risk ($) | Target Reward ($) | R-Multiple |"
    )
    md.append("|---|---|---|---|---|---|---|---|")

    for r in prediction_results:
        sym = r["symbol"]
        if sym in FUTURES_CONTRACT_SPECS:
            f_risk = calculate_futures_position_risk(
                sym, r["price"], r["stop_loss"], r["take_profit"], account_equity
            )
            md.append(
                f"| **{sym}** | {f_risk['contract_name']} | {f_risk['exchange']} | "
                f"**{f_risk['recommended_contracts']} Contract(s)** | ${f_risk['total_margin_required_usd']:,.2f} | "
                f"${f_risk['total_portfolio_risk_usd']:,.2f} | **+${f_risk['total_portfolio_target_usd']:,.2f}** | "
                f"`{f_risk['reward_to_risk_ratio']} R` |"
            )

    return "\n".join(md)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    test_res = [
        {
            "symbol": "GC=F",
            "price": 4664.40,
            "stop_loss": 4559.99,
            "take_profit": 4838.42,
        },
        {"symbol": "CL=F", "price": 74.80, "stop_loss": 73.03, "take_profit": 77.74},
        {
            "symbol": "ES=F",
            "price": 5980.20,
            "stop_loss": 5849.86,
            "take_profit": 6197.44,
        },
        {
            "symbol": "NQ=F",
            "price": 21250.00,
            "stop_loss": 20736.17,
            "take_profit": 22106.38,
        },
    ]
    print(format_futures_markdown_report(test_res))
