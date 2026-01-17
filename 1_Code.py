import pandas as pd
import numpy as np
import os

# ================================================================================
# CONFIGURATION - 2 STRATEGY COMBINED SYSTEM (1 LONG + 1 SHORT)
# ================================================================================
ANALYSIS_START_DATE = '2022-06-01'
ANALYSIS_END_DATE = '2025-12-31'
STOCKS_PER_STRATEGY = 10  # 10 trades per strategy
TOTAL_STRATEGIES = 2     # 2 strategies total = 20 trades per day
SLIPPAGE_TAX_PER_STOCK = 0.25
PROCESSED_FOLDER = "processed_stock_data_all"
INITIAL_CAPITAL = 100.0
MIN_DATA_POINTS = 60
OUTPUT_FOLDER = "daily_trades_output"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ================================================================================
# LONG STRATEGY ENTRY CONDITIONS
# ================================================================================
# High must be >= 0.3% above Open (ensuring some upward wick exists)
LONG_MIN_HIGH_ABOVE_OPEN_PCT = 0.3
# Low must be >= 2% below Open (this is where we'll enter LONG)
LONG_MIN_LOW_BELOW_OPEN_PCT = 2

# ================================================================================
# SHORT STRATEGY ENTRY CONDITIONS
# ================================================================================
# High must be >= 2% above Open (this is where we'll enter SHORT)
SHORT_MIN_HIGH_ABOVE_OPEN_PCT = 2.0
# Low must be != Open AND >= 0.3% away from Open
SHORT_MIN_LOW_OPEN_DISTANCE_PCT = 0.3

# ================================================================================
# S1_LONG: Resistance Rejection (LONG)
# ================================================================================
S1_LONG_LOOKBACK_DAYS = 10
S1_LONG_RESISTANCE_TOLERANCE = 1.0
S1_LONG_MIN_REJECTION = 0.5

# ================================================================================
# S1_SHORT: Support Bounce (SHORT)
# ================================================================================
S1_SHORT_LOOKBACK_DAYS = 10
S1_SHORT_SUPPORT_TOLERANCE = 1
S1_SHORT_MIN_BOUNCE = 0.5


# ================================================================================
# HELPER FUNCTIONS
# ================================================================================
def check_high_above_open(high, open_price, min_pct):
    """Check if high is at least min_pct above open"""
    if open_price == 0:
        return False
    high_above_open_pct = ((high - open_price) / open_price) * 100
    return high_above_open_pct >= min_pct


def check_low_below_open(low, open_price, min_pct):
    """Check if low is at least min_pct below open"""
    if open_price == 0 or low == open_price:
        return False
    low_below_open_pct = ((open_price - low) / open_price) * 100
    return low_below_open_pct >= min_pct


def check_low_open_distance(low, open_price, min_pct=0.2):
    """Check if low is at least min_pct away from open"""
    if open_price == 0 or low == open_price:
        return False
    distance_pct = abs((low - open_price) / open_price) * 100
    return distance_pct >= min_pct


def get_entry_price_long(open_price, pct_below):
    """Get long entry price at pct_below the open"""
    return open_price * (1 - pct_below / 100)


def get_entry_price_short(open_price, pct_above):
    """Get short entry price at pct_above the open"""
    return open_price * (1 + pct_above / 100)


# ================================================================================
# MAIN PROGRAM
# ================================================================================
print("=" * 80)
print("2 STRATEGY COMBINED TRADING SYSTEM")
print("=" * 80)
print("STRATEGIES:")
print("  S1_LONG:  Resistance Rejection (LONG) - 10 trades/day")
print("  S1_SHORT: Support Bounce (SHORT) - 10 trades/day")
print("=" * 80)
print(f"Total Trades per Day: {STOCKS_PER_STRATEGY * TOTAL_STRATEGIES}")
print("=" * 80)
print("LONG Entry Conditions:")
print(f"  - High >= {LONG_MIN_HIGH_ABOVE_OPEN_PCT}% above Open")
print(f"  - Low >= {LONG_MIN_LOW_BELOW_OPEN_PCT}% below Open")
print(f"  - Entry: LONG at {LONG_MIN_LOW_BELOW_OPEN_PCT}% below Open")
print("SHORT Entry Conditions:")
print(f"  - High >= {SHORT_MIN_HIGH_ABOVE_OPEN_PCT}% above Open")
print(f"  - Low >= {SHORT_MIN_LOW_OPEN_DISTANCE_PCT}% away from Open")
print(f"  - Entry: SHORT at {SHORT_MIN_HIGH_ABOVE_OPEN_PCT}% above Open")
print("=" * 80)
print(f"Analysis Period: {ANALYSIS_START_DATE} to {ANALYSIS_END_DATE}")
print(f"Slippage/Tax: {SLIPPAGE_TAX_PER_STOCK}%")
print(f"Output Folder: {OUTPUT_FOLDER}")
print("=" * 80)

# Trade storage for each strategy
s1_long_trades = []   # Resistance Rejection (LONG)
s1_short_trades = []  # Support Bounce (SHORT)

# Get all stock files
all_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(".csv")]
total_files = len(all_files)
processed_count = 0
skipped_count = 0

print(f"\nProcessing {total_files} stock files...")

for file_name in all_files:
    stock_symbol = file_name.replace('.csv', '')
    file_path = os.path.join(PROCESSED_FOLDER, file_name)
    
    try:
        data = pd.read_csv(file_path)
        data['Price'] = pd.to_datetime(data['Price'])
        data = data[(data['Price'] >= ANALYSIS_START_DATE) & (data['Price'] <= ANALYSIS_END_DATE)]
        data = data.sort_values(by='Price').reset_index(drop=True)

        if len(data) < MIN_DATA_POINTS:
            skipped_count += 1
            continue
        
        for i in range(MIN_DATA_POINTS, len(data)):
            today_open = data['Open'].iloc[i]
            today_high = data['High'].iloc[i]
            today_low = data['Low'].iloc[i]
            today_close = data['Close'].iloc[i]
            current_date = data['Price'].iloc[i].date()
            
            # Previous day data
            prev1_open = data['Open'].iloc[i-1]
            prev1_high = data['High'].iloc[i-1]
            prev1_low = data['Low'].iloc[i-1]
            prev1_close = data['Close'].iloc[i-1]
            
            # ========================================================================
            # CHECK LONG ENTRY CONDITIONS
            # ========================================================================
            long_entry_valid = (
                check_high_above_open(today_high, today_open, LONG_MIN_HIGH_ABOVE_OPEN_PCT) and
                check_low_below_open(today_low, today_open, LONG_MIN_LOW_BELOW_OPEN_PCT)
            )
            
            if long_entry_valid:
                # Calculate LONG entry/exit
                long_entry_price = get_entry_price_long(today_open, LONG_MIN_LOW_BELOW_OPEN_PCT)
                long_exit_price = today_close
                long_profit_abs = long_exit_price - long_entry_price
                long_profit_pct = (long_profit_abs / long_entry_price) * 100
                long_profit_pct_after_costs = long_profit_pct - SLIPPAGE_TAX_PER_STOCK
                
                # ====================================================================
                # S1_LONG: Resistance Rejection (LONG)
                # Price touched resistance and got rejected - We go LONG on oversold dip
                # ====================================================================
                if i >= S1_LONG_LOOKBACK_DAYS:
                    start_idx = max(0, i - S1_LONG_LOOKBACK_DAYS)
                    resistance_level = data['High'].iloc[start_idx:i].max()
                    
                    if resistance_level > 0 and prev1_close > 0:
                        resistance_touch = abs(prev1_high - resistance_level) / resistance_level * 100
                        rejection_from_resistance = ((resistance_level - today_open) / resistance_level) * 100
                        gap_pct = ((today_open - prev1_close) / prev1_close) * 100
                        
                        # Condition: touched resistance, got rejected, gap down
                        if resistance_touch <= S1_LONG_RESISTANCE_TOLERANCE and rejection_from_resistance >= S1_LONG_MIN_REJECTION and gap_pct < 0:
                            signal_strength = rejection_from_resistance + abs(gap_pct)
                            s1_long_trades.append({
                                'Entry_Date': current_date, 'Stock': stock_symbol, 'Direction': 'LONG',
                                'Strategy': 'S1_Resistance_Rejection',
                                'Entry_Price': long_entry_price, 'Exit_Price': long_exit_price,
                                'Open': today_open, 'High': today_high, 'Low': today_low, 'Close': today_close,
                                'Resistance_Level': resistance_level,
                                'Prev_Open': prev1_open, 'Prev_High': prev1_high, 'Prev_Low': prev1_low, 'Prev_Close': prev1_close,
                                'Profit_%': long_profit_pct, 'Profit_%_After_Costs': long_profit_pct_after_costs,
                                'Signal_Strength': signal_strength
                            })
            
            # ========================================================================
            # CHECK SHORT ENTRY CONDITIONS
            # ========================================================================
            short_entry_valid = (
                check_high_above_open(today_high, today_open, SHORT_MIN_HIGH_ABOVE_OPEN_PCT) and
                check_low_open_distance(today_low, today_open, SHORT_MIN_LOW_OPEN_DISTANCE_PCT)
            )
            
            if short_entry_valid:
                # Calculate SHORT entry/exit
                short_entry_price = get_entry_price_short(today_open, SHORT_MIN_HIGH_ABOVE_OPEN_PCT)
                short_exit_price = today_close
                short_profit_abs = short_entry_price - short_exit_price
                short_profit_pct = (short_profit_abs / short_entry_price) * 100
                short_profit_pct_after_costs = short_profit_pct - SLIPPAGE_TAX_PER_STOCK
                
                # ====================================================================
                # S1_SHORT: Support Bounce (SHORT)
                # ====================================================================
                if i >= S1_SHORT_LOOKBACK_DAYS:
                    start_idx = max(0, i - S1_SHORT_LOOKBACK_DAYS)
                    support_level = data['Low'].iloc[start_idx:i].min()
                    
                    if support_level > 0 and prev1_close > 0:
                        support_touch = abs(prev1_low - support_level) / support_level * 100
                        bounce_from_support = ((today_open - support_level) / support_level) * 100
                        gap_pct = ((today_open - prev1_close) / prev1_close) * 100
                        
                        if support_touch <= S1_SHORT_SUPPORT_TOLERANCE and bounce_from_support >= S1_SHORT_MIN_BOUNCE and gap_pct > 0:
                            signal_strength = bounce_from_support + gap_pct
                            s1_short_trades.append({
                                'Entry_Date': current_date, 'Stock': stock_symbol, 'Direction': 'SHORT',
                                'Strategy': 'S1_Support_Bounce',
                                'Entry_Price': short_entry_price, 'Exit_Price': short_exit_price,
                                'Open': today_open, 'High': today_high, 'Low': today_low, 'Close': today_close,
                                'Support_Level': support_level,
                                'Prev_Open': prev1_open, 'Prev_High': prev1_high, 'Prev_Low': prev1_low, 'Prev_Close': prev1_close,
                                'Profit_%': short_profit_pct, 'Profit_%_After_Costs': short_profit_pct_after_costs,
                                'Signal_Strength': signal_strength
                            })
        
        processed_count += 1
        if processed_count % 50 == 0:
            print(f"  Processed {processed_count}/{total_files} stocks...")
                    
    except Exception as e:
        skipped_count += 1
        continue

print(f"\nProcessed: {processed_count} stocks, Skipped: {skipped_count} stocks")


# ================================================================================
# PROCESS INDIVIDUAL STRATEGY RESULTS
# ================================================================================
print("\n" + "=" * 80)
print("INDIVIDUAL STRATEGY RESULTS")
print("=" * 80)

strategies = {
    'S1_Resistance_Rejection': s1_long_trades,
    'S1_Support_Bounce': s1_short_trades
}

strategy_summaries = []
strategy_daily_dfs = {}

for strategy_name, trades in strategies.items():
    direction = 'LONG' if strategy_name == 'S1_Resistance_Rejection' else 'SHORT'
    
    print(f"\n{'-' * 60}")
    print(f"STRATEGY: {strategy_name} ({direction})")
    print(f"{'-' * 60}")
    
    if not trades:
        print("No trades generated!")
        strategy_summaries.append({
            'Strategy': strategy_name, 'Direction': direction, 'Total_Trades': 0, 'Trading_Days': 0,
            'Win_Rate_%': 0, 'Avg_Daily_Profit_%': 0, 'Total_Profit_%': 0
        })
        strategy_daily_dfs[strategy_name] = pd.DataFrame()
        continue
    
    trades_df = pd.DataFrame(trades)
    print(f"Total Trades: {len(trades_df)}")
    
    # Save all trades for this strategy
    all_trades_file = os.path.join(OUTPUT_FOLDER, f"{strategy_name}_all_trades.csv")
    trades_df.to_csv(all_trades_file, index=False)
    print(f"Saved all trades to: {all_trades_file}")
    
    # Group by date and select top trades by signal strength
    unique_dates = sorted(trades_df['Entry_Date'].unique())
    daily_summaries = []
    daily_selected_trades = []

    for dt in unique_dates:
        day_trades = trades_df[trades_df['Entry_Date'] == dt]
        top_trades = day_trades.nlargest(STOCKS_PER_STRATEGY, 'Signal_Strength')
        
        # Store selected trades
        for _, trade in top_trades.iterrows():
            daily_selected_trades.append(trade.to_dict())
        
        avg_profit_pct = top_trades['Profit_%_After_Costs'].mean()
        daily_summaries.append({
            'Entry_Date': dt, 
            'Strategy': strategy_name,
            'Direction': direction,
            'Num_Stocks': len(top_trades), 
            'Avg_Profit_%': avg_profit_pct,
            'Total_Profit_%': top_trades['Profit_%_After_Costs'].sum()
        })

    # Save selected trades (top 10 per day)
    selected_trades_df = pd.DataFrame(daily_selected_trades)
    selected_trades_file = os.path.join(OUTPUT_FOLDER, f"{strategy_name}_selected_trades.csv")
    selected_trades_df.to_csv(selected_trades_file, index=False)
    print(f"Saved selected trades (top 10/day) to: {selected_trades_file}")

    daily_df = pd.DataFrame(daily_summaries).sort_values(by='Entry_Date').reset_index(drop=True)
    strategy_daily_dfs[strategy_name] = daily_df
    
    # Calculate metrics
    total_days = len(daily_df)
    percent_positive_days = ((daily_df['Avg_Profit_%'] > 0).sum() / total_days) * 100 if total_days > 0 else 0
    total_profit_pct = daily_df['Avg_Profit_%'].sum()
    avg_daily_profit_pct = daily_df['Avg_Profit_%'].mean()

    print(f"Trading Days: {total_days}")
    print(f"Win Rate: {percent_positive_days:.2f}%")
    print(f"Total Profit %: {total_profit_pct:.2f}%")
    print(f"Avg Daily Profit %: {avg_daily_profit_pct:.4f}%")
    
    strategy_summaries.append({
        'Strategy': strategy_name, 'Direction': direction, 'Total_Trades': len(trades_df),
        'Trading_Days': total_days, 'Win_Rate_%': round(percent_positive_days, 2),
        'Avg_Daily_Profit_%': round(avg_daily_profit_pct, 4), 'Total_Profit_%': round(total_profit_pct, 2)
    })


# ================================================================================
# COMBINED PORTFOLIO ANALYSIS
# ================================================================================
print("\n" + "=" * 80)
print("COMBINED PORTFOLIO ANALYSIS (20 TRADES PER DAY)")
print("=" * 80)

# Combine all daily results
all_daily_data = []
for strategy_name, daily_df in strategy_daily_dfs.items():
    if not daily_df.empty:
        for _, row in daily_df.iterrows():
            all_daily_data.append({
                'Entry_Date': row['Entry_Date'],
                'Strategy': strategy_name,
                'Direction': row['Direction'],
                'Num_Stocks': row['Num_Stocks'],
                'Strategy_Avg_Profit_%': row['Avg_Profit_%'],
                'Strategy_Total_Profit_%': row['Total_Profit_%']
            })

combined_df = pd.DataFrame(all_daily_data)

if combined_df.empty:
    print("No trades generated across any strategy!")
else:
    # Group by date to get daily portfolio performance
    daily_portfolio = []
    all_dates = sorted(combined_df['Entry_Date'].unique())
    
    for dt in all_dates:
        day_data = combined_df[combined_df['Entry_Date'] == dt]
        
        # Sum of all trades taken that day
        total_trades = day_data['Num_Stocks'].sum()
        
        # Calculate weighted average profit
        total_profit_all_strategies = day_data['Strategy_Total_Profit_%'].sum()
        
        if total_trades > 0:
            avg_profit_per_trade = total_profit_all_strategies / total_trades
        else:
            avg_profit_per_trade = 0
        
        # Track which strategies traded
        strategies_traded = day_data['Strategy'].tolist()
        num_strategies = len(strategies_traded)
        
        daily_portfolio.append({
            'Entry_Date': dt,
            'Total_Trades': total_trades,
            'Num_Strategies': num_strategies,
            'Strategies': ', '.join(strategies_traded),
            'Total_Profit_%': total_profit_all_strategies,
            'Avg_Profit_Per_Trade_%': avg_profit_per_trade
        })
    
    portfolio_df = pd.DataFrame(daily_portfolio).sort_values(by='Entry_Date').reset_index(drop=True)
    
    # Save daily portfolio performance
    portfolio_file = os.path.join(OUTPUT_FOLDER, "daily_portfolio_performance.csv")
    portfolio_df.to_csv(portfolio_file, index=False)
    print(f"\nSaved daily portfolio performance to: {portfolio_file}")
    
    # Portfolio Metrics
    total_trading_days = len(portfolio_df)
    full_trading_days = len(portfolio_df[portfolio_df['Total_Trades'] == 20])
    avg_trades_per_day = portfolio_df['Total_Trades'].mean()
    positive_days = (portfolio_df['Avg_Profit_Per_Trade_%'] > 0).sum()
    win_rate = (positive_days / total_trading_days) * 100 if total_trading_days > 0 else 0
    avg_daily_profit = portfolio_df['Avg_Profit_Per_Trade_%'].mean()
    total_profit = portfolio_df['Total_Profit_%'].sum()
    
    # Sharpe Ratio
    daily_returns = portfolio_df['Avg_Profit_Per_Trade_%']
    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if len(daily_returns) > 1 and daily_returns.std() > 0 else 0
    
    print(f"\nTotal Trading Days: {total_trading_days}")
    print(f"Full Trading Days (20 trades): {full_trading_days}")
    print(f"Average Trades per Day: {avg_trades_per_day:.2f}")
    print(f"\nWin Rate (Positive Days): {win_rate:.2f}%")
    print(f"Average Daily Profit (per trade): {avg_daily_profit:.4f}%")
    print(f"Total Profit %: {total_profit:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    
    # Capital Growth Simulation
    print("\n" + "-" * 60)
    print("CAPITAL GROWTH SIMULATION")
    print("-" * 60)
    
    capital = INITIAL_CAPITAL
    capital_history = []
    
    for idx, row in portfolio_df.iterrows():
        daily_return = row['Avg_Profit_Per_Trade_%']
        capital = capital * (1 + daily_return / 100)
        capital_history.append({
            'Date': row['Entry_Date'], 
            'Capital': capital,
            'Daily_Return_%': daily_return,
            'Trades': row['Total_Trades']
        })
    
    capital_df = pd.DataFrame(capital_history)
    
    # Save capital growth
    capital_file = os.path.join(OUTPUT_FOLDER, "capital_growth.csv")
    capital_df.to_csv(capital_file, index=False)
    print(f"Saved capital growth to: {capital_file}")
    
    final_capital = capital
    
    # Max Drawdown
    capital_df['Peak'] = capital_df['Capital'].cummax()
    capital_df['Drawdown'] = ((capital_df['Capital'] - capital_df['Peak']) / capital_df['Peak']) * 100
    max_drawdown = capital_df['Drawdown'].min() if len(capital_df) > 0 else 0
    
    # Yearly CAGR Calculation
    print("\n" + "-" * 60)
    print("YEARLY PERFORMANCE")
    print("-" * 60)
    
    capital_df['Date'] = pd.to_datetime(capital_df['Date'])
    capital_df['Year'] = capital_df['Date'].dt.year
    
    yearly_performance = []
    years = sorted(capital_df['Year'].unique())
    
    prev_year_end_capital = INITIAL_CAPITAL
    
    for year in years:
        year_data = capital_df[capital_df['Year'] == year]
        
        if len(year_data) > 0:
            year_start_capital = prev_year_end_capital
            year_end_capital = year_data['Capital'].iloc[-1]
            year_return = ((year_end_capital - year_start_capital) / year_start_capital) * 100
            
            # Trading days in this year
            year_trading_days = len(year_data)
            
            # Average daily return for this year
            year_daily_returns = year_data['Daily_Return_%']
            avg_year_daily_return = year_daily_returns.mean()
            
            yearly_performance.append({
                'Year': year,
                'Start_Capital': round(year_start_capital, 2),
                'End_Capital': round(year_end_capital, 2),
                'Return_%': round(year_return, 2),
                'Trading_Days': year_trading_days,
                'Avg_Daily_Return_%': round(avg_year_daily_return, 4)
            })
            
            prev_year_end_capital = year_end_capital
    
    yearly_df = pd.DataFrame(yearly_performance)
    
    # Save yearly performance
    yearly_file = os.path.join(OUTPUT_FOLDER, "yearly_performance.csv")
    yearly_df.to_csv(yearly_file, index=False)
    print(f"Saved yearly performance to: {yearly_file}")
    
    print("\nYearly Performance:")
    print(yearly_df.to_string(index=False))
    
    # Overall CAGR (from start to end)
    cagr = 0
    if len(capital_df) > 0:
        start_date = capital_df['Date'].iloc[0]
        end_date = capital_df['Date'].iloc[-1]
        years_elapsed = (end_date - start_date).days / 365.25
        if years_elapsed > 0 and final_capital > 0:
            cagr = (((final_capital / INITIAL_CAPITAL) ** (1 / years_elapsed)) - 1) * 100
    
    print(f"\nInitial Capital: ₹{INITIAL_CAPITAL:.2f}")
    print(f"Final Capital: ₹{final_capital:.2f}")
    print(f"Total Return: {((final_capital/INITIAL_CAPITAL)-1)*100:.2f}%")
    print(f"Overall CAGR: {cagr:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    
    # Strategy Contribution Analysis
    print("\n" + "-" * 60)
    print("STRATEGY CONTRIBUTION ANALYSIS")
    print("-" * 60)
    
    strategy_contrib = []
    for strategy_name, daily_df in strategy_daily_dfs.items():
        if not daily_df.empty:
            direction = 'LONG' if strategy_name == 'S1_Resistance_Rejection' else 'SHORT'
            total_strat_profit = daily_df['Total_Profit_%'].sum()
            avg_strat_profit = daily_df['Avg_Profit_%'].mean()
            strat_days = len(daily_df)
            strategy_contrib.append({
                'Strategy': strategy_name,
                'Direction': direction,
                'Trading_Days': strat_days,
                'Total_Profit_%': round(total_strat_profit, 2),
                'Avg_Daily_Profit_%': round(avg_strat_profit, 4)
            })
    
    contrib_df = pd.DataFrame(strategy_contrib)
    contrib_df = contrib_df.sort_values(by='Total_Profit_%', ascending=False)
    print(contrib_df.to_string(index=False))
    
    # Save contribution analysis
    contrib_file = os.path.join(OUTPUT_FOLDER, "strategy_contribution.csv")
    contrib_df.to_csv(contrib_file, index=False)
    print(f"\nSaved strategy contribution to: {contrib_file}")
    
    # LONG vs SHORT Analysis
    print("\n" + "-" * 60)
    print("LONG vs SHORT ANALYSIS")
    print("-" * 60)
    
    long_profit = contrib_df[contrib_df['Direction'] == 'LONG']['Total_Profit_%'].sum()
    short_profit = contrib_df[contrib_df['Direction'] == 'SHORT']['Total_Profit_%'].sum()
    
    print(f"LONG Strategies Total Profit: {long_profit:.2f}%")
    print(f"SHORT Strategies Total Profit: {short_profit:.2f}%")
    print(f"Combined Total Profit: {long_profit + short_profit:.2f}%")


# ================================================================================
# FINAL SUMMARY
# ================================================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print("\nIndividual Strategy Results:")
summary_df = pd.DataFrame(strategy_summaries)
print(summary_df.to_string(index=False))

# Save summary
summary_file = os.path.join(OUTPUT_FOLDER, "strategy_summary.csv")
summary_df.to_csv(summary_file, index=False)
print(f"\nSaved strategy summary to: {summary_file}")

print("\n" + "=" * 80)
print("COMBINED PORTFOLIO PERFORMANCE")
print("=" * 80)
print(f"Strategies: 2 (1 LONG + 1 SHORT)")
print(f"Trades per Strategy: {STOCKS_PER_STRATEGY}")
print(f"Total Trades per Day: {STOCKS_PER_STRATEGY * TOTAL_STRATEGIES}")
print(f"Analysis Period: {ANALYSIS_START_DATE} to {ANALYSIS_END_DATE}")
print("-" * 60)
if not combined_df.empty:
    print(f"Total Trading Days: {total_trading_days}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Avg Daily Profit (per trade): {avg_daily_profit:.4f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Overall CAGR: {cagr:.2f}%")
    print(f"Final Capital (from ₹{INITIAL_CAPITAL}): ₹{final_capital:.2f}")
print("=" * 80)
print("\nALL CSV FILES SAVED TO FOLDER: " + OUTPUT_FOLDER)
print("=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
