import requests
import json
import sys 

def queryChainDirectory(chain):
    url=f"https://chains.cosmos.directory/{chain}"
    response=requests.get(url)
    chainresults=response.json()["chain"]
    print(chainresults.keys())
    print(chainresults["fees"]["fee_tokens"][0])
    print(chainresults["fees"])
    print(chainresults["staking"].keys())
    return chainresults


def getNetworkResults(chainresults):
    chain_name=chainresults["chain_name"]
    chain_id=chainresults["chain_id"]
    bech32_prefix=chainresults["bech32_prefix"]
    fee_minimum_gas_price=chainresults["fees"]["fee_tokens"][0]["fixed_min_gas_price"]
    fee_denomination=chainresults["fees"]["fee_tokens"][0]["denom"]
    staking_denomination=chainresults["staking"]["staking_tokens"][0]["denom"]


    networkresults=[chain_name,
         chain_id,
         bech32_prefix,
         fee_minimum_gas_price,
         fee_minimum_gas_price,
        fee_denomination,
        staking_denomination]
    print(networkresults)

chainresults=queryChainDirectory("injective")
getNetworkResults(chainresults)

