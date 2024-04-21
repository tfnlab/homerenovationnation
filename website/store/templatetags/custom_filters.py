# custom_filters.py
import requests
from django import template
import requests

register = template.Library()

@register.filter
def get_last_segment(value):
    return value.split('/')[-1]

@register.filter
def round_to_integer(value):
    return round(value)

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