import requests
from typing import List    

class Blockchain:
    id: int
    name: str
    shortname: str
    explorer_url: None
    default_token_id: int
    required_network_confirmations_for_withdrawal: int
    required_network_confirmations_for_crypto_balance: int
    has_global_deposit_address: bool
    has_case_sensitive_addresses: bool
    is_active: bool

    def __init__(self, id: int, name: str, shortname: str, explorer_url: None, default_token_id: int, required_network_confirmations_for_withdrawal: int, required_network_confirmations_for_crypto_balance: int, has_global_deposit_address: bool, has_case_sensitive_addresses: bool, is_active: bool) -> None:
        self.id = id
        self.name = name
        self.shortname = shortname
        self.explorer_url = explorer_url
        self.default_token_id = default_token_id
        self.required_network_confirmations_for_withdrawal = required_network_confirmations_for_withdrawal
        self.required_network_confirmations_for_crypto_balance = required_network_confirmations_for_crypto_balance
        self.has_global_deposit_address = has_global_deposit_address
        self.has_case_sensitive_addresses = has_case_sensitive_addresses
        self.is_active = is_active
    
    def __str__(self):
        return "({}, {})".format(self.id, self.shortname)

    def __repr__(self):
        return "({}, {})".format(self.id, self.shortname)

class TokenType:
    id: int
    name: str
    is_active: bool

    def __init__(self, id: int, name: str, is_active: bool) -> None:
        self.id = id
        self.name = name
        self.is_active = is_active
    
    def __str__(self):
        return "({}, {})".format(self.id, self.name)
    
    def __repr__(self):
        return "({}, {})".format(self.id, self.name)

class Token:
    id: int
    blockchain_id: int
    asset_id: int
    token_type_id: int
    contract_address: str
    contract_creation_height: int
    precision: int
    is_supported_by_proof: bool
    token_index: int
    is_active: bool

    def __init__(self, id: int, blockchain_id: int, asset_id: int, token_type_id: int, contract_address: str, contract_creation_height: int, precision: int, is_supported_by_proof: bool, token_index: int, is_active: bool) -> None:
        self.id = id
        self.blockchain_id = blockchain_id
        self.asset_id = asset_id
        self.token_type_id = token_type_id
        self.contract_address = contract_address
        self.contract_creation_height = contract_creation_height
        self.precision = precision
        self.is_supported_by_proof = is_supported_by_proof
        self.token_index = token_index
        self.is_active = is_active
    
    def __str__(self):
        return "('tokenId':{}, 'blockchainId':{}, 'assetId':{})".format(self.id, self.blockchain_id, self.asset_id)

    def __repr__(self):
        return "('tokenId':{}, 'blockchainId':{}, 'assetId':{})".format(self.id, self.blockchain_id, self.asset_id)

class Asset:
    id: int
    name: str
    amount_precision: int
    asset_type: str
    bancs_currency_id: str
    symbol: str
    automatic_withdrawal_limit: int
    automatic_withdrawal_limit_in_chf: int
    is_active: bool
    token_ids: List[int]

    def __init__(self, id: int, name: str, amount_precision: int, asset_type: str, bancs_currency_id: str, symbol: str, automatic_withdrawal_limit: int, automatic_withdrawal_limit_in_chf: int, is_active: bool, token_ids: List[int]) -> None:
        self.id = id
        self.name = name
        self.amount_precision = amount_precision
        self.asset_type = asset_type
        self.bancs_currency_id = bancs_currency_id
        self.symbol = symbol
        self.automatic_withdrawal_limit = automatic_withdrawal_limit
        self.automatic_withdrawal_limit_in_chf = automatic_withdrawal_limit_in_chf
        self.is_active = is_active
        self.token_ids = token_ids

    def __str__(self):
        return "({}, {}, {})".format(self.id, self.symbol, self.token_ids)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.symbol, self.token_ids)        

class TokenMaster:
    env:str
    base_url:str
    asset_list:List[Asset]
    blockchain_list:List[Blockchain]
    tokenType_list:List[TokenType]
    token_list:List[Token]

    def __init__(self, env:str="test"):
        self.env = env
        self.base_url = "https://tokenmaster-api.btcs{}.net".format(env)
        self.assets = dict()
        self.blockchains = dict()
        self.token_types = dict()
        self.tokens = dict()

        # -----------------------  Game Plan  -----------------------
        # 1. load assets
        # 2. load bloackchains
        # 3. load token types
        # 4. load tokens

        # ----------------------- load assets -----------------------
        loaded_assets = TokenMaster.get_all("{}/assets".format(self.base_url))
        for a in loaded_assets:
            trs = []
            if a["tokenReferences"]:
                for tr in a["tokenReferences"]:
                    trs.append(tr["id"])

            self.assets[a["id"]] = Asset( 
                a["id"], 
                a["name"], 
                a["amountPrecision"], 
                a["assetType"], 
                a["bancsCurrencyId"], 
                a["symbol"], 
                a["automaticWithdrawalLimit"], 
                a["automaticWithdrawalLimitInChf"], 
                a["isActive"], 
                trs
            )
    
        # ----------------------- load blockchains -----------------------
        loaded_blockchains = TokenMaster.get_all("{}/blockchains".format(self.base_url))
        for b in loaded_blockchains:
            self.blockchains[b["id"]] = (Blockchain(
                b["id"],
                b["name"],
                b["shortname"],
                b["explorerUrl"],
                b["defaultTokenId"],
                b["requiredNetworkConfirmationsForWithdrawal"],
                b["requiredNetworkConfirmationsForCryptoBalance"],
                b["hasGlobalDepositAddress"],
                b["hasCaseSensitiveAddresses"],
                b["isActive"]
            ))
        
        # ----------------------- load token types -----------------------
        loaded_token_types = TokenMaster.get_all("{}/tokentypes".format(self.base_url))
        for tt in loaded_token_types:
            self.token_types[tt["id"]] = TokenType(
                tt["id"],
                tt["name"],
                tt["isActive"]
            )

        # ----------------------- load tokens -----------------------
        loaded_tokens = TokenMaster.get_all("{}/tokens".format(self.base_url))
        
        for t in loaded_tokens:            
            self.tokens[t["id"]] = Token(
                t["id"],
                t["blockchainId"],
                t["assetId"],
                t["tokenTypeId"],
                t["contractAddress"],
                t["contractCreationHeight"],
                t["precision"],
                t["isSupportedByProof"],
                t["tokenIndex"],
                t["isActive"],

            )

        self.asset_list = TokenMaster.get_values(self.assets)
        self.blockchain_list = TokenMaster.get_values(self.blockchains)
        self.token_types = TokenMaster.get_values(self.token_types)
        self.token_list = TokenMaster.get_values(self.tokens)

        print("Token Master successfully cached!")

    def get_all(url):
        l = []
        take = 100
        offset = 0

        while True:
            req_url = "{}?Skip={}&Take={}&autoResolve=true".format(url, offset*take, take)
            response = requests.request("GET", req_url)
        
            try:
                res_json = response.json()
                
                l.extend(res_json["items"])
                if len(res_json["items"]) == 0:
                    break
            except:
                print(req_url)
            
            offset += 1
        return l
    
    def get_values(dictionary):
        values = []
        for key, value in dictionary.items():
            values.append(value)
        return values

    def get_asset_for_symbol(self, symbol):
        for asset in self.asset_list:
            if asset.symbol == symbol:
                return asset
        raise Exception("No asset found for symbol: {}".format(symbol))
                
    def get_tokens_for_symbol(self, symbol):
        tokens = []
        asset = self.get_asset_for_symbol(symbol)
        for token in self.token_list:
            if token.asset_id == asset.id:
                tokens.append(token)
                
        if len(tokens) == 0:
            raise Exception("No tokens found for symbol: {}".format(symbol))

        return tokens

    def get_blockchains_for_asset(self, id):
        asset = self.assets.get(id)
        tokens = asset.tokens
        blockchain_ids = []
        print(tokens)
        for token in tokens:
            blockchain_ids.append(token.blockchain_id)
        return blockchain_ids

    def normalize_balance(self, token_id, balance):
        precision = self.tokens.get(token_id).precision
        return int(balance)/10**precision
    
if __name__ == "__main__":
    tm = TokenMaster(env="prod")
    #print(tm.normalize_balance(7, "123456789123456789"))

    print(tm.assets[7])
    print(tm.tokens[7])