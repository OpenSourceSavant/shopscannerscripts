import os
import requests
import csv
import json
from db_operations import get_smartproxy_amazon_token
from bs4 import BeautifulSoup

def get_amazon_data(amazon_url):
    url = "https://scrape.smartproxy.com/v1/tasks"
    active_token = get_smartproxy_amazon_token()
    print('##########ACTIVE TOKEN####################',active_token)
    payload = {
        "target": "amazon",
        "url": amazon_url,
        "parse": True,
        "device_type": "desktop_chrome"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {active_token}"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    result_data = {}  # Dictionary to store the result fields

    if response.status_code == 200:
        data = response.json()
        #print(data)
        if data:       
            result_data['productTitle'] = data['results'][0]['content']['title']
            result_data['imageUrl'] = data['results'][0]['content']['images'][0]
            result_data['dealPrice'] = 0
            result_data['mrp'] = 0

            ##Get Brand Info
            #result_data['brand'] = data['results'][0]['content']['brand']

            #print(result_data['brand'])

           # Check if price_buybox or price or deal_price exists and set dealPrice accordingly
            if 'price_buybox' in data['results'][0]['content']:
                result_data['dealPrice'] = data['results'][0]['content']['price_buybox']
            elif 'price' in data['results'][0]['content']:
                result_data['dealPrice'] = data['results'][0]['content']['price']
            elif 'deal_price' in data['results'][0]['content']:
                result_data['dealPrice'] = data['results'][0]['content']['deal_price']
            
            #print(data['results'][0]['content'])

            
            # Set mrp if price_strikethrough exists
            if 'price_strikethrough' in data['results'][0]['content']:
                result_data['mrp'] = data['results'][0]['content']['price_strikethrough']
                
            result_data['category'] = data['results'][0]['content']['category'][0]['ladder'][0]['name']


            # getCategory(deal)
        else:
            print("No data found in the response.")
    else:
        print("Get Product Info from Amazon Request failed with status code:", response.status_code)

    return result_data

# Usage example:
# deal_data = get_amazon_data(your_deal_object)
# print(json.dumps(deal_data))
