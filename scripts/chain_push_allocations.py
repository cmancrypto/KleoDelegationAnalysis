import json

import pandas as pd
import requests
from get_chain_revenues import get_delegator_list

def get_snapshot_df_list(chain_name : str, list_of_dates : list) -> list[pd.DataFrame]:
    snapshot_df_list=[]
    for date in list_of_dates:
        data=get_delegator_list(chain_name,date)
        delegators=data["delegators"]
        snapshot_df=pd.DataFrame(delegators)
        snapshot_df_list.append(snapshot_df)
    return snapshot_df_list

def merge_snapshot_list(snapshot_df_list, create_check_csv = True):
    merge_index=0
    merge_df=pd.DataFrame
    for snapshot_df in snapshot_df_list:

        if create_check_csv == True:
            snapshot_df.to_csv(f"snapshot_{merge_index}.csv")

        if merge_index==0:
            merge_df=snapshot_df[["address","amount"]]
            merge_index=merge_index+1

        else:
            merge_df=pd.merge(merge_df,snapshot_df[["address","amount"]], on = "address", how = "outer")
            merge_df['amount_x'] = merge_df['amount_x'].fillna(0)
            merge_df['amount_y'] = merge_df['amount_y'].fillna(0)
            merge_df['amount'] = merge_df['amount_x'] + merge_df['amount_y']
            merge_df = merge_df.drop(['amount_x', 'amount_y'], axis=1)
            merge_index=merge_index+1
    if create_check_csv == True:
        merge_df.to_csv("merge.csv")
    return merge_df

def get_shares(merge_df):
    sum_tokens_in_snapshots=merge_df["amount"].sum()
    print(sum_tokens_in_snapshots)
    merge_df["shares"]=merge_df["amount"]/sum_tokens_in_snapshots
    return merge_df

def get_kleo_alloc(merge_df_shares, total_ukleo_alloc):
    merge_df_shares["ukleo"]=merge_df_shares["shares"]*total_ukleo_alloc
    merge_df_shares["ukleo"]=merge_df_shares["ukleo"].round(0)
    formatted_df=merge_df_shares[["address","ukleo"]]
    return formatted_df

def get_kleo_allocations_from_push_snapshots(chain: str, snapshot_date_list: list, total_ukleo_alloc : int):
    snapshot_df_list=get_snapshot_df_list(chain, snapshot_date_list)
    merge_df= merge_snapshot_list(snapshot_df_list)
    shares_df=get_shares(merge_df)
    kleo_alloc_df=get_kleo_alloc(shares_df,total_ukleo_alloc)
    kleo_alloc_df.to_csv("kleo_alloc.csv")
    file_path= f"{chain}_push_ukleo_allocations.json"
    outfile=open(file_path,"w")
    kleo_alloc_dict=kleo_alloc_df.to_dict("records")
    print(kleo_alloc_dict)
    json.dump(kleo_alloc_dict,fp=outfile)






if __name__ == "__main__":
    get_kleo_allocations_from_push_snapshots("akash",["2023-04-21","2023-04-28","2023-05-05","2023-05-12","2023-05-19","2023-05-26","2023-06-02","2023-06-09"],int(425000*1E6))


