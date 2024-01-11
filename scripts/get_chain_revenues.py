import os
import requests
from dotenv import load_dotenv
from utils import convert_address_to_address, get_network_bech32_prefix
import tenacity
from datetime import datetime
import pandas as pd
import json
import numpy as np
from delegations_on_other_chains import get_delegated_amount_by_address


@tenacity.retry(stop=tenacity.stop_after_delay(10))
def get_chain_data(chain: str):
    url=f"https://chains.cosmos.directory/{chain}"
    response= requests.get(url)
    chain_data= response.json()
    return chain_data


def get_prices_from_cosmos_api(chain_data) -> float: 
    try:
        prices=list(chain_data["chain"]["prices"]["coingecko"].values())
        #have to assume that 0 is the native token price
        price=prices[0]["usd"]
        return price
    except KeyError as e:
        print(f"no key for {e}")
        #return price of zero
        return 0

##def get_prices_from_osmosis_api(chain_data) -> float: 
##todo finish this 
    try:
        coin_name=list(chain_data["chain"]["prices"]["coingecko"].values())
        #have to assume that 0 is the native token price
        price=prices[0]["usd"]
        return price
    except KeyError as e:
        print(f"no key for {e}")
        #return price of zero
        return 0


def get_staking_apr(chain_data):
    try: 
        staking_apr=chain_data["chain"]["params"]["calculated_apr"]
        return staking_apr
    except Exception as e: 
        print(f"Unable to get staking_apr for {e}")
        raise ValueError("Staking APR is 0 or not available")
        return 0




@tenacity.retry(stop=tenacity.stop_after_delay(10))
def get_delegator_list(chain_name : str, date : str):
    url=f"https://snapshots.dev.kleomed.es/api/v1/delegator/snapshots/{chain_name}/{date}"
    response= requests.get(url)
    if response.status_code ==200:
        data= response.json()
        return data
    else:
        print(f"error on {date}")
        return None

#todo finish and validator commission
@tenacity.retry(stop=tenacity.stop_after_delay(10))
def get_validator_list():
    url=f"https://snapshots.dev.kleomed.es/api/v1/validators"
    response= requests.get(url)
    response.raise_for_status()
    validator_list=response.json()
    return validator_list

def get_validator_commission(chain : str, validator_address: str) -> float:
    url=f"https://rest.cosmos.directory/{chain}/cosmos/staking/v1beta1/validators/{validator_address}"
    response= requests.get(url)
    response.raise_for_status()
    validator_details=response.json()
    validator_commission=validator_details["validator"]["commission"]["commission_rates"]["rate"]
    return validator_commission

def get_validator_address(chain: str,validator_list : list[dict]):
    for validator in validator_list:
        if validator.get("chain_name")==chain:
            return validator["operator_address"]


def get_chain_revenues(chains : list, date : str = datetime.now().strftime("%y-%m-%d"), manual_apr_chains : list = []) -> list:
    chain_revenues=[]
    failed_chains=[]

    #get the validator list
    try: 
        validator_list= get_validator_list()
    except Exception as e:
        print("error in validator list")
        print(e) 

    #iterate through the chainlist
    for chain in chains:
        try:
            #get the delegator list
            print(f"getting delegator list for {chain}")
            data=get_delegator_list(chain_name=chain,date=date)
            delegators = data["delegators"]
            delegator_df=pd.DataFrame(delegators)
            raw_amount_sum=delegator_df["amount"].sum()

            #get the chain_data json for staking APR and Price
            chain_data=get_chain_data(chain)

            #get the prices
            decimal_divisor=pow(10,get_decimals(chain))
            #this adjusts for the decimals in the return and gets it into "denom" for prices
            amount_sum = raw_amount_sum/decimal_divisor
            print(f"getting price for {chain}")
            price=get_prices_from_cosmos_api(chain_data)
            value_delegated=amount_sum*price
            print(f"value delegated is {value_delegated}")
            #get the staking APR
            manual_apr= check_manual_staking_apr(chain,manual_apr_chains)
            if manual_apr == None:
                staking_apr=get_staking_apr(chain_data)
            else:
                staking_apr=manual_apr
            print(f"staking_apr is {staking_apr}")
            #get the validator share
            #get the correct validator first
            print(f"getting validator info for {chain}")
            validator_address=get_validator_address(chain = chain, validator_list=validator_list)
            print(f"validator_address is {validator_address}")
            validator_commission=get_validator_commission(chain,validator_address)
            print(f"validator_commission is {validator_commission}")

            revenue= float(value_delegated) * float(staking_apr) * float(validator_commission)
            
            if revenue > 0: 
                chain_dict={"chain_name":chain,"date":date,"revenue":revenue,"total_value_delegated":value_delegated}
                chain_revenues.append(chain_dict)
            else: 
                failed_chains.append([chain,"revenue is 0"])
        except Exception as e:
            print(e)
            failed_chains.append([chain,e])
    print("failed chains are: ")
    print(failed_chains)
    return chain_revenues

def get_validator_self_stake(chain,validator_address):
    url= f"https://rest.cosmos.directory/{chain}"
    bech32_prefix=get_network_bech32_prefix(chain)
    chain_validator_prefix=f"{bech32_prefix}valoper"
    converted_address=convert_address_to_address(chain_validator_prefix,validator_address,bech32_prefix)
    self_stake=get_delegated_amount_by_address(url,converted_address)
    return self_stake[0]

def get_self_stake_revenues(chains : list, manual_apr_chains : list = []):
    chain_revenues = []
    failed_chains = []
    # get the validator list
    try:
        validator_list = get_validator_list()
    except Exception as e:
        print("error in validator list")
        print(e)

        # iterate through the chainlist
    for chain in chains:
        print(f"getting self stake revenue for: {chain}")
        try:
            validator_address = get_validator_address(chain=chain, validator_list=validator_list)
            print(validator_address)
            raw_amount_sum=get_validator_self_stake(chain,validator_address)


            # get the chain_data json for staking APR and Price
            chain_data = get_chain_data(chain)

            # get the prices
            decimal_divisor = pow(10, get_decimals(chain))
            # this adjusts for the decimals in the return and gets it into "denom" for prices
            amount_sum = raw_amount_sum / decimal_divisor
            print(f"getting price for {chain}")
            price = get_prices_from_cosmos_api(chain_data)
            value_delegated = amount_sum * price
            print(f"value self delegated is {value_delegated}")
            # get the staking APR
            manual_apr = check_manual_staking_apr(chain, manual_apr_chains)
            if manual_apr == None:
                staking_apr = get_staking_apr(chain_data)
            else:
                staking_apr = manual_apr
            print(f"staking_apr is {staking_apr}")
            revenue = float(value_delegated) * float(staking_apr)

            if revenue > 0:
                chain_dict = {"chain_name": chain,"revenue": revenue}
                chain_revenues.append(chain_dict)
            else:
                failed_chains.append([chain, "revenue is 0"])
        except Exception as e:
            print(e)
            failed_chains.append([chain, e])
    print("failed chains are: ")
    print(failed_chains)
    return chain_revenues

def get_chain_shares_formatted(chain_revenues : list, ukleo_to_split: float) -> list:
    revenue_df=pd.DataFrame(chain_revenues)
    total_value=revenue_df["revenue"].sum()
    revenue_df["share"]=revenue_df["revenue"]/total_value
    revenue_df["cw20_allocation"]=revenue_df["share"]*ukleo_to_split
    revenue_df["cw20_allocation"]=revenue_df["cw20_allocation"].round(0)
    revenue_df["cw20_allocation"] = revenue_df["cw20_allocation"].astype(np.int64)
    formatted_df=revenue_df.drop(labels=["revenue","share"], axis=1)
    print(formatted_df.to_dict('records'))
    return formatted_df.to_dict('records')

def check_manual_staking_apr(string, manual_apr_chains : list):
    for dictionary in manual_apr_chains:
        if "name" in dictionary and dictionary["name"]== string: 
            return dictionary["apr"]
    

def get_decimals(chain : str):
    url=f"https://chains.cosmos.directory/{chain}"
    response= requests.get(url)
    data=response.json()
    denom=data["chain"]["staking"]["staking_tokens"][0]["denom"]
    #check decimals - compare denom in assets against staking denom to get correct asset decimals
    for assets in data["chain"]["assets"]:
        if assets["denom"] == denom:
            decimals = assets["decimals"]
            return decimals
    raise ValueError(f"No asset where denom = {denom}")

def get_formatted_buyback_params_json(chain_shares_formatted : list, write_json_file : bool = True):
    buyback_params={"buyback_params":chain_shares_formatted}
    if write_json_file == True:
        with open("buyback_params.json","w") as file:
            json.dump(buyback_params,file)
    return buyback_params
    


def main(chainlist : list, date: str, ukleo_distribution_amt, manual_apr_chains: list):
        revenues = get_chain_revenues(chainlist,date,manual_apr_chains)
        chain_shares_formatted=get_chain_shares_formatted(revenues,ukleo_distribution_amt)
        buyback_params=get_formatted_buyback_params_json(chain_shares_formatted)
        #print(buyback_params)
        return buyback_params





class ManualAPR: 

    def __init__(self, name, apr):
        self.name= name
        self.apr= apr 

    def to_dict(self):
        return {
            "name" : self.name, 
            "apr" : self.apr
        }


if __name__ == "__main__":
    chainlist= ["juno","passage","sentinel","stargaze","rebus","teritori","jackal","persistence","chihuahua","shentu","kujira","fetchhub","cudos","migaloo","akash"]
    manual_apr_chains = [ManualAPR("jackal",0.30).to_dict(),ManualAPR("kujira",0.01).to_dict(),ManualAPR("cudos",0.08).to_dict(),ManualAPR("stride",0.10).to_dict()]
    print(manual_apr_chains)
    buyback_params=main(chainlist, "2023-09-30", 85192*1E6,manual_apr_chains)
    df=pd.DataFrame(buyback_params["buyback_params"])
    print(df["cw20_allocation"].sum())
    df.to_csv("buyback_params.csv")