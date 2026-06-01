import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.vault_manager import VaultManager, _vault


def setup_function():
    _vault.clear()


def make_vault():
    class FakeConfig:
        VAULT_ENCRYPTION_KEY = ""
        BLIND_QUERY_PROXY = True
    return VaultManager(config=FakeConfig)


def test_store_and_retrieve():
    v = make_vault()
    e = v.store("SOL-PERP", "LONG", 10.0, 150.0, 5.0)
    assert e.id
    assert v.get(e.id) is not None


def test_public_dict_masks_size():
    v = make_vault()
    e = v.store("SOL-PERP", "LONG", 7.5, 150.0, 3.0)
    d = e.to_dict(private=False)
    assert "size" not in d
    assert "masked_size" in d
    assert "7.5" not in d.get("masked_size", "")


def test_private_dict_reveals_size():
    v = make_vault()
    e = v.store("SOL-PERP", "SHORT", 25.0, 200.0, 10.0)
    d = e.to_dict(private=True)
    assert d["size"] == 25.0


def test_close_position_pnl():
    v = make_vault()
    e = v.store("SOL-PERP", "LONG", 10.0, 100.0, 2.0)
    closed = v.close_position(e.id, 110.0)
    assert closed.status == "closed"
    assert closed.pnl_pct is not None
    assert closed.pnl_pct > 0  # long, price went up


def test_close_short_pnl():
    v = make_vault()
    e = v.store("SOL-PERP", "SHORT", 10.0, 100.0, 2.0)
    closed = v.close_position(e.id, 90.0)
    assert closed.pnl_pct > 0  # short, price went down → profit


def test_summary():
    v = make_vault()
    v.store("SOL-PERP", "LONG", 1.0, 100.0, 1.0)
    v.store("BTC-PERP", "SHORT", 0.1, 50000.0, 3.0)
    s = v.summary()
    assert s["total"] == 2
    assert s["open"] == 2
