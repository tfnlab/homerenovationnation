# custom_filters.py
import requests
from django import template
import requests

from datetime import datetime

register = template.Library()

@register.filter
def format_timestamp(timestamp):
    try: 
        # Convert milliseconds to seconds
        timestamp_seconds = timestamp / 1000.0
        # Convert timestamp to datetime object
        created_datetime = datetime.fromtimestamp(timestamp_seconds)
        # Calculate time difference
        time_difference = datetime.now() - created_datetime
        # Format datetime object as desired
        formatted_date = created_datetime.strftime("%a, %d %b %Y")
        formatted_time = created_datetime.strftime("%H:%M:%S")
        # Format time elapsed
        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_elapsed = ""
        if days > 0:
            time_elapsed += f"{days} days "
        if hours > 0:
            time_elapsed += f"{hours} hours "
        if minutes > 0:
            time_elapsed += f"{minutes} minutes "
        if seconds > 0:
            time_elapsed += f"{seconds} seconds"
        return f"{formatted_date} at {formatted_time} ({time_elapsed})"

    except Exception as e:
        print("An error occurred:", e)
        return None  # or any other action you want to take upon encountering an error

@register.filter
def check_status_code(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False

@register.filter
def check_string(value):
    # Count the occurrences of '/' and '.'
    slash_count = value.count('/')
    dot_count = value.count('.')

    # Check conditions
    if slash_count > 2 or dot_count > 1:
        return False
    else:
        return True

@register.filter
def get_last_segment(value):
    return value.split('/')[-1]

@register.filter
def round_to_integer(value):
    try:
        return round(int(value))
    except Exception as e:
        print("An error occurred:", e)
        return None  # or any other action you want to take upon encountering an error

@register.filter
def compare_to_threshold(value, threshold):
    try:
        value = int(value)
        threshold = int(threshold)
        
        if value < threshold:
            return False
        else:
            return True
    except Exception as e:
        print("An error occurred:", e)
        return None  # or any other action you want to take upon encountering an error



@register.filter
def get_wallet_balance(wallet_address):
    # Initialize a Solana RPC client
    # Define RPC server details
    rpc_url = "https://weathered-long-wind.solana-mainnet.quiknode.pro/9c2a29380646c0e36d464da8c7424a981c931107/"  # Replace with your desired Solana RPC URL

    # Wallet address for which you want to check the balance
    wallet_address = wallet_address

    # JSON-RPC request payload to get balance
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }

    # Make the request
    try:
        response = requests.post(rpc_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        balance = data["result"]["value"]
        print("Balance:", balance)
        sol_balance = balance / 10**9        
        return sol_balance   
    except requests.exceptions.RequestException as e:
        print("Error:", e)
    
    # Convert lamports to SOL

def get_token_accounts(wallet_address, token_address):
    rpc_url = "https://weathered-long-wind.solana-mainnet.quiknode.pro/9c2a29380646c0e36d464da8c7424a981c931107/"  # Replace with your desired Solana RPC URL

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"mint": token_address}
        ]
    }

    try:
        response = requests.post(rpc_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data.get("result", [])
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return []

def get_token_account(wallet_address, token_address):
    token_accounts = get_token_accounts(wallet_address, token_address)
    for account in token_accounts:
        if account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("mint", "") == token_address:
            return account
    return None

@register.filter
def get_wallet_token_balance(wallet_address, token_address):
# Define RPC server details
    rpc_url = "https://weathered-long-wind.solana-mainnet.quiknode.pro/9c2a29380646c0e36d464da8c7424a981c931107/"  # Replace with your desired Solana RPC URL

    # Token address and wallet address for which you want to check the balance
    # JSON-RPC request payload to get token balance
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountBalance",
        "params": [
            wallet_address,
            {
                "encoding": "jsonParsed",
                "mint": get_token_accounts(wallet_address, token_address),
                "commitment": "confirmed"  # Example commitment level, replace with the desired commitment level
            }
        ]
    }



    # Make the request
    try:
        response = requests.post(rpc_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        print("Response:", data)  # Print response for debugging
        balance = data.get("result", {}).get("value", {}).get("uiAmount")
        if balance is not None:
            print("Token Balance:", balance)
        else:
            print("Token balance not found in response.")
        print("Token Balance:", balance)
        return balance
    except requests.exceptions.RequestException as e:
        print("Error:", e)    


def needs_red(symbol):
    return not symbol.startswith('$') or not symbol.isupper()