import requests
import pandas as pd
import utils 
import json

def get_chain_slip(make_csv: bool = False) -> list:
    chainlist=[]

    # Define the URL for the chains list page
    chains_url = "https://chains.cosmos.directory/"

    # Send a GET request to the chains list page
    response = utils.get_API_data_with_retry(chains_url)

    # Check if the response was successful (status code 200)
    if response.status_code != 200:
        raise ValueError("Failed to fetch chains list page")

    # Extract the list of chains from the response
    chains = response.json()
    
    for chain in chains["chains"]:
        # Get the chain ID and URL from the chain object
        chain_id = chain["name"]
        chainurl=f"https://chains.cosmos.directory/{chain_id}/chain"
        response = utils.get_API_data_with_retry(chainurl)
        try:
            slip44=response.json()["slip44"]
        except Exception as e: 
            slip44 = None; 
        chainlist.append({f"{chain_id}":slip44})
    
    if make_csv==True:
        with open('chainslip.json', 'w') as f:
            json.dump(chainlist, f)
        
    return(chainlist)


if __name__ == "__main__":
    get_chain_slip(make_csv=True)