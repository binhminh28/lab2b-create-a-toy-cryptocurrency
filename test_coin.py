import unittest, secrets
from coin import Ledger, gen_secret, addr_from_secret, build_tx

class TestCoin(unittest.TestCase):
    def test_happy_path_and_nonce(self):
        l = Ledger()
        sk = gen_secret()
        addr = addr_from_secret(sk)
        to = addr_from_secret(gen_secret())
        l.faucet(addr, 50.0)
        tx1 = build_tx(sk, to, 10.0, l.get_nonce(addr))
        self.assertTrue(l.apply_tx(tx1))
        tx2 = build_tx(sk, to, 5.0, l.get_nonce(addr))
        self.assertTrue(l.apply_tx(tx2))
        self.assertEqual(l.get_balance(addr), 35.0)

    def test_insufficient_balance(self):
        l = Ledger()
        sk = gen_secret()
        addr = addr_from_secret(sk)
        to = addr_from_secret(gen_secret())
        l.faucet(addr, 5.0)
        tx = build_tx(sk, to, 10.0, l.get_nonce(addr))
        self.assertFalse(l.apply_tx(tx))

if __name__ == "__main__":
    unittest.main()
