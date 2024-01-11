import requests
import datetime
from config import api_key

def get_market_cap(coin_names, formatted_date, api_key=None):
    print(formatted_date)
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
            print(data)
            # Check if data is available for the specified coin
            if data:
                # Extract and store the market cap for the coin
                market_cap_data[coin_name] = data['market_data']['market_cap']['usd']
            else:
                print(f"No data available for {coin_name} on {date}")
        else:
            print(f"Error {response.status_code}: {response.text}")

    return market_cap_data

# Example usage:
coin_names = ["akash-network","juno-network","kujira","injective-protocol","fetch-ai","evmos","stargaze"]
date = datetime.datetime(2024, 1, 11) # Replace with your desired date
formatted_date=date.strftime("%d-%m-%Y")
print(formatted_date)
market_cap_result = get_market_cap(coin_names, formatted_date, api_key)

sum_caps=0

# Display the result
print(market_cap_result)
for coin_name, market_cap in market_cap_result.items():
    print(f"{coin_name} Market Cap on {date}: ${market_cap:,}")
    sum_caps=sum_caps+market_cap

print(sum_caps)
    