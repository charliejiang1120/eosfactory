# python3 ./tests/unittest1.py

import setup
import teos
import cleos
import sess
import eosf
import unittest
import json
import time
from termcolor import colored, cprint #sudo python3 -m pip install termcolor

setup.set_verbose(False)
cleos.use_keosd(False)

class Test1(unittest.TestCase):

    def run(self, result=None):
        """ Stop after first error """      
        if not result.failures:
            super().run(result)

    @classmethod
    def setUpClass(cls):
        pass
        
    def setUp(self):
        pass


    def test_04(self):
        global wallet
        global account_eosio
        global alice
        global bob
        global carol

        cprint("""
Start a local test EOSIO node, use `teos.node_reset()`:
        """, 'magenta')

        ok = teos.node_reset()
        self.assertTrue(ok)
        
        cprint("""
Create a local wallet, use `wallet = eosf.Wallet()`:
        """, 'magenta')

        wallet = eosf.Wallet()
        self.assertTrue(not wallet.error)

        cprint("""
Implement the `eosio` master account as a `cleos.AccountEosio` object,
use `account_eosio = cleos.AccountEosio()` 
and `wallet.import_key(account_eosio)`:
        """, 'magenta')

        account_eosio = cleos.AccountEosio()
        wallet.import_key(account_eosio)

        cprint("""
Deploy the `eosio.bios` contract, 
use `cleos.SetContract(account_eosio, "eosio.bios")`:
        """, 'magenta')

        contract_eosio_bios = cleos.SetContract(account_eosio, "eosio.bios")
        self.assertTrue(not contract_eosio_bios.error)

        cprint("""
Create accounts `alice`, `bob` and `carol`:
        """, 'magenta')
        
        alice = eosf.account()
        self.assertTrue(not alice.error)
        alice.account
        wallet.import_key(alice)

        bob = eosf.account()
        self.assertTrue(not bob.error)
        wallet.import_key(bob)        

        carol = eosf.account()
        self.assertTrue(not carol.error)
        wallet.import_key(carol) 

        cprint("""
Inspect the account, use `bob.account()`:
        """, 'magenta')     

        print(bob.account())   


    def test_05(self):
        global wallet
        global alice
        global bob
        global carol
        global account_eosio
        global contract_test

        account_test = eosf.account()
        wallet.import_key(account_test)
        

        contract_test = eosf.Contract(account_test, "eosio.token")
        self.assertTrue(not contract_test.error)

        cprint("""
test contract_test.code():
        """, 'magenta')
        self.assertTrue(not contract_test.code().error)

        cprint("""
test contract_test.deploy():
        """, 'magenta')
        self.assertTrue(contract_test.deploy())

        cprint("""
test contract_test.get_code():
        """, 'magenta')
        self.assertTrue(not contract_test.code().error)

        cprint("""
test contract_test.push_action("create"):
        """, 'magenta')
        self.assertTrue(not contract_test.push_action(
            "create", 
            '{"issuer":"' 
                + str(account_eosio) 
                + '", "maximum_supply":"1000000000.0000 EOS", \
                "can_freeze":0, "can_recall":0, "can_whitelist":0}').error)

        cprint("""
test contract_test.push_action("issue"):
        """, 'magenta')
        self.assertTrue(not contract_test.push_action(
            "issue", 
            '{"to":"' + str(alice)
                + '", "quantity":"100.0000 EOS", "memo":"memo"}', \
                account_eosio).error)

        cprint("""
test contract_test.push_action("transfer", alice):
        """, 'magenta')
        self.assertTrue(not contract_test.push_action(
            "transfer", 
            '{"from":"' 
                + str(alice)
                + '", "to":"' + str(carol)
                + '", "quantity":"25.0000 EOS", "memo":"memo"}', 
            alice).error)

        time.sleep(1)

        cprint("""
test contract_test.push_action("transfer", carol):
        """, 'magenta')
        self.assertTrue(not contract_test.push_action(
            "transfer", 
            '{"from":"' 
                + str(carol)
                + '", "to":"' + str(bob)
                + '", "quantity":"13.0000 EOS", "memo":"memo"}', 
            carol).error)

        cprint("""
test contract_test.push_action("transfer" bob):
        """, 'magenta')
        self.assertTrue(not contract_test.push_action(
            "transfer", 
            '{"from":"' 
                + str(bob)
                + '", "to":"' 
                + str(alice)
                + '", "quantity":"2.0000 EOS", "memo":"memo"}', 
            bob).error)

        cprint("""
Get database table, use `contract_test.get_table("accounts", alice)`:
        """, 'magenta')

        t1 = contract_test.get_table("accounts", alice)
        
        cprint("""
Get database table, use `contract_test.get_table("accounts", bob)`:
        """, 'magenta')

        t2 = contract_test.get_table("accounts", bob)
        
        cprint("""
Get database table, use `contract_test.get_table("accounts", carol)`:
        """, 'magenta')
        
        t3 = contract_test.get_table("accounts", carol)

        cprint("""
self.assertTrue(t1.json["rows"][0]["balance"] == "77.0000 EOS":
        """, 'magenta')

        self.assertTrue(t1.json["rows"][0]["balance"] == '77.0000 EOS')
        
        cprint("""
self.assertTrue(t2.json["rows"][0]["balance"] == "11.0000 EOS":
        """, 'magenta')

        self.assertTrue(t2.json["rows"][0]["balance"] == '11.0000 EOS')
        
        cprint("""
self.assertTrue(t3.json["rows"][0]["balance"] == "12.0000 EOS":
        """, 'magenta')

        self.assertTrue(t3.json["rows"][0]["balance"] == '12.0000 EOS')

        cprint("""
test node.stop():
        """, 'magenta')
        teos.node_stop()


    def tearDown(self):
        pass


    @classmethod
    def tearDownClass(cls):
        teos.node_stop()


if __name__ == "__main__":
    unittest.main()