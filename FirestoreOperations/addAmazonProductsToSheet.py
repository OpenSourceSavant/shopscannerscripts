from db_operations import get_smartproxy_amazon_token
import requests
from deal_structure import Deal
import uuid
from db_operations import create_firestore_document
import time
from google_sheets_operations import write_data_to_sheet

SUB_CATEGORY = 'sunscreen'
AMAZON_URL ='https://www.amazon.in/s?k=electronics&crid=3951DGJY4QKND&sprefix=electronic%2Caps%2C263&ref=nb_sb_noss_1'

items_categories= [
  {
    "amazonurl": "https://www.amazon.in/s?k=facewash",
    "category": "facewash"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=sunscreen",
    "category": "sunscreen"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=face+serum",
    "category": "face serum"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=moisturizer",
    "category": "moisturizer"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=hair+care",
    "category": "hair care"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=make+up",
    "category": "makeup"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=perfumes",
    "category": "perfumes"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=jeans",
    "category": "jeans"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=kurta",
    "category": "kurta"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=pajama",
    "category": "pajama"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=jackets",
    "category": "jackets"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=sweaters",
    "category": "sweaters"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=watches",
    "category": "watches"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=women+jeans",
    "category": "women jeans"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=kurti",
    "category": "kurti"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=women+jackets",
    "category": "women jackets"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=men+formal+shoes",
    "category": "men formal shoes"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=leather+shoes",
    "category": "leather shoes"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=flip+flops",
    "category": "flip flops"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=heels",
    "category": "heels"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=condoms",
    "category": "condoms"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=toothpaste",
    "category": "toothpaste"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=toothbrush",
    "category": "toothbrush"
  },
  {
    "amazonurl": "https://www.amazon.in/s?k=mouthwash",
    "category": "mouthwash"
  }
]

 
  


for item_category in items_categories: 

    url = "https://scrape.smartproxy.com/v1/tasks"
    active_token = get_smartproxy_amazon_token()
    print('##########USING ACTIVE TOKEN####################',active_token)
    payload = {
        "target": "amazon",
        "url": item_category['amazonurl'],
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
                print(item['url'])
                deal = Deal()
                deal.dealId = str(uuid.uuid4())

                deal.store = 'amazon'
                deal.storeUrl= 'https://amazon.in/dp/'+item['url'].split('/dp/', 1)[1][0:10]
                deal.productTitle = item['title']
                deal.imageUrl = item['url_image']
                deal.dealPrice =  item['price_upper']
                deal.mrp = item['price_strikethrough']
                write_data_to_sheet(deal,item_category['category'])
            
            time.sleep(10)
                

        except Exception as e:
            print(e)            