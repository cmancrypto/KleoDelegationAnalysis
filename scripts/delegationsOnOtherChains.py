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
    ##chainBalancesByAddress=queryDelegatedBalancesByAddressList(chain_addresses,ledgerclient)
    chainBalancesByAddress=queryDelegatedBalancesByAddressListAPI(chain_addresses[1:300],chaintoanalyse)
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

def queryDelegatedBalancesByAddressListAPI(chain_addresses, chaintoanalyse):
     chainBalancesByAddress=[]
     chainconfig=getNetworkConfig(chaintoanalyse)
     api=chainconfig["api"]

     for index,address in enumerate(chain_addresses):
        print(f"{index} of {len(chain_addresses)}") 
        url=f"{api}cosmos/staking/v1beta1/delegations/{address}"
        try:
            delegation_response=helper.snapshotDelegatorsUsingAPI(url)
            sum_delegator=0
            if len(delegation_response)>0:
                for delegations in delegation_response:
                    delegation=float(delegations["delegation"]["shares"])
                    sum_delegator=delegation+sum_delegator
                chainBalancesByAddress.append(sum_delegator)
        except Exception as e:
            print("exception occured")
            print(e)
            time.sleep(15)
            try:
                delegation_response=helper.snapshotDelegatorsUsingAPI(url)
                sum_delegator=0
                if len(delegation_response)>0:
                    for delegations in delegation_response:
                        delegation=float(delegations["delegation"]["shares"])
                        sum_delegator=delegation+sum_delegator
                    chainBalancesByAddress.append(sum_delegator)
            except Exception as e:
                print("exception occured")
                print(e) 

     return chainBalancesByAddress

def queryGetAllAccounts(chaintoanalyse):
     chainconfig=getNetworkConfig(chaintoanalyse)
     api=chainconfig["api"]
     url=f"{api}cosmos/auth/v1beta1/accounts?pagination.limit=500000"
     print(url)
     response=requests.get(url)
     return response.json()

def compareDelegatorsWithAnalysisChain(sourcechain,chaintoAnalyse):
    response=queryGetAllAccounts(chaintoAnalyse)["accounts"]
    accountsOnChain=[]
    ##so far, injective accounts are treated differently to akash - unsure if all same. BaseAcccount is for Akash, Injective is EthAccount
    for accounts in response:
        if accounts["@type"]=="/cosmos.auth.v1beta1.BaseAccount":
            try:
                accountsOnChain.append(accounts["address"])
            except Exception as e:
                print(accounts)
                print(f"exception{e}")
        if accounts["@type"]=="/injective.types.v1beta1.EthAccount":
            try:
                accountsOnChain.append(accounts["base_account"]["address"])
            except Exception as e:
                print(accounts)
                print(f"exception{e}")
        else: 
            print(accounts)

    dfAccountsOnChain=pd.DataFrame(accountsOnChain,columns=["address"])

    dfDelegators=getDelegatorsAndConvert(sourcechain)

    chain_addresses=getChainToAnalyseAddresses(sourcechain,chaintoAnalyse,dfDelegators)
    dfchain_addresses=pd.DataFrame(chain_addresses,columns=["address"])

    comparison=helper.createComparisonDelegatorDataFrame(dfAccountsOnChain,dfchain_addresses)

    print(comparison)
    return comparison

def getDelegatorsAndConvert(chain):
    delegation_response=getValidatorDelegationResponseFromAPI(chain)
    dfDelegators=helper.convertJSONtoDataFrame(delegation_response)
    return dfDelegators


##main("juno","akash")
##main("juno","injective")
compareDelegatorsWithAnalysisChain("juno","akash")

