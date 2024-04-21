# custom_filters.py
import requests
from django import template

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