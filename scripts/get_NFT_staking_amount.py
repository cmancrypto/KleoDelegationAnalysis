import stargaze_api_query
from delegations_on_other_chains import queryDelegatedBalancesByAddressListAPI
import pandas as pd

def get_all_owners(collection_addr : str, id_range : list):
    owners=[]
    for index,id in enumerate(id_range):

        owner=stargaze_api_query.query_stargaze_token_owner(collectionAddr=collection_addr,tokenId=str(id))
        print(f"owner of address {index} of {len(id_range)} is {owner}")
        owners.append(owner)
    print(owners)
    return owners

def get_all_delegations(addresses,chain):
        delegations=queryDelegatedBalancesByAddressListAPI(chain_addresses=addresses,chaintoanalyse=chain)
        return delegations



if __name__== "__main__":
    owners=get_all_owners("stars166kqwcu8789xh7nk07fcrdzek54205u8gzas684lnas2kzalksqsg5xhqf", [*range(1,5000)])
    delegations=get_all_delegations(addresses=owners, chain = "stargaze")
    df=pd.DataFrame(delegations)
    sum_column = df.iloc[:, 0].sum()
    print(sum_column/1E6)


