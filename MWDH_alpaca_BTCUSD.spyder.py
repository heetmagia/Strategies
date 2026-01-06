!pip install alpaca-py pandas
# First, install required packages by running this in your terminal:
# pip install alpaca-py pandas

import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from datetime import datetime, timedelta

# ========== API CREDENTIALS ==========
# Get your API keys from: https://app.alpaca.markets/paper/dashboard/overview
# For paper trading: https://app.alpaca.markets/paper/dashboard/overview
# For live trading: https://app.alpaca.markets/live/dashboard/overview

API_KEY = "PK5MR7CNKQHEZXTZA2IS2HN4BV"  # Replace with your actual API key
API_SECRET = "ChBmTzjibJzJjUy79Gh7ivkoiXSiBR4UyykMkhoqsTEC"  # Replace with your actual secret key
PAPER_TRADING = True  # Set to False for live trading

# Initialize Alpaca clients
from alpaca.trading.client import TradingClient

# Historical data client (for fetching price data)
data_client = CryptoHistoricalDataClient()

# Trading client (for placing orders - requires authentication)
trading_client = TradingClient(
    api_key=API_KEY,
    secret_key=API_SECRET,
    paper=PAPER_TRADING  # True = paper t|rading, False = live trading
)

# Test connection
try:
    account = trading_client.get_account()
    print(f"✓ Connected to Alpaca!")
    print(f"Account Status: {account.status}")
    print(f"Trading Mode: {'PAPER' if PAPER_TRADING else 'LIVE'}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print("="*60)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("Please check your API credentials!")
    exit()

client = data_client  # Use data_client for historical data

# Define parameters
symbol = "BTC/USD"
end_date = datetime(2025, 12, 31)
start_date = end_date - timedelta(days=3*365)  # Approximately 3 years

print(f"Fetching BTCUSD data from {start_date.date()} to {end_date.date()}")
print("="*60)

# Function to fetch and process data
def fetch_crypto_data(timeframe, timeframe_name):
    request_params = CryptoBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=timeframe,
        start=start_date,
        end=end_date
    )
    
    bars = client.get_crypto_bars(request_params)
    df = bars.df
    
    # Reset index to make timestamp a column
    df = df.reset_index()
    
    # Keep only closing prices and relevant info
    df_clean = df[['timestamp', 'close', 'volume']].copy()
    df_clean.columns = ['Date', 'Close', 'Volume']
    
    print(f"\n{timeframe_name} Data:")
    print(f"Total records: {len(df_clean)}")
    print(f"Date range: {df_clean['Date'].min()} to {df_clean['Date'].max()}")
    print(f"\nFirst 5 rows:")
    print(df_clean.head())
    print(f"\nLast 5 rows:")
    print(df_clean.tail())
    print(f"\nBasic statistics:")
    print(df_clean['Close'].describe())
    
    return df_clean

# Fetch data for all three timeframes
try:
    # Daily data
    daily_df = fetch_crypto_data(TimeFrame.Day, "DAILY")
    
    print("\n" + "="*60)
    
    # Weekly data
    weekly_df = fetch_crypto_data(TimeFrame.Week, "WEEKLY")
    
    print("\n" + "="*60)
    
    # Monthly data
    monthly_df = fetch_crypto_data(TimeFrame.Month, "MONTHLY")
    
    # Save to CSV files
    daily_df.to_csv('btcusd_daily.csv', index=False)
    weekly_df.to_csv('btcusd_weekly.csv', index=False)
    monthly_df.to_csv('btcusd_monthly.csv', index=False)
    
    print("\n" + "="*60)
    print("\n✓ Data successfully fetched and saved!")
    print("  - btcusd_daily.csv")
    print("  - btcusd_weekly.csv")
    print("  - btcusd_monthly.csv")
    
except Exception as e:
    print(f"\nError fetching data: {e}")
    print("\nNote: You may need to install required packages:")
    print("pip install alpaca-py pandas")
    
    
## FETCHED THE DATA OF M W D OF BTCUSD
    

