#!/usr/bin/env python3
import os, json, hashlib, secrets, argparse
from typing import Dict

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def addr_from_secret(sk: bytes) -> str:
    return sha256_hex(sk)[:40]

class Ledger:
    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.nonces: Dict[str, int] = {}

    def faucet(self, address: str, amount: float):
        self.balances[address] = self.balances.get(address, 0.0) + float(amount)

    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0.0)

    def get_nonce(self, address: str) -> int:
        return self.nonces.get(address, 0)

    def apply_tx(self, tx: dict) -> bool:
        # Verify "signature" (toy)
        unsigned = tx.copy()
        sig = unsigned.pop("signature", None)
        sk_hex = unsigned.pop("sk_hex", None)
        if not sig or not sk_hex:
            return False
        sk = bytes.fromhex(sk_hex)
        expected_addr = addr_from_secret(sk)
        if tx["from"] != expected_addr:
            return False
        unsigned_json = json.dumps(unsigned, sort_keys=True).encode()
        expected_sig = sha256_hex(sk + unsigned_json)
        if sig != expected_sig:
            return False

        # Nonce check
        nonce = unsigned["nonce"]
        if nonce != self.get_nonce(unsigned["from"]):
            return False

        # Balance check
        amount = float(unsigned["amount"])
        if self.get_balance(unsigned["from"]) < amount:
            return False

        # Apply
        self.balances[unsigned["from"]] = self.get_balance(unsigned["from"]) - amount
        self.balances[unsigned["to"]] = self.get_balance(unsigned["to"]) + amount
        self.nonces[unsigned["from"]] = nonce + 1
        return True

def gen_secret() -> bytes:
    return secrets.token_bytes(32)

def build_tx(sk: bytes, to_addr: str, amount: float, nonce: int) -> dict:
    from_addr = addr_from_secret(sk)
    body = {"from": from_addr, "to": to_addr, "amount": float(amount), "nonce": int(nonce)}
    sig = sha256_hex(sk + json.dumps(body, sort_keys=True).encode())
    # attach sk_hex ONLY for toy verify; trong thực tế KHÔNG BAO GIỜ làm vậy.
    body["signature"] = sig
    body["sk_hex"] = sk.hex()
    return body

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("genkey")
    faucet_p = sub.add_parser("faucet")
    faucet_p.add_argument("address")
    faucet_p.add_argument("amount", type=float)

    bal_p = sub.add_parser("balance")
    bal_p.add_argument("address")

    send_p = sub.add_parser("send")
    send_p.add_argument("sk_hex")
    send_p.add_argument("to")
    send_p.add_argument("amount", type=float)

    args = parser.parse_args()
    l = Ledger()

    if args.cmd == "genkey":
        sk = gen_secret()
        addr = addr_from_secret(sk)
        print("secret(hex):", sk.hex())
        print("address:", addr)
    elif args.cmd == "faucet":
        l.faucet(args.address, args.amount)
        print("OK faucet")
    elif args.cmd == "balance":
        print(l.get_balance(args.address))
    elif args.cmd == "send":
        sk = bytes.fromhex(args.sk_hex)
        tx = build_tx(sk, args.to, args.amount, l.get_nonce(addr_from_secret(sk)))
        l.faucet(addr_from_secret(sk), 100.0)  # seed balance for demo
        ok = l.apply_tx(tx)
        print("applied:", ok)
        print("from:", l.get_balance(addr_from_secret(sk)))
        print("to:", l.get_balance(args.to))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
