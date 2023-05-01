
import csv
import delegations_on_other_chains
import os
import csv
import pandas as pd

import utils

if __name__ == "__main__":
    chain_to_get_addresses="akash"
    chains=delegations_on_other_chains.getValidatorChains()
    main_chain_slip44=delegations_on_other_chains.get_slip_44(chain_to_get_addresses)
    print(main_chain_slip44)
    sums=[]
    dfs=[]
    failures=[]
    slip_44_mismatch=[]

    chains.remove(chain_to_get_addresses)
    chains.remove("cosmoshub")

    for chain in chains:
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

    joined_df=pd.concat(dfs,ignore_index=True)
    deduplicated_df = joined_df.drop_duplicates()
    parent_dir = utils.get_parent_dir()
    full_path = os.path.join(parent_dir, f"results/allChainDelegators{chain_to_get_addresses}Address.csv")
    df.to_csv(full_path)