# standard imports
import unittest
import os
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import OverrideGasOracle
from chainlib.connection import RPCConnection
from chainlib.eth.tx import (
        TxFactory,
        receipt,
        )
from hexathon import strip_0x

# local imports
from eth_owned.owned import ERC173

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

script_dir = os.path.realpath(os.path.dirname(__file__))


class TestInterface: #(EthTesterCase):

    def test_owned(self):
        c = ERC173(self.chain_spec)
        o = c.owner(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        owner = c.parse_owner(r)
        self.assertEqual(owner, strip_0x(self.accounts[0]))


    def test_transfer_ownership(self):
        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
        c = ERC173(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[2], self.accounts[1])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)
        
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = ERC173(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1])
        r = self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
 
        o = c.owner(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        owner = c.parse_owner(r)
        self.assertEqual(owner, strip_0x(self.accounts[1]))
      

#    def test_accept_ownership(self):
#        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
#        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1])
#        r = self.conn.do(o)
#
#        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.accept_ownership(self.address, self.accounts[2])
#        r = self.conn.do(o)
#
#        o = receipt(tx_hash_hex)
#        r = self.conn.do(o)
#        self.assertEqual(r['status'], 0)
#
#        nonce_oracle = RPCNonceOracle(self.accounts[1], self.conn)
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.accept_ownership(self.address, self.accounts[1])
#        r = self.conn.do(o)
#
#        o = receipt(tx_hash_hex)
#        r = self.conn.do(o)
#        self.assertEqual(r['status'], 1)
#
#        o = c.owner(self.address, sender_address=self.accounts[0])
#        r = self.conn.do(o)
#        owner = c.parse_owner(r)
#        self.assertEqual(owner, strip_0x(self.accounts[1]))
#
#
#    def test_take_ownership(self):
#        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
#        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.address)
#        r = self.conn.do(o)
#
#        (tx_hash_hex, o) = c.take_ownership(self.address, self.accounts[0], self.address)
#        r = self.conn.do(o)
#
#        o = receipt(tx_hash_hex)
#        r = self.conn.do(o)
#        self.assertEqual(r['status'], 1)
#
#        o = c.owner(self.address, sender_address=self.accounts[0])
#        r = self.conn.do(o)
#        owner = c.parse_owner(r)
#        self.assertEqual(owner, strip_0x(self.address))
#
#
#    def test_ownership_final(self):
#        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
#        gas_oracle = OverrideGasOracle(limit=8000000, conn=self.conn)
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1], final=True)
#        r = self.conn.do(o)
#
#        c = Owned(self.chain_spec, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle, signer=self.signer)
#        (tx_hash_hex, o) = c.transfer_ownership(self.address, self.accounts[0], self.accounts[1], final=True)
#        r = self.conn.do(o)
#        o = receipt(tx_hash_hex)
#        r = self.conn.do(o)
#        self.assertEqual(r['status'], 0)


if __name__ == '__main__':
    unittest.main()
