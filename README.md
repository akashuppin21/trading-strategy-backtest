# Algorithmic Trading Strategy - Contrarian Intraday System

## 🎯 Unique Approach

**Using Daily OHLC Data for Intraday Trading with Contrarian Logic**

This strategy identifies **bullish signals** (support bounce, resistance rejection) but takes **opposite positions** for intraday profits:
- When bullish signals trigger → Market rallies ~2% → Traders book profits → **I SHORT the reversal**
- When bearish signals trigger → Market dips → Value buyers enter → **I LONG the bounce**

## 📊 Backtest Results (2022-2025)

| Metric | Value |
|--------|-------|
| **CAGR** | 213.88% |
| **Sharpe Ratio** | 9.49 |
| **Win Rate** | 75.60% |
| **Max Drawdown** | -4.74% |
| **Total Return** | 3,113% |
| **Capital Growth** | ₹100 → ₹3,213 |

## 🔧 Technical Details

- **Language**: Python
- **Data Source**: NSE Daily OHLC
- **Strategy**: 2 combined (1 Long + 1 Short)
- **Trades per Day**: 20 (10 per strategy)
- **Backtesting Period**: June 2022 - Dec 2025

## 💡 Key Features

- Automated stock screening across entire market
- Signal strength ranking for trade selection
- Transaction cost & slippage included (0.25%)
- Risk management with max trades per day
- Daily portfolio rebalancing

## 🚀 Technologies

- Pandas & NumPy for data analysis
- Technical analysis using OHLC patterns
- Backtesting framework built from scratch

## 📈 Performance by Year

| Year | Return | Trading Days |
|------|--------|--------------|
| 2022 | 2.86% | 10 |
| 2023 | 165.38% | 245 |
| 2024 | 303.51% | 246 |
| 2025 | 191.72% | 249 |

## ⚠️ Disclaimer

This is for educational purposes only. Past performance doesn't guarantee future results.

## 📫 Contact

[Your Email] | [LinkedIn Profile]
