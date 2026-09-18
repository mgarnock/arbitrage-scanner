# Financial Arbitrage Scanner

A Python engine designed to detect and log cross-market sports arbitrage opportunities in real time by polling betting odds across multiple sportsbooks via REST APIs.

## Features
- **Real-Time Market Polling:** Queries external odds providers via RESTful API endpoints.
- **Arbitrage Detection:** Evaluates decimal and American odds across bookmakers to identify guaranteed profit spreads ($Implied\ Probability < 1.0$).
- **Optimal Stake Sizing:** Calculates risk-free bet allocations and bankroll distribution using two-way arbitrage formulas.
- **Automated Logging:** Aggregates and displays actionable spreads with current bookmaker pricing.

## Tech Stack
- **Language:** Python 3
- **Libraries:** `requests`, `json`
- **Concepts:** REST APIs, Dictionary Mapping, Algorithmic Stake Sizing

## Setup & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mgarnock/arbitrage-scanner.git](https://github.com/mgarnock/arbitrage-scanner.git)
   cd arbitrage-scanner
