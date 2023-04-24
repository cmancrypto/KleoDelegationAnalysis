import json
import os
from datetime import datetime, date

import pandas as pd

import utils
from delegator_snapshot_utils import getDelegatorsAndConvert


# this script will do a snapshot of all validators
# it will query a pre-generated "validator.json" file which contains all of the validators that Kleomedes has (can be re-generated using getValidator.py)
# snapChainList takes this list of chains and queries each of them saving a snapshot and putting into the log file (csv and json) details of the snapshot so it can be recalled later for data analysis
# created by Cman


def take_snapshot(chain):
    df = getDelegatorsAndConvert(chain)
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
    parent_dir = utils.get_parent_dir()
    filename = f"{chain}{date_time}.csv"
    full_path = os.path.join(parent_dir, "snapshots", filename)
    df.to_csv(full_path, index=False)
    return [filename, chain, df]


def logSnapshot(filename, chain, sum, count_delegators):
    # Log the filename and date
    log_filename = 'log.csv'
    parent_dir = utils.get_parent_dir()
    full_path = os.path.join(parent_dir, log_filename)
    log_df = pd.DataFrame({
        'filename': [filename],
        'date': [date.today()],
        "chain": [chain],
        "tokensum": sum,
        "count_delegators": count_delegators
    })
    log_df.to_csv(full_path, index=False, mode='a', header=not os.path.exists(full_path))


##define a function to do the snapshot and then log it, wrapped in try except and returns a success parameter
def take_snapshot_and_log(chain_to_snap):
    try:
        [filename, chain, df] = take_snapshot(chain_to_snap)
        sum = df["value"].sum()
        countdelegators = len(df["value"])
        logSnapshot(filename, chain, sum, countdelegators)
        success = True
    except Exception as e:
        print(e)
        success = False
    return success


def snapChainList(list_of_chains, excluded_chains: list):
    for chain in list_of_chains:
        print(f"trying to snapshot {chain}")
        if chain not in excluded_chains:
            try:
                take_snapshot_and_log(chain)
                print(f"snapshot of: {chain} success")
            except Exception as e:
                print(f"error:{e} on {chain}")
        else:
            print(f"{chain} is on excluded list")


def getChainList(path):
    with open(utils.get_absolute_parent_file_path(path), "r") as f:
        data = json.load(f)
    chain_list = list(data.keys())
    return chain_list


if __name__ == "__main__":
    ##can create new validator list if reqd out of get getValidator.py
    chainlist = getChainList("validatorlist.json")
    print(chainlist)
    snapChainList(chainlist, excluded_chains=["cosmoshub"])
