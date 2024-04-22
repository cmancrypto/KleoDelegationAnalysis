from get_NFT_staking_amount import get_all_owners_from_snapshot, convert_owners_address
from get_chain_revenues import get_delegator_list
from utils import convert_address_to_address
import pandas as pd
import json

##this tool is used with a snapshot from https://studio.stargaze.zone/snapshots/holders/ to check their delegations to Kleomedes using the Kleomedes API
##it can create a distribution snapshot for Kleo at a scaling amount (i.e 0.1 Kleo/Stars)
##it treats NFT holders of multiple as 1x NFT holder no scaling applied


def main(chain: str, snapshot_date: str, NFT_snapshot_filepath : str, create_snapshot : bool = False, create_distribution_json : bool = False):
    ##get the delegator list using the Kleomedes API at a date
    delegator_list = get_delegator_list(chain_name=chain, date=snapshot_date)
    delegators = delegator_list["delegators"]
    delegator_df = pd.DataFrame(delegators)
    ##get the list of NFT holders
    nft_owners=get_all_owners_from_snapshot(NFT_snapshot_filepath)
    print(delegator_df)


    #check which delegator addresses from the dataframe are in owners
    mask=delegator_df["address"].isin(nft_owners)
    delegator_df.to_csv("NFT_push_start.csv")
    #make a new dataframe from the delegator_df mask so that we're not manipulating a slice
    snapshot_delegators=delegator_df[mask].copy()
    print(snapshot_delegators)


    if create_snapshot == True:
        #sets our bech32 conversion
        #todo - make this calculate from chain using utils get bech32
        from_chain_bech32 = "stars"
        to_chain_bech32 = "juno"

        #use this for scaling airdrops - converts the amount of tokens (as utokens) into a secoond token (in our case Kleo)
        #is multiplicative - i.e amount * convered_amount_scaling = converted amount
        converted_amount_scaling=0.1


        for index, row in snapshot_delegators.iterrows():
            snapshot_delegators.loc[index,"converted_address"]=convert_address_to_address(fromchain_bech32=from_chain_bech32,tochain_bech32=to_chain_bech32,address=row["address"])
            ###first scale, then convert to integer to round down, then to string for json
            snapshot_delegators.loc[index,"converted_amount_str"]=str(int(row["amount"]*converted_amount_scaling))
            ##keep the raw converted amount to do sums on or normal integer things
            snapshot_delegators.loc[index, "converted_amount"] = (int(row["amount"] * converted_amount_scaling))

        if create_distribution_json == True:
            distribution_df=pd.DataFrame()
            ##use the strings for json snapshot - not the integers
            distribution_df[["address","amount"]]=snapshot_delegators[["converted_address","converted_amount_str"]]
            #distribution_df.to_json("nft_snapshot.json")
            kleo_alloc_dict = distribution_df.to_dict("records")
            print(kleo_alloc_dict)
            outfile = open("nft_snapshot.json", "w")
            json.dump(kleo_alloc_dict, fp=outfile)
            total_distribution=snapshot_delegators["converted_amount"].sum()
            total_staked = snapshot_delegators["amount"].sum()
            print(f"total to distribute is: {total_distribution/1E6}")
            print(f"total staked is: {total_staked/1E6}")





    snapshot_delegators.to_csv(f"NFT_snapshot_delegators{snapshot_date}.csv")


main(chain = "stargaze", snapshot_date= "2024-04-17", NFT_snapshot_filepath= "snapshot.csv", create_snapshot=True, create_distribution_json=True)

