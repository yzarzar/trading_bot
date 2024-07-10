import configparser
from binance.client import Client
import json
import math

def get_balance_for_asset(asset_symbol):
    # Fetch account information
    print("Fetching account information...")
    account_info = client.futures_account()
    print("Account information fetched successfully.")

    # Extract the balance information for the specified asset
    for asset in account_info['assets']:
        if asset['asset'] == asset_symbol:
            return asset

    return None

def get_symbol_info(symbol):
    exchange_info = client.futures_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            return s
    return None

def place_order(symbol, side, quantity):
    try:
        # Place a market order
        print(f"Placing {side} order for {quantity} {symbol}...")
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print("Order placed successfully.")
        return order
    except Exception as e:
        print(f"An error occurred while placing the order: {e}")
        return None

def get_current_price(symbol):
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"An error occurred while fetching the current price: {e}")
        return None

if __name__ == "__main__":
    # Read API key and secret from config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('BINANCE', 'API_KEY')
    api_secret = config.get('BINANCE', 'API_SECRET')

    # Initialize Binance Client
    client = Client(api_key, api_secret, testnet=True)

    # Specify the asset symbol you are interested in
    asset_symbol = 'USDT'
    
    # Get the balance for the specified asset
    balance = get_balance_for_asset(asset_symbol)
    
    if balance:
        # Convert the balance dictionary to a JSON string
        balance_json = json.dumps(balance, indent=4)
        print(f"Balance information for {asset_symbol} in JSON format:\n{balance_json}")
    else:
        print(f"No balance information found for {asset_symbol}.")

    # Example of placing an order
    order_symbol = 'BTCUSDT'  # The trading pair symbol
    order_side = 'BUY'        # The side of the order, either 'BUY' or 'SELL'
    
    # Get the current price of the asset
    current_price = get_current_price(order_symbol)
    
    if current_price:
        # Calculate the minimum order quantity to meet the 100 USDT notional value requirement
        min_notional_value = 100  # Minimum notional value in USDT
        order_quantity = min_notional_value / current_price

        # Get symbol info to determine the correct step size
        symbol_info = get_symbol_info(order_symbol)
        if symbol_info:
            step_size = float([f['stepSize'] for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'][0])
            min_qty = float([f['minQty'] for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'][0])
            max_qty = float([f['maxQty'] for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'][0])

            # Ensure quantity is a multiple of step size and within the allowed range
            order_quantity = max(min_qty, min(max_qty, math.floor(order_quantity / step_size) * step_size))
            
            # Check if the order quantity meets the minimum notional value requirement
            notional_value = order_quantity * current_price
            if notional_value < min_notional_value:
                # Adjust the order quantity to meet the minimum notional value
                order_quantity = math.ceil(min_notional_value / current_price / step_size) * step_size
                print(f"Adjusted order quantity to meet minimum notional value: {order_quantity}")

            # Place the order
            order_response = place_order(order_symbol, order_side, order_quantity)
            
            if order_response:
                # Convert the order response to a JSON string
                order_response_json = json.dumps(order_response, indent=4)
                print(f"Order response in JSON format:\n{order_response_json}")
        else:
            print(f"Failed to fetch symbol info for {order_symbol}, order not placed.")
    else:
        print("Failed to fetch the current price, order not placed.")
