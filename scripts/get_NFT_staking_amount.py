import stargaze_api_query
from delegations_on_other_chains import queryDelegatedBalancesByAddressListAPI, queryGetAllAccounts
import pandas as pd
from utils import get_network_bech32_prefix, convert_address_to_address

#tools to check the staking balance of owners of an NFT collection

#todo use the all accounts API call rather than 3000 individual API calls


#main
#used to check the staking balance of owners of an NFT collection
#requires collection addr, id range, chain to check (has to be same as collection addr)
def main(filename,chain):
    owners = get_all_owners_from_snapshot(filename)
    if not chain == "stargaze":
        owners=convert_owners_address(owners,chain)
    delegations = get_all_delegations(addresses=owners, chain=chain)
    df = pd.DataFrame(delegations)
    sum_column = df.iloc[:, 0].sum()
    print(sum_column / 1E6)

##converts the owners list of addresses from STARS to chain
def convert_owners_address(owners : list, chain : str):
    converted_owners=[]
    bech32_prefix=get_network_bech32_prefix(chain)
    for owner in owners:
        chain_address = convert_address_to_address(fromchain_bech32="stars", address=owner, tochain_bech32=bech32_prefix)
        converted_owners.append(chain_address)
    return converted_owners

#deprecated
##this method was made to use the stargaze API, this should be deprecated in favour of using the stargaze snapshot utility
#returns a list of owners STARS address
def get_all_owners_stargaze_api(collection_addr : str, id_range : list)-> list:
    owners=[]
    for index,id in enumerate(id_range):

        owner=stargaze_api_query.query_stargaze_token_owner(collectionAddr=collection_addr,tokenId=str(id))
        print(f"owner of address {index} of {len(id_range)} is {owner}")
        owners.append(owner)
    print(owners)
    return owners

##this method uses the csv from https://studio.stargaze.zone/snapshots/holders/ to create the owners shapshot
##this is the preferred method - owners snapshot has to go in the parent directory
##name can be whatever
def get_all_owners_from_snapshot(filename : str):
    full_path=f"../{filename}"
    df = pd.read_csv(full_path)
    owners=df["address"].tolist()
    print(owners)
    return(owners)
def get_all_delegations(addresses,chain):
        delegations=queryDelegatedBalancesByAddressListAPI(chain_addresses=addresses,chaintoanalyse=chain)
        return delegations


if __name__== "__main__":
    main(filename="snapshot.csv",chain = "dydx")



