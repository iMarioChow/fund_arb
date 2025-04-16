import time
import threading
import sys
import os
from hyperliquid_local.sdk_wrapper import *
from bybit_local.sdk_wrapper_bybit import *

TRADE_USD = 10
LEVERAGE = 5

# Initialize global variables
open_positions_list = []


def safe_float(val, default=0.0):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return default


def get_safe_float(value):
    try:
        return float(value.get("value", 0.0)) if isinstance(value, dict) else float(value)
    except (ValueError, TypeError):
        return 0.0


def close_position_menu():
    # Hyperliquid positions
    hl_summary = get_account_summary()
    hl_positions = hl_summary.get("assetPositions", [])
    
    # Bybit positions
    bybit_positions = get_positions()
    open_positions_list = []
    if bybit_positions.get("retCode") == 0:
        for idx, pos in enumerate(bybit_positions.get("result", {}).get("list", []), 1):
            if safe_float(pos.get("size")) > 0:
                open_positions_list.append({
                    "index": idx,
                    "symbol": pos.get("symbol").replace("USDT", ""),
                    "side": pos.get("side"),
                    "size": safe_float(pos.get("size"))
                })
    
    # Display all positions
    if not hl_positions:
        print("✅ No Hyperliquid positions to close.")
        hl_has_positions = False
    else:
        hl_has_positions = True
        print("\nHyperliquid Positions:")
        for idx, p in enumerate(hl_positions, start=1):
            pos_data = p.get("position", {})
            symbol = pos_data.get("coin")
            szi = get_safe_float(pos_data.get("szi"))
            entry_px = get_safe_float(pos_data.get("entryPx"))
            print(f"{idx}. {symbol} | {szi:.4f} @ {entry_px:.2f}")

    if not open_positions_list:
        print("📭 No Bybit positions to close.")
        bybit_has_positions = False
    else:
        bybit_has_positions = True
        print("\nBybit Positions:")
        for pos in open_positions_list:
            print(f" {pos['index']}. {pos['symbol']} ({pos['side']}, Size: {pos['size']})")

    if not (hl_has_positions or bybit_has_positions):
        return

    try:
        sel = input("\nEnter position number to close (or 'cancel'): ").strip().lower()
        if sel == "cancel":
            return
        idx = int(sel) - 1

        # Close Hyperliquid position
        if idx < len(hl_positions):
            pos_data = hl_positions[idx].get("position", {})
            symbol = pos_data.get("coin")
            szi = get_safe_float(pos_data.get("szi"))
            if szi != 0:
                is_buy = szi < 0  # reverse direction for closing
                print(f"🔻 Closing HL position on {symbol}...")
                res = exchange.market_close(symbol)
                pretty_print(res)

        # Close Bybit position
        selected = next((p for p in open_positions_list if p["index"] == int(sel)), None)
        if selected:
            symbol = selected["symbol"]
            side = "Sell" if selected["side"] == "Buy" else "Buy"  # reverse the side
            qty = selected["size"]
            print(f"🔻 Closing Bybit {symbol} position ({side} side) with qty: {qty}")
            res = close_position(f"{symbol}USDT", side, qty)
            pretty_print(res)

    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    except Exception as e:
        print(f"⚠️ Error closing position: {e}")

def place_trade_both_exchanges():
    # Step 1: Ask for the exchange(s) to trade on
    exchange_choice = input("Select exchange to trade on (1. Bybit, 2. Hyperliquid, 3. Both): ").strip()

    if exchange_choice not in ('1', '2', '3'):
        print("❌ Invalid exchange choice.")
        return

    # Step 2: Ask for long/short and trade size
    side = input("🔘 Enter trade side (long/short): ").strip().lower()
    if side not in ("long", "short"):
        print("❌ Invalid side choice. Please choose 'long' or 'short'.")
        return

    try:
        trade_usd = float(input("💵 Trade size in USD (e.g., 50): ").strip())
    except ValueError:
        print("⚠️ Invalid trade size. Using default = $10.")
        trade_usd = 10

    # Ask for leverage
    try:
        leverage = float(input("📈 Leverage (e.g. 5): ").strip())
    except ValueError:
        leverage = 5
        print("⚠️ Invalid leverage. Using default = 5x.")

    # Step 3: Execute trade for Bybit or Hyperliquid, based on exchange choice

    if exchange_choice == '1' or exchange_choice == '3':  # Bybit
        # Ask for symbol
        symbol_input = input("🔍 Symbol (e.g. BTC): ").strip().upper()
        symbol = symbol_input if symbol_input.endswith("USDT") else f"{symbol_input}USDT"

        qty = calculate_qty(symbol, trade_usd)
        if qty <= 0:
            print("❌ Invalid quantity, cannot proceed.")
            return

        print(f"⚙️ Setting leverage {leverage}x for {symbol}...")
        set_leverage(symbol, buy_leverage=leverage, sell_leverage=leverage)

        print(f"📤 Placing {side.upper()} order on {symbol} with quantity: {qty}")
        result = place_market_order(symbol, side, qty)
        pretty_print(result)

    if exchange_choice == '2' or exchange_choice == '3':  # Hyperliquid
        try:
            symbol = input("🔍 Enter token symbol (e.g. BTC, ETH): ").strip().upper()
            asset_id, resolved_symbol = resolve_asset_id(symbol)
            if asset_id is None:
                print(f"❌ Could not resolve asset ID for {symbol}")
                return

            mids = get_all_mids()
            mark_px = float(mids.get(resolved_symbol, 0))

            funding_rate, next_funding_ts = get_predicted_funding(resolved_symbol)
            print(f"\n🔍 {resolved_symbol} Price: {mark_px:.2f} USD")
            print(f"📈 Predicted Funding Rate: {funding_rate:.4f}%")

            decision = input(f"💡 Trade {resolved_symbol}? (long / short / skip): ").strip().lower()
            if decision not in ("long", "short"):
                return

            # Size calculation and trade execution
            account_value = get_account_value()
            size = calculate_asset_size(resolved_symbol, mark_px, account_value, leverage, trade_usd)
            if size <= 0:
                return

            is_buy = decision == "long"
            print(f"{'🔼' if is_buy else '🔽'} Opening {decision.upper()} {size:.4f} {resolved_symbol} (ID: {asset_id})")
            result = place_market_order(asset=resolved_symbol, is_buy=is_buy, size=size, slippage=0.01)
            pretty_print(result)

        except Exception as e:
            print(f"⚠️ Error in search_token: {e}")
            
def display_status_fixed():
    hl_summary = get_account_summary()
    hl_account_value = safe_float(hl_summary.get("marginSummary", {}).get("accountValue"))
    hl_positions = hl_summary.get("assetPositions", [])
    hl_mids = get_all_mids()

    bybit_positions_data = get_positions()
    bybit_positions = bybit_positions_data.get("result", {}).get("list", []) if bybit_positions_data.get("retCode", -1) == 0 else []
    bybit_balances = get_wallet_balances()
    bybit_account_value = sum(
        safe_float(coin.get("equity"))
        for acc in bybit_balances.values()
        if acc.get("retCode") == 0
        for item in acc["result"]["list"]
        for coin in item.get("coin", [])
        if coin.get("coin") == "USDT"
    )

    hl_pnls = {}
    hl_position_map = {}
    for p in hl_positions:
        pos_data = p.get("position", {})
        symbol = pos_data.get("coin")
        szi = safe_float(pos_data.get("szi"))
        entry_px = safe_float(pos_data.get("entryPx"))
        mark_px = float(hl_mids.get(symbol, 0))
        unrealized_pnl = szi * (mark_px - entry_px)
        realized_pnl = safe_float(pos_data.get("realizedPnl", 0))
        hl_pnls[symbol] = unrealized_pnl + realized_pnl  # Net PnL
        hl_position_map[symbol] = pos_data

    bybit_pnls = {}
    bybit_position_map = {}
    if bybit_positions_data.get("retCode") == 0:
        for pos in bybit_positions:
            size = safe_float(pos.get("size"))
            if size == 0:
                continue
            symbol = pos.get("symbol").replace("USDT", "")
            unrealized_pnl = safe_float(pos.get("unrealisedPnl"))
            realized_pnl = safe_float(pos.get("cumRealisedPnl"))
            bybit_pnls[symbol] = unrealized_pnl + realized_pnl  # Net PnL
            bybit_position_map[symbol] = pos

    all_symbols = sorted(set(list(hl_pnls.keys()) + list(bybit_pnls.keys())))

    print("\n📊 Combined Trade Table")
    print("=================================================================================================================================")
    print(f"{'Symbol':<10}| {'HL Side':<8}| {'HL Sz':<8}| {'HL Entry':<10}| {'HL Net PnL':<8}|| {'BY Side':<8}| {'BY Sz':<8}| {'BY Entry':<10}| {'BY Net PnL':<8}|| {'Total Net PnL':<8}")
    print("---------------------------------------------------------------------------------------------------------------------------------")

    for symbol in all_symbols:
        hl = hl_position_map.get(symbol, {})
        hl_sz = safe_float(hl.get("szi"))
        hl_entry = safe_float(hl.get("entryPx"))
        hl_side = "LONG" if hl_sz > 0 else "SHORT" if hl_sz < 0 else "-"
        hl_net_pnl = f"{hl_pnls.get(symbol, 0.0):+.2f}"

        by = bybit_position_map.get(symbol, {})
        by_sz = safe_float(by.get("size"))
        by_entry = safe_float(by.get("avgEntryPrice"))
        if by_entry == 0 and by_sz > 0:
            by_entry = safe_float(by.get("positionValue")) / by_sz
        by_side = by.get("side", "-") if by else "-"
        by_net_pnl = f"{bybit_pnls.get(symbol, 0.0):+.2f}"

        total_net_pnl = hl_pnls.get(symbol, 0.0) + bybit_pnls.get(symbol, 0.0)

        print(f"{symbol:<10}| {hl_side:<8}| {hl_sz:<8.2f}| {hl_entry:<10.4f}| {hl_net_pnl:<8}|| {by_side:<8}| {by_sz:<8.2f}| {by_entry:<10.4f}| {by_net_pnl:<8}|| {total_net_pnl:+.2f}")

    total_net_pnl = sum(hl_pnls.get(sym, 0.0) + bybit_pnls.get(sym, 0.0) for sym in all_symbols)
    
    print("---------------------------------------------------------------------------------------------------------------------------------")
    print(f"💰 HL Account Value: {hl_account_value:.2f} USD | BYBIT Account Value: {bybit_account_value:.2f} USD | Total Value: {hl_account_value + bybit_account_value:.2f} USD")
    print(f"💸 Total Net PnL: {total_net_pnl:+.2f} USD")

    # Update Funding Rates Table with PnL calculation
    print("\n📈 Current Funding Rates (Hourly) & Expected Funding PnL")
    print("====================================================================================================")
    print(f"{'Symbol':<10}| {'HL Rate/h':<10}| {'BY Rate/h':<10}| {'Next Funding':<20}| {'Est. Funding/h':<25}")
    print("----------------------------------------------------------------------------------------------------")

    for symbol in all_symbols:
        hl_rate, hl_next = get_predicted_funding(symbol)
        by_rate, by_next = get_funding_info(f"{symbol}USDT")

        # Get position sizes and prices
        hl_sz = safe_float(hl_position_map.get(symbol, {}).get("szi", 0))
        by_sz = safe_float(bybit_position_map.get(symbol, {}).get("size", 0))
        by_side = bybit_position_map.get(symbol, {}).get("side", "-")
        if by_side == "Sell":
            by_sz = -by_sz

        hl_mark = float(hl_mids.get(symbol, 0))
        by_mark = safe_float(bybit_position_map.get(symbol, {}).get("markPrice", 0))
        if by_mark == 0:
            by_mark = hl_mark

        # Calculate funding PnL per hour
        if hl_sz > 0:  # Long position
            hl_funding_pnl = -(hl_sz * hl_mark * hl_rate / 100)
        else:  # Short position
            hl_funding_pnl = (abs(hl_sz) * hl_mark * hl_rate / 100)

        if by_sz > 0:  # Long position
            by_funding_pnl = -(by_sz * by_mark * by_rate / 100)
        else:  # Short position
            by_funding_pnl = (abs(by_sz) * by_mark * by_rate / 100)

        total_funding_pnl = hl_funding_pnl + by_funding_pnl

        # Calculate total position value for percentage
        hl_pos_value = abs(hl_sz * hl_mark) if hl_sz != 0 else 0
        by_pos_value = abs(by_sz * by_mark) if by_sz != 0 else 0
        total_pos_value = hl_pos_value + by_pos_value

        # Calculate percentage return
        hourly_pct = (total_funding_pnl / total_pos_value * 100) if total_pos_value > 0 else 0

        # Format next funding time
        next_funding_time = ""
        if hl_next:
            next_funding_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(hl_next / 1000))
        elif by_next:
            next_funding_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(by_next / 1000))

        # Format rates with consistent precision
        hl_rate_str = f"{hl_rate:>8.4f}%" if hl_rate != 0 else " " * 9
        by_rate_str = f"{by_rate:>8.4f}%" if by_rate != 0 else " " * 9

        # Format funding PnL with both USD and percentage
        if total_pos_value > 0:
            funding_display = f"{total_funding_pnl:>+.4f} USD ({hourly_pct:>+.4f}%/h)"
        else:
            funding_display = "-"

        print(f"{symbol:<10}| {hl_rate_str}| {by_rate_str}| {next_funding_time:<20}| {funding_display:<25}")

    print("----------------------------------------------------------------------------------------------------")
    # Add commands display at the end of status
    print("\n💡 Available Commands:")
    print("1. close - Close positions")
    print("2. quit  - Exit program")
    print("\n🎯 Enter command: ", end='', flush=True)


def auto_refresh():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        display_status_fixed()
        time.sleep(200)


def main():
    print("📟 Combined Trader v2")
    threading.Thread(target=auto_refresh, daemon=True).start()

    while True:
        print("\n💡 Available Commands:")
        print("1. open  - Open new positions")
        print("2. close - Close positions")
        print("3. refresh - Refresh status")
        print("4. quit  - Exit program")
        cmd = input("🎯 Enter command: ").strip().lower()

        if cmd == "open":
            place_trade_both_exchanges()
        elif cmd == "close":
            close_position_menu()
        elif cmd == "refresh":
            display_status_fixed()
        elif cmd == "quit":
            print("👋 Exiting.")
            break
        else:
            print("❌ Invalid command.")



if __name__ == "__main__":
    main()


