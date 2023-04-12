import os

import pandas as pd

import utils
from delegatorSnapshotUtils import getDelegatorsAndConvert, \
    snapshotDelegatorsUsingAPI, createComparisonDelegatorDataFrame


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
            delegation_response = snapshotDelegatorsUsingAPI(url)
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
    ##this would be much better with using seed until it runs out
    api = utils.getAPIURl(chaintoanalyse)
    url = f"{api}/cosmos/auth/v1beta1/accounts?pagination.limit=500000"
    print(url)
    try:
        response = utils.get_API_data_with_retry(url)
        print(response.raise_for_status())
    except Exception as e:
        print(f"{chaintoanalyse} didn't accept long query")
        ##some chains don't like the long query - this only does first 30k - doesn't check length
        url = f"{api}/cosmos/auth/v1beta1/accounts?pagination.limit=30000"
        response = utils.get_API_data_with_retry(url)
    return response.json()


def compare_delegators_with_analysis_chain(sourcechain, chaintoAnalyse):
    response = queryGetAllAccounts(chaintoAnalyse)["accounts"]
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
        else:
            print("Account [@type] doesn't match existing schema for:")
            try:
                print(accounts["@type"])
            except Exception as e:
                print(e)

    df_accounts_on_chain = pd.DataFrame(accounts_on_chain, columns=["address"])

    df_delegators = getDelegatorsAndConvert(sourcechain)

    chain_addresses = getChainToAnalyseAddresses(sourcechain, chaintoAnalyse, df_delegators)
    df_chain_addresses = pd.DataFrame(chain_addresses, columns=["address"])
    comparison = createComparisonDelegatorDataFrame(df_accounts_on_chain, df_chain_addresses)
    print(f"{len(comparison)} addresses found in {chaintoAnalyse} with delegations to Kleomedes in {sourcechain}")
    return comparison


if __name__ == "__main__":
    # chains=["sommelier","quicksilver","axelar","osmosis","cosmoshub","shentu","secretnetwork","migaloo","stafihub","nois","carbon","canto",]
    # chains=["akash"]
    chains = ["cudos"]
    sums = []
    failures = []
    for chain in chains:
        try:
            [sum, df] = main("juno", chain)
            sums.append([sum, chain])
        except Exception as e:
            print(e)
            failures.append(chain)
    print(sums)
    print(failures)
    df = pd.DataFrame(sums)
    parent_dir = utils.get_parent_dir()
    full_path = os.path.join(parent_dir, "results/allChainSumsFromJunoDelegators.csv")
    df.to_csv(full_path)
