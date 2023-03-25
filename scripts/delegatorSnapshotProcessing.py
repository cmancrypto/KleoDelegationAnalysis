import requests
import pandas as pd
import json

def snapshotDelegatorsUsingAPI(url: str, createcsv: bool = False):
    #bool doesn't work yet - too lazy
    response=requests.get(url)
    delegation_responses=response.json()["delegation_responses"]
    return delegation_responses

def snapshotDelegatorsFromJSON(filepath: str):
    f=open(filepath)
    delegation_responses=json.load(f)["delegation_responses"]
    return delegation_responses


def convertDelegationResponseToDataFrame(data)->pd.DataFrame:
    delegators=[]
    for dicts in data:
        address=dicts["delegation"]["delegator_address"]
        value=dicts["delegation"]["shares"]
        address_value_dict={"address":address,"value":value}
        delegators.append(address_value_dict)
    dfDelegators = pd.DataFrame(delegators)
    return dfDelegators

def convertStrValuestoFloatValues(dfDelegators):
    dfDelegators["value"]=dfDelegators["value"].astype(float)
    return dfDelegators

def createComparisonDelegatorDataFrame(dfDelegatorSnapOne, dfDelegatorSnapTwo):
    ##returns a dataFrame(address,value) from SnapTwo that had addresses in SnapOne 
    dfComparisonDelegator=dfDelegatorSnapTwo[dfDelegatorSnapTwo.address.isin(dfDelegatorSnapOne.address)]
    return dfComparisonDelegator

def sumDelegations(dfDelegator):
    delegationTotal=dfDelegator.sum()
    return delegationTotal

##go from JSON to DataFrame with values 
def convertJSONtoDataFrame(delegation_responses):
    dfDelegators=convertDelegationResponseToDataFrame(delegation_responses)
    dfDelegators=convertStrValuestoFloatValues(dfDelegators)
    return dfDelegators