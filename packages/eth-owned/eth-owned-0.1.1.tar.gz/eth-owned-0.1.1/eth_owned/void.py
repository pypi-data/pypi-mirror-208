# standard imports
import logging
import json
import os

# external imports
from chainlib.eth.tx import (
        TxFactory,
        TxFormat,
        )
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractDecoder,
        ABIContractType,
        abi_decode_single,
        )
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.error import RequestMismatchException
from hexathon import (
        add_0x,
        strip_0x,
        )

logg = logging.getLogger()

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class VoidOwner(TxFactory):

    __abi = None
    __bytecode = None

    @staticmethod
    def abi():
        if VoidOwner.__abi == None:
            f = open(os.path.join(datadir, 'VoidOwner.json'), 'r')
            VoidOwner.__abi = json.load(f)
            f.close()
        return VoidOwner.__abi


    @staticmethod
    def bytecode():
        if VoidOwner.__bytecode == None:
            f = open(os.path.join(datadir, 'VoidOwner.bin'))
            VoidOwner.__bytecode = f.read()
            f.close()
        return VoidOwner.__bytecode


    @staticmethod
    def gas(code=None):
        return 500000


    def constructor(self, sender_address):
        code = VoidOwner.bytecode()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)
