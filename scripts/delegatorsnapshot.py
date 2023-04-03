from delegatorSnapshotUtils import getValidatorDelegationResponseFromAPI, getDelegatorsAndConvert

def takeSnapshot(chain):
    df=getDelegatorsAndConvert(chain)
    print(df)

takeSnapshot("juno")