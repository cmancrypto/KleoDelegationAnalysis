import requests
import pandas as pd
import json
import delegatorSnapshotUtils as helper


def main():
    ##read API for current snapshot
    url = "https://juno-api.kleomedes.network/cosmos/staking/v1beta1/validators/junovaloper1x8u2ypdr35802tjyjqyxan8x85fzxe6sk0qmh8/delegations?pagination.limit=50000"
    current_delegation_response = helper.snapshotDelegatorsUsingAPI(url)
    dfCurrentDelegators = helper.convertJSONtoDataFrame(current_delegation_response)

    ##read the json for historical snapshot
    path = "final-snapshot.json"
    historical_delegation_response = helper.snapshotDelegatorsFromJSON(path)
    dfHistoricalDelegators = helper.convertJSONtoDataFrame(historical_delegation_response)

    sumCurrent = helper.sumDelegations(dfCurrentDelegators.value)
    sumHistorical = helper.sumDelegations(dfHistoricalDelegators.value)

    print(f"current snap: {sumCurrent} tokens")
    print(f"previous snap: {sumHistorical} tokens")

    comparisonDelegatorFrame = helper.createComparisonDelegatorDataFrame(dfHistoricalDelegators, dfCurrentDelegators)
    comparisonSumValues = helper.sumDelegations(comparisonDelegatorFrame.value)

    comparisonGrowthFrame = helper.createComparisonDelegatorDataFrame(dfCurrentDelegators, dfHistoricalDelegators)
    comparisonGrowthSum = helper.sumDelegations(comparisonGrowthFrame.value)

    print(f"from snapshot 1 still in snapshot 2 : {comparisonSumValues}")
    retained = comparisonSumValues / sumHistorical
    print(f"{round(retained * 100, 1)} % retained between snaps")
    print(
        f"addresses in both snaps had : {comparisonGrowthSum} in first snap and then  {comparisonSumValues}in 2nd - this is growth of {round(comparisonGrowthSum / comparisonSumValues, 1) * 100}%")
    print(
        f"there were {len(dfHistoricalDelegators)} delegators in first snap and there's now {len(comparisonDelegatorFrame)} of these delegators left")
    print(
        f"delegators from our first snap make up {round((comparisonSumValues / sumCurrent) * 100, 1)} % of our current delegators")


main()
