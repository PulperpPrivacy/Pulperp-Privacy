import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.anthropic.com/v1")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "claude-sonnet-4-6")
    DEEPINFRA_API_KEY: str = os.getenv("DEEPINFRA_API_KEY", "")
    DEEPINFRA_BASE_URL: str = os.getenv("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    DEEPINFRA_MODEL_NAME: str = os.getenv("DEEPINFRA_MODEL_NAME", "meta-llama/Meta-Llama-3.1-70B-Instruct")

    # Solana
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    SOLANA_WS_URL: str = os.getenv("SOLANA_WS_URL", "wss://api.mainnet-beta.solana.com")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")
    HELIUS_RPC_URL: str = os.getenv("HELIUS_RPC_URL", "")

    # Privacy
    VAULT_ENCRYPTION_KEY: str = os.getenv("VAULT_ENCRYPTION_KEY", "")
    PRIVACY_COMMITMENT_SALT: str = os.getenv("PRIVACY_COMMITMENT_SALT", "")
    BLIND_QUERY_PROXY: bool = os.getenv("BLIND_QUERY_PROXY", "true").lower() == "true"

    # CoinGecko
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    COINGECKO_BASE_URL: str = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")

    # Flask
    DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("FLASK_PORT", "5001"))

    # Signal
    SIGNAL_CONFIDENCE_THRESHOLD: float = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.65"))
    MAX_LLM_CALLS: int = int(os.getenv("MAX_LLM_CALLS", "10"))
    SUPPORTED_MARKETS: list[str] = [
        m.strip()
        for m in os.getenv(
            "SUPPORTED_MARKETS",
            "SOL-PERP,BTC-PERP,ETH-PERP,WIF-PERP,BONK-PERP,JUP-PERP"
        ).split(",")
    ]

    @classmethod
    def validate(cls) -> None:
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required. Copy .env.example to .env")
        if not cls.SOLANA_RPC_URL:
            raise ValueError("SOLANA_RPC_URL is required")
