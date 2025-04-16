from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import json

# Load config
import os
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

ACCOUNT_ADDRESS = config["account_address"]
SECRET_KEY = config["secret_key"]

# Init wallet
wallet = Account.from_key(SECRET_KEY)

# Init clients (✅ CORRECT ORDER: wallet first, then URL)
exchange = Exchange(
    wallet,
    constants.MAINNET_API_URL,
    account_address=ACCOUNT_ADDRESS
)

info = exchange.info  # already initialized inside Exchange class

# === 📊 Account Info ===
def get_account_summary():
    return info.user_state(ACCOUNT_ADDRESS)

def get_open_orders():
    return info.open_orders(ACCOUNT_ADDRESS)

def get_user_fills():
    return info.user_fills(ACCOUNT_ADDRESS)

def get_user_rate_limit():
    return info.user_rate_limit(ACCOUNT_ADDRESS)

# === 📈 Limit Order
def place_limit_order(
    asset: str,
    is_buy: bool,
    size: float,
    price: float,
    tif: str = "Gtc",
    reduce_only: bool = False,
    cloid: str = None,
    builder: dict = None
):
    order_type = {"limit": {"tif": tif}}
    return exchange.order(
        name=asset,
        is_buy=is_buy,
        sz=size,
        limit_px=price,
        order_type=order_type,
        reduce_only=reduce_only,
        cloid=cloid,
        builder=builder
    )

# === ⚡️ Market Order
def place_market_order_hl(
    asset: str,
    is_buy: bool,
    size: float,
    slippage: float = 0.01,
    reduce_only: bool = False,
    cloid: str = None,
    builder: dict = None
):
    return exchange.market_open(
        name=asset,
        is_buy=is_buy,
        sz=size,
        slippage=slippage,
        cloid=cloid,
        builder=builder
    )

# ✅ API Wallet Approval (not needed in this version if wallet is handled in constructor)
def approve_api_wallet(api_wallet_address: str):
    return exchange.approve_agent(
        agent_address=api_wallet_address,
        privkey=SECRET_KEY
    )

# Pretty Printer
def pretty_print(data):
    import pprint
    pprint.pprint(data)


import requests
import time

def get_all_mids():
    try:
        response = requests.post(
            url="https://api.hyperliquid.xyz/info",
            json={"type": "allMids"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Failed to fetch mids: {response.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️ Error fetching mids: {e}")
        return {}

def get_predicted_funding(symbol):
    try:
        payload = {"type": "predictedFundings"}
        response = requests.post(
            url="https://api.hyperliquid.xyz/info",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            return 0.0, None

        data = response.json()
        for asset_entry in data:
            if asset_entry[0].upper() == symbol.upper():
                for venue, details in asset_entry[1]:
                    if venue == "HlPerp":
                        funding_rate = float(details.get("fundingRate", 0)) * 100
                        next_ts = details.get("nextFundingTime", None)

                        # Add 1 hour (3600000ms) to the current time for comparison
                        next_funding_time = next_ts + 3600000 if next_ts else None
                        if next_funding_time and next_funding_time > int(time.time() * 1000):
                            return funding_rate, next_funding_time
                        else:
                            return funding_rate, None
        return 0.0, None
    except Exception as e:
        print(f"⚠️ Failed to fetch predicted funding: {e}")
        return 0.0, None
