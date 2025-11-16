#!/usr/bin/env python3
import os, json, hashlib, secrets, argparse
from typing import Dict

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

# tạo ra mã băm sha-256 sau đó lấy 40 ký tự đầu 
def addr_from_secret(sk: bytes) -> str:
    return sha256_hex(sk)[:40]

class Ledger:
    # khởi tạo Ledger với:
    # - biến balances - lưu số dư dạng - ví dụ: {'address1':100.0}
    # - biến nonces - lưu số nonce của ví - ví dụ: {'address1': 0}
    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.nonces: Dict[str, int] = {}

    # nạp tiền vào 1 địa chỉ ví:
    # lấy số dư hiện tại của ví (nếu không có trả về 0.0) và cộng cho amount
    def faucet(self, address: str, amount: float):
        self.balances[address] = self.balances.get(address, 0.0) + float(amount)

    # lấy số dư hiện tại của ví (nếu không có trả về 0.0) 
    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0.0)

    # lấy số nonce hiện tại của ví, nếu chưa có giao dịch nào trả về 0.0 
    def get_nonce(self, address: str) -> int:
        return self.nonces.get(address, 0)

    # hàm lưu giao dịch vào ledger
    def apply_tx(self, tx: dict) -> bool:
        # Verify "signature" (toy)
        # shallow copy giao dịch
        unsigned = tx.copy()
        # lấy và xóa sig và sk_hex ra khỏi bản copy
        sig = unsigned.pop("signature", None)
        sk_hex = unsigned.pop("sk_hex", None)
        # nếu không có sig hoặc không có sk_hex thì return false
        if not sig or not sk_hex:
            return False
        # nếu có thì chuyển từ hex sang dạng bytes và thử tạo lại địa chỉ 
        sk = bytes.fromhex(sk_hex)
        expected_addr = addr_from_secret(sk)
        # so sánh địa chỉ giao dịch (bản copy) và địa chỉ thật từ trong body
        # nếu không khớp return false
        if tx["from"] != expected_addr:
            return False
        # nếu 2 địa chỉ khớp nhau thì
        # chuyển giao dịch copy thành chuỗi JSON và encode
        unsigned_json = json.dumps(unsigned, sort_keys=True).encode()
        # thử tạo lại chữ ký bằng cách băm khóa và nội dung giao dịch 
        expected_sig = sha256_hex(sk + unsigned_json)
        
        # so sánh chữ ký được tạo lại và chữ ký trong body
        # không khớp return false 
        if sig != expected_sig:
            return False

        # Nonce check
        nonce = unsigned["nonce"]
        # lấy số nonce từ trong body và so sánh với ledger
        # nếu không khớp return false
        if nonce != self.get_nonce(unsigned["from"]):
            return False

        # Balance check
        amount = float(unsigned["amount"])
        # lấy lấy số amount trong body và so sánh với balance của địa chỉ ví
        # balance < số tiền chuyển thì return false
        if self.get_balance(unsigned["from"]) < amount:
            return False

        # Apply
        # 3 kiểm tra signature, nonce và balance đều true 
        # thì cập nhật balance lại cho người gửi, người nhận,
        # tăng số nouce cho người gửi
        self.balances[unsigned["from"]] = self.get_balance(unsigned["from"]) - amount
        self.balances[unsigned["to"]] = self.get_balance(unsigned["to"]) + amount
        self.nonces[unsigned["from"]] = nonce + 1
        return True

#  hàm trả về 1 chuỗi 32 byte ngẫu nhiên
def gen_secret() -> bytes:
    return secrets.token_bytes(32)

#  hàm tạo 1 giao dịch
def build_tx(sk: bytes, to_addr: str, amount: float, nonce: int) -> dict:
    # tạo địa chỉ từ secret key
    from_addr = addr_from_secret(sk)
    # tạo body cho giao dịch
    body = {"from": from_addr, "to": to_addr, "amount": float(amount), "nonce": int(nonce)}
    # tạo chữ ký (sig) bằng cách băm sk và chuỗi JSON đã được encode của body
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

    sub.add_parser("send2")

    args = parser.parse_args()
    l = Ledger()

    if args.cmd == "genkey":
        sk = gen_secret() # tạo khóa bí mật
        addr = addr_from_secret(sk) # tạo địa chỉ từ khóa bí mật đó
        print("secret(hex):", sk.hex()) 
        print("address:", addr)
    elif args.cmd == "faucet":
        l.faucet(args.address, args.amount) # gọi hàm faucet để nạp tiền
        print("OK faucet")
    elif args.cmd == "balance":
        print(l.get_balance(args.address)) # lấy số dư
    elif args.cmd == "send":
        sk = bytes.fromhex(args.sk_hex) # lấy secret key từ hex (convert hex -> bytes)
        tx = build_tx(sk, args.to, args.amount, l.get_nonce(addr_from_secret(sk))) # gọi hàm tạo giao dịch
        l.faucet(addr_from_secret(sk), 100.0)  # seed balance for demo
        ok = l.apply_tx(tx) # lưu giao dịch vào ledger và in ra kết quả
        print("applied:", ok) 
        print("from:", l.get_balance(addr_from_secret(sk)))
        print("to:", l.get_balance(args.to))
    elif args.cmd == "send2": # bài tập gửi 2 giao dịch cùng address với nouce tăng dần
        sk = gen_secret()
        addr = addr_from_secret(sk)
        to = addr_from_secret(gen_secret())
        l.faucet(addr, 50.0)
        tx1 = build_tx(sk, to, 10.0, l.get_nonce(addr))
        ok = l.apply_tx(tx1)
        print(f"send 10.0 from {addr} to {to} is {ok} with nonce ({l.get_nonce(addr)}) -> balance {l.get_balance(addr)}")
        tx2 = build_tx(sk, to, 5.0, l.get_nonce(addr))
        ok = l.apply_tx(tx2)
        print(f"send 5.0 from {addr} to {to} is {ok} with nonce ({l.get_nonce(addr)}) -> balance {l.get_balance(addr)}")


    else:
        parser.print_help()

if __name__ == "__main__":
    main()
