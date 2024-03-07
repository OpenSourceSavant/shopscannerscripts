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

IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)


def check_duplicate_amazon_url(amazon_url):
    df = pd.read_csv('amazon_deals.csv')
    if not df.empty:
        df['message_time'] = pd.to_datetime(df['message_time'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(pytz.utc).dt.tz_convert(IST)

        # Filter rows with the same amazon_url in the last 40 minutes
        filtered_df = df[(df['amazon_url'] == amazon_url) & (df['message_time'] >= datetime.now(IST) - timedelta(minutes=40))]

        if not filtered_df.empty:
            print(f"The Amazon URL {amazon_url} is already present in the CSV file within the last 40 minutes.")
            return True

    return False

def main(url, messageReceived):
    amazon_url = ''
    if 'dp' in url or '/d/' in url or 'indiadesire' in url:
        id = url.split('/dp/', 1)[1][0:10] if 'dp' in url else url.split('amazon.in/d/', 1)[1][0:10] if '/d/' in url else url.split('redirectpid1=', 1)[1][0:10]
        amazon_url = f'https://www.amazon.in/dp/{id}'
    elif 'product' in url:
        id = url.split('product/', 1)[1][0:10]
        amazon_url = f'https://www.amazon.in/dp/{id}'

    print('########AMAZON URL##########',amazon_url)

    if amazon_url != '' and not check_duplicate_amazon_url(amazon_url):
        print('amazon URL created and is not repeated')
        # Add the code to append the new record to the CSV file with amazon_url and current time
        new_record = pd.DataFrame({'amazon_url': [amazon_url], 'message_time': [datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')]})
        new_record.to_csv('amazon_deals.csv', mode='a', header=False, index=False)

        ## Now Fetch amazon data using Scraper
        ## Also create deal object now
        deal = Deal()
        deal.messageReceived = messageReceived
        deal.finalMessage = messageReceived
        deal.dealId = str(uuid.uuid4())
        deal.store = 'amazon'
        amazon_data = get_amazon_data(amazon_url)
        deal.separatedText = re.sub(r"http\S+", "", messageReceived).replace('\n\n','\n')
        deal.storeUrl = amazon_url + "?tag=shopscanner0a-21"
        if amazon_data:
            deal.productTitle = amazon_data["productTitle"]
            deal.imageUrl = amazon_data["imageUrl"]
            deal.dealPrice = amazon_data["dealPrice"]
            deal.mrp = amazon_data["mrp"]
            deal.dealPercent = round((deal.mrp - deal.dealPrice) * 100 / deal.mrp)
            deal.category = amazon_data["category"]
            ##create firestore document
            if deal.dealPrice>0:
                create_firestore_document(deal)
                send_message_to_queue('deal', deal.to_json())

            
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <url> <message_received>")
        sys.exit(1)

    url = sys.argv[1]
    messageReceived = sys.argv[2]

    main(url, messageReceived)
