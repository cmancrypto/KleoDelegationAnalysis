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

def merge_snapshot_list(snapshot_df_list):
    merge_index=0
    merge_df=pd.DataFrame
    for snapshot_df in snapshot_df_list:
        if merge_index==0:
            merge_df=snapshot_df[["address","amount"]]
            merge_index=merge_index+1
        else:
            merge_df=pd.merge(merge_df,snapshot_df[["address","amount"]], on = "address", how = "outer")
            merge_df['amount_x'] = merge_df['amount_x'].fillna(0)
            merge_df['amount_y'] = merge_df['amount_y'].fillna(0)
            merge_df['amount'] = merge_df['amount_x'] + merge_df['amount_y']
            merge_df = merge_df.drop(['amount_x', 'amount_y'], axis=1)
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
    print(formatted_df)
    return formatted_df

def get_kleo_allocations_from_push_snapshots(chain: str, snapshot_date_list: list, total_ukleo_alloc : int):
    snapshot_df_list=get_snapshot_df_list(chain, snapshot_date_list)
    merge_df= merge_snapshot_list(snapshot_df_list)
    shares_df=get_shares(merge_df)
    kleo_alloc_df=get_kleo_alloc(shares_df,total_ukleo_alloc)
    file_path= f"{chain}_push_ukleo_allocations.json"
    kleo_alloc_df.to_json(file_path)




if __name__ == "__main__":
    get_kleo_allocations_from_push_snapshots("akash",["2023-04-30","2023-05-10","2023-05-20"],int(425000*1E6))


