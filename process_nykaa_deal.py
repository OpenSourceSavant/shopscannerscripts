import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from deal_structure import Deal  # Assuming Deal is defined in deal_structure module
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


def check_duplicate_nykaa_url(nykaa_url):
    df = pd.read_csv('nykaa_deals.csv')
    if not df.empty:
        df['message_time'] = pd.to_datetime(df['message_time'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(pytz.utc).dt.tz_convert(IST)

        # Filter rows with the same amazon_url in the last 40 minutes
        filtered_df = df[(df['nykaa_url'] == nykaa_url) & (df['message_time'] >= datetime.now(IST) - timedelta(minutes=40))]

        if not filtered_df.empty:
            print(f"The Nykaa URL {nykaa_url} is already present in the CSV file within the last 40 minutes.")
            return True

    return False

def main(url, messageReceived):
    nykaa_url = ''
    
    if 'linkredirect.in' in url:
        parts = url.split('&dl=')
        nykaa_url = parts[1]
        print(nykaa_url)

   


    if nykaa_url != '' and not check_duplicate_nykaa_url(nykaa_url):
        print('nykaa URL created and is not repeated')
        # Add the code to append the new record to the CSV file with myntra url and current time
        url = "https://scrape.smartproxy.com/v1/tasks"
        active_token = 'VTAwMDAxNTA5NTA6UFcxZTEyYzE2YTE5NjNhMTBkYjYxYjIwYWVkODZmMDQ2NzI='

        payload = {
        "target": "universal",
        "url": nykaa_url,
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
                class_to_find = 'productWrapper css-17nge1h'
                items = soup.find_all('div', class_=class_to_find)

                for index, item in enumerate(items):
                    # Stop the loop after 4 iterations
                    if index >= 4:
                        break
                    print(item)
                    productTitle = item.find('div', class_='css-xrzmfa').text.strip()

                    # Extract image URL
                    imageUrl = item.find('img', class_='css-11gn9r6').get('src', '')
                    
                    
                    # Extract dealPrice
                    dealPrice_text = item.find('span', class_='css-111z9ua').text.strip()
                    numeric_part = re.search(r'\d+', dealPrice_text)
                    dealPrice = int(numeric_part.group()) if numeric_part else None
                    print("Deal Price:", dealPrice)
                    


                    
                    # Extract MRP
                    mrp_text = item.find('span', class_='css-17x46n5').find('span').text.strip()
                    numeric_part_mrp = re.search(r'\d+', mrp_text)
                    mrp = int(numeric_part_mrp.group()) if numeric_part_mrp else None
                    print("MRP:", mrp)
                    
                    
                    
                    # Extract discountPercentage
                    discountPercentage = round((mrp - dealPrice) * 100 / mrp) if mrp and dealPrice else None
                    print("Discount Percentage:", discountPercentage)





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
                    deal.store = 'nykaa'
                    deal.dealId = str(uuid.uuid4())
                    deal.separatedText = re.sub(r"http\S+", "", messageReceived).replace('\n\n','\n')
                    deal.storeUrl = nykaa_url
                    if deal.dealPrice>0:
                        create_firestore_document(deal)
                        send_message_to_queue('deal', deal.to_json())
                    new_record = pd.DataFrame({'nykaa_url': [nykaa_url], 'message_time': [datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')]})
                    new_record.to_csv('nykaa_deals.csv', mode='a', header=False, index=False)

        else:
            print('Nykaa Token Not Working')
        
        

            
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <url> <message_received>")
        sys.exit(1)

    url = sys.argv[1]
    messageReceived = sys.argv[2]

    main(url, messageReceived)
