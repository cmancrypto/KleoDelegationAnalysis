import pandas as pd

import get_chain_revenues
from get_chain_revenues import ManualAPR
import tenacity


def get_all_kleomedes_chains(validator_list):
    chain_list=[]
    for validator in validator_list:
        if validator.get("status")=="BOND_STATUS_BONDED":
            chain_list.append(validator["chain_name"])
    return chain_list

def main(manual_apr_chains: list, date):
    validator_list=get_chain_revenues.get_validator_list()
    chains=get_all_kleomedes_chains(validator_list)
    revenues = get_chain_revenues.get_chain_revenues(chains,date, manual_apr_chains)
    return revenues

def main_self_stake_revenues(manual_apr_chains):
    validator_list = get_chain_revenues.get_validator_list()
    chainlist = get_all_kleomedes_chains(validator_list)
    self_stake_revenues=get_chain_revenues.get_self_stake_revenues(chainlist, manual_apr_chains)
    return self_stake_revenues

if __name__ == "__main__":
    date="2023-08-03"
    manual_apr_chains = [ManualAPR("jackal", 0.30).to_dict(), ManualAPR("kujira", 0.01).to_dict(), ManualAPR("cudos", 0.08).to_dict(), ManualAPR("stride", 0.10).to_dict()]
    self_stake=main_self_stake_revenues(manual_apr_chains)
    print(self_stake)
    df_self_stake=pd.DataFrame(self_stake)
    df_self_stake.to_csv("selfStakeRevenue.csv")
    revenues=main(manual_apr_chains,date)
    df=pd.DataFrame(revenues)
<<<<<<< Updated upstream
    revenue_sum=df["revenue"].sum()
    df.to_csv("KleoRevenue.csv")
    print(revenues)
    print(revenue_sum)
=======
    print(df)
    revenuetotal=df["revenue"].sum()
    df.to_csv("KleoRevenue.csv")
    print(revenues)
    print(f"total revenue : {revenuetotal}")
    
>>>>>>> Stashed changes

