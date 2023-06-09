import requests
import pandas as pd
import utils
import json


def get_chain_list():
    chainlist = []

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
        print(chain.keys())
        # Get the chain ID and URL from the chain object
        chain_id = chain["name"]
        chainlist.append(chain_id)
    return (chainlist)


def get_all_chains_and_coingeckoid():
    chainlist = []
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
        print(chain.keys())
        chain_data = {}
        # Get the chain ID and URL from the chain object
        name = chain.get("name")
        coingecko_id = chain.get("coingecko_id")
        chain_data = {"name": name, "coingecko_id": coingecko_id}
        chainlist.append(chain_data)
    return (chainlist)


if __name__ == "__main__":
    get_chain_list()
