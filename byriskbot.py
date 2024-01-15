
import ccxt
import time
import schedule
import pandas as pd
from pybit.unified_trading import HTTP



bybit = ccxt.bybit({
    'apiKey': 'i1UQddbDArbewF1ETS',
    'secret': 'VHyrOH6gKFjyyPf3zkceaNskQOEWM1Vj63bP',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }

})

# Create direct HTTP session instance
api_key = "i1UQddbDArbewF1ETS"
api_secret = "VHyrOH6gKFjyyPf3zkceaNskQOEWM1Vj63bP"

session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    testnet= True,#False
)

bybit.set_sandbox_mode(True) # activates testnet mode
#bybit future contract enable
bybit.options["dafaultType"] = 'future'
bybit.load_markets()
def get_balance():
    params ={'type':'swap', 'code':'USDT'}
    account = bybit.fetch_balance(params)['USDT']['total']
    print(account)
get_balance()
#stoploss


def kill_switch():
    try:
        positions = bybit.fetch_positions()
        print(f"{positions}information")
    
        for position in positions:
            if abs(position['contracts']) > 0:
                

                ds = position['id']
                symbol = position['symbol']
                entryPrice = position['entryPrice']
                amount = position['contracts']
                
                type = 'market'
                orderbook = bybit.fetch_l2_order_book(symbol)
                price = orderbook['asks'][0][0]
                
                print(f"{symbol} and {entryPrice}, {amount}")
                
                if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                    print("Skipping position pnl due to value being zero")
                    continue
                
                #pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
                pnl = position['unrealizedPnl'] * 100

                
                print(f"pnl {pnl} percent")
                

                
                    
                if pnl <= -4 or pnl >= 20:
                #print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                    print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                
            
                    if position['side'] =='short':
                        response = session.get_positions(
                            category="linear",
                            symbol="SOLUSDT",
                        )
                        print(f"{response}information")
                        positions = response['result']['list']
                        for position in positions:
                            unrealized_pnl = position['unrealisedPnl']
                            size = position['size']
                            
                            side = 'buy'
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
                    else :
                        response = session.get_positions(
                            category="linear",
                            symbol="SOLUSDT",
                        )
                        #print(f"{response}information")
                        positions = response['result']['list']
                        for position in positions:
                            
                            size = position['size']
                            
                            side = 'sell'
                            symbol = position['symbol']
                            order = session.place_order(
                                category="linear",
                                symbol=symbol,
                                side=side,
                                orderType="Market",
                                qty=size,
                                timeInForce="GTC",
                            )
                        
                        if order:
                            print(f"Position closed: {order}")
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

                        

# Run the kill switch function
kill_switch()
#schedule.every(20).seconds.do(kill_switch)

while True:
    schedule.run_pending()
    time.sleep(20)
