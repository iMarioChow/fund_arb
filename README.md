# 💸 Funding Arbitrage Bot (Bybit + Hyperliquid)

This is a live arbitrage trading bot that monitors and trades between **Bybit** and **Hyperliquid** to profit from funding rate discrepancies. It allows you to manually or automatically open and close positions across both exchanges using a terminal-based GUI.

---

## 🚀 Features

- 🧮 **Real-Time Arbitrage Display**
  - View open positions across both exchanges with real-time PnL.
  - Tracks funding rates and expected funding PnL hourly.
  
- 🔁 **Dual-Exchange Trading**
  - Open hedged long/short trades across Bybit and Hyperliquid.
  - Automatically flips side on the opposite exchange.

- ⌨️ **Interactive Terminal GUI**
  - Type commands to open, close, or refresh your trades.

- 💹 **PnL & Funding Tracking**
  - Displays both realized and unrealized PnL.
  - Includes funding rate differentials and estimated impact.

- 🛠️ **Extensible Structure**
  - Easily add more exchanges, automation logic, or data logging.

---

## 📦 Setup

### 1. Clone the repo

```bash
git clone https://github.com/iMarioChow/fund_arb.git
cd fund_arb
