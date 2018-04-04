#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/range/algorithm/find_if.hpp>
#include <boost/range/algorithm/sort.hpp>
#include <boost/range/adaptor/transformed.hpp>
#include <boost/algorithm/string/predicate.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/range/algorithm/copy.hpp>
#include <boost/algorithm/string/classification.hpp>

#include <fc/variant.hpp>
#include <fc/io/json.hpp>
#include <fc/exception/exception.hpp>
#include <eosio/utilities/key_conversion.hpp>
#include <fc/io/fstream.hpp>
#include <eosio/chain_plugin/chain_plugin.hpp>


#include <IR/Module.h>
#include <IR/Validate.h>
#include <WAST/WAST.h>
#include <WASM/WASM.h>
#include <Runtime/Runtime.h>


#include <teoslib/control/config.hpp>
#include <teoslib/eos_interface.hpp>
#include <teoslib/command/get_commands.hpp>

using namespace std;
using namespace eosio;
using namespace eosio::chain;
using namespace eosio::utilities;
using namespace boost::filesystem;

/*
// There are methodes calling the node, namelly:

  template<typename T>
  fc::variant call( const std::string& server, uint16_t port,
                    const std::string& path,
                    const T& v );
  template<typename T>
  fc::variant call( const std::string& path, const T& v );

// We want to use our owm call system. It follows te relevant mapping.
// 
  template<typename T>
  fc::variant something = call(host, port, path, const T& v);
  
  CallChain callSomething(path, fc::variant(v));
  if (callSomething.isError_) {
    return callSomething;
  }
  something = callSomething.fcVariant_;

  // for example:
  auto info = get_info();
  // maps to the following:
  CallChain callGetInfo(string(getCommandPath + "get_info")); 
    // second arg is defaulted!

  if (callGetInfo.isError_) {
    return callGetInfo;
  }
  info = callGetInfo.fcVariant_.as<chain_apis::read_only::get_info_results>();

  // for example:
  auto push = call(push_txn_func, packed_transaction(trx, compression));
  // maps to the following:
  CallChain callPush(push_txn_func, packed_transaction(trx, compression));
  if(callPush.isError_) {
    return callPush;
  }
  push = callPush.fcVariant_.as<chain_apis::read_write::push_transaction_results>();
*/
const string chain_func_base = "/v1/chain";
const string get_required_keys = chain_func_base + "/get_required_keys";
const string push_txn_func = chain_func_base + "/push_transaction";
const string wallet_func_base = "/v1/wallet";
const string wallet_public_keys = wallet_func_base + "/get_public_keys";
const string wallet_sign_trx = wallet_func_base + "/sign_transaction";

namespace teos {
  namespace command {

    KeyPair::KeyPair() {
      auto pk = private_key_type::generate();
      publicKey = string(pk.get_public_key());
      privateKey = string(pk);
    }

    string KeyPair::privateK() {
      KeyPair kp;
      return kp.privateKey;
    }

    string KeyPair::prk = KeyPair::privateK();

#define CODE_PATH boost::str(boost::format("%1% (%2% [%3%]) ") \
  % __func__ % __FILE__ % __LINE__)

    //////////////////////////////////////////////////////////////////////////
    // class CallChain
    //////////////////////////////////////////////////////////////////////////
    class CallChain : public TeosCommand
    {
      std::string requestStr;
    public:
      fc::variant fcVariant_;

      bool fcaVariant2ptree(const fc::variant& postData, ptree& json) {
        if (!postData.is_null()) {
          requestStr = fc::json::to_string(postData);
          stringstream ss;
          ss << requestStr;
          try {
            read_json(ss, json);
            stringstream ss1;
            json_parser::write_json(ss1, json, false);
            return true;
          }
          catch (exception& e) {
            putError(e.what(), CODE_PATH);
          }
        }
        return true;
      }

      CallChain(string path, const fc::variant& postData = fc::variant())
        : TeosCommand(path)
      {
        if (fcaVariant2ptree(postData, reqJson_)) {
          callEosd();
        }
        //std::cout << path << std::endl;
        //std::cout << requestStr << std::endl;
        //std::cout << fc::json::to_pretty_string(fcVariant_) << std::endl;
        if (isError_) {
          //std::cout << responseToString(false) << std::endl;
        }
      }

      CallChain(fc::variant fcVariant)
      {
        fcVariant_ = fcVariant;
        fcaVariant2ptree(fcVariant_, respJson_);
      }

      std::string normRequest(ptree &regJson) { return requestStr; }
      void normResponse(std::string response, ptree &respJson);
    };

    void CallChain::normResponse(std::string response, ptree &respJson) {
      fcVariant_ = fc::json::from_string(response);
      stringstream ss;
      ss << response;
      try {
        read_json(ss, respJson);
        stringstream ss1; // Try to write respJson, in order to check it.
        json_parser::write_json(ss1, respJson, false);
      }
      catch (exception& e) {
        putError(e.what(), CODE_PATH);
      }
    }

    using namespace teos::command;

    CallChain sign_transaction(chain::signed_transaction& trx)
    {
      // TODO better error checking
      /*
      const auto& public_keys = call(
        wallet_host, wallet_port, wallet_public_keys);
      */
      CallChain callPublicKeys(wallet_public_keys);
      if(callPublicKeys.isError_) {
        return callPublicKeys;
      }
      const auto& public_keys = callPublicKeys.fcVariant_;
      auto get_arg = fc::mutable_variant_object
            ("transaction", (transaction)trx)
            ("available_keys", public_keys);
      /*
      const auto& required_keys = call(host, port, get_required_keys, get_arg);
      */
      CallChain callRequiredKeys(get_required_keys, get_arg);
      if(callRequiredKeys.isError_){
        return callRequiredKeys;
      }
      const auto& required_keys = callRequiredKeys.fcVariant_;
      // TODO determine chain id
      fc::variants sign_args = {fc::variant(trx), required_keys["required_keys"]
        , fc::variant(chain_id_type{})};
      /*
      const auto& signed_trx = call(
        wallet_host, wallet_port, wallet_sign_trx, sign_args);
      trx = signed_trx.as<signed_transaction>();        
      */
      return CallChain(wallet_sign_trx, sign_args);
    }

    TeosCommand push_transaction(
      signed_transaction& trx,
      int expirationSec,
      bool tx_skip_sign,
      bool tx_dont_broadcast,
      bool tx_force_unique,
      packed_transaction::compression_type compression = packed_transaction::none)
    {
      //callGetInfo == call(host, port, get_info_func)  
      CallChain callGetInfo(string(getCommandPath + "get_info"));
      if (callGetInfo.isError_) {
        return callGetInfo;
      }

      auto info = callGetInfo.fcVariant_.as<chain_apis::read_only::get_info_results>();
      trx.expiration = info.head_block_time + fc::seconds(expirationSec);
      trx.set_reference_block(info.head_block_id);

      if (!tx_skip_sign) {
        CallChain callSign = sign_transaction(trx);
        if (callSign.isError_) {
          return callSign;
        }
        trx = callSign.fcVariant_.as<signed_transaction>();
      }
      
      if (!tx_dont_broadcast) {
        //return call(push_txn_func, packed_transaction(trx, compression));
        CallChain callPushTransaction(
          push_txn_func,
          fc::variant(trx));
        return callPushTransaction;        
      } else {
        return CallChain(fc::variant(trx));
      }

    }

    vector<chain::permission_level> get_account_permissions(const vector<string>& permissions) {
      auto fixedPermissions = permissions | boost::adaptors::transformed([](const string& p) {
          vector<string> pieces;
          split(pieces, p, boost::algorithm::is_any_of("@"));
          //EOSC_ASSERT(pieces.size() == 2, "Invalid permission: ${p}", ("p", p));
          return chain::permission_level{ .actor = pieces[0], .permission = pieces[1] };
      });
      vector<chain::permission_level> accountPermissions;
      boost::range::copy(fixedPermissions, back_inserter(accountPermissions));
      return accountPermissions;
    }

    TeosCommand assemble_wast(const std::string& wast, vector<uint8_t>& wasm)
    {
      IR::Module module;
      std::vector<WAST::Error> parseErrors;
      WAST::parseModule(wast.c_str(), wast.size(), module, parseErrors);
      if (parseErrors.size())
      {
        stringstream  msg;
        msg << "Error parsing WebAssembly text file:" << std::endl;
        for (auto& error : parseErrors)
        {
          msg << ":" << error.locus.describe() << ": " << error.message.c_str() << std::endl;
          msg << error.locus.sourceLine << std::endl;
          msg << std::setw(error.locus.column(8)) << "^" << std::endl;
        }
        return TeosCommand(msg.str(), CODE_PATH);
      }

      try
      {
        // Serialize the WebAssembly module.
        Serialization::ArrayOutputStream stream;
        WASM::serialize(stream, module);
        wasm = stream.getBytes();
      }
      catch (Serialization::FatalSerializationException exception)
      {
        stringstream  msg;
        msg << "Error serializing WebAssembly binary file:" << std::endl;
        msg << exception.message << std::endl;

        return TeosCommand(msg.str(), CODE_PATH);
      }
      return TeosCommand(CODE_PATH);
    }

    /*
      // Originally:
      fc::variant push_actions(...
    */
    TeosCommand send_actions(
      std::vector<chain::action>&& actions,
      int expirationSec,
      bool tx_skip_sign,
      bool tx_dont_broadcast,
      bool tx_force_unique,       
      packed_transaction::compression_type compression = packed_transaction::none ) 
    {
      /*
        // Originally:
        cout << fc::json::to_pretty_string(
          push_actions(std::forward<decltype(actions)>(actions), compression)
            ) << endl;
      */
      
      // push_actions(...) body:
      signed_transaction trx;
      trx.actions = std::forward<decltype(actions)>(actions);

      return  push_transaction(trx, expirationSec, tx_skip_sign, tx_dont_broadcast, 
          tx_force_unique, compression)/*.fcVariant_*/;
    }

    chain::action create_newaccount(
        const name& creator, const name& newaccount, 
        public_key_type owner, public_key_type active, vector<string> permission) 
      {
        return action {
            permission.empty() 
              ? vector<chain::permission_level>{{creator,config::active_name}} 
              : get_account_permissions(permission),
            contracts::newaccount{
              .creator      = creator,
              .name         = newaccount,
              .owner        = eosio::chain::authority{1, {{owner, 1}}, {}},
              .active       = eosio::chain::authority{1, {{active, 1}}, {}},
              .recovery     = eosio::chain::authority{1, {}, {{{creator, config::active_name}, 1}}}
            }
        };
      }

    TeosCommand createAccount(
      string creator, string accountName,
      string ownerKeyStr, string activeKeyStr, 
      string permission,
      int expiration, 
      bool skipSignature, bool dontBroadcast, bool forceUnique)
    {
      vector<string> permissions = {};
      if(!permission.empty()){
        boost::split(permissions, permission, boost::is_any_of(","));
      }
      if(permissions.empty()){
        cout << "is empty" << endl;
      } else {
        cout << "is not empty" << endl;
      }

      public_key_type owner_key, active_key;      
      try {
        owner_key = public_key_type(ownerKeyStr);
        active_key = public_key_type(activeKeyStr);
      }
      catch (const std::exception& e) {
        return TeosCommand(e.what(), CODE_PATH);
      }
      return send_actions(
        {create_newaccount(creator, accountName, owner_key, active_key, permissions)}, 
        expiration, skipSignature, dontBroadcast, forceUnique); 
    }

    TeosCommand setContract(
      string account, string wastFile, string abiFile,
      bool skipSignature, int expiration
      )
    {
      // namespace bfs = boost::filesystem;

      // try 
      // {
      //   TeosCommand status;
      //   bfs::path wastFilePath 
      //     = teos::control::getContractFile(&status, wastFile); 
      //   if (status.isError_) {
      //     return status;
      //   }    

      //   std::string wast;
      //   fc::read_file_contents(wastFilePath, wast);
      //   vector<uint8_t> wasm;

      //   const string binary_wasm_header = "\x00\x61\x73\x6d";
      //   if(wast.compare(0, 4, binary_wasm_header) == 0) {
      //     wasm = vector<uint8_t>(wast.begin(), wast.end());
      //   }
      //   else {
      //     status = assemble_wast(wast, wasm);
      //     if (status.isError_) {
      //       return status;
      //     }          
      //   }

      //   chain::contracts::setcode handler;
      //   handler.account = account;
      //   handler.code.assign(wasm.begin(), wasm.end());

      //   chain::signed_transaction trx;
      //   trx.actions.emplace_back( vector<chain::permission_level>{{account,"active"}}, handler);

      //   if (!abiFile.empty()) 
      //   {
      //     TeosCommand status;
      //     bfs::path abiFilePath 
      //       = teos::control::getContractFile(&status, abiFile); 
      //     if (status.isError_) {
      //       return status;
      //     }         
          
      //     chain::contracts::setabi handler;
      //     handler.account = account;
      //     handler.abi = fc::json::from_file(abiFilePath).as<chain::contracts::abi_def>();
      //     trx.actions.emplace_back( vector<chain::permission_level>{{account,"active"}}, handler);
      //   }
      //   //std::cout << "Publishing contract..." << std::endl;
      //   return push_transaction(trx, !skipSignature, expiration);
      // }
      // catch (const std::exception& e) {
      //   return TeosCommand(e.what(), CODE_PATH);
      // }
    }

    TeosCommand getCode(string accountName, string wastFile, string abiFile) 
    {
      /*
      auto result = call(
        get_code_func, fc::mutable_variant_object("account_name", 
        accountName));
      */
      CallChain callGetCode(string(getCommandPath + "get_code"), 
        fc::mutable_variant_object("account_name", accountName));
      auto result = callGetCode.fcVariant_;

      if (!wastFile.empty()) {
        auto code = result["wast"].as_string();

        std::ofstream out(wastFile.c_str());
        if (out.is_open()) {
          out << code;
        }
        else {
          return TeosCommand(boost::str(boost::format(
              "Cannot open the wast file:\n %1%\n") % wastFile), CODE_PATH);
        }
      }

      if (abiFile.size()) {
        auto abi = fc::json::to_pretty_string(result["abi"]);
        std::ofstream out(abiFile.c_str());
        if (out.is_open()) {
          out << abi;
        }
        else {
          return TeosCommand(boost::str(boost::format(
              "Cannot open the abi file:\n %1%\n") % abiFile), CODE_PATH);
        } 
      }
      return callGetCode;
    }

    uint64_t generate_nonce_value() {
      return fc::time_point::now().time_since_epoch().count();
    }

    TeosCommand pushAction(string contract, string action, string data, 
      const vector<string> scopes, const vector<string> permissions, 
      bool skipSignature, int expiration, 
      bool tx_force_unique)
    {
      // try {
      //   auto arg = fc::mutable_variant_object ("code", contract) ("action", action)
      //     ("args", fc::json::from_string(data));

      //   //auto result = call(json_to_bin_func, arg);
      //   CallChain call("/v1/chain/abi_json_to_bin", arg);
      //   auto result = call.fcVariant_;

      //   auto accountPermissions = get_account_permissions(permissions);

      //   chain::signed_transaction trx;
      //   trx.actions.emplace_back(accountPermissions, contract, action, result.get_object()["binargs"]
      //     .as<chain::bytes>());

      //   if (tx_force_unique) {
      //     trx.actions.emplace_back( generate_nonce() );
      //   }

      //   return push_transaction(trx, !skipSignature, expiration);
      // }
      // catch (const std::exception& e) {
      //   return TeosCommand(e.what(), CODE_PATH);
      // }
    }

  }
}