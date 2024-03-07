import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from deal_structure import Deal  # Assuming Deal is defined in deal_structure module
from get_amazon_data import get_amazon_data
import pytz
import uuid
import re
from db_operations import create_firestore_document
from send_msg_main_queue import send_message_to_queue
from urllib.parse import urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup

IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)


def check_duplicate_myntra_url(myntra_url):
    df = pd.read_csv('myntra_deals.csv')
    if not df.empty:
        df['message_time'] = pd.to_datetime(df['message_time'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(pytz.utc).dt.tz_convert(IST)

        # Filter rows with the same amazon_url in the last 40 minutes
        filtered_df = df[(df['myntra_url'] == myntra_url) & (df['message_time'] >= datetime.now(IST) - timedelta(minutes=40))]

        if not filtered_df.empty:
            print(f"The Myntra URL {myntra_url} is already present in the CSV file within the last 40 minutes.")
            return True

    return False

def main(url, messageReceived):
    myntra_url = ''
    
    if 'linkredirect.in' in url:
        parts = url.split('&dl=')
        myntra_url = parts[1]
        print(myntra_url)

   


    if myntra_url != '' and not check_duplicate_myntra_url(myntra_url):
        print('Myntra URL created and is not repeated')
        # Add the code to append the new record to the CSV file with amazon_url and current time
        url = "https://scrape.smartproxy.com/v1/tasks"
        active_token = 'VTAwMDAxNTA5NTA6UFcxZTEyYzE2YTE5NjNhMTBkYjYxYjIwYWVkODZmMDQ2NzI='

        payload = {
        "target": "universal",
        "url": myntra_url,
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
                    # Stop the loop after 4 iterations
                    if index >= 4:
                        break
                    #print(item)
                    productTitle = item.find('img', class_='img-responsive').get('alt', '')
                    # Extract image URL
                    imageUrl = item.find('img', class_='img-responsive').get('src', '')
                    
                    
                    # Extract dealPrice
                    dealPrice_text = item.find('span', class_='product-discountedPrice').text.strip()
                    numeric_part = re.search(r'\d+', dealPrice_text)
                    # Check if numeric part is found and convert to integer
                    if numeric_part:
                        dealPrice = int(numeric_part.group())
                        print(dealPrice)
                    else:
                        print("No numeric value found in the dealPrice.")
                    
                    product_li = item.find('li', class_='product-base')
                    if product_li:
                        product_a = product_li.find('a')
                        if product_a:
                            href_value = product_a.get('href', '')
                            storeUrl = href_value

                    
                    # Extract MRP
                    mrp_text = item.find('span', class_='product-strike').text.strip()
                    numeric_part_mrp = re.search(r'\d+', mrp_text)

                    # Check if numeric part is found and convert to integer
                    if numeric_part_mrp:
                        mrp = int(numeric_part_mrp.group())
                        print("MRP:", mrp)
                    else:
                        print("No numeric value found in the MRP.")
                    
                    
                    
                    # Extract discountPercentage
                    discountPercentage = round((mrp - dealPrice) * 100 / mrp) if mrp > 0 else 0
                    # Print or use the extracted values





                    print("Product Title:", productTitle)
                    print("Image URL:", imageUrl)
                    print("Deal Price:", dealPrice)
                    print("MRP:", mrp)
                    print("Discount Percentage:", discountPercentage)

                    deal = Deal()
                    deal.messageReceived = messageReceived
                    deal.productTitle = productTitle
                    deal.imageUrl = imageUrl
                    deal.dealPrice = dealPrice
                    deal.mrp = mrp
                    deal.dealPercent = discountPercentage
                    deal.store = 'myntra'
                    deal.dealId = str(uuid.uuid4())
                    deal.separatedText = re.sub(r"http\S+", "", messageReceived).replace('\n\n','\n')
                    deal.storeUrl= 'https://www.myntra.com/'+ storeUrl
                    if deal.dealPrice>0:
                        create_firestore_document(deal)
                        send_message_to_queue('deal', deal.to_json())

        new_record = pd.DataFrame({'myntra_url': [myntra_url], 'message_time': [datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')]})
        new_record.to_csv('myntra_deals.csv', mode='a', header=False, index=False)

        

            
if __name__ == "__main__":


    url = sys.argv[1]
    messageReceived = sys.argv[2]

    main(url, messageReceived)
