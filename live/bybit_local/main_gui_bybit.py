import math
import time
from datetime import datetime
from sdk_wrapper_bybit import *

TRADE_USD = 10


def safe_float(val, default=0.0):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return default


def display_status():
    print("\n==============================")
    balances = get_wallet_balances()

    print("💰 Wallet Balances:")
    for account_type, data in balances.items():
        if data and data.get("retCode") == 0:
            print(f"\n→ {account_type} Account")
            for item in data["result"]["list"]:
                for coin in item.get("coin", []):
                    symbol = coin.get("coin")
                    equity = safe_float(coin.get("equity", 0))
                    available = safe_float(coin.get("availableToWithdraw", 0))
                    if equity > 0:
                        print(f"   {symbol}: {equity:.4f} ")
        else:
            continue
    global open_positions_list
    open_positions_list = []

    positions = get_positions()
    if positions["retCode"] == 0:
        print("\n📊 Open Positions:")
        index = 1
        for pos in positions["result"]["list"]:
            size = safe_float(pos.get("size", 0))
            if size == 0:
                continue

            symbol = pos.get("symbol")
            side = pos.get("side", "-")

            position_value = safe_float(pos.get("positionValue", 0))
            entry_price = safe_float(pos.get("avgEntryPrice", 0))
            if entry_price == 0 and size > 0 and position_value > 0:
                entry_price = position_value / size  # fallback estimate

            mark_price = safe_float(pos.get("markPrice", 0))
            pnl = safe_float(pos.get("unrealisedPnl", 0))
            entry_value = size * entry_price
            pnl_percent = ((pnl / abs(entry_value)) * 100) if entry_value else 0

            # Get fresh funding rate and next funding time
            funding_rate, next_funding_time = get_funding_info(symbol)

            print(f"\n{index}. {symbol} Position")
            print(f"   Size          : {size:.4f}")
            if entry_price > 0:
                print(f"   Entry Price   : {entry_price:.5f}")
            else:
                print(f"   Entry Price   : Pending (not filled yet)")
            print(f"   Mark Price    : {mark_price:.5f}")
            print(f"   PnL           : {pnl:.4f} USD")
            print(f"   PnL %%        : {pnl_percent:.5f}%")
            print(f"   Entry Value   : {entry_value:.4f} USD")
            print(f"   Funding Rate  : {funding_rate:.4f}%")
            if next_funding_time:
                try:
                    ts = int(next_funding_time)
                    now = int(time.time() * 1000)
                    diff_sec = max((ts - now) / 1000, 0)
                    readable_time = datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S UTC')
                    hours, rem = divmod(int(diff_sec), 3600)
                    minutes, seconds = divmod(rem, 60)
                    print(f"   Next Funding  : {readable_time} (in {hours}h {minutes}m {seconds}s)")
                except:
                    print(f"   Next Funding  : {next_funding_time}")

            open_positions_list.append({
                "index": index,
                "symbol": symbol,
                "side": side,
                "size": size
            })
            index += 1

        if index == 1:
            print("   📭 No open positions.")
    else:
        print("⚠️ Error fetching positions.")


def calculate_qty(symbol, usd_value):
    price = get_price(symbol)
    if price <= 0:
        return 0.0

    min_qty, step, precision = get_symbol_precision(symbol)
    raw_qty = usd_value / price
    rounded_qty = math.floor(raw_qty / step) * step
    return round(max(rounded_qty, min_qty), precision)


def place_trade(side):
    symbol_input = input("🔍 Symbol (e.g. BTC): ").strip().upper()
    symbol = symbol_input if symbol_input.endswith("USDT") else f"{symbol_input}USDT"

    try:
        usd = float(input("💵 Trade Size USD (e.g. 10): ").strip())
    except:
        usd = TRADE_USD
        print(f"⚠️ Invalid input, defaulting to {usd} USD")

    try:
        lev = float(input("📈 Leverage (e.g. 5): ").strip())
    except:
        lev = 5
        print("⚠️ Invalid leverage, defaulting to 5x")

    qty = calculate_qty(symbol, usd)
    if qty <= 0:
        print("❌ Invalid quantity, cannot proceed.")
        return

    print(f"⚙️ Setting leverage {lev}x for {symbol}...")
    set_leverage(symbol, buy_leverage=lev, sell_leverage=lev)

    print(f"📤 Placing {side.upper()} order on {symbol} with quantity: {qty}")
    result = place_market_order(symbol, side, qty)
    pretty_print(result)


def close_trade():
    if not open_positions_list:
        print("📭 No open positions to close.")
        return

    print("\nSelect position to close:")
    for pos in open_positions_list:
        print(f" {pos['index']}. {pos['symbol']} ({pos['side']}, Size: {pos['size']})")

    try:
        choice = int(input("Enter position number to close: ").strip())
        selected = next((p for p in open_positions_list if p["index"] == choice), None)

        if not selected:
            print("❌ Invalid selection.")
            return

        symbol = selected["symbol"]
        side = selected["side"]
        qty = selected["size"]

        print(f"📤 Closing {symbol} position ({side} side) with qty: {qty}")
        result = close_position(symbol, side, qty)
        pretty_print(result)

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("📟 Bybit Manual Trader [Pybit Edition]")
    import threading

    def auto_refresh():
        while True:
            display_status()
            time.sleep(10)

    # Start background thread for auto-refresh
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()

    while True:
        cmd = input("\n🕹 Command [long / short / close / quit]: ").strip().lower()
        if cmd == "":
            continue  # Let it keep refreshing
        elif cmd == "long":
            place_trade("Buy")
        elif cmd == "short":
            place_trade("Sell")
        elif cmd == "close":
            close_trade()
        elif cmd == "quit":
            print("👋 Exiting bot.")
            break
        else:
            print("❌ Invalid command. Use: long / short / close / quit")


if __name__ == "__main__":
    open_positions_list = []
    main()
