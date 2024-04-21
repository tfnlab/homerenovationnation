# custom_filters.py
from django import template
from solana.account import Account
from solana.rpc.api import Client

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
    rpc_client = Client("https://api.mainnet-beta.solana.com")

    # Get account information
    account_info = rpc_client.get_account_info(wallet_address)
    
    # Check if the account exists
    if account_info is None:
        print("Account not found.")
        return None
    
    # Decode the account data to extract the balance
    balance = account_info["result"]["value"]["lamports"]
    
    # Convert lamports to SOL
    sol_balance = balance / 10**9
    
    return sol_balance   