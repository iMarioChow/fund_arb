from pybit.unified_trading import HTTP
import json
import math
import pprint

import os
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path) as f:
    config = json.load(f)["bybit"]



# Initialize Bybit session
session = HTTP(
    testnet=config.get("testnet", False),
    api_key=config["api_key"],
    api_secret=config["api_secret"],
    log_requests=True
)

import time

def get_funding_info(symbol):
    try:
        data = session.get_tickers(category="linear", symbol=symbol)
        ticker = data["result"]["list"][0]

        # Correct variable names!
        prev_ts, next_ts = get_funding_periods(symbol)

        if prev_ts and next_ts:
            interval_ms = next_ts - prev_ts
            interval_hours = round(interval_ms / (1000 * 60 * 60*2), 2)

            predicted_funding = safe_float(ticker.get("fundingRate", 0)) * 100  # % per period

            return round(predicted_funding, 6), next_ts, interval_hours
        else:
            return 0.0, None, 0.0

    except Exception as e:
        print(f"⚠️ Failed to get funding info for {symbol}: {e}")
        return 0.0, None, 0.0


def safe_float(val, default=0.0):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return default

def close_selected_position():
    symbol_input = input("🔍 Enter Symbol to Close (e.g. BTC): ").strip().upper()
    symbol = symbol_input if symbol_input.endswith("USDT") else f"{symbol_input}USDT"
    core_symbol = symbol.replace("USDT", "")

    exchange_choice = input("🧭 Which exchange to close? [hl / bybit / all]: ").strip().lower()

    # === Close Hyperliquid
    if exchange_choice in ["hl", "all"]:
        hl_summary = get_account_summary()
        hl_positions = hl_summary.get("assetPositions", [])
        for p in hl_positions:
            pos_data = p.get("position", {})
            sym = pos_data.get("coin")
            if sym.upper() == core_symbol.upper():
                szi = safe_float(pos_data.get("szi"))
                if szi != 0:
                    is_buy = szi < 0  # Reverse the position
                    print(f"🔻 Closing HL position on {core_symbol} (size: {abs(szi)})...")
                    res = place_market_order(asset=core_symbol, is_buy=is_buy, size=abs(szi), slippage=0.01)
                    pretty_print(res)
                else:
                    print(f"ℹ️ No open HL position for {core_symbol}")
                break
        else:
            print(f"❌ No HL position found for {core_symbol}")

    # === Close Bybit
    if exchange_choice in ["bybit", "all"]:
        positions = get_positions()
        if positions["retCode"] == 0:
            pos_list = positions["result"]["list"]
            for pos in pos_list:
                sym = pos.get("symbol")
                if sym.upper() == symbol.upper():
                    size = safe_float(pos.get("size"))
                    side = pos.get("side")
                    if size > 0:
                        print(f"🔻 Closing BYBIT position on {symbol} (size: {size}, side: {side})...")
                        res = close_position(symbol, side, size)
                        pretty_print(res)
                    else:
                        print(f"ℹ️ No open BYBIT position for {symbol}")
                    break
            else:
                print(f"❌ No BYBIT position found for {symbol}")
        else:
            print(f"⚠️ Failed to get BYBIT positions: {positions.get('retMsg', 'Unknown error')}")

# === Wallet balances
def get_wallet_balances():
    balances = {}
    try:
        balances["UNIFIED"] = session.get_wallet_balance(accountType="UNIFIED")
    except Exception as e:
        balances["UNIFIED"] = {"retCode": -1, "retMsg": str(e)}
    try:
        balances["CONTRACT"] = session.get_wallet_balance(accountType="CONTRACT")
    except Exception as e:
        balances["CONTRACT"] = {"retCode": -1, "retMsg": str(e)}
    return balances

# === Get open positions
def get_positions():
    try:
        return session.get_positions(category="linear", settleCoin="USDT")
    except Exception as e:
        return {"retCode": -1, "retMsg": str(e)}


# === Get price
def get_price(symbol):
    try:
        data = session.get_tickers(category="linear", symbol=symbol)
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return 0.0

# === Get symbol precision
def get_symbol_precision(symbol):
    try:
        data = session.get_instruments_info(category="linear", symbol=symbol)
        item = data["result"]["list"][0]
        lot = item["lotSizeFilter"]
        min_qty = float(lot["minOrderQty"])
        step = float(lot["qtyStep"])
        precision = abs(int(round(-1 * math.log10(step)))) if step < 1 else 0
        return min_qty, step, precision
    except:
        return 0.01, 0.01, 2

# === Set leverage
def set_leverage(symbol, buy_leverage=5, sell_leverage=5):
    return session.set_leverage(
        category="linear",
        symbol=symbol,
        buyLeverage=str(buy_leverage),
        sellLeverage=str(sell_leverage)
    )

# === Place market order
def place_market_order_bybit(symbol, side, qty):
    return session.place_order(
        category="linear",
        symbol=symbol,
        side=side,
        orderType="Market",
        qty=qty
    )

# === Close position
def close_position(symbol, side, qty):
    close_side = "Sell" if side == "Buy" else "Buy"
    return place_market_order_bybit(symbol, close_side, qty)

# === Pretty print
def pretty_print(data):
    pprint.pprint(data)

def get_funding_periods(symbol):
    try:
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"

        history = session.get_funding_rate_history(
            category="linear",
            symbol=symbol,
            limit=5
        )

        entries = history["result"]["list"]
        timestamps = [int(entry["fundingRateTimestamp"]) for entry in entries]


        timestamps.sort(reverse=True)

        for i in range(len(timestamps) - 1):
            last_ts = timestamps[i]
            prev_ts = timestamps[i + 1]
            interval_ms = last_ts - prev_ts
            interval_h = interval_ms / (1000 * 60 * 60)

            if interval_ms > 0:
                next_ts = last_ts + interval_ms
                return prev_ts, next_ts

        print(f"❌ No valid interval found for {symbol}")
        return None, None

    except Exception as e:
        print(f"⚠️ Failed to get funding periods for {symbol}: {e}")
        return None, None



# === Test function
if __name__ == "__main__":
    test_symbols = ["MELANIAUSDT", "BTCUSDT", "ETHUSDT"]
    
    for symbol in test_symbols:
        print(f"\nTesting funding periods for {symbol}")
        last_ts, next_ts = get_funding_periods(symbol)
        
        if last_ts and next_ts:
            print(f"Last funding: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_ts/1000))}")
            print(f"Next funding: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_ts/1000))}")
            interval_hours = (next_ts - last_ts) / (1000 * 60 * 60)
            print(f"Interval: {interval_hours} hours")
        else:
            print("Failed to get funding periods")