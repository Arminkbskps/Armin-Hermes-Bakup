#!/usr/bin/env python3
"""
Decrypt Electron safeStorage / VS Code SecretStorage blobs from state.vscdb.

Usage:
    python extract_electron_secrets.py --match ahefi
    python extract_electron_secrets.py --match ahefi --db path/to/state.vscdb --local-state path/to/Local\ State

Outputs JSON: { secret_name: plaintext_string, ... }
Requires: pip install cryptography  (already present in Hermes' Python)
Windows-only (DPAPI).
"""
import argparse
import base64
import ctypes
import json
import os
import sqlite3
import sys
from ctypes import wintypes

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    print("ERROR: pip install cryptography", file=sys.stderr)
    sys.exit(1)


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def dpapi_unprotect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    buf = ctypes.create_string_buffer(data, len(data))
    blob_in = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    ):
        raise OSError("DPAPI CryptUnprotectData failed (wrong user/machine?)")
    out = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    kernel32.LocalFree(blob_out.pbData)
    return out


def get_aes_key(local_state_path: str) -> bytes:
    with open(local_state_path, encoding="utf-8") as f:
        ls = json.load(f)
    enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])
    if enc_key[:5] != b"DPAPI":
        raise ValueError(f"unexpected prefix: {enc_key[:5]!r}")
    return dpapi_unprotect(enc_key[5:])


def decrypt_blob(buf: bytes, aes_key: bytes) -> str:
    if buf[:3] == b"v10":
        nonce, ct = buf[3:15], buf[15:]
        return AESGCM(aes_key).decrypt(nonce, ct, None).decode("utf-8", "replace")
    return dpapi_unprotect(buf).decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", required=True, help="substring to filter secret keys")
    ap.add_argument(
        "--db",
        default=os.path.join(
            os.environ.get("APPDATA", ""), "Code", "User", "globalStorage", "state.vscdb"
        ),
    )
    ap.add_argument(
        "--local-state",
        default=os.path.join(os.environ.get("APPDATA", ""), "Code", "Local State"),
    )
    args = ap.parse_args()

    aes_key = get_aes_key(args.local_state)
    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT key, value FROM ItemTable WHERE key LIKE 'secret://%' AND key LIKE ?",
        (f"%{args.match}%",),
    ).fetchall()
    con.close()

    if not rows:
        print(f"no secrets matching '{args.match}' in {args.db}", file=sys.stderr)
        sys.exit(2)

    results = {}
    for k, v in rows:
        name = json.loads(k.split("secret://", 1)[1])["key"]
        buf = bytes(json.loads(v)["data"])
        results[name] = decrypt_blob(buf, aes_key)

    json.dump(results, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
