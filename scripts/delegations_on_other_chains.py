import os
import csv
import pandas as pd

import utils
from delegator_snapshot_utils import getDelegatorsAndConvert, \
    snapshot_delegators_using_API, createComparisonDelegatorDataFrame, get_all_pages_of_key_from_API_response

import get_chain_list


##this queries the API for source chain to determine who is delegating to Kleomedes validator on Source Chain
##then converts the address to the chain to analyse address format (only works for BECH32 normal conversions, INJ so far is rekt, use publicKeyUtils for this)
##queries chain to analyse and gets ALL accounts on the chain, checks if the address to analyse is part of the accounts in chain 
##then returns DELEGATED tokens of the chain (not balance held) for each address from the source chain that was delegated to Kleo 
##purpose of this is to determine how many Kleo delegators have presence in another chain


def main(sourcechain, chaintoanalyse):
    df_comparison = compare_delegators_with_analysis_chain(sourcechain, chaintoanalyse)
    chain_addresses = df_comparison["address"]
    print(f"Querying {sourcechain} delegators to Kleomedes balances on {chaintoanalyse}")
    chain_balances_by_address = queryDelegatedBalancesByAddressListAPI(chain_addresses, chaintoanalyse)
    df = pd.DataFrame(chain_balances_by_address)
    print(df.columns)
    parent_dir = utils.get_parent_dir()
    filename = f"{sourcechain}balancesOn{chaintoanalyse}.csv"
    full_path = os.path.join(parent_dir, "results", filename)
    df.to_csv(full_path)
    sum_column = df.iloc[:, 0].sum()
    return sum_column, df


def getChainToAnalyseAddresses(sourcechain, chaintoanalyse, dfDelegators):
    chain_addresses = []
    sourceprefix = utils.get_network_bech32_prefix(sourcechain)
    analysechainprefix = utils.get_network_bech32_prefix(chaintoanalyse)
    for delegator in dfDelegators["address"]:
        chain_address = utils.convert_address_to_address(sourceprefix, delegator, analysechainprefix)
        chain_addresses.append(chain_address)
    return chain_addresses


def queryDelegatedBalancesByAddressListAPI(chain_addresses, chaintoanalyse):
    chainBalancesByAddress = []
    chainconfig = utils.get_network_config(chaintoanalyse)
    api = utils.getAPIURl(chaintoanalyse)

    for index, address in enumerate(chain_addresses):
        print(f"{index} of {len(chain_addresses)}")
        url = f"{api}/cosmos/staking/v1beta1/delegations/{address}"
        try:
            delegation_response = snapshot_delegators_using_API(url)
            sum_delegator = 0
            if len(delegation_response) >= 0:
                for delegations in delegation_response:
                    delegation = float(delegations["delegation"]["shares"])
                    sum_delegator = delegation + sum_delegator
                chainBalancesByAddress.append([sum_delegator, str(address)])
        except Exception as e:
            print("exception occured")
            print(e)

    return chainBalancesByAddress


def queryGetAllAccounts(chaintoanalyse):
    api = utils.getAPIURl(chaintoanalyse)
    url = f"{api}/cosmos/auth/v1beta1/accounts?pagination.limit=10000"
    try:
        # returns the response["accounts"] - has full retry and handles pagination
        accounts = get_all_pages_of_key_from_API_response(url, "accounts")
    except Exception as e:
        print(e)
        return None
    return accounts


def compare_delegators_with_analysis_chain(sourcechain, chaintoAnalyse):
    response = queryGetAllAccounts(chaintoAnalyse)
    accounts_on_chain = []
    ##so far, injective accounts are treated differently to akash - unsure if all same. BaseAcccount is for Akash, Injective is EthAccount
    for accounts in response:
        if accounts["@type"] == "/cosmos.auth.v1beta1.BaseAccount":
            try:
                accounts_on_chain.append(accounts["address"])
            except Exception as e:
                print(f"exception{e}")
        elif accounts["@type"] == "/injective.types.v1beta1.EthAccount" or accounts[
            "@type"] == "/ethermint.types.v1.EthAccount":
            try:
                accounts_on_chain.append(accounts["base_account"]["address"])
            except Exception as e:

                print(f"exception{e}")
        #else:
            #print("Account [@type] doesn't match existing schema for:")
            #try:
                #print(accounts["@type"])
            #except Exception as e:
                #print(e)

    df_accounts_on_chain = pd.DataFrame(accounts_on_chain, columns=["address"])

    df_delegators = getDelegatorsAndConvert(sourcechain)

    chain_addresses = getChainToAnalyseAddresses(sourcechain, chaintoAnalyse, df_delegators)
    df_chain_addresses = pd.DataFrame(chain_addresses, columns=["address"])
    comparison = createComparisonDelegatorDataFrame(df_accounts_on_chain, df_chain_addresses)
    print(f"{len(comparison)} addresses found in {chaintoAnalyse} with delegations to Kleomedes in {sourcechain}")
    return comparison


def get_slip_44(chain_name):
        chainurl=f"https://chains.cosmos.directory/{chain_name}/chain"
        response = utils.get_API_data_with_retry(chainurl)
        try:
            slip44=response.json()["slip44"]
        except Exception as e: 
            slip44 = None; 
        return slip44

def getValidatorChains():
    # Open the CSV file
    with open('validatorlist.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        # Create a list to store the chain values
        chains = []

        # Iterate through the rows of the CSV file
        for row in reader:
            # Get the chain value for the current row
            chain = row['chain']

            # Add the chain value to the list (if it's not already there)
            if chain not in chains:
                chains.append(chain)
    return chains




if __name__ == "__main__":
    # chains=["sommelier","quicksilver","axelar","osmosis","cosmoshub","shentu","secretnetwork","migaloo","stafihub","nois","carbon","canto",]
    # chains=["akash"]
    #chains=get_chain_list.get_chain_list()
    chains=["akash","kava","cerberus"]
    main_chain="juno"
    exclusion_list=[main_chain, "evmos","canto","injective","cosmoshub","cronos","cryptoorgchain","osmosis","secret","terra","terra2","thorchain","acrechain", "8ball"]
    main_chain_slip44=get_slip_44(main_chain)
    for chain in exclusion_list:
        print(f"removing{chain}")
        try:
            chains.remove(chain)
        except Exception as e: 
            print(e)
    sums = []
    failures = []
    slip_44_mismatch=[]


    for chain in chains:

    
        print(chain)
        if get_slip_44(chain) == main_chain_slip44: 
            try:
                [sum, df] = main(main_chain, chain)
                sums.append([sum, chain])
                print(sums)
            except Exception as e:
                print(e)
                failures.append(chain)
        else: 
            slip_44_mismatch.append(chain)

    print(sums)
    print(failures)
    df = pd.DataFrame(sums)
    parent_dir = utils.get_parent_dir()
    full_path = os.path.join(parent_dir, f"results/allChainSumsFrom{main_chain}Delegators.csv")
    df.to_csv(full_path)
