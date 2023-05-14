
import csv
import delegations_on_other_chains
import os
import csv
import pandas as pd

import utils

## takes a snapshot of all kleomedes validators on Kleomedes chains and converts addresses that also have an account on "chain to get addresses"
##in the chain to get addresses bech32 format - will also create a csv for each chain as part of delegations_on_other_chains
def get_addresses_on_chain_for_all_chains(chain_to_get_addresses : str, chains_to_ignore : list = ["cosmoshub"]):
        
        chains=delegations_on_other_chains.getValidatorChains()
        main_chain_slip44=delegations_on_other_chains.get_slip_44(chain_to_get_addresses)
        sums=[]
        dfs=[]
        failures=[]
        slip_44_mismatch=[]

        if chain_to_get_addresses in chains:
            chains.remove(chain_to_get_addresses)

        for chain in chains:
            if chain not in chains_to_ignore:
                print(chain)
                chainslip44=delegations_on_other_chains.get_slip_44(chain)
                if delegations_on_other_chains.get_slip_44(chain) == main_chain_slip44:
                        print(f"chainslip match for {chain}")
                        try:
                            [sum, df] = delegations_on_other_chains.main(chain, chain_to_get_addresses)
                            sums.append([sum, chain])
                            dfs.append(df)
                            #print(sum)
                            #print(df)
                        except Exception as e: 
                            print(e)
                            failures.append(chain)
                else: 
                    slip_44_mismatch.append(chain)
            print("slip44 mismatches:")
            print(slip_44_mismatch)
            print("failures:")
            print(failures)
    
        return dfs

def get_chains_from_csv(chain_to_get_addresses : str, chains_to_ignore : list = ["cosmoshub"]):
        chains=delegations_on_other_chains.getValidatorChains()
        main_chain_slip44=delegations_on_other_chains.get_slip_44(chain_to_get_addresses)
        if chain_to_get_addresses in chains:
            chains.remove(chain_to_get_addresses)
        dfs=[]
        for chain in chains:
            if chain not in chains_to_ignore:
                print(chain)
                chainslip44=delegations_on_other_chains.get_slip_44(chain)
                if delegations_on_other_chains.get_slip_44(chain) == main_chain_slip44:
                    try:
                        parent_dir = utils.get_parent_dir()
                        filename = f"{chain}balancesOn{chain_to_get_addresses}.csv"
                        full_path = os.path.join(parent_dir, "results", filename)
                        df = pd.read_csv(full_path, index_col=0)
                        df["source_chain"] = chain
                        dfs.append(df)
                    except Exception as e:
                         print(e)
        combined_df=pd.concat(dfs,ignore_index=True)
        combined_df.drop_duplicates(subset='1', inplace=True)
        combined_df=combined_df[combined_df["0"] != 0]
        full_path = os.path.join(parent_dir, f"results/allChainDelegators{chain_to_get_addresses}Address.csv")
        combined_df.to_csv(full_path)
        print(combined_df)

if __name__ == "__main__":
    #get_addresses_on_chain_for_all_chains("sommelier")
    get_chains_from_csv("akash")