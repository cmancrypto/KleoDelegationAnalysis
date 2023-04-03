import requests 
import pandas as pd
import delegatorSnapshotProcessing as helper
import utils 
import time
from constants import COSMOS_DIR_API, COSMOS_DIR_REST_PROXY,validator_address
from cosmpy.aerial.client import LedgerClient, NetworkConfig

##this queries the API for source chain to determine who is delegating to Kleomedes validator on Source Chain (requires having validator address in constants.py)
##then converts the address to the chain to analyse address format (only works for BECH32 normal conversions, INJ so far is rekt, use publicKeyUtils for this)
##queries chain to analyse and gets ALL accounts on the chain, checks if the address to analyse is part of the accounts in chain 
##then returns DELEGATED tokens of the chain (not balance held) for each address from the source chain that was delegated to Kleo 
##purpose of this is to determine how many Kleo delegators have presence in another chain


def main(sourcechain,chaintoanalyse):
    dfcomparison=compareDelegatorsWithAnalysisChain(sourcechain,chaintoanalyse)
    chain_addresses=dfcomparison["address"]
    print(f"Querying {sourcechain} delegators to Kleomedes balances on {chaintoanalyse}")
    ##chainBalancesByAddress=queryDelegatedBalancesByAddressList(chain_addresses,ledgerclient) ##has issues with injectives long int()
    chainBalancesByAddress=queryDelegatedBalancesByAddressListAPI(chain_addresses,chaintoanalyse)
    df=pd.DataFrame(chainBalancesByAddress)
    print(df.columns)
    df.to_csv(f"results/{sourcechain}balancesOn{chaintoanalyse}.csv")
    sum_column=df.iloc[:,0].sum()
    return sum_column,df

            
def getValidatorDelegationResponseFromAPI(sourcechain):
    validatoraddress=validator_address[sourcechain]
    api=utils.getAPIURl(sourcechain)
    query=f"/cosmos/staking/v1beta1/validators/{validatoraddress}/delegations?pagination.limit=50000"
    url=f"{api}{query}"
    delegation_response=helper.snapshotDelegatorsUsingAPI(url)
    return delegation_response

def getChainToAnalyseAddresses(sourcechain,chaintoanalyse,dfDelegators):
    chain_addresses=[]
    sourceprefix=utils.get_network_bech32_prefix(sourcechain)
    analysechainprefix=utils.get_network_bech32_prefix(chaintoanalyse)
    for delegator in dfDelegators["address"]:
        chain_address=utils.convert_address_to_address(sourceprefix,delegator,analysechainprefix)
        chain_addresses.append(chain_address)
    return chain_addresses

def queryDelegatedBalancesByAddressListAPI(chain_addresses, chaintoanalyse):
     chainBalancesByAddress=[]
     chainconfig=utils.get_network_config(chaintoanalyse)
     api=utils.getAPIURl(chaintoanalyse)

     for index,address in enumerate(chain_addresses):
        print(f"{index} of {len(chain_addresses)}") 
        url=f"{api}/cosmos/staking/v1beta1/delegations/{address}"
        try:
            delegation_response=helper.snapshotDelegatorsUsingAPI(url)
            sum_delegator=0
            if len(delegation_response)>=0:
                for delegations in delegation_response:
                    delegation=float(delegations["delegation"]["shares"])
                    sum_delegator=delegation+sum_delegator
                chainBalancesByAddress.append([sum_delegator,str(address)])
        except Exception as e:
            print("exception occured")
            print(e)

     return chainBalancesByAddress

def queryGetAllAccounts(chaintoanalyse):
     api=utils.getAPIURl(chaintoanalyse)
     url=f"{api}/cosmos/auth/v1beta1/accounts?pagination.limit=500000"
     print(url)
     response=utils.get_API_data_with_retry(url)
     print(response.raise_for_status())
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
                print(f"exception{e}")
        elif accounts["@type"]=="/injective.types.v1beta1.EthAccount" or accounts["@type"]=="/ethermint.types.v1.EthAccount":
            try:
                accountsOnChain.append(accounts["base_account"]["address"])
            except Exception as e:

                print(f"exception{e}")
        else: 
            print("Account [@type] doesn't match existing schema for:")
            try:
                print(accounts["@type"])
            except Exception as e:
                print(e)

    dfAccountsOnChain=pd.DataFrame(accountsOnChain,columns=["address"])

    dfDelegators=getDelegatorsAndConvert(sourcechain)

    chain_addresses=getChainToAnalyseAddresses(sourcechain,chaintoAnalyse,dfDelegators)
    dfchain_addresses=pd.DataFrame(chain_addresses,columns=["address"])
    comparison=helper.createComparisonDelegatorDataFrame(dfAccountsOnChain,dfchain_addresses)
    print(f"{len(comparison)} addresses found in {chaintoAnalyse} with delegations to Kleomedes in {sourcechain}")
    return comparison

def getDelegatorsAndConvert(chain):
    delegation_response=getValidatorDelegationResponseFromAPI(chain)
    dfDelegators=helper.convertJSONtoDataFrame(delegation_response)
    return dfDelegators


if __name__=="__main__":
    #chains=["sommelier","quicksilver","axelar","osmosis","cosmoshub","shentu","secretnetwork","migaloo","stafihub","nois","carbon","canto",]
    #chains=["akash"]
    chains=["gravitybridge","umee"]
    sums=[]
    failures=[]
    for chain in chains:
        try: 
            [sum,df]=main("juno",chain)
            sums.append([sum,chain])
        except Exception as e:
            print(e)
            failures.append(chain)
    print(sums)
    print(failures)
    df=pd.DataFrame(sums)
    df.to_csv(f"results/allChainSumsFromJunoDelegators.csv")