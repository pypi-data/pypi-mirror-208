# external imports
from chainlib.eth.tx import TxFormat
from chainlib.eth.tx import TxFactory
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.contract import ABIContractType
from hexathon import add_0x

class EthWriter(TxFactory):

    def __single_address_method(self, method, contract_address, sender_address, address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method(method)
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def add_writer(self, contract_address, sender_address, address, tx_format=TxFormat.JSONRPC):
        return self.__single_address_method('addWriter', contract_address, sender_address, address, tx_format)


    def delete_writer(self, contract_address, sender_address, address, tx_format=TxFormat.JSONRPC):
        return self.__single_address_method('deleteWriter', contract_address, sender_address, address, tx_format)


    def is_writer(self, contract_address, address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('isWriter')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        return o
