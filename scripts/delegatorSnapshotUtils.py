import requests
import pandas as pd
import json
import utils
from constants import COSMOS_DIR_API, COSMOS_DIR_REST_PROXY


def snapshotDelegatorsUsingAPI(url: str, createcsv: bool = False):
    # bool doesn't work yet - too lazy
    response = utils.get_API_data_with_retry(url)
    delegation_responses = response.json()["delegation_responses"]
    return delegation_responses


def snapshotDelegatorsFromJSON(filepath: str):
    f = open(filepath)
    delegation_responses = json.load(f)["delegation_responses"]
    return delegation_responses


def convertDelegationResponseToDataFrame(data) -> pd.DataFrame:
    delegators = []
    for dicts in data:
        address = dicts["delegation"]["delegator_address"]
        value = dicts["delegation"]["shares"]
        address_value_dict = {"address": address, "value": value}
        delegators.append(address_value_dict)
    df_delegators = pd.DataFrame(delegators)
    return df_delegators


def convertStrValuestoFloatValues(dfDelegators):
    dfDelegators["value"] = dfDelegators["value"].astype(float)
    return dfDelegators


def createComparisonDelegatorDataFrame(dfDelegatorSnapOne, dfDelegatorSnapTwo):
    ##returns a dataFrame(address,value) from SnapTwo that had addresses in SnapOne 
    dfComparisonDelegator = dfDelegatorSnapTwo[dfDelegatorSnapTwo.address.isin(dfDelegatorSnapOne.address)]
    return dfComparisonDelegator


def sumDelegations(dfDelegator):
    delegationTotal = dfDelegator.sum()
    return delegationTotal


##go from JSON to DataFrame with values
def convertJSONtoDataFrame(delegation_responses):
    dfDelegators = convertDelegationResponseToDataFrame(delegation_responses)
    dfDelegators = convertStrValuestoFloatValues(dfDelegators)
    return dfDelegators


##return delegator snapshot
def getValidatorDelegationResponseFromAPI(sourcechain):
    validatoraddress = getValidatorAddress(sourcechain)
    api = utils.getAPIURl(sourcechain)
    ##pagination here may be an issue eventually
    query = f"/cosmos/staking/v1beta1/validators/{validatoraddress}/delegations?pagination.limit=50000"
    url = f"{api}{query}"
    delegation_response = snapshotDelegatorsUsingAPI(url)
    return delegation_response


##returns the validator addresses reading a pre-built validatorlist.json
def getValidatorAddress(chain):
    with open(utils.get_absolute_parent_file_path("validatorlist.json"), 'r') as f:
        data = json.load(f)
    # Get the validator address for a given chain name
    if chain in data:
        validator_address = data[chain]
        return validator_address
    else:
        print(f"No validator address found for {chain}")


# convert delegators to dataframe - uses getValidatorDelegationResponseFromAPI
def getDelegatorsAndConvert(chain):
    delegation_response = getValidatorDelegationResponseFromAPI(chain)
    dfDelegators = convertJSONtoDataFrame(delegation_response)
    return dfDelegators
