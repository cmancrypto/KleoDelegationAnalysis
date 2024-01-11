import requests
import datetime
from config import api_key

def get_market_cap(coin_names, date, api_key=None):
    # CoinGecko API endpoint for historical market data
    endpoint = "https://api.coingecko.com/api/v3/coins/markets"

    # Convert the date to a Unix timestamp (in seconds)
    timestamp = int(date.timestamp())

    # Initialize an empty dictionary to store market cap data for each coin
    market_cap_data = {}

    for coin_name in coin_names:
        # Set parameters for the API request
        params = {
            'vs_currency': 'usd',
            'ids': coin_name,
            'order': 'market_cap_desc',
            'per_page': 1,
            'page': 1,
            'date': timestamp
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
                market_cap_data[coin_name] = data[0]['market_cap']
            else:
                print(f"No data available for {coin_name} on {date}")
        else:
            print(f"Error {response.status_code}: {response.text}")

    return market_cap_data

# Example usage:
coin_names = ["akash-network","juno-network","archway","kujira","injective-protocol"]
date = datetime.datetime(2023, 1, 1)  # Replace with your desired date


market_cap_result = get_market_cap(coin_names, date, api_key)

# Display the result
for coin_name, market_cap in market_cap_result.items():
    print(f"{coin_name} Market Cap on {date}: ${market_cap:,}")
