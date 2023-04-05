import requests
import pandas as pd
import utils 
import json

chainlist=[]
validatorlist=[]

# Define the URL for the chains list page
chains_url = "https://chains.cosmos.directory/"

# Send a GET request to the chains list page
response = utils.get_API_data_with_retry(chains_url)

# Check if the response was successful (status code 200)
if response.status_code != 200:
    raise ValueError("Failed to fetch chains list page")

# Extract the list of chains from the response
chains = response.json()

# Loop through each chain in the list
for chain in chains["chains"]:
    # Get the chain ID and URL from the chain object
    chain_id = chain["name"]
    print(chain_id)
    ##this uses bad pagination, but should be ok until there's 5k validators on a chain or until a chain doesn't accept 5k pagination
    chain_url = f"https://rest.cosmos.directory/{chain_id}/cosmos/staking/v1beta1/validators?pagination.limit=5000"
    try:
            # Send a GET request to the validators endpoint for this chain
            response = utils.get_API_data_with_retry(f"{chain_url}",retries=3)
            ##handle failed return
            if response==None:
                continue
        # Check if the response was successful (status code 200)
            if response.status_code != 200:
                print(f"Failed to fetch validators for chain {chain_id}")
                continue

        # Extract the list of validators from the response
            validators = response.json()["validators"]

            # Loop through each validator in the list
            for validator in validators:
                # Check if the validator's moniker is Kleomedes
                if validator["description"]["moniker"] == "Kleomedes" or validator["description"]["moniker"] == "kleomedes":
                    # Found the Kleomedes validator, print its address
                    print(f"Kleomedes validator found on chain {chain_id}, address: {validator['operator_address']}")
                    validatorlist.append(validator['operator_address'])
                    chainlist.append(chain_id)
        # Finished looping through all chains
    except Exception as e:
        print(e)


#make csv 
df=pd.DataFrame({"chain": chainlist, "address":validatorlist})
df.to_csv("validatorlist.csv")

#make the json, with chainlist as keys and validators as values
chainValidatorDict=dict(zip(chainlist,validatorlist))
with open('validatorlist.json', 'w') as f:
    json.dump(chainValidatorDict, f)
print("Done")
