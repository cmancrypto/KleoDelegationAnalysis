from delegatorSnapshotUtils import getValidatorDelegationResponseFromAPI, getDelegatorsAndConvert
from datetime import datetime, date 
import pandas as pd
import os
import json

#this script will do a snapshot of all validators
#it will query a pre-generated "validator.json" file which contains all of the validators that Kleomedes has (can be re-generated using getValidator.py)
#snapChainList takes this list of chains and queries each of them saving a snapshot and putting into the log file (csv and json) details of the snapshot so it can be recalled later for data analysis
#created by Cman



def takeSnapshot(chain):
    df=getDelegatorsAndConvert(chain)
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
    filename=f"./snapshots/{chain}{date_time}.csv"
    df.to_csv(filename, index=False)
    return [filename, chain, df]


def logSnapshot(filename,chain,sum,countdelegators):
    # Log the filename and date
    log_filename = 'log.csv'
    log_df = pd.DataFrame({
        'filename': [filename],
    'date': [date.today()],
    "chain": [chain],
    "tokensum": sum,
    "countdelegators": countdelegators
    })
    log_df.to_csv(log_filename, index=False, mode='a', header=not os.path.exists(log_filename))

##define a function to do the snapshot and then log it, wrapped in try except and returns a success parameter
def takeSnapshotandLog(chaintosnap):
    try: 
        [filename,chain,df]=takeSnapshot(chaintosnap)
        sum=df["value"].sum()
        countdelegators=len(df["value"])
        logSnapshot(filename,chain,sum,countdelegators)
        success=True
    except Exception as e: 
        print(e)
        success=False
    return success


def snapChainList(list_of_chains):
    for chain in list_of_chains:
        try:
            print(chain)
            takeSnapshotandLog(chain)
        except Exception as e: 
            print(f"error:{e} on {chain}")

def getChainList(path):
    with open(path,"r") as f: 
        data=json.load(f)
    chain_list=list(data.keys())
    return chain_list


if __name__ == "__main__":
    ##can create new validator list if reqd out of get getValidator.py
    chainlist=getChainList("validatorlist.json")
    snapChainList(chainlist)