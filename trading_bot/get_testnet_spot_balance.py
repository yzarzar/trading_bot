import configparser
from binance.client import Client
import json
import sys

def get_spot_account_balance(symbol):
    try:
        # Fetch account information
        print("Fetching account information...")
        account_info = client.get_account()

        # Filter and return the balance of the specified asset
        for balance in account_info['balances']:
            if balance['asset'] == symbol:
                return balance['free']

        # If balance not found, return None
        return None

    except Exception as e:
        print(f"An error occurred while fetching account information: {e}")
        return None

if __name__ == "__main__":
    # Read API key and secret from config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('BINANCE', 'API_KEY')
    api_secret = config.get('BINANCE', 'API_SECRET')

    # Initialize Binance Client in testnet mode
    client = Client(api_key, api_secret, testnet=True)
    
    # Specify the asset symbol from command-line argument or config
    if len(sys.argv) > 1:
        asset_symbol = sys.argv[1]
    else:
        asset_symbol = 'USDT'  # Default to USDT if no symbol provided

    # Get the spot account balance for the specified asset
    balance = get_spot_account_balance(asset_symbol)

    if balance is not None:
        print(f"{asset_symbol} Balance: {balance}")
    else:
        print(f"Failed to fetch {asset_symbol} balance.")
