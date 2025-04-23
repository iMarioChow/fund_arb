# 🚀 Fund Arbitrage Trading System

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

A sophisticated trading system enabling arbitrage trading between Hyperliquid and Bybit exchanges, focusing on funding rate arbitrage opportunities.

## �� Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

This system enables traders to:
- Execute synchronized trades across Hyperliquid and Bybit
- Monitor and capitalize on funding rate differentials
- Manage positions with real-time updates
- Track PnL and account values across exchanges

## ✨ Features

### Multi-Exchange Trading
- 🔄 Synchronized trading on Hyperliquid and Bybit
- 📊 Real-time position monitoring
- 🔍 Cross-exchange position management

### Funding Rate Arbitrage
- 📈 Real-time funding rate monitoring
- 💰 Arbitrage opportunity detection
- 📊 Hourly funding rate differentials
- 💵 Estimated funding arbitrage profits

### Position Management
- 🎯 Precision position sizing
- ⚖️ Automatic leverage management
- 🔄 Cross-exchange position synchronization
- 🛑 Selective or bulk position closing

### Real-time Monitoring
- �� Live account value tracking
- 📊 Position status updates
- 💰 PnL tracking
- ⏰ Auto-refresh functionality

## 🏗 Architecture

### Core Components

#### Main GUI (`main_gui_combined.py`)
```python
# Key functionalities
- User interface management
- Position control
- Status monitoring
- Command processing
```

#### Hyperliquid Integration (`hyperliquid_local/sdk_wrapper.py`)
```python
# Key functionalities
- API integration
- Account management
- Order execution
- Market data retrieval
```

#### Bybit Integration (`bybit_local/sdk_wrapper_bybit.py`)
```python
# Key functionalities
- API integration
- Position management
- Order execution
- Market data retrieval
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fund-arb.git
cd fund-arb
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
cp hyperliquid_local/config.example.json hyperliquid_local/config.json
cp bybit_local/config.example.json bybit_local/config.json
```

## 💻 Usage

### Available Commands
```bash
1. open   - Open new positions
2. close  - Close positions
3. refresh - Refresh status
4. quit   - Exit program
```

### Position Opening Process
1. Select exchange (Bybit/Hyperliquid)
2. Enter trade size (USD)
3. Set leverage
4. Enter symbol
5. System places opposite position

### Status Display
- Combined position table
- Funding rates and PnL
- Account values
- Auto-refresh (200s)

## ⚙️ Configuration

### Required Files
- `hyperliquid_local/config.json`
- `bybit_local/config.json`

### Configuration Structure
```json
{
    "hyperliquid": {
        "account_address": "YOUR_ADDRESS",
        "secret_key": "YOUR_SECRET_KEY"
    },
    "bybit": {
        "api_key": "YOUR_API_KEY",
        "api_secret": "YOUR_API_SECRET",
        "testnet": false
    }
}
```

## 🔒 Security

### Features
- 🔑 Secure API key management
- 🔐 Wallet approval system
- ⚠️ Comprehensive error handling
- 🛡️ Input validation

### Best Practices
- Never commit API keys
- Use environment variables
- Regular key rotation
- Monitor API usage

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.

---

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## 🙏 Acknowledgments

- Hyperliquid Team
- Bybit Team
- Open Source Community

---

Made with ❤️ by Mario
