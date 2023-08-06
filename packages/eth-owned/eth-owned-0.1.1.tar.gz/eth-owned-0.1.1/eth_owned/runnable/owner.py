"""Query owner (EIP 173) of contract

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import sys
import os
import json
import argparse
import logging

# external imports
from funga.eth.signer import EIP155Signer
from funga.eth.keystore.dict import DictKeystore
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.error import JSONRPCException

# local imports
from eth_owned.owned import Owned

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

default_format = 'terminal'

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='RPC provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
#argparser.add_argument('-a', '--contract-address', dest='a', required=True, type=str, help='Contract address')
#argparser.add_argument('-f', '--format', dest='f', type=str, default=default_format, help='Output format [human, brief]')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('address', type=str, nargs='?', help='Address to check registration for')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

chain_spec = ChainSpec.from_chain_str(args.i)

rpc = EthHTTPConnection(args.p)
#account_registry_address = args.a
address = args.address


def main():
    c = Owned(chain_spec)
    o = c.owner(address)

    r = rpc.do(o)
    owner = c.parse_owner(r)
    print(owner)


if __name__ == '__main__':
    main()
