# Pulperp Privacy 🫥

<div align="center">

**The first privacy layer for Solana perpetual markets.**
*Your positions are nobody's business.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![CI](https://github.com/PulperpPrivacy/PulperpPrivacy/actions/workflows/ci.yml/badge.svg)](https://github.com/PulperpPrivacy/PulperpPrivacy/actions)
[![Solana](https://img.shields.io/badge/Solana-mainnet-9945FF.svg)](https://solana.com/)

</div>

---

## What is Pulperp Privacy?

Pulperp Privacy is an **open-source privacy infrastructure** for Solana perpetual markets.

On-chain perpetuals are fully transparent by design. Every position, every size, every liquidation price — visible to anyone with an RPC endpoint. Whales track you. Bots front-run you. The market knows your stop before you do.

Pulperp Privacy is the layer that changes that.

> *"Every trade you make on Solana perps is public. Your entry, your size, your liquidation. Pulperp Privacy is what you use when you'd rather they didn't know."*

### Core Features

- **Privacy Engine** — commitment-based position masking using hash commitments before revealing on-chain
- **Confidential Vault** — encrypted local position store; your sizes never leave your machine in plaintext
- **Stealth Signals** — LLM-generated market signals without exposing your trading history or strategy
- **ZK-Ready Architecture** — designed to plug into Solana ZK compression and light protocol when production-ready
- **Blind Analytics** — query market data (funding, OI, liquidations) without associating queries to a wallet
- **Web Dashboard** — dark, minimal Vue3 UI for position management and signal monitoring

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Pulperp Privacy                         │
│                                                           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │   Trader    │───▶│   Privacy    │───▶│   Vault     │  │
│  │  (you)      │    │   Engine     │    │  (encrypted)│  │
│  └─────────────┘    │  commit →    │    └─────────────┘  │
│                     │  mask →      │                      │
│                     │  reveal only │    ┌─────────────┐  │
│                     │  when needed │───▶│   Solana    │  │
│                     └──────┬───────┘    │   Mainnet   │  │
│                            │            └─────────────┘  │
│                     ┌──────▼───────┐                      │
│                     │ Stealth LLM  │                      │
│                     │  Signals     │                      │
│                     │  (no wallet  │                      │
│                     │   metadata)  │                      │
│                     └──────────────┘                      │
└──────────────────────────────────────────────────────────┘
```

---

## Narrative

Solana perps are the most watched order book in crypto.

Every liquidation is on-chain. Every large position shows up in OI data. Every time you open a 500k SOL-PERP long, three bots already know your liquidation price and are queuing up to push it there.

The infrastructure was never built with trader privacy in mind. It was built for speed and transparency — which are great properties for settlement, terrible properties for staying alive in a degen market.

Pulperp Privacy is the answer to that problem.

We didn't build a new DEX. We built a **privacy layer on top of existing Solana perp infrastructure** — Drift, Zeta, Mango — that lets you:

- Commit to a position before broadcasting it
- Store your sizes locally, encrypted, never in plaintext anywhere on-chain
- Generate trade signals from LLMs without attaching your wallet to the query
- Reveal only what the protocol requires, nothing more

The name is intentional. **Pulp** — raw, unfiltered, direct. **Perp** — perpetuals. **Privacy** — obvious.

We're not trying to be anonymous. We're trying to be untrackable by the people who want to trade against you.

---

## Quickstart

### Docker

```bash
git clone https://github.com/PulperpPrivacy/PulperpPrivacy.git
cd PulperpPrivacy
cp .env.example .env
docker compose up
```

Frontend: http://localhost:3000  
Backend: http://localhost:5001

### Manual

```bash
cd backend && pip install -e . && python run.py
cd frontend && npm install && npm run dev
```

---

## Configuration

```env
LLM_API_KEY=your_key
LLM_MODEL_NAME=claude-sonnet-4-6

SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
VAULT_ENCRYPTION_KEY=generate_with_script

PRIVACY_COMMITMENT_SALT=random_32_byte_hex
BLIND_QUERY_PROXY=true
```

---

## Supported Markets

| Protocol | Market | Privacy Status |
|----------|--------|---------------|
| Drift Protocol | SOL, BTC, ETH, WIF, BONK | ✅ Commitment-masked |
| Zeta Markets | SOL, BTC, ETH | 🔄 Beta |
| Mango v4 | SOL, BTC | 🔄 Beta |

---

## Project Structure

```
pulperp-privacy/
├── backend/
│   ├── app/
│   │   ├── api/          # position, signal, vault endpoints
│   │   ├── models/       # PrivatePosition, Commitment, Signal
│   │   ├── services/     # privacy engine, vault, LLM, Solana
│   │   └── utils/        # logger, cache, crypto helpers
│   └── scripts/          # agent runner, key generation
├── frontend/
│   └── src/
│       ├── views/        # Dashboard, Vault, Signals, Analytics
│       └── components/   # PositionCard, SignalFeed, VaultStatus
└── tests/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built on Solana. Privacy by design. Named after the pulp.</sub>
</div>
