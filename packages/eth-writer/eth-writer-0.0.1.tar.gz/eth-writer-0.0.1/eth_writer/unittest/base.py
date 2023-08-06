# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt

# local imports
from eth_writer import EthWriter


class TestEthWriterInterface:

    def test_add_delete(self):
        writer_contract_address = self.contracts['writer']
        publisher_address = self.roles.get('publisher')
        writer_account = self.roles['writer']

        nonce_oracle = RPCNonceOracle(self.publisher, conn=self.conn)
        c = EthWriter(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        o = c.is_writer(writer_contract_address, publisher_address, sender_address=publisher_address)
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 1)

        self.alice = self.accounts[1]
        (tx_hash, o) = c.add_writer(writer_contract_address, publisher_address, writer_account)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.is_writer(writer_contract_address, writer_account, sender_address=publisher_address)
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 1)

        self.alice = self.accounts[1]
        (tx_hash, o) = c.delete_writer(writer_contract_address, publisher_address, writer_account)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.is_writer(writer_contract_address, self.alice, sender_address=publisher_address)
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 0)
