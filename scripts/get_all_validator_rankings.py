import json
import utils
import pandas as pd

def get_validator_list(chain):
    url=f"https://validators.cosmos.directory/chains/{chain}"
    response = utils.get_API_data_with_retry(url)
    validators=response.json()["validators"]
    return validators

def get_validator_ranks_from_validator_response(validator_list):
    validator_tokens=[]
    for validator in validator_list:
            if validator["active"] == True:
                validator_dict={"rank":validator["rank"],"delegations":validator["tokens"],"moniker":validator["moniker"]}
                validator_tokens.append(validator_dict)
    #validator_rank_list=validator_rank_list.sort(reverse=True)
    print(len(validator_tokens))
    #validator_tokens.sort(reverse = False)
    return validator_tokens

def get_percentile_value(validator_rank_list,percentile: int =80):
    converted_percentile=percentile/100
    print(converted_percentile)
    rank=int(converted_percentile*len(validator_rank_list))
    print(rank)
    df=pd.DataFrame(validator_rank_list)
    delegation_at_percentile=df.loc[df["rank"] == rank]["delegations"].values[0]
    print(delegation_at_percentile)
    return delegation_at_percentile
     
def get_all_chains():
    # Define the URL for the chains list page
    chains_url = "https://chains.cosmos.directory/"

    # Send a GET request to the chains list page
    response = utils.get_API_data_with_retry(chains_url)

    # Check if the response was successful (status code 200)
    if response.status_code != 200:
        raise ValueError("Failed to fetch chains list page")

    # Extract the list of chains from the response
    chains = response.json()
    
    return chains
    
def get_all_chains_validator_by_percentile(percentile:int):
    all_delegations_at_percentile = []
    chains=get_all_chains()  
    for chain in chains["chains"]:
        print(chain)
        response=get_validator_list(chain)
        ranks=get_validator_ranks_from_validator_response(response)
        delegation_at_percentile = get_percentile_value(ranks,percentile)
        delegation_dict= {"chain": chain, "delegation":delegation_at_percentile}
        all_delegations_at_percentile.append(delegation_dict)
    
    with open(f'delegations{percentile}percentile.json', 'w') as f:
            json.dump(all_delegations_at_percentile, f)

def get_list_chains_validator_by_percentile(percentile:int,chains:list):
    all_delegations_at_percentile = []
    for chain in chains:
        print(chain)
        response=get_validator_list(chain)
        ranks=get_validator_ranks_from_validator_response(response)
        delegation_at_percentile = get_percentile_value(ranks,percentile)
        delegation_dict= {"chain": chain, "delegation":delegation_at_percentile}
        all_delegations_at_percentile.append(delegation_dict)
        
    with open(f'delegations{percentile}percentile.json', 'w') as f:
            json.dump(all_delegations_at_percentile, f)





if __name__ == "__main__":
    get_list_chains_validator_by_percentile(75,["umee","akash","coreum","cudos"])