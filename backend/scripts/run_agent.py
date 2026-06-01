#!/usr/bin/env python3
"""
Run Pulperp Privacy signal agent.

Usage:
    python scripts/run_agent.py                  # all markets, blind mode
    python scripts/run_agent.py SOL-PERP         # single market
    python scripts/run_agent.py SOL-PERP --full  # non-blind mode
"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import Config
from app.services.signal_generator import SignalGenerator
from app.utils.logger import get_logger

logger = get_logger("run_agent")


def print_signal(sig) -> None:
    icon = {"LONG": "🟢", "SHORT": "🔴", "NEUTRAL": "⚪"}.get(sig.direction, "⚪")
    blind_tag = "[BLIND]" if sig.blind_mode else "[FULL]"
    print(f"\n{'='*60}")
    print(f"{icon} {sig.symbol}  {sig.direction}  conf={sig.confidence:.0%}  {sig.timeframe}  {blind_tag}")
    print(f"   Price:     ${sig.price:,.2f}")
    print(f"   Funding:   {sig.funding_rate_8h*100:.4f}% (8h)")
    print(f"   OI Imbal:  {sig.oi_imbalance*100:+.1f}%")
    print(f"\n   Thesis: {sig.thesis}")
    if sig.risks:
        print(f"\n   Risks:")
        for r in sig.risks:
            print(f"     - {r}")
    if sig.privacy_note:
        print(f"\n   🫥 Privacy: {sig.privacy_note}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", nargs="?")
    parser.add_argument("--full", action="store_true", help="Disable blind mode")
    args = parser.parse_args()

    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    gen = SignalGenerator()
    blind = not args.full

    if args.symbol:
        symbol = args.symbol.upper()
        print_signal(gen.generate(symbol, blind=blind))
    else:
        signals = gen.generate_all(blind=blind)
        for s in signals:
            print_signal(s)


if __name__ == "__main__":
    main()
