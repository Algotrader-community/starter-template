# risk managment 1.47 = stoploss = 0.4 multiplied by leverage(10) = 4 percent takeprofit = 0.65* 10 = 6.5
# idea close below ema 50 short the close or high above ema20 with stochastic greater 70 and adx above 25
#idea long close above ema 50 and close or high below ema20 with stochastic greater 24 and adx above 25

import ccxt
import pandas as pd
import pandas_ta as ta
import numpy
import time
import schedule
from pybit.unified_trading import HTTP

bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }

})


# Create direct HTTP session instance
api_key = ""
api_secret = ""

session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    testnet= False,
)


#bybit.set_sandbox_mode(True) # activates testnet mode
#bybit future contract enable
bybit.options["dafaultType"] = 'future'
bybit.load_markets()
def get_balance():
    params ={'type':'swap', 'code':'USDT'}
    account = bybit.fetch_balance(params)['USDT']['total']
    print(account)
get_balance()
#stoploss



#Step 4: Fetch historical data
symbol = 'AXS/USDT'
amount = 0.7 
type = 'market'
timeframe = '30m'
limit = 200
ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

# Convert the data into a pandas DataFrame for easy manipulation
df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Timestamp', inplace=True)
print(df)
# Step 5: Calculate technical indicators

#df.ta.ema(length=20, append=True)
a = ta.adx(df['High'], df['Low'], df['Close'], length = 14)
df = df.join(a)
#print(df)
df.ta.ema(length=11, append=True)
df.ta.ema(length=200, append=True)
df.ta.ema(length=50, append=True)
df.ta.ema(length=100, append=True)
df.ta.vwap(append=True)





print(df)
# Define the conditions for short and long trades
# close above ema200 but less than ema100 or ema 50, pullback close above ema 21, 11 or 9

long_condition = ((df["Close"] > df["EMA_200"])& (df["Close"] < df["EMA_100"])& (df["Close"] < df["EMA_11"]) & (df["Close"] < df["EMA_50"]) & (df["Close"] < df["VWAP_D"])& (df["EMA_50"] < df["VWAP_D"]) & (df["ADX_14"] > 23.4))

long_trades = df.loc[long_condition]
#print(long_trades)
# Define the conditions for short and long trades

#short_condition = ((df["Close"] < df["EMA_9"]) & (df["Close"] < df["VWAP_D"]) & (df["ADX_14"] > 25))


# Filter the DataFrame based on the conditions



# Step 3: Define the trading bot function

def trading_bot(df):
    try:

        positions = bybit.fetch_positions()

        check_positions = [position for position in positions if 'AXS' in position['symbol']]
        print(f"open position {positions}")
        openorder = bybit.fetch_open_orders(symbol='AXS/USDT')

        
        if not check_positions:
            # Step 6: Implement the trading strategy
            for i, row in df.iterrows():
                
                if not long_trades.empty:
                    response = session.place_order(
                        category="linear",
                        symbol="AXSUSDT",
                        side="Sell",
                        orderType="Market",
                        qty="1.3",
                        timeInForce="GTC",
                    )
                    
                    
                    print(f"long order placed: {response}")
                    #print(f"long order placed:")
                    time.sleep(60)
                    break
                
                        
                    # Step 7: Check for signals and execute trades
                    # Check if there is an open trade position
                    # If there is no open position, place a limit order to enter the trade at the current market price
                    #pass
                else:
                    print(f"checking for long signals")
                    
                    time.sleep(60)
                    break
        else:
            print("There is already an open position.")
            positions = bybit.fetch_positions()
            #print(f"{positions}information")
    
            for position in positions:
                if abs(position['contracts']) > 0:
                    

                    ids = position['id']
                    symbol = position['symbol']
                    entryPrice = position['entryPrice']
                    amount = position['contracts']
                    
                    
                    
                    print(f"{symbol} and {entryPrice}, {amount}")
                    
                    if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                        print("Skipping position pnl due to value being zero")
                        continue
                    
                    #pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
                    pnl = position['unrealizedPnl'] * 100

                    
                    print(f"pnl {pnl} percent")
                    
                        
                    if pnl <= -15 or pnl >= 29:
                    #print(f"Closing position for {symbol} with PnL: {pnl}%")
                    
                        print(f"Closing position for {symbol} with PnL: {pnl}%")
                    
                    
                
                        
                        response = session.get_positions(
                            category="linear",
                            symbol="AXSUSDT",
                        )
                        print(f"{response}information")
                        positions = response['result']['list']
                        for position in positions:
                            unrealized_pnl = position['unrealisedPnl']
                            size = position['size']
                            
                            side = 'Buy'
                            symbol = position['symbol']
                            order = session.place_order(
                                category="linear",
                                symbol=symbol,
                                side=side,
                                orderType="Market",
                                qty=size,
                                timeInForce="GTC",
                            )
                            
                            
                        print(f"long order placed: {order}")
                        if order:
                            print(f"Position closed: {order}")
                    
                
            time.sleep(20)

    except ccxt.RequestTimeout as e:
        print(f"A request timeout occurred: {e}")
        # Handle request timeout error

    except ccxt.AuthenticationError as e:
        print(f"An authentication error occurred: {e}")
        # Handle authentication error

    except ccxt.ExchangeError as e:
        print(f"An exchange error occurred: {e}")
        # Handle exchange error

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle all other unexpected errors

# Run the trading_bot function
trading_bot(df)

schedule.every(1).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(10)

