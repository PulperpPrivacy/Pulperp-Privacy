from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import Config
from app.utils.logger import get_logger
from app.utils.retry import retry
from app.utils.rate_limiter import llm_limiter
from app.utils.helpers import trim_context

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are Pulperp — a privacy-first AI analyst for Solana perpetual markets.

You generate precise market signals based on on-chain data while deliberately omitting any wallet-identifying information.

Your analysis covers: funding rates, OI imbalance, liquidation cascades, basis, and market regime.

Respond in this exact format only:
DIRECTION: [LONG/SHORT/NEUTRAL]
CONFIDENCE: [0.0-1.0]
TIMEFRAME: [1h/4h/1d]
THESIS: [2-3 sentences, cite specific data]
RISKS: [bullet points starting with -]
PRIVACY_NOTE: [one line on what data was NOT used to protect trader identity]"""


@dataclass
class AnalystSignal:
    direction: str
    confidence: float
    timeframe: str
    thesis: str
    risks: list[str]
    privacy_note: str
    raw: str


class LLMAnalyst:
    def __init__(self, config: type = Config):
        self._api_key = config.LLM_API_KEY
        self._base_url = config.LLM_BASE_URL.rstrip("/")
        self._model = config.LLM_MODEL_NAME
        self._http = httpx.Client(timeout=60.0)

    def close(self) -> None:
        self._http.close()

    @retry(max_attempts=3, delay=2.0, backoff=2.0)
    def analyze(self, market_summary: str, blind: bool = True) -> AnalystSignal:
        llm_limiter.acquire()

        context = trim_context(market_summary)
        if blind:
            context = f"[BLIND MODE — no wallet metadata]\n\n{context}"

        user_msg = (
            f"Analyze this Solana perp market data and generate a privacy-preserving signal:\n\n"
            f"{context}\n\n"
            f"Do not reference any wallet address, position history, or trader identity."
        )

        is_anthropic = "anthropic" in self._base_url
        if is_anthropic:
            payload = {
                "model": self._model, "max_tokens": 600,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_msg}],
            }
            headers = {"x-api-key": self._api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
            resp = self._http.post(f"{self._base_url}/messages", headers=headers, json=payload)
        else:
            payload = {
                "model": self._model, "max_tokens": 600,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
            }
            headers = {"Authorization": f"Bearer {self._api_key}", "content-type": "application/json"}
            resp = self._http.post(f"{self._base_url}/chat/completions", headers=headers, json=payload)

        resp.raise_for_status()
        data = resp.json()
        raw = data["content"][0]["text"] if is_anthropic else data["choices"][0]["message"]["content"]
        return self._parse(raw)

    def _parse(self, raw: str) -> AnalystSignal:
        lines = raw.strip().split("\n")
        direction, confidence, timeframe, thesis, risks, privacy_note = "NEUTRAL", 0.5, "4h", "", [], ""
        for line in lines:
            line = line.strip()
            if line.startswith("DIRECTION:"):
                direction = line.split(":", 1)[1].strip().upper()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("TIMEFRAME:"):
                timeframe = line.split(":", 1)[1].strip()
            elif line.startswith("THESIS:"):
                thesis = line.split(":", 1)[1].strip()
            elif line.startswith("-") and thesis:
                risks.append(line[1:].strip())
            elif line.startswith("PRIVACY_NOTE:"):
                privacy_note = line.split(":", 1)[1].strip()
        return AnalystSignal(
            direction=direction, confidence=confidence, timeframe=timeframe,
            thesis=thesis, risks=risks, privacy_note=privacy_note, raw=raw,
        )
