#!/usr/bin/env python3
"""Generate vault encryption key and commitment salt for .env"""
import secrets

key = secrets.token_hex(32)
salt = secrets.token_hex(32)
print(f"\nAdd these to your .env:\n")
print(f"VAULT_ENCRYPTION_KEY={key}")
print(f"PRIVACY_COMMITMENT_SALT={salt}\n")
