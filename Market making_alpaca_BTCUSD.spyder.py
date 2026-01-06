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
    paper=PAPER_TRADING  # True = paper trading, False = live trading
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
    
    
import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestOrderbookRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import time

# Initialize client (no API key needed for market data)
client = CryptoHistoricalDataClient()

print("="*80)
print("LIVE ORDER BOOK MONITOR - BTC/USD")
print("="*80)
print("\nPress Ctrl+C to stop monitoring\n")

def get_orderbook_data():
    """Fetch and display live orderbook"""
    try:
        # Get orderbook
        request = CryptoLatestOrderbookRequest(symbol_or_symbols=["BTC/USD"])
        orderbook = client.get_crypto_latest_orderbook(request)
        
        btc_book = orderbook["BTC/USD"]
        
        # Get current price
        bars_request = CryptoBarsRequest(
            symbol_or_symbols=["BTC/USD"],
            timeframe=TimeFrame.Minute,
            limit=1
        )
        bars = client.get_crypto_bars(bars_request)
        current_price = float(bars.df['close'].iloc[-1])
        
        print(f"\nDebug - Orderbook type: {type(btc_book)}")
        print(f"Debug - Orderbook attributes: {dir(btc_book)}")
        if btc_book.bids:
            print(f"Debug - First bid type: {type(btc_book.bids[0])}")
            print(f"Debug - First bid attributes: {dir(btc_book.bids[0])}")
        
        # Extract bid and ask data - try different attribute names
        try:
            best_bid = float(btc_book.bids[0].price) if btc_book.bids else 0
            best_ask = float(btc_book.asks[0].price) if btc_book.asks else 0
            best_bid_size = float(btc_book.bids[0].size) if btc_book.bids else 0
            best_ask_size = float(btc_book.asks[0].size) if btc_book.asks else 0
        except AttributeError:
            # Try alternative attribute names
            best_bid = float(btc_book.bids[0][0]) if btc_book.bids else 0
            best_ask = float(btc_book.asks[0][0]) if btc_book.asks else 0
            best_bid_size = float(btc_book.bids[0][1]) if btc_book.bids else 0
            best_ask_size = float(btc_book.asks[0][1]) if btc_book.asks else 0
        
        spread = best_ask - best_bid
        spread_pct = (spread / current_price) * 100 if current_price > 0 else 0
        
        # Display
        print(f"\n{'='*80}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        print(f"\n📊 CURRENT MARKET:")
        print(f"   Last Price:     ${current_price:,.2f}")
        print(f"   Best Bid:       ${best_bid:,.2f} ({best_bid_size:.6f} BTC)")
        print(f"   Best Ask:       ${best_ask:,.2f} ({best_ask_size:.6f} BTC)")
        print(f"   Spread:         ${spread:.2f} ({spread_pct:.4f}%)")
        
        print(f"\n📈 BID SIDE (Buy Orders):")
        print(f"   {'Price':<15} {'Size':<15}")
        print(f"   {'-'*30}")
        for bid in btc_book.bids[:5]:
            try:
                price = float(bid.price)
                size = float(bid.size)
            except AttributeError:
                price = float(bid[0])
                size = float(bid[1])
            print(f"   ${price:>13,.2f}  {size:>13.6f} BTC")
        
        print(f"\n📉 ASK SIDE (Sell Orders):")
        print(f"   {'Price':<15} {'Size':<15}")
        print(f"   {'-'*30}")
        for ask in btc_book.asks[:5]:
            try:
                price = float(ask.price)
                size = float(ask.size)
            except AttributeError:
                price = float(ask[0])
                size = float(ask[1])
            print(f"   ${price:>13,.2f}  {size:>13.6f} BTC")
        
        print(f"\n💡 STRATEGY INSIGHTS:")
        print(f"   - If you place buy at ${best_bid:.2f}, you're at best bid")
        print(f"   - If you place sell at ${best_ask:.2f}, you're at best ask")
        print(f"   - Current spread is ${spread:.2f}")
        print(f"   - Your target spread is $5.00")
        
        if spread < 5:
            print(f"\n⚠️  WARNING: Market spread (${spread:.2f}) is LESS than your target ($5.00)")
            print(f"   Your orders may not fill unless you cross the spread!")
        else:
            print(f"\n✅ Market spread (${spread:.2f}) is wider than your target ($5.00)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fetching orderbook: {e}")
        return False

# Monitor orderbook
try:
    while True:
        if get_orderbook_data():
            print(f"\n{'─'*80}")
            print("Refreshing in 10 seconds... (Press Ctrl+C to stop)")
            time.sleep(10)
        else:
            print("Retrying in 5 seconds...")
            time.sleep(5)
            
except KeyboardInterrupt:
    print("\n\n✓ Monitoring stopped by user")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    
SYMBOL = "BTC/USD"
QTY = 0.001

SPREAD = 25            # USD
STOP_LOSS = 150        # USD
COOLDOWN_SECONDS = 120 # 2 minutes

POLL_INTERVAL = 2      # seconds

from alpaca.data.requests import CryptoLatestOrderbookRequest

def get_best_bid_ask(client):
    book = client.get_crypto_latest_orderbook(
        CryptoLatestOrderbookRequest(symbol_or_symbols=[SYMBOL])
    )[SYMBOL]

    best_bid = float(book.bids[0].price)
    best_ask = float(book.asks[0].price)

    return best_bid, best_ask


def cancel_all(trading_client):
    try:
        trading_client.cancel_orders()
    except:
        pass


def wait_for_fill(trading_client):
    while True:
        orders = trading_client.get_orders(status="open")
        if len(orders) == 0:
            return
        time.sleep(1)


def get_inventory(trading_client):
    try:
        pos = trading_client.get_position("BTCUSD")
        return float(pos.qty), float(pos.avg_entry_price)
    except:
        return 0.0, 0.0


import time
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def market_make_once(data_client, trading_client):
    # 1. Read orderbook
    best_bid, best_ask = get_best_bid_ask(data_client)

    buy_price  = best_bid
    sell_price = buy_price + SPREAD

    print(f"Placing BUY @ {buy_price} | SELL @ {sell_price}")

    # 2. Place BUY order first
    buy_order = trading_client.submit_order(
        LimitOrderRequest(
            symbol=SYMBOL,
            qty=QTY,
            side=OrderSide.BUY,
            limit_price=buy_price,
            time_in_force=TimeInForce.GTC
        )
    )

    # 3. Wait for BUY fill
    wait_for_fill(trading_client)

    inventory, entry_price = get_inventory(trading_client)
    if inventory == 0:
        print("Buy did not fill. Skipping cycle.")
        return False

    print(f"BUY FILLED @ {entry_price}")

    # 4. Place SELL order
    sell_order = trading_client.submit_order(
        LimitOrderRequest(
            symbol=SYMBOL,
            qty=QTY,
            side=OrderSide.SELL,
            limit_price=sell_price,
            time_in_force=TimeInForce.GTC
        )
    )

    # 5. Monitor SELL or STOP LOSS
    while True:
        best_bid, best_ask = get_best_bid_ask(data_client)
        mid = (best_bid + best_ask) / 2

        unrealized_pnl = (mid - entry_price) * inventory

        # STOP LOSS
        if unrealized_pnl <= -STOP_LOSS:
            print("🛑 STOP LOSS HIT")
            cancel_all(trading_client)

            # Market exit
            trading_client.submit_order(
                LimitOrderRequest(
                    symbol=SYMBOL,
                    qty=inventory,
                    side=OrderSide.SELL,
                    limit_price=best_bid,
                    time_in_force=TimeInForce.GTC
                )
            )

            wait_for_fill(trading_client)
            return "STOP"

        # SELL FILLED
        open_orders = trading_client.get_orders(status="open")
        if len(open_orders) == 0:
            print("✅ SELL FILLED — CYCLE COMPLETE")
            return "DONE"

        time.sleep(POLL_INTERVAL)

MAX_DAILY_LOSS = 300
daily_pnl = 0

while True:
    try:
        result = market_make_once(data_client, trading_client)

        if result == "STOP":
            daily_pnl -= STOP_LOSS

            # KILL SWITCH
            if daily_pnl <= -MAX_DAILY_LOSS:
                print("☠️ DAILY KILL SWITCH TRIGGERED")
                cancel_all(trading_client)
                break

            print("❄️ Cooling down for 2 minutes...")
            time.sleep(COOLDOWN_SECONDS)

        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        cancel_all(trading_client)
        time.sleep(10)
        
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus

def wait_for_fill(trading_client):
    while True:
        request = GetOrdersRequest(status=OrderStatus.OPEN)
        orders = trading_client.get_orders(request)

        if len(orders) == 0:
            return

        time.sleep(1)

def wait_for_order_fill(trading_client, order_id, timeout=60):
    start = time.time()

    while time.time() - start < timeout:
        order = trading_client.get_order_by_id(order_id)

        if order.status == "filled":
            return "FILLED"

        if order.status in ["canceled", "rejected"]:
            return "FAILED"

        time.sleep(1)

    return "TIMEOUT"

buy_order = trading_client.submit_order(...)

status = wait_for_order_fill(trading_client, buy_order.id)
def market_make_once():
    # your trading logic

    if status != "FILLED":
        print("Buy not filled, skipping cycle")
        return   # ✅ VALID

while True:
    try:
        market_make_once()
        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        cancel_all()
        time.sleep(10)

MIN_LIVE_SECONDS = 15




    
