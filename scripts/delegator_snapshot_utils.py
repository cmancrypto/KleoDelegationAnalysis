import requests
import pandas as pd
import json
import utils
from constants import COSMOS_DIR_API, COSMOS_DIR_REST_PROXY


def snapshot_delegators_using_API(url: str):
    delegation_responses = get_all_pages_of_key_from_API_response(url=url, key_to_return="delegation_responses")
    return delegation_responses


def snapshotDelegatorsFromJSON(filepath: str):
    f = open(filepath)
    delegation_responses = json.load(f)["delegation_responses"]
    return delegation_responses


def snapshot_delegators_from_csv(csv_file_path):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)
        return df
    except Exception as e:
        print("Error:", str(e))
        return None

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
    # pagination fixed
    query = f"/cosmos/staking/v1beta1/validators/{validatoraddress}/delegations?pagination.limit=1000"
    url = f"{api}{query}"
    delegation_response = snapshot_delegators_using_API(url)
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


def get_all_pages_of_key_from_API_response(url, key_to_return: str) -> list:
    """

    :param url: API response url
    :param key_to_return: the desired Key from the API response to return i.e "accounts" or "delegation_responses"
    :return: array of responses from the API
    """
    # set up pagination_key to iterate through all the responses
    pagination_key = None
    # create empty delegations_responses
    key_to_return_responses = []
    # create infinite loop to evaluate pagination key
    while True:
        # set API query params
        params = {"pagination.key": pagination_key}
        # return response
        response = utils.get_API_data_with_retry(url, params=params)
        # check if response is valid, this should be certain with "retry" but to be sure
        if response.status_code == 200:
            # add response to the list
            key_to_return_responses.extend(response.json()[key_to_return])
        # check if there is "pagination" and "next_key" in the response
        if 'pagination' in response.json() and 'next_key' in response.json()["pagination"]:
            # if next key value is None - break
            if response.json()["pagination"]["next_key"] is None:
                break
            pagination_key = response.json()["pagination"]["next_key"]
            params = {"pagination.key": pagination_key}
        else:
            print("break")
            break
    return key_to_return_responses
