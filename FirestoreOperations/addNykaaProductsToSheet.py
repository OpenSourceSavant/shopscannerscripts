import requests
from deal_structure import Deal
import uuid
import time
import json
from bs4 import BeautifulSoup
import re
from google_sheets_operations import write_data_to_sheet
requests.packages.urllib3.disable_warnings()


items_categories = [


    {"searchTerm": "beauty"},
    {"searchTerm": "skincare"},
    {"searchTerm": "facewash"},
    {"searchTerm": "hair oil"},
    {"searchTerm": "face serum"},
    {"searchTerm": "shampoo"},
    {"searchTerm": "sunscreen"},
    {"searchTerm": "lotion"},
    {"searchTerm": "polish"},
    {"searchTerm": "cream"},
    {"searchTerm": "deo"},
    {"searchTerm": "perfume"},
    {"searchTerm": "makeup"},
    {"searchTerm": "conditioner"},
    {"searchTerm": "gift pack"},
    {"searchTerm": "Toothpaste"},
    {"searchTerm": "bath"},
    {"searchTerm": "soap"},
    {"searchTerm": "lipcare"},
    {"searchTerm": "face wipes"},
    {"searchTerm": "sheet masks"},

   




]

for item_category in items_categories: 

    url = "https://scrape.smartproxy.com/v1/tasks"
    active_token = 'VTAwMDAxNTA5NTA6UFcxZTEyYzE2YTE5NjNhMTBkYjYxYjIwYWVkODZmMDQ2NzI='
    search_term = item_category.get("searchTerm", "")
    payload = {
        "target": "universal",
        "url": f"https://www.nykaa.com/search/result/?q={search_term}",
        "locale": "en-us",
        "geo": "India",
        "headless": "html",
        "device_type": "desktop_chrome"
        }
    
    headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {active_token}"
        }

    
    response = requests.post(url, json=payload, headers=headers)
    data = json.loads(response.text)
    result_data = {}  # Dictionary to store the result fields

    if response.status_code == 200:
        data = response.json()
        #print(data)
        if data:     
            html_content = data.get('results', [])[0].get('content', '') if data.get('results') else ''
            soup = BeautifulSoup(html_content, 'html.parser')
            class_to_find = 'productWrapper css-17nge1h'
            items = soup.find_all('div', class_=class_to_find)

            for index, item in enumerate(items):
                if index>15:
                    break
                try:
                    productTitle = item.find('div', class_='css-xrzmfa').text.strip()
                    imageUrl = item.find('img', class_='css-11gn9r6').get('src', '')

                    dealPrice_text = item.find('span', class_='css-111z9ua').text.strip()
                    numeric_part = re.search(r'\d+', dealPrice_text)
                    dealPrice = int(numeric_part.group()) if numeric_part else None

                    mrp_text = item.find('span', class_='css-17x46n5').find('span').text.strip()
                    numeric_part_mrp = re.search(r'\d+', mrp_text)
                    mrp = int(numeric_part_mrp.group()) if numeric_part_mrp else None

                    discountPercentage = round((mrp - dealPrice) * 100 / mrp) if mrp and dealPrice else None

                    storeUrl = item.find('a', class_='css-qlopj4')['href']
                    print(storeUrl)                    
                    deal = Deal()
                    deal.dealId = str(uuid.uuid4())
                    deal.store = 'nykaa'
                    deal.storeUrl= 'https://www.nykaa.com'+ storeUrl
                    deal.productTitle = productTitle
                    deal.imageUrl = imageUrl
                    deal.dealPrice =  dealPrice
                    deal.mrp = mrp
                    write_data_to_sheet(deal,search_term)

                except Exception as e:
                        print(e,index)
    time.sleep(10)            