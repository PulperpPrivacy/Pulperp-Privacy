import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.privacy_engine import PrivacyEngine
from app.utils.helpers import generate_salt


def make_engine():
    class FakeConfig:
        PRIVACY_COMMITMENT_SALT = generate_salt()
        VAULT_ENCRYPTION_KEY = ""
        BLIND_QUERY_PROXY = True
    return PrivacyEngine(config=FakeConfig)


def test_commit_returns_commitment():
    engine = make_engine()
    c = engine.commit_position("SOL-PERP", "LONG", 10.0, 150.0, 5.0)
    assert c.commitment_hash
    assert len(c.commitment_hash) == 64  # sha256 hex
    assert c.masked_size
    assert not c.revealed


def test_commit_different_sizes_different_hash():
    engine = make_engine()
    c1 = engine.commit_position("SOL-PERP", "LONG", 10.0, 150.0, 5.0)
    c2 = engine.commit_position("SOL-PERP", "LONG", 50.0, 150.0, 5.0)
    assert c1.commitment_hash != c2.commitment_hash


def test_reveal_marks_revealed():
    engine = make_engine()
    c = engine.commit_position("SOL-PERP", "LONG", 10.0, 150.0, 5.0)
    revealed = engine.reveal_commitment(c, 10.0, 150.0, 5.0)
    assert c.revealed is True
    assert c.reveal_hash is not None
    assert revealed.size == 10.0
    assert revealed.entry_price == 150.0


def test_blind_query_key_unique():
    engine = make_engine()
    k1 = engine.blind_query_key("wallet_abc")
    k2 = engine.blind_query_key("wallet_abc")
    assert k1 != k2  # nonce-based, always unique


def test_masked_size_does_not_reveal_exact():
    engine = make_engine()
    c = engine.commit_position("SOL-PERP", "LONG", 7.5, 150.0, 3.0)
    assert "7.5" not in c.masked_size
