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

    
    {"searchTerm": "women apparel"},
    {"searchTerm": "men apparel"},
    {"searchTerm": "men beauty"},
    {"searchTerm": "nivea"},
    {"searchTerm": "nova"},
    {"searchTerm": "sports shoes"},
    {"searchTerm": "backpack"},
    {"searchTerm": "travel pillow"},
    {"searchTerm": "sandals"},
    {"searchTerm": "women dress"},




]

for item_category in items_categories: 

    url = "https://scrape.smartproxy.com/v1/tasks"
    active_token = 'VTAwMDAxNTA5NTA6UFcxZTEyYzE2YTE5NjNhMTBkYjYxYjIwYWVkODZmMDQ2NzI='
    search_term = item_category.get("searchTerm", "")
    payload = {
        "target": "universal",
        "url": f"https://www.myntra.com/{search_term}",
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
            class_to_find = 'product-base'
            items = soup.find_all('li', class_=class_to_find)

            for index, item in enumerate(items):
                if index>15:
                    break
                try:
                    productTitle = item.find('img', class_='img-responsive').get('alt', '')
                    imageUrl = item.find('img', class_='img-responsive').get('src', '')
                    product_li = soup.find('li', class_='product-base')
                    
                    if product_li:
                        product_a = product_li.find('a')
                        if product_a:
                            href_value = product_a.get('href', '')
                            storeUrl = href_value
                            print("Href value:", href_value)
                        else:
                            print("No <a> tag found inside <li class='product-base'>")

                    
                    # Extract dealPrice
                    dealPrice_text = item.find('span', class_='product-discountedPrice').text.strip()
                    numeric_part = re.search(r'\d+', dealPrice_text)
                    # Check if numeric part is found and convert to integer
                    if numeric_part:
                        dealPrice = int(numeric_part.group())
                        print(dealPrice)
                    else:
                        print("No numeric value found in the dealPrice.")
                    
                    # Extract MRP
                    mrp_text = item.find('span', class_='product-strike').text.strip()
                    numeric_part_mrp = re.search(r'\d+', mrp_text)

                    # Check if numeric part is found and convert to integer
                    if numeric_part_mrp:
                        mrp = int(numeric_part_mrp.group())
                        print("MRP:", mrp)
                    else:
                        print("No numeric value found in the MRP.")
                        
                    deal = Deal()
                    deal.dealId = str(uuid.uuid4())

                    deal.store = 'myntra'
                    
                    deal.storeUrl= 'https://www.myntra.com/'+ storeUrl
                    deal.productTitle = productTitle
                    deal.imageUrl = imageUrl
                    deal.dealPrice =  dealPrice
                    deal.mrp = mrp
                    write_data_to_sheet(deal,search_term)

                except Exception as e:
                        print(e,index)
    time.sleep(10)            