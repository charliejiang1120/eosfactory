
import json
import os
import subprocess
import amaxfactory.core.logger as logger
import amaxfactory.core.errors as errors
import amaxfactory.core.teos as teos
import amaxfactory.core.cleos as cleos
import amaxfactory.core.manager as manager
import amaxfactory.core.testnet as testnet
import amaxfactory.core.interface as interface
import amaxfactory.shell.wallet as wallet
import amaxfactory.shell.account as account
import amaxfactory.shell.contract as contract
from amaxfactory.bean.bean_list import *
from amaxfactory.bean.test_create_bean import Create

verbosity =  logger.verbosity
Verbosity =  logger.Verbosity

SCENARIO =  logger.SCENARIO
COMMENT =  logger.COMMENT
TRACE =  logger.TRACE
INFO =  logger.INFO
OUT =  logger.OUT
DEBUG =  logger.DEBUG

Error = errors.Error
LowRamError = errors.LowRamError
MissingRequiredAuthorityError = errors.MissingRequiredAuthorityError
DuplicateTransactionError = errors.DuplicateTransactionError

CreateKey = cleos.CreateKey
Permission = interface.Permission

create_wallet = wallet.create_wallet
get_wallet = wallet.get_wallet

Account = account.Account
MasterAccount = account.MasterAccount
create_account = account.create_account
new_account = account.new_account
create_master_account = account.create_master_account
new_master_account = account.new_master_account

print_stats = account.print_stats

Contract = contract.Contract
ContractBuilder = contract.ContractBuilder
project_from_template = teos.project_from_template

reboot = manager.reboot
reset = manager.reset
resume = manager.resume
stop = manager.stop

info = manager.info
status = manager.status

Testnet =  testnet.Testnet
get_testnet =  testnet.get_testnet
testnets =  testnet.testnets


from amaxfactory.config import *

verbosity([Verbosity.INFO, Verbosity.OUT,Verbosity.ERROR])


def build(contracts_dir=None,build=True,git_pull=False):
    build_sh_path = FACTORY_DIR + "/templates/build_temp.sh"
    if contracts_dir:
        if CONTRACT_WORKSPACE != None:
            contracts_dir = CONTRACT_WORKSPACE + contracts_dir
        
        if git_pull:
            build_commond = "cd " + contracts_dir + " && git stash save 'xx'&& git pull "
            print(build_commond)
            res = os.popen(build_commond).read()
            print(res)

        build_commond = "cd " + contracts_dir 
        if build:
            # build_commond += " && cp -rf {} .  && ./build_temp.sh && rm build_temp.sh".format(build_sh_path)
            build_commond += "&& ./build.sh -y"
        build_commond += f"&&cp -rf build/contracts/* {CONTRACT_WASM_PATH}"
        print(build_commond)
        res = subprocess.call(build_commond,shell=True)
        if res != 0 : raise Exception("build commond failed")
        
        assert "Error" not in str(res)
    Create().create()


def deploy_amax():
    return AMAX_TOKEN().setup()


def deploy_apl_newbie():

    amax = new_master_account()
    admin = new_account(amax,"admin")
    aplink_token = new_account(amax,'aplink.token')
    aplinknewbie = new_account(amax,'aplinknewbie')

    smart = Contract(aplink_token, 
        wasm_file=CONTRACT_WASM_PATH + 'aplink/aplink.token/aplink.token.wasm',
        abi_file=CONTRACT_WASM_PATH + "aplink/aplink.token/aplink.token.abi")
    smart.deploy()

    smart = Contract(aplinknewbie, 
        wasm_file=CONTRACT_WASM_PATH + 'aplink/aplink.newbie/aplink.newbie.wasm',
        abi_file=CONTRACT_WASM_PATH + "aplink/aplink.newbie/aplink.newbie.abi")
    smart.deploy()

    aplink_token.set_account_permission(add_code=True)
    aplinknewbie.set_account_permission(add_code=True)

    aplink_token.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.0000 APL"
        },
        permission=[(admin, Permission.ACTIVE), (aplink_token, Permission.ACTIVE)])

    aplink_token.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.0000 APL", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))


    table_admin = aplink_token.table("accounts", admin)
    assert table_admin.json["rows"][0]["balance"] == '1000000000.0000 APL'
    
    return aplink_token


def deploy_mtoken():

    amax = new_master_account()
    admin = new_account(amax,"admin")
    amax_mtoken = new_account(amax,'amax.mtoken')

    smart = Contract(amax_mtoken, 
        wasm_file=CONTRACT_WASM_PATH + 'xchain/amax.mtoken/amax.mtoken.wasm',
        abi_file=CONTRACT_WASM_PATH + "xchain/amax.mtoken/amax.mtoken.abi")
    smart.deploy()

    amax_mtoken.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.00000000 MBTC"
        },
        permission=[(admin, Permission.ACTIVE), (amax_mtoken, Permission.ACTIVE)])

    amax_mtoken.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.00000000 MBTC", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))

    amax_mtoken.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.00000000 METH"
        },
        permission=[(admin, Permission.ACTIVE), (amax_mtoken, Permission.ACTIVE)])

    amax_mtoken.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.00000000 METH", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))

    amax_mtoken.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.00000000 MBNB"
        },
        permission=[(admin, Permission.ACTIVE), (amax_mtoken, Permission.ACTIVE)])

    amax_mtoken.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.00000000 MBNB", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))

    amax_mtoken.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.000000 MUSDT"
        },
        permission=[(admin, Permission.ACTIVE), (amax_mtoken, Permission.ACTIVE)])

    amax_mtoken.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.000000 MUSDT", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))

    amax_mtoken.push_action(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "1000000000.000000 MUSDC"
        },
        permission=[(admin, Permission.ACTIVE), (amax_mtoken, Permission.ACTIVE)])

    amax_mtoken.push_action(
        "issue",
        {
            "to": admin, "quantity": "1000000000.000000 MUSDC", "memo": ""
        },
        permission=(admin, Permission.ACTIVE))

    table_admin = amax_mtoken.table("accounts", admin)
    assert table_admin.json["rows"][0]["balance"] == '1000000000.00000000 MBNB'
    assert table_admin.json["rows"][1]["balance"] == '1000000000.00000000 MBTC'
    assert table_admin.json["rows"][2]["balance"] == '1000000000.00000000 METH'
    assert table_admin.json["rows"][3]["balance"] == '1000000000.000000 MUSDC'
    assert table_admin.json["rows"][4]["balance"] == '1000000000.000000 MUSDT'
    
    return amax_mtoken


def deploy_ntoken(name = "amax.ntoken"):

    amax = new_master_account()
    admin = new_account(amax,"admin")

    amax_ntoken = new_account(amax,name)
    
    smart = Contract(amax_ntoken, 
        wasm_file=CONTRACT_WASM_PATH + 'nftone/amax.ntoken/amax.ntoken.wasm',
        abi_file=CONTRACT_WASM_PATH + "nftone/amax.ntoken/amax.ntoken.abi")
    smart.deploy()

    amax_ntoken.pushaction(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "10000",
            "symbol":[1,0],
            "token_uri":"xx",
            "ipowner":admin
        },
        admin)

    amax_ntoken.push_action(
        "issue",
        {
            "to": admin, 
            "quantity": [10000,[1,0]],
            "memo": ""
        },
        admin)

    amax_ntoken.pushaction(
        "create",
        {
            "issuer": admin,
            "maximum_supply": "10000",
            "symbol":[2,0],
            "token_uri":"xxx",
            "ipowner":admin
        },
        admin)

    amax_ntoken.push_action(
        "issue",
        {
            "to": admin, 
            "quantity": [10000,[2,0]],
            "memo": ""
        },
        admin)



    table_admin = amax_ntoken.table("accounts", admin)
    assert table_admin.json["rows"][0]["balance"]["amount"] == 10000
    
    return amax_ntoken


def deploy_farm():

    amax = new_master_account()
    admin = new_account(amax,"admin")

    aplink_farm = new_account(amax,'aplink.farm')
    
    smart = Contract(aplink_farm, 
        wasm_file=CONTRACT_WASM_PATH + 'aplink/aplink.farm/aplink.farm.wasm',
        abi_file=CONTRACT_WASM_PATH + "aplink/aplink.farm/aplink.farm.abi")
    smart.deploy()

    aplink_farm.set_account_permission(add_code=True)

    aplink_farm.pushaction(
        "init",
        {
            "landlord": admin,
            "jamfactory": admin,
            "last_lease_id":1,
            "last_allot_id":1
        },
        aplink_farm)

    return aplink_farm


def create_action_demo(file_name,contract_name,abi_file_path,dir):
        obj = json.load(open(abi_file_path))
        
        content = 'from amaxfactory.beans.base.amcli import runaction\nfrom base.baseClass import baseClass\n\n'
        demo = 'from amaxfactory.eosf import * \n\n'
        demo += f'def test_start():\n\treset()\n\tmaster = new_master_account()\n\t{file_name} = new_account("{contract_name}")\n'
        for action in obj['actions']:
            for struct in obj['structs']:
                struct_name = struct['name']
                if action['name'] == struct_name:
                    print(struct_name)
                    print(struct['fields'])
                    func = '\tdef ' + struct_name + '(self,'
                    body = f'''self.response = runaction(self.contract + f""" {struct_name} '['''
                    kv = ''
                    for key in struct['fields']:
                        key_type = key['type']
                        key_name = key['name']
                        value = ""
                        if key_type == 'name':
                            value = "'user1'"
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'string':
                            value = "'x'"
                            body += '"{' + key_name + '}"' + ','
                        elif str(key_type).find('uint') >= 0:
                            value = 1
                            body += "{" + key_name + "}" + ','
                        elif key_type == 'symbol':
                            value = "'8,AMAX'"
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'asset':
                            value = '"0.10000000 AMAX"'
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'bool':
                            value = "'true'"
                            body += '"{' + key_name + '}"' + ','
                        else :
                            value = '1'
                            body += '"{' + key_name + '}"' + ','

                        kv += f'"{key_name}":{value},'
                    kv = "{"+kv+"},"
                    kv += "admin"
                    demo += f'\ndef test_{struct_name}():\n\t{file_name} = new_account("{contract_name}")\n\tadmin = new_account("admin")\n\t{file_name}.pushaction("{struct_name}",{kv}) \n'
                    func += kv
                    body = body[0:-1]
                    content += func + '):\n\t\t'
                    content += body + ''']' -p {submitter_}""") \n'''
                    content += '\t\treturn self\n\n'
        for table in obj['tables']:
            name = table['name']
            func = '\tdef ' + name + '(self,'
        # os.popen(f"mkdir {contract}case")
        # with open(f'/root/contracts/pythonProject1/{contract}case/{contract}.py', 'w', encoding='UTF-8') as file:
        #     file.write(content)
        
        print(dir)
        with open(f'{dir}/test_{file_name}demo.py', 'w', encoding='UTF-8') as file:
            file.write(demo)



def create_bean(contract_name,abi_file_path,dir,abi_in_factory=False):
        
        obj_name = str(contract_name).replace(".","_")
        content = 'from amaxfactory.beans.base.amcli import runaction\nfrom base.baseClass import baseClass\n\n'
        
        demo = f'''import os
from amaxfactory.core.account import CreateAccount
import amaxfactory.shell.account as account
import amaxfactory.shell.contract as contract
from amaxfactory.bean.bean_init import *

Contract = contract.Contract

new_account = account.new_account
create_master_account = account.create_master_account
new_master_account = account.new_master_account

class {str(obj_name).upper()}(CreateAccount):
	def __init__(self,contract_name="{contract_name}"):
		self.name = contract_name
		master = new_master_account()
		{obj_name} = new_account(master,contract_name,factory=True)
		smart = Contract({obj_name}, 
			wasm_file=os.getenv("FACTORY_DIR") + "/templates/wasm/" + "{str(abi_file_path).replace("abi","wasm")}",
			abi_file=os.getenv("FACTORY_DIR") + "/templates/wasm/" + "{abi_file_path}")
		smart.deploy()
		self = {obj_name}
		self.set_account_permission(add_code=True)
    
	def setup(self):
		{obj_name}_init(self)
		return self

	def __str__(self):
		return self.name
            \n'''
        # demo = 'import os\nfrom amaxfactory.eosf import * \n\n'
        # demo += f'class {str(contract_name).upper()}:\n'
        # demo += f'\tdef __init__(self):\n'
        # demo += f'\t\tself.abi_path = os.getenv("FACTORY_DIR") + "/templates/wasm/" + "{abi_file_path}"\n'
        # demo += f'\t\tself.abi_path = os.getenv("FACTORY_DIR") + "/templates/wasm/" + "{str(abi_file_path).replace("abi","wasm")}"\n'

        if abi_in_factory:
            abi_file_path = os.getenv("FACTORY_DIR") + "/templates/wasm/" + abi_file_path

        obj = json.load(open(abi_file_path))
        for action in obj['actions']:
            for struct in obj['structs']:
                struct_name = struct['name']
                if action['name'] == struct_name:
                    print(struct_name)
                    print(struct['fields'])
                    func = '\tdef ' + struct_name + '(self,'
                    body = f'''self.response = runaction(self.contract + f""" {struct_name} '['''
                    kv = ''
                    kk = ''
                    for key in struct['fields']:
                        key_type = key['type']
                        key_name = key['name']
                        value = ""
                        if key_type == 'name':
                            value = "'user1'"
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'string':
                            value = "'x'"
                            body += '"{' + key_name + '}"' + ','
                        elif str(key_type).find('uint') >= 0:
                            value = 1
                            body += "{" + key_name + "}" + ','
                        elif key_type == 'symbol':
                            value = "'8,AMAX'"
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'asset':
                            value = '"0.10000000 AMAX"'
                            body += '"{' + key_name + '}"' + ','
                        elif key_type == 'bool':
                            value = "'true'"
                            body += '"{' + key_name + '}"' + ','
                        else :
                            value = []
                            body += '"{' + key_name + '}"' + ','

                        if key_name=="from":
                            kv += f'from_={value},'
                            kk += f'"{key_name}":from_,'
                        else:
                            kv += f'{key_name}={value},'
                            kk += f'"{key_name}":{key_name},'
                    kk = "{"+kk+"}"
                    kv += 'submitter_="admin",expect_asset=True'
                    
                    demo += f'\n\tdef {struct_name}(self,{kv}):\n'
                    # demo += f'\t\tassert self.body\n'
                    demo += f'\t\tself.pushaction("{struct_name}",{kk},submitter_,expect_asset=expect_asset) \n'

                    kv += "admin"
                    func += kv
                    body = body[0:-1]
                    content += func + '):\n\t\t'
                    content += body + ''']' -p {submitter_}""") \n'''
                    content += '\t\treturn self\n\n'
        for table in obj['tables']:
            demo += f'''
	def get_{str(table["name"]).replace(".","_")}(self,scope):
		return self.table("{table["name"]}",scope).json\n'''
        # os.popen(f"mkdir {contract}case")
        # with open(f'/root/contracts/pythonProject1/{contract}case/{contract}.py', 'w', encoding='UTF-8') as file:
        #     file.write(content)
        
        print(dir)
        with open(f'{dir}/{obj_name}.py', 'w', encoding='UTF-8') as file:
            file.write(demo)


