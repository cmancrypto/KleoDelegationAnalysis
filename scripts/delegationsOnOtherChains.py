import requests 
import pandas as pd
import json
import delegatorSnapshotProcessing as helper
import utils 
import yaml
import time
from cosmpy.aerial.client import LedgerClient, NetworkConfig

def main(sourcechain,chaintoanalyse): 
    delegation_response=getValidatorDelegationResponseFromAPI(sourcechain)
    dfDelegators=helper.convertJSONtoDataFrame(delegation_response)
    chain_addresses=getChainToAnalyseAddresses(sourcechain,chaintoanalyse,dfDelegators)
    networkcfg= getNetworkConfig(chaintoanalyse)
    ledgercfg=getLedgerClientConfig(networkcfg)
    ledgerclient=utils.getCosmpyClient(ledgercfg)
    print(f"Querying {sourcechain} delegators to Kleomedes balances on {chaintoanalyse}")
    chainBalancesByAddress=queryDelegatedBalancesByAddressList(chain_addresses,ledgerclient)
    df=pd.DataFrame(chainBalancesByAddress)
    df.to_csv(f"balances{chaintoanalyse}.csv")
            
def getValidatorDelegationResponseFromAPI(sourcechain):
    sourcechainconfig=getNetworkConfig(sourcechain)
    validatoraddress=sourcechainconfig["validator"]
    api=sourcechainconfig["api"]
    query=f"cosmos/staking/v1beta1/validators/{validatoraddress}/delegations?pagination.limit=50000"
    url=f"{api}{query}"
    delegation_response=helper.snapshotDelegatorsUsingAPI(url)
    return delegation_response

def getChainToAnalyseAddresses(sourcechain,chaintoanalyse,dfDelegators):
    chain_addresses=[]
    sourceconfig=getNetworkConfig(sourcechain)
    chaintoanalyseconfig=getNetworkConfig(chaintoanalyse)
    for delegator in dfDelegators["address"]:
        chain_address=utils.convert_address_to_address(sourceconfig["addressprefix"],delegator,chaintoanalyseconfig["addressprefix"])
        chain_addresses.append(chain_address)
    return chain_addresses

def getNetworkConfig(chain):
    with open("networkconfig.yaml", "r") as file:   
        networkconfig=yaml.safe_load(file)
        chainconfig=networkconfig["networks"][chain]
    return chainconfig

def getLedgerClientConfig(chainconfig):
    config=chainconfig["config"]
    ledgercfg=NetworkConfig(**config)
    print(ledgercfg)
    return ledgercfg

def queryDelegatedBalancesByAddressList(chain_addresses,ledgerclient):
    chainBalancesByAddress=[]   
    for index,address in enumerate(chain_addresses):
            print(f"{index} of {len(chain_addresses)}") 
            try:
                s=ledgerclient.query_staking_summary(address)
                if s.total_staked>0:
                    chainBalancesByAddress.append([address,s.total_staked])
            except Exception as e:
                print("exception occured")
                print(e)
                time.sleep(0.5)
                try:
                    s=ledgerclient.query_staking_summary(address)
                    print("retry success")
                    if s.total_staked>0:
                        chainBalancesByAddress.append([address,s.total_staked])
                except: 
                    print("retry failed") 
    return(chainBalancesByAddress) 


main("juno","akash")
main("juno","injective")
