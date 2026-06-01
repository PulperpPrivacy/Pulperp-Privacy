# Contributing to Pulperp Privacy

PRs welcome.

## Setup

```bash
git clone https://github.com/PulperpPrivacy/PulperpPrivacy.git
cd PulperpPrivacy
cp .env.example .env
python backend/scripts/keygen.py  # generate vault keys
npm run setup
```

## Tests

```bash
pytest tests/ -v
```

No API keys needed for tests.

## Commits

Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`

## What we want

- Real ZK proof integration (Solana ZK compression, Light Protocol)
- Actual on-chain commitment verification
- Encrypted file-based vault (AES-256)
- WebSocket streaming for live market data
- Homomorphic commitment schemes for position aggregation
