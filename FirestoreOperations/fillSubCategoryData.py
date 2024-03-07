from db_operations import get_smartproxy_amazon_token
import requests
from deal_structure import Deal
import uuid
from db_operations import create_firestore_document
import time
SUB_CATEGORY = 'sunscreen'
AMAZON_URL ='https://www.amazon.in/s?k=laptop&rh=p_n_deal_type%3A26921224031&dc&qid=1709571337&rnid=26921223031&ref=sr_nr_p_n_deal_type_2&ds=v1%3AnR7dY%2FRPv0bPqDYYoYHMfKMkqb4KgSCf%2BuqyCOt6O7E'

url = "https://scrape.smartproxy.com/v1/tasks"
active_token = get_smartproxy_amazon_token()
print('##########USING ACTIVE TOKEN####################',active_token)
payload = {
    "target": "amazon",
    "url": AMAZON_URL,
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
    
    try:
        data = response.json()
        #print(data)
        items = data['results'][0]['content']['results']['organic']
        for index, item in enumerate(items):
            
            deal = Deal()
            deal.dealId = str(uuid.uuid4())
            deal.store = 'amazon'
            deal.productTitle = item['title']
            deal.imageUrl = item['url_image']
            deal.dealPrice =  item['price_upper']
            deal.mrp = item['price_strikethrough']
            if deal.dealPrice>0:
                create_firestore_document(deal)
                time.sleep(20)

    except Exception as e:
        print(e)            