import os
import requests
from dotenv import load_dotenv
import tenacity
from datetime import datetime
import pandas as pd

##this is deprecated - can do easier with chain directory which does it all for us 
@tenacity.retry(stop=tenacity.stop_after_delay(10))
def get_prices(coingecko_id_list : list) -> requests.models.Response:

    load_dotenv()
    ##this is a CMC API_Key
    API_KEY = os.getenv('API_KEY')

    slugs = coingecko_id_list

    # URL for the CoinMarketCap API
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    # parameters for the API request, including the API key and the list of slugs
    params = {
    'slug': ','.join(slugs),
    'convert': 'USD'
    }

    # headers for the API request, including the API key
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
    }

    # send the API request and get the response
    response = requests.get(url, headers=headers, params=params)
    # check if the request was successful
    if response.status_code == 200:
    # parse the response JSON data
        data = response.json()

        # iterate over the cryptocurrency data and build a dictionary with the current price of each cryptocurrency
        prices = {}
        for id, info in data['data'].items():
            slug = info['slug']
            price = info['quote']['USD']['price']
            prices[slug] = price
    else:
        # if the request was unsuccessful, print the error message
        print(f'Request failed with status code {response.status_code}: {response.text}')

    return prices

##only returns current price, does not return historical prices
def get_prices_from_cosmos_api(chain : str) -> float: 
    url=f"https://chains.cosmos.directory/{chain}"
    response= requests.get(url)
    data= response.json()
    try:
        prices=list(data["chain"]["prices"]["coingecko"].values())
        #have to assume that 0 is the native token price
        price=prices[0]["usd"]
        return price
    except KeyError as e:
        print(f"no key for {e}")
        #return price of zero
        return 0

def get_delegator_list(chain_name : str, date : str):
    url=f"https://snapshots.dev.kleomed.es/api/v1/delegator/snapshots/{chain_name}/{date}"
    response= requests.get(url)
    if response.status_code ==200:
        data= response.json()
        return data
    else: 
        return None


def get_chain_revenues(chains : list, date : str = datetime.now().strftime("%y-%m-%d") ) -> list:
    chain_revenues=[]
    for chain in chains:
        try:
            data=get_delegator_list(chain_name=chain,date=date)
            delegators = data["delegators"]
            delegator_df=pd.DataFrame(delegators)
            raw_amount_sum=delegator_df["amount"].sum()
            decimal_divisor=pow(10,get_decimals(chain))
            #this adjusts for the decimals in the return and gets it into "denom" for prices
            amount_sum = raw_amount_sum/decimal_divisor
            price=get_prices_from_cosmos_api(chain)
            value_delegated=amount_sum*price
            chain_dict={"chain_name":chain,"value_delegated":value_delegated}
            chain_revenues.append(chain_dict)
        except Exception as e:
            print(e)
    return chain_revenues

def get_chain_shares(chain_revenues : list, tokens_to_split: float):
    revenue_df=pd.DataFrame(chain_revenues)
    total_value=revenue_df["value_delegated"].sum()
    revenue_df["share"]=revenue_df["value_delegated"]/total_value
    print(revenue_df.to_dict('records'))
    return revenue_df.to_dict('records')


def get_decimals(chain : str):
    url=f"https://chains.cosmos.directory/{chain}"
    response= requests.get(url)
    data=response.json()
    denom=data["chain"]["staking"]["staking_tokens"][0]["denom"]
    #check if the decimals in 
    for assets in data["chain"]["assets"]:
        if assets["denom"] == denom:
            decimals = assets["decimals"]
            return decimals
    raise ValueError(f"No asset where denom = {denom}")

#get_prices_from_cosmos_api("juno")
#get_chain_revenues(["juno"],"2023-04-30")
revenues=get_chain_revenues(["juno","akash"],"2023-05-04")
get_chain_shares(revenues)