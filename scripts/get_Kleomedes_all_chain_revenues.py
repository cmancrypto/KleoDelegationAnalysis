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

if __name__ == "__main__":
    date="2023-07-23"
    manual_apr_chains = [ManualAPR("jackal", 0.30).to_dict(), ManualAPR("kujira", 0.01).to_dict(), ManualAPR("cudos", 0.08).to_dict(), ManualAPR("stride", 0.10).to_dict()]
    revenues=main(manual_apr_chains,date)
    df=pd.DataFrame(revenues)
    df.to_csv("KleoRevenue.csv")
    print(revenues)

