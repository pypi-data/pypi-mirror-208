# external imports
from hexathon import (
        add_0x,
    )

# local imports
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractDecoder,
        ABIContractType,
        abi_decode_single,
    )
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.eth.tx import (
        TxFactory,
        TxFormat,
        )
from chainlib.eth.constant import ZERO_ADDRESS

class ERC173(TxFactory):

    def transfer_ownership(self, contract_address, sender_address, new_owner_address, final=False, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        if final:
            enc.method('transferOwnershipFinal')
        else:
            enc.method('transferOwnership')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(new_owner_address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def owner(self, contract_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('owner')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    @classmethod
    def parse_owner(self, v):
        return abi_decode_single(ABIContractType.ADDRESS, v)
