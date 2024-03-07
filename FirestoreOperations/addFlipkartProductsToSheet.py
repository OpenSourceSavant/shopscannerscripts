import requests
from deal_structure import Deal
import uuid
import time
requests.packages.urllib3.disable_warnings()
import json

headers = {
    'Fk-Affiliate-Id': 'arorakara1',
    'Fk-Affiliate-Token': '445cfc7694e9424f8547980ae80ac08a'
}

api_url = 'https://affiliate-api.flipkart.net/affiliate/1.0/search.json'

params = {
'query': 'iphone',
'resultCount': 5 # Limiting result count to a maximum of 10
}
response = requests.get(api_url, headers=headers, params=params)
data = json.loads(response.text)
print(data)
#items = data['productInfoList']
##for index, item in enumerate(items):
#        print(item['productBaseInfo']['productIdentifier']['productId'])


                