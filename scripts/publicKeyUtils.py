import delegations_on_other_chains
import csv
import pandas as pd


##this code is specifically for querying delegators and then spitting out the public key in a CSV 
##this can then be used to query the shitty chains that don't use the standard bech32 conversion 

##queries delegators on Source Chain 
##gets public keys from API response

# creates a file called input.csv
# use typescript script utilsTS to turn it into address.csv

def getDelegatorsPublicKeysToCSV(sourcechain):
    dfDelegators = delegations_on_other_chains.getDelegatorsAndConvert(sourcechain)
    response = delegations_on_other_chains.queryGetAllAccounts(sourcechain)
    accounts = response["accounts"]

    with open('input.csv', 'w', newline="") as csvfile:
        # Create CSV writer object
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(['address'])
        for account in accounts:
            try:
                ##only get the pub keys for kleo delegators, this could be done better, but i'd already written it to get all pub keys for the chain
                if account["address"] in dfDelegators["address"].tolist():
                    print(account)
                    try:  ##this catches entries without a pub_key key
                        if account["pub_key"] is not None:
                            ##we have to use this since some of the addresses have multiple public keys in a key called "public_keys" 
                            if "public_keys" not in account["pub_key"]:
                                writer.writerow([account["pub_key"]["key"]])
                            else:
                                for count, keys in enumerate(account["pub_key"]["public_keys"]):
                                    print(keys)
                                    writer.writerow([keys["key"]])
                    except KeyError as e:
                        print(e)
            except KeyError as e:
                print(e)


def importCSVCheckBalances(chaintoanalyse):
    # define the name of the CSV file
    csv_file = 'addresses.csv'

    # create an empty list to store the addresses
    addresses = []

    # open the CSV file and read its contents
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        # skip the header row, if there is one
        next(reader, None)
        # loop over each row in the file and append the address to the list
        for row in reader:
            address = row[0]
            addresses.append(address)
    ##chain_addresses are the converted addresses
    chain_addresses = addresses

    # get all of the addresses on the chain - so we can check if the converted addresses are even there.
    allAddresses = delegations_on_other_chains.queryGetAllAccounts(chaintoanalyse)["accounts"]
    accountsOnChain = []
    for accounts in allAddresses:
        if accounts["@type"] == "/cosmos.auth.v1beta1.BaseAccount":
            try:
                accountsOnChain.append(accounts["address"])
                print(accounts)
            except Exception as e:
                print(f"exception{e}")
        elif accounts["@type"] == "/injective.types.v1beta1.EthAccount" or accounts[
            "@type"] == "/ethermint.types.v1.EthAccount":
            try:
                accountsOnChain.append(accounts["base_account"]["address"])
                print(accounts)
            except Exception as e:

                print(f"exception{e}")
        else:
            print("Account [@type] doesn't match existing schema for:")
            print(accounts)

    dfAllAddresses = pd.DataFrame({"address": accountsOnChain})
    dfchain_addresses = pd.DataFrame({"address": chain_addresses})
    dfComparison = dfAllAddresses[dfAllAddresses.address.isin(dfchain_addresses.address)]
    comparison_addresses = dfComparison.address.tolist()
    print(comparison_addresses)
    chainBalancesByAddress = delegations_on_other_chains.queryDelegatedBalancesByAddressListAPI(comparison_addresses,
                                                                                                chaintoanalyse)
    df = pd.DataFrame(chainBalancesByAddress)
    df.to_csv(f"results/delegatorbalancesOn{chaintoanalyse}.csv")


if __name__ == "__main__":
    getDelegatorsPublicKeysToCSV("juno")
    answer = input("run the typescript file to process input.csv and create addresses.csv")
    importCSVCheckBalances("injective")
