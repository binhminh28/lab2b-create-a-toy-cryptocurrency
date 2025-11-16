import unittest, secrets
from coin import Ledger, gen_secret, addr_from_secret, build_tx

class TestCoin(unittest.TestCase):
    # happy case cho giao dịch thành công
    def test_happy_path_and_nonce(self):
        l = Ledger()
        sk = gen_secret() # tạo secret key cho người gửi
        addr = addr_from_secret(sk) # tạo địa chỉ ví cho người gửi bằng sk
        to = addr_from_secret(gen_secret())  # tạo địa chỉ cho người nhận
        l.faucet(addr, 50.0) # nạp 50 đơn vị tiền cho địa chỉ của người gửi
        tx1 = build_tx(sk, to, 10.0, l.get_nonce(addr)) # tạo 1 giao dịch để gửi 10 coin 
        self.assertTrue(l.apply_tx(tx1)) # apply giao dịch tx1, expected là true
        tx2 = build_tx(sk, to, 5.0, l.get_nonce(addr)) # tạo 1 giao dịch để gửi 5 coin 
        self.assertTrue(l.apply_tx(tx2)) # apply giao dịch tx2, expected là true
        self.assertEqual(l.get_balance(addr), 35.0) # expected cho balance ví gửi gửi là 35.0 coin

    # test case cho trường hợp không đủ số dư
    def test_insufficient_balance(self):
        l = Ledger()
        sk = gen_secret() # tạo secret key cho người gửi
        addr = addr_from_secret(sk) # tạo địa chỉ ví cho người gửi bằng sk
        to = addr_from_secret(gen_secret()) # tạo địa chỉ cho người nhận
        l.faucet(addr, 5.0) # nạp 5 đơn vị tiền cho địa chỉ của người gửi
        tx = build_tx(sk, to, 10.0, l.get_nonce(addr)) # chuyển 10.0 đơn vị tiền cho người nhận
        self.assertFalse(l.apply_tx(tx)) # expected là false, do số dư người gửi là 5.0

if __name__ == "__main__":
    unittest.main()
