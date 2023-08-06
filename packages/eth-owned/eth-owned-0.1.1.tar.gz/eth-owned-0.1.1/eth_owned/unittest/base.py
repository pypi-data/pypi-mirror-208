# standard imports
import unittest
import os
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import OverrideGasOracle
from chainlib.connection import RPCConnection
from chainlib.eth.tx import TxFactory
from chainlib.eth.tx import receipt
from hexathon import strip_0x

# local imports
from eth_owned import ERC173

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

script_dir = os.path.realpath(os.path.dirname(__file__))


class TestOwned(EthTesterCase):

    def setUp(self):
        super(TestOwned, self).setUp()
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)

        f = open(os.path.join(script_dir, '..', 'data', 'OwnedSimple.bin'))
        code = f.read()
        f.close()

        txf = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        tx = txf.template(self.accounts[0], None, use_nonce=True)
        tx = txf.set_code(tx, code)
        (tx_hash_hex, o) = txf.build(tx)

        r = self.conn.do(o)
        logg.debug('Owned test conrtact published with hash {}'.format(r))

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.address = r['contract_address']
