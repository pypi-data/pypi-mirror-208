"""Adds a new Address declaration
.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import os
import logging

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from hexathon import (
        add_0x,
        strip_0x,
        )
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings


# local imports
from eth_address_declarator.declarator import AddressDeclarator

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    hsh = strip_0x(config.get('_POSARG'))
    if len(hsh) != 64:
        raise ValueError('declaration hash must be 32 bytes')
    config.add(hsh, '_DECLARATION')
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.WALLET | arg_flags.EXEC

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('declaration', type=str, help='SHA256 sum of endorsement data to add')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='declaration')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    conn = settings.get('CONN')
    c = AddressDeclarator(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('FEE_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )
    subject_address = to_checksum_address(settings.get('RECIPIENT'))
    contract_address = to_checksum_address(settings.get('EXEC'))

    (tx_hash_hex, o) = c.add_declaration(
            settings.get('EXEC'),
            settings.get('SENDER_ADDRESS'),
            settings.get('RECIPIENT'),
            add_0x(config.get('_DECLARATION')),
            )

    if settings.get('RPC_SEND'):
        conn.do(o)
        if config.true('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)

        print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()
