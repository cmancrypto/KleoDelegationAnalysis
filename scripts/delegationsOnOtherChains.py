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
    
    for index,address in enumerate(akash_addresses):
        print(index)
        url=f"https://akash-api.polkachu.com/cosmos/staking/v1beta1/delegations/{address}"
        try:
            delegation_response=helper.snapshotDelegatorsUsingAPI(url)
            sum_delegator=0
            if len(delegation_response)>0:
                for delegations in delegation_response:
                    delegation=float(delegations["delegation"]["shares"])
                    sum_delegator=delegation+sum_delegator
                akash_balances.append(sum_delegator)
        except:
            print("exception occured")
    df=pd.DataFrame(akash_balances)
    df.to_csv("akash_balances.csv")
            

main()
