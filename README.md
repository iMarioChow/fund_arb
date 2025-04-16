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
```

###2. Create & activate a Python environment
   
```bash

conda create -n fund_arb python=3.11
conda activate fund_arb
```
Or using venv:
```bash
python3 -m venv venv
source venv/bin/activate
```
###3. Install dependencies
```bash
pip install -r requirements.txt
```
Dependencies include:
pybit, eth_account, websockets, requests, numpy, pandas, etc.

🔑 Configuration
🔐 Bybit API Keys
Set your API keys in:

```arduino
live/bybit_local/config.json
```
```bash
{
  "api_key": "YOUR_BYBIT_API_KEY",
  "api_secret": "YOUR_BYBIT_API_SECRET"
}
```
🔐 Hyperliquid Wallet
Place your wallet private key in:

```arduino
live/hyperliquid_local/config.json
```
```json
{
  "secret_key": "YOUR_PRIVATE_KEY"
}
```
⚠️ Do NOT commit this file to GitHub!
Consider using environment variables or secret managers for production.

🧪 Running the GUI Bot
```bash
python live/main_gui_combined.py
```
You'll see:
```sql
📊 Combined Trade Table
Symbol    | HL Side | HL Size | HL PnL | BY Side | BY Size | BY PnL | Net PnL
--------------------------------------------------------------------------------
```

💡 Available Commands:
1. open     - Open new positions
2. close    - Close positions
3. refresh  - Refresh current status
4. quit     - Exit program
Then type your desired action (e.g. open) and follow the prompts.

💡 Strategy: What This Bot Does
This bot opens hedged arbitrage positions:

Example: Long ETH on Bybit, short ETH on Hyperliquid

Profits from:

Funding rate differentials

Spread discrepancies

Targets delta-neutral exposure

Over time, you collect positive funding or profit from price mean reversion.

📈 Example Use
```bash
> open
Select exchange to long (1. Bybit, 2. Hyperliquid): 1
💵 Trade size in USD: 50
📈 Leverage: 10
🔍 Symbol: ETH

Placing BUY order on Bybit...
Placing SHORT order on Hyperliquid...
✅ Done.
```
🧠 Roadmap & Ideas
 Auto-trading based on funding thresholds

 CSV or database logging

 Discord/Telegram alerts

 Web dashboard or Streamlit GUI

 Add more exchanges (e.g. Binance, OKX)

🙏 Acknowledgements
Bybit API Docs

Hyperliquid Docs

pybit library

📜 License
MIT License © 2025 Mario Chow
