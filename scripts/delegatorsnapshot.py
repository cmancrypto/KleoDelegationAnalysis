from delegatorSnapshotUtils import getValidatorDelegationResponseFromAPI, getDelegatorsAndConvert
from datetime import datetime, date 
import pandas as pd
import os

def takeSnapshot(chain):
    df=getDelegatorsAndConvert(chain)
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
    filename=f"./snapshots/{chain}{date_time}.csv"
    df.to_csv(filename, index=False)
    return [filename, chain, df]


def logSnapshot(filename,chain):
    # Log the filename and date
    log_filename = 'log.csv'
    log_df = pd.DataFrame({
        'filename': [filename],
    'date': [date.today()],
    "chain": [chain]
    })
    log_df.to_csv(log_filename, index=False, mode='a', header=not os.path.exists(log_filename))

##define a function to do the snapshot and then log it, wrapped in try except and returns a success parameter
def takeSnapshotandLog(chaintosnap):
    try: 
        [filename,chain,df]=takeSnapshot(chaintosnap)
        logSnapshot(filename,chain)
        success=True
    except Exception as e: 
        print(e)
        success=False
    return success


def snapChainList(list_of_chains):
    for chain in list_of_chains:
        try:
            takeSnapshotandLog(chain)
        except Exception as e: 
            print(f"error:{e}")
    
if __name__ == "__main__":
    chainlist=["juno","kava","akash","cudos"]
    snapChainList(chainlist)