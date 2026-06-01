import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.utils.helpers import (
    generate_commitment, generate_salt, mask_size,
    pct_change, clamp, safe_div, trim_context, annualized_funding,
)
from app.utils.cache import TTLCache
from app.utils.rate_limiter import RateLimiter, SlidingWindowLimiter


def test_commitment_deterministic():
    c1 = generate_commitment("value", "salt")
    c2 = generate_commitment("value", "salt")
    assert c1 == c2

def test_commitment_different_values():
    assert generate_commitment("a", "s") != generate_commitment("b", "s")

def test_salt_unique():
    salts = {generate_salt() for _ in range(50)}
    assert len(salts) == 50

def test_mask_size_buckets():
    assert mask_size(0.05) == "<0.1"
    assert mask_size(0.3) == "<0.5"
    assert mask_size(3.0) == "<5"
    assert mask_size(1500.0) == ">1000"

def test_pct_change():
    assert abs(pct_change(100, 110) - 10.0) < 0.001
    assert pct_change(0, 100) == 0.0

def test_clamp():
    assert clamp(5, 0, 1) == 1.0
    assert clamp(-1, 0, 1) == 0.0

def test_safe_div():
    assert safe_div(10, 2) == 5.0
    assert safe_div(10, 0) == 0.0

def test_trim_context():
    t = "x" * 20000
    r = trim_context(t, max_tokens=100)
    assert "[truncated]" in r

def test_annualized_funding():
    assert annualized_funding(0.0001) > 0

def test_ttl_cache():
    c = TTLCache(ttl=60)
    c.set("k", "v")
    assert c.get("k") == "v"
    c.delete("k")
    assert c.get("k") is None

def test_ttl_expiry():
    c = TTLCache(ttl=1)
    c.set("k", "v", ttl=0.01)
    time.sleep(0.05)
    assert c.get("k") is None

def test_rate_limiter():
    r = RateLimiter(calls_per_second=100, burst=5)
    assert r.acquire(timeout=1.0) is True

def test_sliding_window():
    s = SlidingWindowLimiter(max_calls=2, window_seconds=60)
    assert s.acquire() is True
    assert s.acquire() is True
    assert s.acquire() is False
