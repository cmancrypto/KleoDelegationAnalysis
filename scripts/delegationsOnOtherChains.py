import requests 
import pandas as pd
import json
import delegatorSnapshotProcessing as helper
import utils 

def main(): 
    url="https://juno-api.kleomedes.network/cosmos/staking/v1beta1/validators/junovaloper1x8u2ypdr35802tjyjqyxan8x85fzxe6sk0qmh8/delegations?pagination.limit=50000"
    delegation_response=helper.snapshotDelegatorsUsingAPI(url)
    dfDelegators=helper.convertJSONtoDataFrame(delegation_response)
    akash_addresses=[]
    for delegator in dfDelegators["address"]:
        akash_address=utils.convert_address_to_address("juno",delegator,"akash")
        akash_addresses.append(akash_address)
    print(len(akash_addresses))
    
    akash_balances=[]

    cfg=utils.getAkashCFG()
    client=utils.getCosmpyClient(cfg)

    for index,address in enumerate(akash_addresses):
        print(index)
        try:
            s=client.query_staking_summary(address)
            if s.total_staked>0:
                akash_balances.append([address,s.total_staked])
                print(akash_balances)
        except:
            print("exception occured")
    df=pd.DataFrame(akash_balances)
    df.to_csv("akash_balances_2.csv")
            

main()
