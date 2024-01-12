import requests
import datetime
from config import api_key
import pandas as pd
def get_market_cap(coin_names, formatted_date, api_key=None):
    # Initialize an empty dictionary to store market cap data for each coin
    market_cap_data = {}

    for coin_name in coin_names:
        endpoint = f"https://api.coingecko.com/api/v3/coins/{coin_name}/history"
        # Set parameters for the API request
        params = {
            'vs_currency': 'usd',
            'date': formatted_date,
        }


        # Include API key in headers if provided
        headers = {}
        if api_key:
            headers['x-cg-demo-api-key'] = api_key

        # Make the API request
        response = requests.get(endpoint, params=params, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Check if data is available for the specified coin
            if data:
                # Extract and store the market cap for the coin
                market_cap_data[coin_name] = data['market_data']['market_cap']['usd']
            else:
                print(f"No data available for {coin_name} on {date}")
        else:
            print(f"Error {response.status_code}: {response.text}")

    return market_cap_data

def get_all_market_caps(dates,coin_names):
    all_market_caps=[]
    for date in dates:
        formatted_date=date.strftime("%d-%m-%Y")
        market_cap_result = get_market_cap(coin_names, formatted_date, api_key)
        date_market_cap_dict= {date:market_cap_result}
        for coin_name, market_cap in market_cap_result.items():
            print(f"{coin_name} Market Cap on {formatted_date}: ${market_cap:,}")
        all_market_caps.append(date_market_cap_dict)
    return all_market_caps

#"injective-protocol"
coin_names = ["akash-network","juno-network","kujira","fetch-ai","evmos","stargaze"]
dates = [datetime.datetime(2023, 1, 1),datetime.datetime(2024, 1, 1)]

all_market_caps=get_all_market_caps(dates,coin_names)

all_dataframes=[]
for market_caps in all_market_caps:
    df=pd.DataFrame(market_caps)
    all_dataframes.append(df)

result=pd.concat(all_dataframes, axis=1, join = "inner")
print(result)