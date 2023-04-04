import requests
import pandas as pd
chainlist=[]
validatorlist=[]

# Define the URL for the chains list page
chains_url = "https://chains.cosmos.directory/"

# Send a GET request to the chains list page
response = requests.get(chains_url)

# Check if the response was successful (status code 200)
if response.status_code != 200:
    raise ValueError("Failed to fetch chains list page")

# Extract the list of chains from the response
chains = response.json()

# Loop through each chain in the list
for chain in chains["chains"]:
    # Get the chain ID and URL from the chain object
    chain_id = chain["name"]
    chain_url = f"https://rest.cosmos.directory/{chain_id}/cosmos/staking/v1beta1/validators"

    # Send a GET request to the validators endpoint for this chain
    response = requests.get(f"{chain_url}")

    # Check if the response was successful (status code 200)
    if response.status_code != 200:
        print(f"Failed to fetch validators for chain {chain_id}")
        continue

    # Extract the list of validators from the response
    validators = response.json()["validators"]

    # Loop through each validator in the list
    for validator in validators:
        # Check if the validator's moniker is Kleomedes
        if validator["description"]["moniker"] == "Kleomedes":
            # Found the Kleomedes validator, print its address
            print(f"Kleomedes validator found on chain {chain_id}, address: {validator['operator_address']}")
            validatorlist.append(validator['operator_address'])
            chainlist.append(chain_id)
# Finished looping through all chains
df=pd.DataFrame({"chain": chainlist, "address":validatorlist})
df.to_json('validatorlist.json', orient='records')
df.to_csv("validatorlist.csv")
print("Done")
