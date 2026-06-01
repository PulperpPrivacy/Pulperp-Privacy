# Pulperp Privacy

## Overview
Privacy layer for Solana perpetual markets. Commitment-based position masking, encrypted vault, LLM blind signals, blind analytics.

## Stack
- **Backend**: Python 3.11, Flask 3.0, httpx
- **Frontend**: Vue 3 + Vite, Pinia, Axios
- **AI**: Anthropic Claude (primary), DeepInfra (fallback)
- **Chain**: Solana RPC (Helius preferred)

## Structure
```
backend/app/
  config.py             — env config
  api/
    position.py         — open/close/list positions
    signal.py           — generate blind signals
    vault.py            — vault status, commit, keygen
  models/
    position.py         — PrivatePosition
  services/
    solana_client.py    — RPC + CoinGecko price
    privacy_engine.py   — commitment scheme, blind query keys
    vault_manager.py    — encrypted position storage
    llm_analyst.py      — blind LLM signal generation
    signal_generator.py — orchestrates signal pipeline
  utils/
    logger, cache, rate_limiter, retry, helpers (crypto utils)

frontend/src/
  views/Dashboard.vue   — stats + open position form
  views/Vault.vue       — all positions table
  views/Signals.vue     — blind signal feed
  views/Analytics.vue   — per-market blind analysis

tests/
  test_utils.py
  test_privacy_engine.py
  test_vault_manager.py
```

## API
- `POST /api/position/open` — `{symbol, direction, size, entry_price, leverage}`
- `POST /api/position/:id/close` — `{exit_price}`
- `GET  /api/position/` — list all positions (masked by default)
- `POST /api/signal/generate` — `{symbol, blind?}`
- `GET  /api/vault/status`
- `GET  /api/vault/keygen` — generate VAULT_ENCRYPTION_KEY + PRIVACY_COMMITMENT_SALT

## Privacy design
- Position sizes masked via `mask_size()` buckets in all public API responses
- Commitments: H(symbol || direction || size || entry || leverage || nonce || salt)
- Blind query keys rotate per request to prevent wallet-RPC correlation
- LLM queries sent in BLIND MODE — no wallet info in context

## Dev
```bash
npm run dev
pytest tests/ -v
python backend/scripts/keygen.py  # generate secrets
```
