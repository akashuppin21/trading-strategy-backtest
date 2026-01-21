# Algorithmic Trading Strategy - Contrarian Intraday System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Strategy Overview

### The Contrarian Approach

This is a **contrarian intraday trading system** that uses Daily OHLC data to identify reversal opportunities:

**Core Logic:**
- When **bullish signals** appear → Market rallies ~2% → Early traders book profits → **I SHORT the reversal**
- When **bearish signals** appear → Market dips → Value buyers enter → **I LONG the bounce**

**The Edge:** Most traders follow signals blindly. This strategy exploits the profit-booking behavior that follows every sharp move.

### How It Works in Real-Time

**Pre-Market (9:00 AM):**
- System scans all NSE stocks available for intraday trading on Zerodha
- Generates 20-50 potential signals using previous day's OHLC data

**Market Open (9:15 AM):**
- Strategy generates signals based on support/resistance levels
- Identifies stocks showing early momentum

**Entry Execution (9:17 AM onwards):**
- **For SHORT trades:** Monitor stocks where (Low - Open) > 0.3%
- **For LONG trades:** Monitor stocks where (Open - High) > 0.3%
- Place limit orders at entry levels:
  - SHORT: 2% above Open
  - LONG: 2% below Open

**Order Management:**
- Place ~12 orders to get 5 fills (execution rate ~40-50%)
- Use leverage or capital as per risk appetite
- All positions closed by 3:15 PM (intraday)

### Strategy Components

**S1_Resistance_Rejection (LONG):**
- Identifies when price touches resistance and gets rejected
- Enter LONG when market gaps down after rejection (oversold bounce)

**S1_Support_Bounce (SHORT):**
- Identifies when price touches support and bounces
- Enter SHORT when market gaps up after bounce (overbought reversal)

## 🛡️ Risk Management & Live Execution

### Real-Time Risk Controls

The strategy employs **4 critical monitoring systems** that run continuously during market hours to protect capital and optimize execution:

#### 1. Daily Loss Limit Monitor
**File:** `daily_loss_limit.py` *(Not in GitHub - Proprietary)*

**Function:** Real-time P&L tracking with circuit breaker
- Monitors aggregate daily P&L across all positions
- **Trigger:** If daily loss exceeds **2% of total capital**
- **Action:** Immediately liquidates ALL positions (both long and short)
- **Purpose:** Prevents catastrophic drawdown on volatile days

**Example:** With ₹10,00,000 capital, if loss reaches ₹20,000 → Auto-exit everything

#### 2. Long Trades Monitor
**File:** `long_trades_monitor.py` *(Not in GitHub - Proprietary)*

**Function:** Individual position risk management for long trades
- **Level 1 Alert:** If any long position moves **±4%**
  - Action: Close **50% of that position**
- **Level 2 Alert:** If any long position moves **±8%**
  - Action: Close **100% of that position**
- Protects against both adverse moves (stop-loss) and captures profits on winners

**Logic:** Partial exits at 4% allow the position to continue if momentum persists, while 8% is the hard exit

#### 3. Short Trades Monitor
**File:** `short_trades_monitor.py` *(Not in GitHub - Proprietary)*

**Function:** Individual position risk management for short trades
- **Level 1 Alert:** If any short position moves **±4%**
  - Action: Close **50% of that position**
- **Level 2 Alert:** If any short position moves **±8%**
  - Action: Close **100% of that position**
- Same logic as long trades but applied to short positions separately

**Note:** Separate files for long and short allow independent monitoring and quicker execution

#### 4. Order Fill Manager
**File:** `order_fill_manager.py` *(Not in GitHub - Proprietary)*

**Function:** Smart order cancellation to prevent over-exposure
- **Scenario:** System places ~20 orders (10 long + 10 short) at market open
- **Monitoring:** Continuously checks filled positions
- **Trigger:** Once **5 long positions** are filled
  - Action: **Cancel all remaining unfilled long orders**
- **Trigger:** Once **5 short positions** are filled
  - Action: **Cancel all remaining unfilled short orders**
- **Purpose:** Maintains exactly 5+5 position balance, prevents accidental over-trading

**Why This Matters:** Ensures consistent position sizing and prevents the system from entering 15-20 trades if market is highly volatile

### Why These Files Are Not on GitHub

These proprietary risk management systems represent **years of real-money trading experience** and contain:
- Zerodha API credentials and authentication logic
- Custom position tracking algorithms
- Real-time data processing techniques
- Execution optimization strategies
- Personal risk tolerance parameters

**Security & Competitive Advantage:** These systems are the operational backbone that makes the strategy viable in live markets. They're not shared publicly to:
1. Protect API security
2. Maintain competitive edge
3. Prevent misuse by inexperienced traders

### Live Execution Workflow

```
09:00 AM → Signal Generation
        ↓
09:15 AM → Market Opens
        ↓
09:17 AM → Place ~20 Limit Orders (10 Long + 10 Short)
        ↓
        ├→ Order Fill Manager: Monitors filled positions
        │  └→ Cancel excess orders once 5+5 filled
        ↓
        ├→ Long Trades Monitor: Checks each long position
        │  ├→ ±4% move? Exit 50%
        │  └→ ±8% move? Exit 100%
        ↓
        ├→ Short Trades Monitor: Checks each short position
        │  ├→ ±4% move? Exit 50%
        │  └→ ±8% move? Exit 100%
        ↓
        └→ Daily Loss Limit: Monitors total P&L
           └→ Loss > 2%? Liquidate everything
        ↓
03:15 PM → Auto-close all remaining positions
        ↓
03:30 PM → Generate daily report
```

### Risk Management Philosophy

**Layered Defense System:**
1. **Position Level:** Individual stock monitoring (±4%/±8% exits)
2. **Strategy Level:** Balanced 5+5 long/short exposure
3. **Portfolio Level:** 2% daily loss limit
4. **Time Level:** Intraday only (no overnight risk)

**Capital Preservation First:** The 2% daily loss limit ensures that even in the worst-case scenario, you can't lose more than 2% on any single day. Over 100 trading days, you'd need 50 consecutive max-loss days to blow up the account (statistically impossible with 63% win rate).

## 📊 Backtest Results (2018-2025)

### 7-Year Performance Summary

| Metric | Value |
|--------|-------|
| **Overall CAGR** | 140.17% |
| **Total Return** | 88,676% |
| **Sharpe Ratio** | 4.99 |
| **Win Rate** | 63.62% |
| **Max Drawdown** | -11.44% |
| **Capital Growth** | ₹100 → ₹88,777 |
| **Total Trading Days** | 1,916 |
| **Avg Daily Return** | 0.36% |

### Year-by-Year Performance

| Year | Return % | Trading Days | Avg Daily Return % | Capital Growth |
|------|----------|--------------|-------------------|----------------|
| 2018 | 103.69% | 186 | 0.39% | ₹100 → ₹204 |
| 2019 | 363.80% | 243 | 0.64% | ₹204 → ₹945 |
| 2020 | 282.33% | 251 | 0.55% | ₹945 → ₹3,612 |
| 2021 | 148.61% | 248 | 0.37% | ₹3,612 → ₹8,980 |
| 2022 | 97.43% | 248 | 0.28% | ₹8,980 → ₹17,729 |
| 2023 | 52.12% | 245 | 0.18% | ₹17,729 → ₹26,969 |
| 2024 | 123.16% | 246 | 0.33% | ₹26,969 → ₹60,184 |
| 2025 | 47.51% | 249 | 0.16% | ₹60,184 → ₹88,777 |

### Strategy Performance Breakdown

| Strategy | Direction | Win Rate | Avg Daily Profit | Total Trades |
|----------|-----------|----------|------------------|--------------|
| S1_Resistance_Rejection | LONG | 57.42% | 0.34% | 35,984 |
| S1_Support_Bounce | SHORT | 59.66% | 0.39% | 76,350 |

**Key Finding:** SHORT strategies slightly outperform LONG strategies (3,669% vs 3,017% total profit)

## 📊 Visual Performance Analysis

### Equity Curve - Capital Growth
![Equity Curve](equity_curve.png)

### Yearly Returns
![Yearly Returns](yearly_returns.png)

### Strategy Performance Comparison
![Strategy Comparison](strategy_comparison.png)

### Drawdown Analysis
![Drawdown Chart](drawdown_chart.png)

### Monthly Returns Heatmap
![Monthly Returns](monthly_returns_heatmap.png)

## 🔬 Rigorous Backtesting Approach

### Multiple Testing Methods

1. **Signal Strength Based** (Primary Method)
   - Ranks all signals by strength indicators
   - Selects top 5-10 stocks per strategy daily
   - **Result:** 140% CAGR with 4.99 Sharpe Ratio

2. **Random Selection**
   - Randomly picks stocks from signal pool
   - Tests if edge exists without optimization bias
   - **Result:** Consistent profitability across random samples

3. **Variable Position Sizing**
   - Tested with 1, 2, 3, 4, 5...15 stocks per day
   - Analyzed risk-return tradeoffs
   - **Optimal:** 5 LONG + 5 SHORT = 10 total trades/day

### Why 5+5 Configuration?

**Risk Management Benefits:**
- **Diversification:** Reduces single-stock risk
- **Lower Drawdown:** Max DD reduced from -22% to -11%
- **Better Accuracy:** Win rate improved from ~55% to 63%
- **Balanced Exposure:** Equal long/short positions hedge market risk

## 🛠️ Technical Implementation

### Technology Stack

- **Language:** Python 3.8+
- **Data Sources:** 
  - yfinance (historical data)
  - Zerodha Kite API (live data & execution)
- **Libraries:** Pandas, NumPy
- **Backtesting:** Custom framework built from scratch
- **Automation:** Fully automated via Zerodha Kite API

### Data Universe

- **Source:** All stocks available for intraday trading on Zerodha
- **Market:** NSE (National Stock Exchange)
- **Frequency:** Daily OHLC data
- **Period:** 2018-2025 (7 years)

### Automation Workflow
```
09:00 AM → System scans all NSE stocks
        ↓
09:15 AM → Generates 20-50 signals
        ↓
09:17 AM → Filters stocks by entry conditions
        ↓
        → Places limit orders (12 orders → 5 fills expected)
        ↓
        → Monitors positions throughout the day
        ↓
03:15 PM → Auto-closes all positions
        ↓
        → Generates daily P&L report
```

### Entry Criteria Validation

**The Key Innovation:**

Traditional backtests can't verify if High/Low levels were actually achievable intraday. This strategy solves that:

**For SHORT Trades:**
1. At 9:17 AM, check: `(Open - Low) / Open > 0.3%`
2. If true, place limit order at `Open + 2%`
3. Monitor until filled or day end

**For LONG Trades:**
1. Check: `(High - Open) / Open > 0.3%`
2. If true, place limit order at `Open - 2%`
3. Monitor until filled or day end

**Execution Reality:**
- ~12 orders placed → ~5 fills (40-50% fill rate)
- Accounts for slippage (0.25% per trade)
- Realistic position sizing with/without leverage

## 💡 Key Features

✅ **Fully Automated Execution** via Zerodha Kite API  
✅ **Real-time Stock Screening** across entire NSE universe  
✅ **Signal Strength Ranking** for optimal trade selection  
✅ **Transaction Costs Included** (0.25% slippage + tax)  
✅ **Multi-Layered Risk Management** (4 monitoring systems)  
✅ **Daily Rebalancing** - no overnight risk  
✅ **Backtested Across Multiple Methods** to avoid overfitting  

## 📈 Risk Management Summary

### Position Sizing
- Maximum 10 trades per day (5 LONG + 5 SHORT)
- Equal capital allocation per trade
- Optional leverage usage based on risk appetite

### Risk Metrics
- **Max Drawdown:** -11.44%
- **Sharpe Ratio:** 4.99 (excellent risk-adjusted returns)
- **Win Rate:** 63.62%
- **Daily Loss Limit:** 2% of capital (hard stop)
- **Position Exit Triggers:** ±4% (50% exit), ±8% (100% exit)

### Stop Loss & Exits
- All positions closed by 3:15 PM (no overnight risk)
- Intraday monitoring with automated exit at close
- Risk of gap-ups/gap-downs eliminated
- Real-time position monitoring via 4 proprietary systems

## 🚀 Why This Strategy Works

1. **Behavioral Edge:** Exploits profit-booking after momentum moves
2. **Data Edge:** Uses daily OHLC for intraday decisions (uncommon approach)
3. **Market Structure:** Indian markets show strong mean reversion intraday
4. **Execution Edge:** Automated system removes emotional decisions
5. **Diversification:** Multiple stocks + both directions = lower risk
6. **Risk Controls:** 4-layer monitoring system prevents catastrophic losses

## 📁 Project Structure
```
trading-strategy-backtest/
│
├── main.py                         # Main backtesting script
├── README.md                       # This file
│
├── daily_trades_output/            # Results folder
│   ├── capital_growth.csv
│   ├── yearly_performance.csv
│   ├── strategy_summary.csv
│   └── [other result files]
│
└── live_execution/                 # NOT IN GITHUB (Proprietary)
    ├── daily_loss_limit.py         # 2% daily loss circuit breaker
    ├── long_trades_monitor.py      # Individual long position risk manager
    ├── short_trades_monitor.py     # Individual short position risk manager
    └── order_fill_manager.py       # Smart order cancellation system
```

## 🎓 Background

**Professional Context:**
- Bachelor's in Engineering (BE)
- 2.5 years at Mercedes Benz R&D
- 4 years of active trading experience
- Deep understanding of Indian equity markets
- Expertise in Python & automation

**This project demonstrates:**
- Quantitative strategy development
- Systematic backtesting methodology
- Risk management implementation
- Production-ready code architecture
- Real-world market knowledge
- Live trading execution systems

## 🔮 Future Enhancements

- [ ] Machine learning for dynamic position sizing
- [ ] Additional technical indicators for signal filtering
- [ ] Multi-timeframe analysis
- [ ] Real-time performance dashboard
- [ ] Advanced portfolio optimization
- [ ] Options strategies integration

## ⚠️ Disclaimer

**Important:**
- This is for educational and demonstration purposes only
- Trading involves substantial risk of loss
- Always do your own research before investing
- Past performance does not guarantee future results
- The author is not responsible for any financial losses
- Risk management systems are proprietary and not included in this repository

## 📫 Contact

- **Email:** [Your Email]
- **LinkedIn:** [Your LinkedIn Profile]

---

**⭐ If you find this project interesting, please consider giving it a star!**

*Developed as a demonstration of quantitative trading skills for career opportunities in algorithmic trading and quantitative finance.*

---

## 📝 License

This project is licensed under the MIT License.
