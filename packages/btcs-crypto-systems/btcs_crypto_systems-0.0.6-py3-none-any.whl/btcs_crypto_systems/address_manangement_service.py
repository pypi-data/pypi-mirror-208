import requests

class AMS():
    env = ""

    def __init__(self, env="test"):
        self.env = env

    def get_addresses(self, account, blockchain_id=None, include_balances=False):
        offset = 0
        take = 100
        addresses = []

        while True:
            print("...collecting addresses, done with {} addresses".format(offset*take))

            try:
                url = ""
                if blockchain_id:
                    url = "https://ams.btcs{}.net/api/AddressManagement/addresses?Skip={}&Take={}&AccountRef={}&BlockchainId={}&IncludeBalances={}".format(self.env, offset*take, take, account, blockchain_id, include_balances)
                else:
                    url = "https://ams.btcs{}.net/api/AddressManagement/addresses?Skip={}&Take={}&AccountRef={}&IncludeBalances={}".format(self.env, offset*take, take, account, include_balances)
                response = requests.request("GET", url)
                addresses_res = response.json()
                addresses.extend(addresses_res)
                offset += 1
                if len(addresses_res) == 0:
                    break
            except:
                print("Error with URL: {}".format(url))
        
        return addresses